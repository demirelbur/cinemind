# Dataset Setup and Enrichment

CineMind uses a TMDB-based movie catalog that is enriched with metadata, editorial tags, and semantic embeddings.

## Data licensing note

This repository's code license does not automatically apply to movie data.

- TMDB/Kaggle data remains subject to the original dataset/provider terms.
- You are responsible for complying with TMDB, Kaggle, and any downstream usage restrictions.
- Review and follow attribution/redistribution requirements before publishing derived datasets.

## Step 1: Download the raw dataset

Use a Kaggle TMDB dataset such as `tmdb/tmdb-movie-metadata`:

```bash
uv run kaggle datasets download -d tmdb/tmdb-movie-metadata
unzip tmdb-movie-metadata.zip -d data/raw
```

## Step 2: Transform the raw data

```bash
uv run python scripts/transform_tmdb.py
```

Produces cleaned output:

- `data/processed/movies_clean.csv`
- `data/processed/movies_clean.jsonl`
- `data/processed/rejected_rows.csv`

## Step 3: Load into PostgreSQL

```bash
uv run alembic upgrade head
uv run python scripts/load_movies.py
```

## Step 4: Enrich with TMDB metadata

Requires `TMDB_READ_ACCESS_TOKEN` in your `.env`.

```bash
uv run python scripts/enrich_movies.py
```

This script performs the following enrichment for each movie:

1. **TMDB API matching** — matches local movies to TMDB records using title + year similarity (confidence threshold ≥ 70%)
2. **Poster URL** — high-resolution poster image for use in the UI
3. **Backdrop URL** — cinematic still for subtle card backgrounds
4. **Trailer URL** — YouTube trailer link
5. **Editorial tags** — rules-based tags derived from genre, keywords, synopsis, rating, and era
6. **Cast / crew** — director and lead actors (up to 3)
7. **Semantic embedding** — 1536-dim vector via `gte-Qwen2-7B` (sentence-transformers) for vector similarity search
8. **Vote count** — number of TMDB/IMDb votes used for quality gating

The enrichment script is idempotent — re-running it skips already-enriched movies.

## Standalone embedding generation

If you have a separate machine (e.g., DGX Spark) for embedding generation:

```bash
uv run python scripts/generate_embeddings.py
```

This generates embeddings remotely without stopping the enrichment pipeline.

## Database schema

The `movies` table has 25 columns:

| Group | Columns |
|---|---|
| **Identity** | `id`, `imdb_title`, `tmdb_id`, `title`, `release_year` |
| **Content** | `overview`, `genres[]`, `runtime_minutes` |
| **Ratings** | `imdb_rating`, `tmdb_rating`, `vote_count`, `popularity` |
| **Media** | `poster_url`, `backdrop_url`, `trailer_url` |
| **People** | `director`, `lead_actor`, `lead_actor_2`, `lead_actor_3` |
| **Classification** | `recommended_for`, `audience` |
| **Discovery** | `editorial_tags[]`, `embedding` (vector(1536)) |
| **Metadata** | `enriched_at` |
