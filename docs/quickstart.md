# Quickstart

## 1. Install dependencies

```bash
uv sync
```

## 2. Configure environment variables

Copy `.env.example` and fill in your values:

```bash
cp .env.example .env
```

Required variables:

- `OPENROUTER_API_KEY` — your OpenRouter API key
- `DATABASE_URL` — PostgreSQL connection string

Optional:

- `TMDB_READ_ACCESS_TOKEN` — needed for `scripts/enrich_movies.py`

Security notes:

- Never commit `.env` to Git.
- Use strong, unique secrets for database and API keys.

## 3. Prepare the database

Run migrations:

```bash
uv run alembic upgrade head
```

Load the base movie catalog:

```bash
uv run python scripts/load_movies.py
```

Enrich with TMDB metadata (posters, backdrops, tags, embeddings):

```bash
uv run python scripts/enrich_movies.py
```

> Requires `TMDB_READ_ACCESS_TOKEN` in your `.env`. Skips movies already enriched.

For PostgreSQL installation on macOS, see [postgresql_setup.md](postgresql_setup.md).

## 4. Run the backend

```bash
uv run uvicorn cinemind.api.main:app --reload
```

Endpoints:

- `GET /health` — health check
- `POST /recommend` — recommendation endpoint
- Swagger UI: http://127.0.0.1:8000/docs

## 5. Run the frontend

```bash
cd frontend && npm install && npm run dev
```

Frontend runs at http://localhost:3000.

## 6. Run full stack with Docker Compose

```bash
docker compose up --build
```

Starts PostgreSQL, FastAPI backend, and Next.js frontend in one command.
