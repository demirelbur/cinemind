# 🎬 CineMind

CineMind is a grounded, LLM-assisted movie recommendation app.

It takes natural-language preferences, parses intent with an LLM, retrieves candidates from PostgreSQL, and returns structured recommendations with short explanations.

![CineMind](images/cinemind-version.png)

## 🌟 Highlights

- Natural-language queries with strict typed responses
- Two-stage pipeline: intent parsing and grounded recommendation
- Deterministic PostgreSQL retrieval (no free-form SQL generation)
- FastAPI backend, Streamlit frontend, pytest-based test strategy
- Production-minded MVP with clear upgrade path

## ℹ️ Overview

CineMind uses a two-agent orchestration flow:

1. Agent 1 parses user text into `ParsedPreferences` and performs deterministic retrieval.
2. Agent 2 ranks only from retrieved candidates and generates grounded explanations.

This design keeps recommendations explainable and testable while still benefiting from LLM flexibility.

## ⬇️ Installation & Quick Start

CineMind can be run in two ways: **Docker Compose** (recommended) or **locally** with `uv`.

### Option 1: Docker Compose (Recommended)

Requires Docker and Docker Compose. This starts PostgreSQL, the FastAPI backend, and the Streamlit frontend in one command.

```bash
# Set your OpenRouter API key
export OPENROUTER_API_KEY="your-key-here"

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

Access the app:

- **Frontend**: <http://localhost:8501>
- **API**: <http://localhost:8000>
- **API Docs (Swagger)**: <http://localhost:8000/docs>

Stop services:

```bash
docker compose down
```

### Option 2: Local Development

Minimum requirements: Python 3.11+, PostgreSQL running locally (port 5432).

```bash
# 1. Install dependencies
uv sync

# 2. Ensure PostgreSQL is running with database `cinemind_db`
#    See [docs/postgresql_setup.md](docs/postgresql_setup.md) for macOS setup

# 3. Run database migrations
uv run alembic upgrade head

# 4. Load movie seed data
uv run python scripts/load_movies.py

# 5a. Start FastAPI backend (terminal 1)
uv run uvicorn cinemind.api.main:app --reload

# 5b. Start Streamlit frontend (terminal 2)
uv run streamlit run src/cinemind/frontend/app.py
```

Access the app at:

- **Frontend**: <http://localhost:8501>
- **API**: <http://localhost:8000>

## 🚀 Usage

Ask for recommendations in natural language through the Streamlit UI, Swagger docs at <http://localhost:8000/docs>, or the API directly:

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "I want a nice comedy about friendship", "max_results": 5}'
```

### Example Queries

**Basic genre:**
- "Recommend 3 sci-fi movies"
- "I want to watch a comedy"
- "Suggest some horror films"

**Genre + year range:**
- "Sci-fi movies from the 80s"
- "Comedy movies from the 90s"
- "Drama films after 2015"
- "Action movies before 2000"

**Genre + mood / theme:**
- "Dark thriller movies about revenge"
- "Light-hearted comedies about friendship"
- "Intense action movies with space themes"

**Audience filter:**
- "Family-friendly sci-fi movies"
- "Horror movies for adults"
- "Comedy for kids"

**Highly rated:**
- "Top-rated drama movies"
- "Highly rated science fiction from the 70s"

**Exclusions:**
- "Drama movies but no romance"
- "Action films without any comedy"

**Complex multi-signal:**
- "Recommend 3 dark sci-fi movies from the 80s for teens with themes of survival"
- "I want uplifting comedies for the family, nothing too old"
- "Give me 5 highly rated thrillers, no horror please"

**Broad / minimal constraints:**
- "Something highly rated"
- "Recommend me a good movie"

## 🔧 Environment Variables

The following must be configured (via `.env` file or environment):

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `OPENROUTER_API_KEY` | yes | — | OpenRouter API key for LLM calls |
| `DATABASE_URL` | yes | — | PostgreSQL connection string (e.g., `postgresql+psycopg://user:pass@localhost:5432/cinemind_db`) |
| `LLM_PROVIDER` | no | `openrouter` | Must be the literal string `openrouter` |
| `LLM_MODEL_NAME` | no | `openai/gpt-4o` | Model name with provider prefix (e.g., `openai/gpt-4o`, `anthropic/claude-sonnet-4-20250514`) |
| `CINEMIND_API_BASE_URL` | no | `http://127.0.0.1:8000` | Backend URL used by the Streamlit frontend |

## 📚 Documentation

- Quickstart: [docs/quickstart.md](docs/quickstart.md)
- PostgreSQL setup (macOS): [docs/postgresql_setup.md](docs/postgresql_setup.md)
- Dataset setup and data licensing notes: [docs/dataset_setup.md](docs/dataset_setup.md)
- Testing guide: [docs/testing.md](docs/testing.md)
- Architecture notes: [docs/architecture_notes.md](docs/architecture_notes.md)
- Docs index: [docs/README.md](docs/README.md)

## 🧪 Testing

Quick deterministic test run:

```bash
uv run pytest -m "not llm"
```

For full test strategy, including live LLM tests, see [docs/testing.md](docs/testing.md).

## 💭 Feedback and Contributing

Questions, ideas, and bug reports are welcome.

- Open an issue for bugs or feature requests.
- Open a pull request for improvements.

## 🗺️ Roadmap

- Add `pgvector` for semantic search
- Hybrid retrieval (filters + vector similarity)
- Improve reranking with deterministic pre-scoring
- Add feedback loops
- Docker Compose for one-command local startup ✅

## 📄 License

This project is licensed under Apache License 2.0.

See [LICENSE](LICENSE) for the full text.

Note: dataset licensing is separate from source-code licensing. See [docs/dataset_setup.md](docs/dataset_setup.md).
