# 🎬 CineMind

CineMind is an LLM-based movie recommender that:

- accepts natural-language user preferences
- retrieves matching movies from a PostgreSQL database
- uses one LLM stage to parse intent and another to rank and explain recommendations
- returns structured recommendations in a strict schema

The project is designed as an MVP that still follows production-minded practices: strict validation, clear data boundaries, PostgreSQL-backed retrieval, deterministic search, and grounded recommendation generation.

![CineMind](images/cinemind-version.png)

## Product Overview

CineMind uses a two-stage recommendation pipeline.

### Agent 1 — Intent + Retrieval

Agent 1:

- parses the user query into a structured `ParsedPreferences` model
- retrieves grounded candidate movies from PostgreSQL
- returns a typed `RetrievalResult`

### Agent 2 — Grounded Recommendation

Agent 2:

- receives the original user query
- receives the `RetrievalResult`
- ranks the strongest candidates
- writes short grounded explanations
- returns a `RecommendationResponse`

## API and Domain Models

### External/API-facing

- `RecommendRequest`
- `RecommendationResponse`

### Internal Domain

- `ParsedPreferences`
- `MovieRecord`
- `MovieRecommendation`
- `RetrievalResult`

## Validation Philosophy

CineMind validates data at every important boundary.

- **Boundary 1 — external input**
  Validate `RecommendRequest`

- **Boundary 2 — LLM structured output**
  Validate `ParsedPreferences`

- **Boundary 3 — DB retrieval output**
  Validate or construct `MovieRecord`

- **Boundary 4 — final recommender output**
  Validate `RecommendationResponse`

This keeps the app reliable even though it uses LLMs internally.

## Architecture

The end-to-end flow is:

1. User enters a natural-language movie request
2. Agent 1 parses the request into `ParsedPreferences`
3. PostgreSQL retrieval returns candidate movies
4. Agent 2 selects the best matches from those candidates
5. The API returns structured recommendations
6. Streamlit renders the results in a chat-style interface

## Tech Stack

- **Python**
- **Pydantic** for schema validation
- **PydanticAI** for LLM-powered agents
- **PostgreSQL** for movie storage and retrieval
- **SQLAlchemy + Alembic** for DB access and migrations
- **FastAPI** for the backend API
- **Streamlit** for the frontend
- **pytest** for testing
- **uv** for dependency and environment management

## Project Structure

```text
cinemind/
  data/
    raw/
    processed/
  scripts/
    transform_tmdb.py
    load_movies.py
    test_agent1.py
    test_agent2.py
  src/cinemind/
    agents/
    api/
    db/
    frontend/
    prompts/
    retrieval/
    schemas/
    services/
  tests/
  pyproject.toml
  README.md
```

## Dataset Setup

CineMind uses a TMDB-based dataset that is transformed into a normalized internal schema.

### Download the dataset

You can use a Kaggle TMDB dataset such as `tmdb/tmdb-movie-metadata`.

```bash
uv run kaggle datasets download -d tmdb/tmdb-movie-metadata
unzip tmdb-movie-metadata.zip -d data/raw
```

Make sure your Kaggle CLI credentials are configured before running this.

### Transform the raw data

```bash
uv run python scripts/transform_tmdb.py
```

This produces cleaned output such as:

- `data/processed/movies_clean.csv`
- `data/processed/movies_clean.jsonl`
- `data/processed/rejected_rows.csv`

## PostgreSQL Setup (macOS)

If you already use Homebrew:

```bash
brew update
brew install postgresql@16
```

### Start PostgreSQL

```bash
brew services start postgresql@16
```

### Verify installation

```bash
psql --version
```

### Verify PostgreSQL is running

```bash
brew services list
```

You should see something like:

```bash
postgresql@16  started  ...
```

If it is not started:

```bash
brew services start postgresql@16
```

### Connect to PostgreSQL

```bash
psql postgres
```

If it works, you will see:

```bash
postgres=#
```

### Create the database

Inside `psql`, run:

```sql
CREATE DATABASE cinemind;
```

Then check:

```sql
\l
```

### Create a user

Still inside `psql`:

```sql
CREATE USER cinemind_user WITH PASSWORD 'password';
ALTER USER cinemind_user WITH SUPERUSER;
```

For local development, `SUPERUSER` is acceptable and simpler.

### Test the connection

Exit:

```sql
\q
```

Then run:

```bash
psql -U cinemind_user -d cinemind
```

## App Setup

### 1. Install dependencies

```bash
uv sync
```

Or, if needed:

```bash
uv add fastapi uvicorn sqlalchemy alembic "psycopg[binary]" python-dotenv streamlit requests pandas kaggle pydantic pydantic-ai
```

### 2. Create a `.env` file

At the project root, create `.env`:

```env
DATABASE_URL=postgresql://cinemind_user:password@localhost:5432/cinemind
CINEMIND_API_BASE_URL=http://127.0.0.1:8000
OPENAI_API_KEY=your_key_here
```

If you are using a different provider through PydanticAI, add the required provider key instead.

### 3. Run Alembic migrations

```bash
uv run alembic upgrade head
```

### 4. Load the processed movie dataset into PostgreSQL

```bash
uv run python scripts/load_movies.py
```

## Running the Backend

Start the FastAPI backend:

```bash
uv run uvicorn cinemind.api.main:app --reload
```

Useful endpoints:

- `GET /health`
- `POST /recommend`
- Swagger UI: `http://127.0.0.1:8000/docs`

## Running the Frontend

Start the Streamlit frontend:

```bash
uv run streamlit run src/cinemind/frontend/app.py
```

Then open the local Streamlit URL shown in the terminal.

The frontend:

- provides a chat-style interaction flow
- sends requests to the FastAPI backend
- renders grounded recommendations using a cinematic card layout

## Running the Full App

In one terminal:

```bash
uv run uvicorn cinemind.api.main:app --reload
```

In another terminal:

```bash
uv run streamlit run src/cinemind/frontend/app.py
```

## Testing

### Run deterministic tests only

```bash
uv run pytest -m "not llm"
```

### Run live LLM integration tests

```bash
uv run pytest -m llm -s
```

The test campaign is intentionally split into:

- deterministic schema and wrapper tests
- live LLM integration tests

This makes the test strategy realistic for an LLM-based system.

## Important Things to Know

### 1. Retrieval is deterministic

The LLM does **not** generate SQL directly.

Instead:

- the parser turns user language into `ParsedPreferences`
- the retrieval layer uses deterministic PostgreSQL filtering
- Agent 2 ranks only within grounded candidates

This makes the system easier to test, safer, and more production-friendly.

### 2. Agent 2 is grounded

Agent 2 is only allowed to recommend movies from the retrieved candidate set.

That reduces hallucination risk and keeps explanations grounded in real database records.

### 3. `max_results` is optional

Users usually do not think in exact counts.

CineMind supports both:

- an explicit API override via `RecommendRequest.max_results`
- an inferred count from the query, such as “top ten movies”

The final result count is resolved by the orchestration layer.

### 4. Rejected rows are expected

During dataset transformation, some rows may be rejected if they fail the `MovieRecord` schema.

This is intentional and improves data quality.

### 5. This is an MVP with a clean upgrade path

The current version uses PostgreSQL only.

A natural next step is:

- PostgreSQL + `pgvector`
- semantic search
- hybrid retrieval
- better reranking

## Example User Queries

- “Recommend a good comedy movie from the 90s.”
- “Give me 3 dark sci-fi movies after 2010.”
- “Recommend a family-friendly movie, no horror.”
- “What are the top ten thrillers before 2000?”
- “Recommend something emotional about friendship.”

## Future Improvements

- add `pgvector` for semantic search
- hybrid retrieval: SQL filters + vector similarity
- add feedback loops
- use real TMDB posters in the frontend
- improve reranking with deterministic pre-scoring
- add Docker Compose for one-command local startup

## Summary

CineMind is a grounded, LLM-assisted movie recommender with:

- strict typed contracts
- PostgreSQL-backed retrieval
- two-stage recommendation logic
- a testable architecture
- a frontend that is fast to demo

It is intentionally designed to be simple enough for an MVP while still being strong enough to discuss in a mock interview.
