# CineMind — Agent Context

CineMind is a grounded, LLM-assisted movie recommendation application. It parses a natural-language query into structured preferences, retrieves candidate movies from PostgreSQL using deterministic filters, then has a second LLM agent rank the candidates and generate short, explainable recommendations.

Dependencies are managed with `uv`. Python >= 3.11 is required.

## Quick Commands

```bash
uv sync                        # install all dependencies
uv run uvicorn cinemind.api.main:app --reload   # start FastAPI backend on :8000
cd frontend && npm run dev   # start Next.js frontend on :3000
uv run pytest                  # run full test suite
uv run pytest -m "not llm"     # run tests only (skips live LLM calls)
uv run ruff check src/         # lint
uv run mypy src/               # type check
```

## Project Structure

```
src/cinemind/
├── agents/                     # LLM agent factories and prompt wiring
│   ├── intent_parser_agent.py  # Agent 1 — parses query into ParsedPreferences
│   ├── intent_retrieval_agent.py  # orchestrates Agent 1 + candidate retrieval
│   └── recommendation_agent.py   # Agent 2 — ranks candidates, produces final response
├── api/                        # FastAPI entry point and routes
│   ├── main.py                 # app creation (calls load_dotenv)
│   └── routes.py               # /recommend endpoint
├── core/
│   └── config.py               # env-based settings (LLM_PROVIDER, LLM_MODEL_NAME, etc.)
├── db/
│   └── session.py              # SQLAlchemy engine + session factory
├── frontend/
│   └── (Next.js app)           # Next.js frontend (see frontend/)
├── prompts/                    # .md prompt templates
│   ├── INTENT_PARSER_SYSTEM.md
│   └── RECOMMENDATION_AGENT_SYSTEM.md
├── retrieval/
│   └── search.py               # deterministic PostgreSQL candidate retrieval
├── schemas/
│   ├── api.py                  # RecommendRequest, RecommendationResponse
│   ├── preferences.py          # ParsedPreferences (validate + normalize user intent)
│   ├── recommendation.py       # RecommendationContext
│   └── retrieval.py            # RetrievalResult
└── services/
    └── recommendation_service.py  # end-to-end pipeline orchestration
```

## Architecture

### Two-Agent Recommendation Pipeline

```
User Query (string)
  → Agent 1 (Intent Parser) → ParsedPreferences
  → Deterministic Retrieval → Candidate Movie Records
  → Agent 2 (Ranked Recommendation) → RecommendationResponse
```

1. **`intent_parser_agent`** reads the user's free-text query and returns a `ParsedPreferences` object (genre, mood, year range, themes, exclusions, desired result count).
2. **`intent_retrieval_agent`** orchestrates Agent 1 output with a SQL retrieval against PostgreSQL to produce `RetrievalResult` (preferences + candidates).
3. **`recommendation_agent`** receives the candidates plus parsed preferences as context, ranks them, and produces a `RecommendationResponse` with grounded explanations.
4. **`recommendation_service`** wires the full pipeline end-to-end.

### Important Convention: `load_dotenv` Placement

`load_dotenv()` must **only** be called at entry points:

- `src/cinemind/api/main.py` — backend entry
- `src/cinemind/frontend/app.py` — frontend entry
- `tests/conftest.py` — test entry

**Never** call `load_dotenv()` in imported library modules (e.g., `db/session.py`, agent files, `core/config.py`). Entry points are responsible for loading; library modules read `os.getenv()` values that are already in the environment.

### Important Convention: Agent Instantiation

Agents are created via **factory functions** decorated with `functools.cache` (e.g. `get_intent_parser_agent()`, `get_recommendation_agent()`). This ensures a single cached instance per process without eagerly initializing at import time.

### Important Convention: LLM Configuration

Environment variables in `.env`:

| Variable | Required | Default | Notes |
|---|---|---|---|
| `OPENROUTER_API_KEY` | yes | — | API key for OpenRouter |
| `DATABASE_URL` | yes | — | PostgreSQL connection string |
| `LLM_PROVIDER` | no | `openrouter` | Must be the literal string `openrouter` |
| `LLM_MODEL_NAME` | no | `openai/gpt-4o` | **Must include provider prefix**, e.g. `openai/gpt-4o`, `anthropic/claude-sonnet-4-20250514` |
| `CINEMIND_API_BASE_URL` | no | `http://127.0.0.1:8000` | Used by the frontend to reach backend |

**Critical:** `LLM_MODEL_NAME` **must** use the `provider/model` format. `pydantic_ai`'s `OpenRouterProvider.model_profile()` unconditionally splits the model name on `/` to resolve the underlying provider profile. A bare name like `gpt-4o` will raise `ValueError: not enough values to unpack`.

`LLM_PROVIDER` must be the literal string `"openrouter"` — this is the value expected by `pydantic_ai`'s `OpenRouterModel(provider=...)`.

### Schemas

- **`RecommendRequest`**: incoming API body with `query` (str) and optional `max_results` (int, max 10).
- **`ParsedPreferences`**: normalized struct with genre, moods, themes, exclude_genres, year_range, desired_results. Contains validators that normalize mood to lowercase and deduplicate exclude_genres.
- **`RecommendationContext`**: passes query, preferences, candidates, and final result count to Agent 2.
- **`RecommendationResponse`**: final output — `query` echo + list of recommendation items.

### Testing

Tests live under `tests/`. Key files:

- `test_intent_parser_unit.py` — unit tests, monkeypatch the `get_intent_parser_agent` factory
- `test_intent_parser_integration.py` — live LLM tests tagged `@pytest.mark.llm`
- `test_agent2_integration.py` — end-to-end pipeline test with Agent 2
- `test_preferences_schema.py` — schema validation and normalization
- `test_recommendation_services.py` — pipeline service tests, monkeypatch `run_intent_retrieval_agent`

Run fast (skip live LLM):
```bash
uv run pytest -m "not llm"
```

### Pre-Existing Type Issues

There are 9 pre-existing mypy errors across 3 files (`retrieval/search.py`, `agents/intent_parser_agent.py`, `agents/recommendation_agent.py`) related to `pydantic_ai`'s generic type signatures and some literal type narrowing. These do not affect runtime behavior and are tracked separately.

### Recent Fixes

1. **`LLM_PROVIDER` value** — was incorrectly set to `openrouter:openai`, causing `ValueError: Unknown provider`. Correct value is the literal `"openrouter"`.
2. **`load_dotenv` in library modules** — removed from `db/session.py` and agent files; added to `tests/conftest.py` so env vars are available at test collection time.
3. **`LLM_MODEL_NAME` format** — was `gpt-4o`, causing `ValueError: not enough values to unpack` in `OpenRouterProvider.model_profile()`. Changed to `openai/gpt-4o`.
4. **Agent lazy initialization** — replaced module-level agent instances with `functools.cache` factory functions to avoid import-time LLM API calls.
