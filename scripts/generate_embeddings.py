"""
generate_embeddings.py

Standalone script to generate semantic embeddings for all enriched movies
in the CineMind database using a local sentence-transformer model on GPU.

Usage on DGX Spark:
    pip install sentence-transformers torch psycopg2-binary pgvector sqlalchemy
    python generate_embeddings.py [--dry-run] [--batch-size N]

Prerequisites:
    • DB reachable at connection string below (or set PGHOST/PGUSER/PASSWORD)
    • GPU available (falls back to CPU if not)
    • sentence-transformers + torch installed
"""

import argparse
import logging
import os
import sys
import time

import psycopg
import torch

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── DB ──────────────────────────────────────────────────────────────────

# Override with environment variables or CLI args
DB_HOST = os.getenv("PGHOST", "localhost")
DB_USER = os.getenv("PGUSER", "cinemind_user")
DB_PASS = os.getenv("PGPASSWORD", "password")
DB_NAME = os.getenv("PGDATABASE", "cinemind")
DB_PORT = os.getenv("PGPORT", "5432")


def get_connection():
    return psycopg.connect(
        host=DB_HOST, port=int(DB_PORT),
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        autocommit=False,
    )


# ── Embedding Model ─────────────────────────────────────────────────────

MODEL_NAME = "Alibaba-NLP/gte-Qwen2-7B-instruct"


def load_model():
    from sentence_transformers import SentenceTransformer
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading model {MODEL_NAME} on {device}...")
    if device == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    model = SentenceTransformer(MODEL_NAME, device=device)
    logger.info("Model loaded.")
    return model


# ── Semantic Text Builder ──────────────────────────────────────────────

def build_semantic_text(movie):
    """Build searchable text for embedding from one movie row."""
    parts = []

    title = movie["title"] or movie["imdb_title"]
    if title:
        parts.append(title)

    genres = movie["genres"] or []
    if genres:
        parts.append(f"Genres: {', '.join(genres)}")

    overview = movie.get("overview")
    if overview:
        parts.append(overview)

    director = movie.get("director")
    if director:
        parts.append(f"Director: {director}")

    cast = [c for c in [movie.get("lead_actor"), movie.get("lead_actor_2"), movie.get("lead_actor_3")] if c]
    if cast:
        parts.append(f"Actors: {', '.join(cast)}")

    tags = movie.get("editorial_tags") or []
    if tags:
        parts.append(f"Tags: {', '.join(tags)}")

    return ". ".join(parts)


# ── Main ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate movie embeddings on DGX Spark")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch-size", type=int, default=64, help="GPU batch size (default: 64)")
    parser.add_argument("--model", type=str, default=MODEL_NAME, help="Sentence-transformers model")
    parser.add_argument("--host", type=str, default=DB_HOST, help="DB host")
    parser.add_argument("--user", type=str, default=DB_USER, help="DB user")
    parser.add_argument("--password", type=str, default=DB_PASS, help="DB password")
    parser.add_argument("--database", type=str, default=DB_NAME, help="DB name")
    args = parser.parse_args()

    global DB_HOST, DB_USER, DB_PASS, DB_NAME
    DB_HOST = args.host
    DB_USER = args.user
    DB_PASS = args.password
    DB_NAME = args.database
    MODEL_NAME = args.model  # type: ignore

    conn = get_connection()
    cur = conn.cursor()

    # Check pgvector extension
    cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
    if not cur.fetchone():
        logger.warning("pgvector extension not found — creating it...")
        try:
            cur.execute("CREATE EXTENSION vector")
            logger.info("pgvector extension created.")
        except Exception as e:
            logger.error(f"Cannot create pgvector extension: {e}")
            logger.error("Run as superuser: psql -c 'CREATE EXTENSION vector;'")
            sys.exit(1)

    # Count total movies to embed
    cur.execute("SELECT COUNT(*) FROM movies WHERE tmdb_id IS NOT NULL")
    total = cur.fetchone()[0]
    logger.info(f"Found {total} enriched movies")

    # Fetch all movies in one query
    cur.execute("""
        SELECT id, imdb_title, title, genres, overview, director,
               lead_actor, lead_actor_2, lead_actor_3, editorial_tags
        FROM movies
        WHERE tmdb_id IS NOT NULL AND embedding IS NULL
        ORDER BY id
    """)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    movies = [dict(zip(cols, row)) for row in rows]

    to_embed = len(movies)
    if not to_embed:
        logger.info("All movies already have embeddings. Nothing to do.")
        return

    logger.info(f"Movies to embed: {to_embed}")

    if args.dry_run:
        logger.info("Dry run — showing sample semantic text:")
        sample = movies[:3]
        for m in sample:
            text = build_semantic_text(m)
            logger.info(f"  [{m['id']}] {m['title']}: {text[:120]}...")
        logger.info(f"Dry run complete. {to_embed} movies would be embedded.")
        return

    # Load model
    model = load_model()

    # Build semantic texts
    logger.info("Building semantic texts...")
    texts = [build_semantic_text(m) for m in movies]

    # Feed-forward encoding in batches
    logger.info(f"Encoding {len(texts)} texts in batches of {args.batch_size}...")
    all_embeddings = []
    start = time.time()

    for i in range(0, len(texts), args.batch_size):
        batch = texts[i : i + args.batch_size]
        emb = model.encode(
            batch,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        all_embeddings.extend(emb.tolist())

        elapsed = time.time() - start
        processed = i + len(batch)
        logger.info(f"  Encoded {processed}/{len(texts)}  ({elapsed:.1f}s elapsed)")

    elapsed_total = time.time() - start
    logger.info(f"All embeddings generated in {elapsed_total:.1f}s")
    emb_dim = len(all_embeddings[0])
    logger.info(f"Embedding dimension: {emb_dim}")

    # Write back to DB in batches
    logger.info("Writing embeddings to database...")
    update_sql = "UPDATE movies SET embedding = %s::vector WHERE id = %s"

    updated = 0
    for emb, movie in zip(all_embeddings, movies):
        try:
            cur.execute(update_sql, (emb, movie["id"]))
            updated += 1
        except Exception as e:
            logger.warning(f"Failed to write embedding for id={movie['id']}: {e}")

    conn.commit()
    logger.info(f"Updated {updated}/{to_embed} movies in database.")

    # Final stats
    cur.execute("SELECT COUNT(*) FROM movies WHERE embedding IS NOT NULL")
    has_emb = cur.fetchone()[0]
    logger.info(f"Movies with embeddings: {has_emb}/{total} ({has_emb/total*100:.1f}%)")


if __name__ == "__main__":
    main()
