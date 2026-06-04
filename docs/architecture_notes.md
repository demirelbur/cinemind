# Architecture Notes

## Two-agent recommendation pipeline

```
User Query → Agent 1 (Intent Parser) → ParsedPreferences
  → Deterministic SQL Retrieval → Candidate Movies
  → Agent 2 (Ranked Recommendation) → RecommendationResponse
```

1. **Agent 1** parses user text into structured `ParsedPreferences` (genre, mood, year range, themes, exclusions).
2. **Retrieval** runs deterministic PostgreSQL queries (not LLM-generated SQL) with optional `pgvector` semantic similarity.
3. **Agent 2** ranks candidates and generates per-movie `reason` strings (the "Why It Matches" text shown on cards).

## Retrieval is deterministic

The LLM does not generate SQL. The retrieval layer uses:

- Genre filtering with PostgreSQL array operators (`genres[]`)
- Year range constraints
- Optional semantic vector similarity via `pgvector`
- Hardcoded audience and rating filters

This keeps the pipeline testable and safe.

## Agent 2 is grounded

Agent 2 can only recommend movies from the candidate set returned by retrieval. It cannot invent movies. Each recommendation includes a `reason` (grounded explanation) and `match_score` (0.0–1.0 float).

## `max_results` is optional

Resolved by either:

- Explicit `RecommendRequest.max_results` (1–10)
- Inferred from the query ("top ten movies" → 10)

## TMDB enrichment

Movies are enriched at load time (not query time) via `scripts/enrich_movies.py`:

- Poster URLs, backdrop URLs, trailer links
- Editorial tags (rules-based)
- Semantic embeddings (`gte-Qwen2-7B`)

Enriched data is stored in `movies` table (25 columns including `embedding` vector).

## Frontend: single transformation layer

The Next.js API route (`api/chat/route.ts`) is the **only** place where backend data is reshaped into the frontend's `MovieRecommendation` type. The client library (`lib/api.ts`) is a thin HTTP caller with zero transformation.

## State management

The frontend uses a minimal Zustand store (`messages`, `isLoading`, `error`). Only the latest user query and result pair are displayed — no chat history is rendered.

## Production deployment

Full stack runs in Docker Compose:

- `db` — PostgreSQL 17 with `pgvector`
- `api` — FastAPI (Uvicorn)
- `web` — Next.js (standalone output)
