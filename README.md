# CineMind

CineMind is a grounded, LLM-assisted movie recommendation app.

It takes natural-language preferences, parses intent with an LLM, retrieves candidates from PostgreSQL, and returns structured recommendations with short, AI-generated explanations.

## Highlights

- Natural-language queries with strict typed responses via Pydantic models
- Two-agent pipeline: intent parsing + grounded ranked recommendation
- Deterministic PostgreSQL retrieval (no free-form SQL generation)
- TMDB-enriched movie catalog: posters, backdrops, trailers, editorial tags, cast, semantic embeddings
- `pgvector`-powered semantic search for natural-language matching
- pydantic_ai handles LLM output validation and automatic retries
- FastAPI backend, Next.js frontend, fully containerized with Docker Compose

## Quick Start

```bash
cp .env.example .env
# Edit .env — set OPENROUTER_API_KEY (required) and optionally TMDB_READ_ACCESS_TOKEN
docker compose up --build
```

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Local Development

Requires Python 3.11+, `uv`, Node.js 20+, `npm`, PostgreSQL 16+.

```bash
# Backend
uv sync
uv run alembic upgrade head
uv run python scripts/load_movies.py       # load base catalog
uv run python scripts/enrich_movies.py     # enrich from TMDB (needs TMDB_READ_ACCESS_TOKEN)
uv run uvicorn cinemind.api.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## API

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "dark sci-fi movies from the 80s", "max_results": 5}'
```

### Example Queries

- "Recommend 3 sci-fi movies from the 80s"
- "Movies like Interstellar but more emotional"
- "Top-rated thrillers, no horror please"
- "Underrated horror films for adults"
- "Family-friendly adventure movies"
- "Comedy movies about friendship from the 90s"
- "Drama movies but no romance"

## Environment Variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `OPENROUTER_API_KEY` | yes | — | OpenRouter API key for LLM calls |
| `DATABASE_URL` | yes | — | PostgreSQL connection string |
| `LLM_PROVIDER` | no | `openrouter` | Must be the literal string `openrouter` |
| `LLM_MODEL_NAME` | no | `openai/gpt-4o` | Must include provider prefix (e.g., `openai/gpt-4o`) |
| `TMDB_READ_ACCESS_TOKEN` | no | — | TMDB Read Access Token (for enrichment script) |
| `NEXT_PUBLIC_API_BASE_URL` | no | `http://localhost:8000` | Frontend → backend URL (Docker: `http://api:8000`) |

> **Critical:** `LLM_MODEL_NAME` must use `provider/model` format. A bare name like `gpt-4o` will cause a startup error.

## Deployment

### Deploy on Hetzner + Cloudflare

1. **Create a Hetzner Cloud Server** — CX23 (2 vCPU, 4 GB RAM, 40 GB NVMe, Ubuntu 24.04)
2. **Set up Cloudflare DNS** — add A record `cinemind` pointing to your server IP, set proxy to **Proxied** (orange cloud). Set SSL/TLS mode to **Flexible**.
3. **SSH in and install Docker**

```bash
ssh root@<your.server.ip>
apt update && apt upgrade -y
apt install -y ca-certificates curl gnupg ufw docker.io docker-compose-plugin
systemctl enable --now docker
ufw allow OpenSSH && ufw allow 80/tcp && ufw --force enable
```

4. **Clone, configure, and start**

```bash
git clone <your-repo-url>
cd cinemind
cp .env.example .env
# Edit .env — set OPENROUTER_API_KEY, DATABASE_URL, TMDB_READ_ACCESS_TOKEN
chmod 600 .env
docker compose up -d --build
```

5. **Enrich movies** (one-time)

```bash
docker compose exec api python /app/scripts/enrich_movies.py
```

6. **Verify** — open https://cinemind.burakdemirel.dev

`main` branch includes Nginx reverse proxy for production. Use `develop` branch for local Docker development without Nginx.

### Manual deploy

```bash
cd /root/cinemind && git pull && docker compose build && docker compose up -d && docker compose logs --tail=50
```

## Documentation

- Quickstart: [docs/quickstart.md](docs/quickstart.md)
- PostgreSQL setup (macOS): [docs/postgresql_setup.md](docs/postgresql_setup.md)
- Dataset & enrichment: [docs/dataset_setup.md](docs/dataset_setup.md)
- Testing: [docs/testing.md](docs/testing.md)
- Architecture: [docs/architecture_notes.md](docs/architecture_notes.md)

## Testing

```bash
uv run pytest                # full suite
uv run pytest -m "not llm"   # skip live LLM calls
```

## License

Apache License 2.0. Dataset licensing is separate — see [docs/dataset_setup.md](docs/dataset_setup.md).
