"""
Enrich movies in the database with TMDB metadata.

For each movie:
  1. Search TMDB by title + year → match with confidence scoring
  2. Fetch full movie details, poster, backdrop, trailer, credits, keywords
  3. Generate editorial tags (rules-based)
  4. Classify audience
  5. Generate semantic embeddings via gte-Qwen2-7B on GPU (DGX Spark)
  6. Store everything in PostgreSQL (no runtime API calls needed after this)

Usage:
  uv run python scripts/enrich_movies.py [--dry-run [--limit N]]

  --dry-run          Run enrichment without writing to DB (debug mode)
  --limit N          Process only the first N movies (default: all)
  --skip-embedding   Skip AI embedding generation (faster, no GPU needed)

Requires:
  TMDB_READ_ACCESS_TOKEN in .env
  NVIDIA GPU (recommended) for embedding generation
"""

from __future__ import annotations

import argparse
import difflib
import json
import logging
import os
import time
import re
from collections import defaultdict
from datetime import datetime
from math import floor
from typing import Any

import requests as req
from sqlalchemy import select
from sqlalchemy.orm import Session

from cinemind.db.models import Movie
from cinemind.db.session import SessionLocal

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ── Embedding Model ────────────────────────────────────────────────

_EMBEDDING_MODEL = None
_EMBEDDING_MODEL_NAME = "Alibaba-NLP/gte-Qwen2-7B-instruct"
_EMBEDDING_DIM = 1536


def _get_embedding_model():
    """Lazy-load the embedding model once, using GPU if available."""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is not None:
        return _EMBEDDING_MODEL, _EMBEDDING_MODEL_NAME

    from sentence_transformers import SentenceTransformer
    from torch import cuda

    device = "cuda" if cuda.is_available() else "cpu"
    logger.info(f"Loading embedding model {_EMBEDDING_MODEL_NAME} on {device}...")
    _EMBEDDING_MODEL = SentenceTransformer(_EMBEDDING_MODEL_NAME, device=device)
    logger.info("Embedding model loaded.")
    return _EMBEDDING_MODEL, _EMBEDDING_MODEL_NAME


TMDB_POSTER_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE = "https://image.tmdb.org/t/p/original"

GENRE_MAP_REVERSE = {
    "action": [28, "Action"],
    "comedy": [35, "Comedy"],
    "drama": [18, "Drama"],
    "sci-fi": [878, "Science Fiction"],
    "thriller": [53, "Thriller"],
    "horror": [27, "Horror"],
    "romance": [10749, "Romance"],
}

EDITORIAL_TAG_RULES: list[dict[str, Any]] = [
    # Each rule: { "tags": [...], "condition": function(genres, overview, keywords) -> bool }
    {"tags": ["Dark", "Suspenseful"], "genre_in": ["thriller", "horror"], "overview_words": ["dark", "terror", "haunted", "murder", "psychological"]},
    {"tags": ["Atmospheric", "Mind-Bending"], "genre_in": ["sci-fi", "thriller"], "overview_words": ["future", "cyber", "dystopian", "consciousness", "reality", "simulation"]},
    {"tags": ["Epic", "Action-Packed"], "genre_in": ["action", "sci-fi"], "overview_words": ["war", "battle", "epic", "journey", "quest", "destroy"]},
    {"tags": ["Heartwarming", "Family Friendly"], "genre_in": ["comedy", "romance"], "overview_words": ["love", "family", "heartwarming", "family-friendly", "friendship"]},
    {"tags": ["Underrated"], "genre_in": [], "min_vote_count": None, "max_rating": 6.5},
    {"tags": ["Cult Classic"], "genre_in": [], "year_max": 2005, "overview_words": ["cult", "iconic", "legendary", "classic", "underground"]},
    {"tags": ["Suspenseful", "Thrilling"], "genre_in": ["thriller", "horror"], "overview_words": ["chase", "escape", "stalker", "serial", "killer"]},
    {"tags": ["Romantic"], "genre_in": ["romance", "drama"], "overview_words": ["love", "romance", "heartbreak", "passion"]},
    {"tags": ["Family Friendly"], "genre_in": ["comedy"], "overview_words": ["family", "funny", "adventure", "animated"]},
]


def setup_tmdb(token: str) -> None:
    """Configure TMDB API with either an API key or a Read Access Token."""
    global TMDB_TOKEN
    TMDB_TOKEN = token


TMDB_TOKEN = None
TMDB_API = "https://api.themoviedb.org/3"


def _tmdb_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "Accept": "application/json",
    }


def _tmdb_get(endpoint: str, params: dict[str, str | int] | None = None) -> dict:
    resp = req.get(f"{TMDB_API}/{endpoint}", headers=_tmdb_headers(), params=params or {}, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ── Confidence Matching ────────────────────────────────────────────────

def compute_confidence(
    tmdb_title: str,
    db_title: str,
    tmdb_year: int | None,
    db_year: int | None,
) -> float:
    """Return confidence score 0–100 for a TMDB match."""
    title_norm_tmdb = re.sub(r'[^a-z0-9 ]', '', tmdb_title.lower()).strip()
    title_norm_db = re.sub(r'[^a-z0-9 ]', '', db_title.lower()).strip()

    if title_norm_tmdb == title_norm_db:
        title_score = 1.0
    else:
        title_score = difflib.SequenceMatcher(None, title_norm_db, title_norm_tmdb).ratio()

    if db_year is not None and tmdb_year is not None:
        year_diff = abs(db_year - tmdb_year)
        if year_diff == 0:
            year_score = 1.0
        elif year_diff == 1:
            year_score = 0.8
        elif year_diff == 2:
            year_score = 0.5
        elif year_diff <= 5:
            year_score = 0.2
        else:
            year_score = 0.0
    else:
        year_score = 0.3

    return round((title_score * 0.7 + year_score * 0.3) * 100, 1)


def search_and_match_movie(title: str, year: int | None, min_confidence: float = 70.0) -> dict | None:
    """Search TMDB for a movie and return best match if confidence ≥ min_confidence."""
    data = _tmdb_get("search/movie", {"query": title, "language": "en", "include_adult": "false"})

    results = data.get("results", [])
    if not results:
        return None

    best = None
    best_confidence = 0.0

    for result in results:
        r_title = result.get("title", "") or ""
        release = result.get("release_date") or ""
        r_year = int(release[:4]) if release and len(release) >= 4 else None

        conf = compute_confidence(r_title, title, r_year, year)
        if conf > best_confidence:
            best_confidence = conf
            best = result

    if best and best_confidence >= min_confidence:
        best["_confidence"] = best_confidence
        return best

    return None


# ── Fetch Steps ────────────────────────────────────────────────────────

def fetch_movie_details(tmdb_id: int) -> dict:
    return _tmdb_get(f"movie/{tmdb_id}", {
        "language": "en",
        "append_to_response": "keywords,credits,videos",
    })


def build_poster_url(data: dict) -> str | None:
    if data.get("poster_path"):
        return f"{TMDB_POSTER_BASE}{data['poster_path']}"
    return None


def build_backdrop_url(data: dict) -> str | None:
    if data.get("backdrop_path"):
        return f"{TMDB_BACKDROP_BASE}{data['backdrop_path']}"
    return None


def build_trailer_url(data: dict) -> str | None:
    videos = data.get("videos", {}).get("results", [])
    priority_order = [
        "Official Trailer",
        "Trailer",
        "Official Teaser",
        "Teaser",
        "Clip",
    ]
    for priority in priority_order:
        for v in videos:
            if (v.get("site") == "YouTube"
                    and priority.lower() in v.get("name", "").lower()
                    and v.get("type", "").lower() in ("trailer", "teaser", "clip")):
                return f"https://www.youtube.com/watch?v={v['key']}"

    # Fallback: first YouTube trailer
    for v in videos:
        if v.get("site") == "YouTube" and v.get("type", "").lower() in ("trailer", "teaser"):
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None


def extract_credits(data: dict) -> tuple[str | None, tuple[str | None, str | None, str | None]]:
    credits = data.get("credits", {})
    # Director
    director = None
    for member in credits.get("crew", []):
        if member.get("job") == "Director":
            director = member.get("name")
            break

    # Top 3 cast
    cast_list = credits.get("cast", [])
    actors = []
    seen = set()
    for member in cast_list:
        name = member.get("name")
        if name and name not in seen and member.get("character"):
            actors.append(name)
            seen.add(name)
        if len(actors) == 3:
            break

    while len(actors) < 3:
        actors.append(None)

    return director, tuple(actors)


def classify_audience(data: dict) -> str:
    genres = data.get("genres", [])
    genre_names = {g.get("name", "").lower() for g in genres}

    if "horror" in genre_names or "thriller" in genre_names:
        return "adults"
    if "action" in genre_names or "science fiction" in genre_names or "drama" in genre_names:
        return "teens"
    if "comedy" in genre_names or "romance" in genre_names or "animation" in genre_names or "family" in genre_names:
        return "family"
    return "teens"


def generate_editorial_tags(
    genres: list[dict],
    overview: str | None,
    keywords: list[str],
    rating: float | None,
    vote_count: int | None,
    year: int | None,
) -> list[str]:
    """Generate 3–5 editorial tags based on content analysis."""
    genre_names = {g.get("name", "").lower() for g in genres}
    ov_lower = (overview or "").lower()

    matched_tags: set[str] = set()

    # Genre-based tags
    genre_tag_map = {
        "action": {"Action-Packed"},
        "sci-fi": {"Sci-Fi"},
        "horror": {"Dark", "Suspenseful"},
        "comedy": {"Comedic"},
        "drama": {"Emotional"},
        "thriller": {"Suspenseful", "Thrilling"},
        "romance": {"Romantic"},
        "adventure": {"Adventure"},
        "mystery": {"Thought-Provoking"},
        "animation": {"Family Friendly"},
    }

    for g in genre_names:
        matched_tags.update(genre_tag_map.get(g, set()))

    # Overview word-based tags
    for keyword_text in keywords:
        kw = keyword_text.lower()
        if any(w in kw for w in ["cult", "iconic", "legendary"]):
            matched_tags.add("Cult Classic")
        if any(w in kw for w in ["futuristic", "cyber", "dystopian"]):
            matched_tags.add("Atmospheric")

    if ov_lower:
        if any(w in ov_lower for w in ["dark", "psychological", "twist"]):
            matched_tags.add("Dark")
        if any(w in ov_lower for w in ["epic", "battle", "quest", "journey"]):
            matched_tags.add("Epic")
        if any(w in ov_lower for w in ["heartwarming", "family", "friendship"]):
            matched_tags.add("Heartwarming")
        if any(w in ov_lower for w in ["mind-bending", "reality", "consciousness", "llm"]):
            matched_tags.add("Mind-Bending")

    # Rating-based
    if rating is not None and vote_count is not None:
        if rating < 6.0 and vote_count > 500:
            matched_tags.add("Underrated")
        if rating >= 8.0:
            matched_tags.add("Highly Rated")
        if rating >= 7.5 and vote_count > 2000:
            matched_tags.add("Must Watch")

    # Year-based
    if year is not None and year < 2000:
        matched_tags.add("Classic")

    # Limit to 3-5
    sorted_tags = sorted(matched_tags)
    return sorted_tags[:5]


def build_semantic_text(movie_data: dict, tags: list[str]) -> str:
    """Build searchable text for embedding."""
    parts = []

    title = movie_data.get("title", "")
    if title:
        parts.append(title)

    genres = [g.get("name", "") for g in movie_data.get("genres", [])]
    if genres:
        parts.append(f"Genres: {', '.join(genres)}")

    overview = movie_data.get("overview", "")
    if overview:
        parts.append(overview)

    credits = movie_data.get("credits", {})
    director = None
    for member in credits.get("crew", []):
        if member.get("job") == "Director":
            director = member.get("name", "")
            break
    if director:
        parts.append(f"Director: {director}")

    cast = credits.get("cast", [])[:3]
    if cast:
        actors = [m.get("name", "") for m in cast if m.get("name")]
        if actors:
            parts.append(f"Actors: {', '.join(actors)}")

    if tags:
        parts.append(f"Tags: {', '.join(tags)}")

    keywords = movie_data.get("keywords", {}).get("keywords", [])
    if keywords:
        kw_names = [k.get("name", "") for k in keywords[:10]]
        parts.append(f"Keywords: {', '.join(kw_names)}")

    return ". ".join(parts)


def generate_embedding(text: str) -> list[float] | None:
    """Generate high-quality embedding using a local sentence-transformer model on DGX Spark."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None

    model, _ = _get_embedding_model()
    embedding = model.encode([text], show_progress_bar=False)
    return embedding[0].tolist()


def generate_embeddings_batch(texts: list[str]) -> list[float | None]:
    """Generate embeddings for multiple texts in one GPU batch."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return [None] * len(texts)

    if not texts:
        return []

    model, _ = _get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return [emb.tolist() for emb in embeddings]


# ── Main Pipeline ──────────────────────────────────────────────────────

def run_enrichment(
    limit: int | None = None,
    dry_run: bool = False,
    skip_embedding: bool = False,
) -> dict[str, int]:
    """Run the full enrichment pipeline. Returns statistics."""

    tmdb_token = os.environ.get("TMDB_READ_ACCESS_TOKEN")
    if not tmdb_token:
        raise RuntimeError("TMDB_READ_ACCESS_TOKEN not set in environment.")

    setup_tmdb(tmdb_token)

    session = SessionLocal()
    try:
        stmt = select(Movie).where(Movie.tmdb_id.is_(None))
        if limit:
            stmt = stmt.limit(limit)

        movies = session.execute(stmt).scalars().all()
        total = len(movies)
        logger.info(f"Found {total} movies to enrich")

        stats = defaultdict(int)
        enriched_movies = []  # track for batch embedding

        for i, movie in enumerate(movies, 1):
            title = movie.imdb_title or "Unknown"
            year = movie.imdb_year

            status = f"[{i}/{total}] {title}"

            # Step 1: Search and match
            match = search_and_match_movie(title, year)
            if not match:
                logger.warning(f"{status} ✗ no TMDB match")
                stats["no_match"] += 1
                continue

            tmdb_id = match["id"]
            confidence = match.get("_confidence", 0)
            logger.info(f"{status} ✓ matched (confidence={confidence})")
            stats["matched"] += 1

            # Step 2: Fetch full details
            try:
                data = fetch_movie_details(tmdb_id)
            except Exception as e:
                logger.error(f"{status} ✗ fetch error: {e}")
                stats["fetch_error"] += 1
                continue

            # Extract fields
            movie.tmdb_id = tmdb_id
            movie.title = data.get("title")
            movie.release_year = int(data.get("release_date", "")[:4]) if data.get("release_date") and len(data["release_date"]) >= 4 else None
            movie.overview = (data.get("overview") or "")[:500]
            movie.genres = list({g["name"] for g in data.get("genres", [])}) or None
            movie.runtime_minutes = data.get("runtime")
            movie.tmdb_rating = data.get("vote_average")
            movie.vote_count = data.get("vote_count")
            movie.popularity = data.get("popularity")

            # Step 3: Poster
            poster = build_poster_url(data)
            if poster:
                movie.poster_url = poster
                stats["posters"] += 1

            # Step 4: Backdrop
            backdrop = build_backdrop_url(data)
            if backdrop:
                movie.backdrop_url = backdrop
                stats["backdrops"] += 1

            # Step 5: Trailer
            trailer = build_trailer_url(data)
            if trailer:
                movie.trailer_url = trailer
                stats["trailers"] += 1

            # Step 6: Cast and Crew
            director, (actor1, actor2, actor3) = extract_credits(data)
            if director:
                movie.director = director
            if actor1:
                movie.lead_actor = actor1
                stats["cast"] += 1
            if actor2:
                movie.lead_actor_2 = actor2
            if actor3:
                movie.lead_actor_3 = actor3

            # Step 7: Audience
            audience = classify_audience(data)
            movie.audience = audience

            # Step 8: Editorial tags
            kw_list = data.get("keywords", {}).get("keywords", [])
            kw_names = [k.get("name", "") for k in kw_list]
            tags = generate_editorial_tags(
                data.get("genres", []),
                data.get("overview"),
                kw_names,
                movie.tmdb_rating,
                movie.vote_count,
                movie.release_year,
            )
            movie.editorial_tags = tags if tags else None
            movie._semantic_text = build_semantic_text(data, tags)

            movie.enriched_at = datetime.now()

            if not dry_run:
                session.add(movie)
            enriched_movies.append(movie)

            stats["success"] += 1
            logger.info(f"  ✓ poster={bool(poster)} backdrop={bool(backdrop)} trailer={bool(trailer)} cast={bool(actor1)} tags={len(tags)}")

            # Rate limit: TMDB ~40 req/s, we do 2 calls per movie (search + detail)
            if i % 10 == 0:
                time.sleep(0.5)

        # Step 9: Batch generate embeddings for all enriched movies
        if not skip_embedding and enriched_movies:
            semantic_texts = [m._semantic_text for m in enriched_movies]
            logger.info(f"Generating embeddings for {len(semantic_texts)} movies in batch...")
            embeddings = generate_embeddings_batch(semantic_texts)
            for movie, emb in zip(enriched_movies, embeddings):
                if emb:
                    movie.embedding = emb
                    stats["embeddings"] += 1
            logger.info(f"Embedded {stats['embeddings']}/{len(enriched_movies)} movies")
        elif not skip_embedding:
            stats["embeddings_skipped"] = 0
        else:
            stats["embeddings_skipped"] = stats["success"]

        if not dry_run:
            session.commit()

        # Final stats
        stats["total"] = total
        logger.info("=" * 60)
        logger.info("ENRICHMENT COMPLETE")
        logger.info(f"  Total movies:           {stats['total']}")
        logger.info(f"  Successfully matched:    {stats['matched']}")
        logger.info(f"  Failed to match:         {stats['no_match']}")
        logger.info(f"  Fetch errors:            {stats['fetch_error']}")
        logger.info(f"  Enriched:                {stats['success']}")
        logger.info(f"  Posters added:           {stats['posters']}")
        logger.info(f"  Backdrops added:         {stats['backdrops']}")
        logger.info(f"  Trailers added:          {stats['trailers']}")
        logger.info(f"  Cast added:              {stats['cast']}")
        logger.info(f"  Embeddings generated:    {stats['embeddings']}")
        logger.info(f"  Embeddings skipped:      {stats['embeddings_skipped']}")
        pct = (stats['matched'] / stats['total'] * 100) if stats['total'] else 0
        logger.info(f"  Completion:              {pct:.1f}%")
        logger.info("=" * 60)

        return dict(stats)

    except Exception:
        if not dry_run:
            session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich movies with TMDB metadata")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to DB")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N movies")
    parser.add_argument("--skip-embedding", action="store_true", help="Skip AI embedding generation")
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    run_enrichment(
        limit=args.limit,
        dry_run=args.dry_run,
        skip_embedding=args.skip_embedding,
    )


if __name__ == "__main__":
    main()
