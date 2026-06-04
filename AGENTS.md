# CineMind — Agent Context

CineMind is a grounded, LLM-assisted movie recommendation application. It parses a natural-language query into structured preferences, retrieves candidate movies from PostgreSQL using deterministic filters, then has a second LLM agent rank the candidates and generate short, explainable recommendations.

Dependencies are managed with `uv`. Python >= 3.11 is required.

## Quick Commands

```bash
# Backend
uv sync                        # install all dependencies
uv run uvicorn cinemind.api.main:app --reload   # start FastAPI backend on :8000

# Frontend
cd frontend && npm run dev   # start Next.js frontend on :3000

# Tests (backend)
uv run pytest                  # run full test suite
uv run pytest -m "not llm"     # run tests only (skips live LLM calls)

# Lint / type check (backend)
uv run ruff check src/         # lint
uv run mypy src/               # type check

# Docker (both services)
docker compose up --build      # build and start all containers
```

## Project Structure

```text
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
│
├── frontend/src/
│   ├── app/
│   │   ├── page.tsx             # main page (empty state, results, loading)
│   │   ├── layout.tsx           # root layout, metadata, system font
│   │   ├── globals.css          # minimal theme tokens + scrollbar + noise
│   │   └── api/chat/route.ts    # proxy to backend — single transformation layer\
│   ├── components/
│   │   ├── chat/                # ChatInput, SuggestedPrompts
│   │   ├── layout/              # AppHeader, BackgroundGlow
│   │   ├── movie/               # MovieCard, WhyItMatches, ImdbRating, MatchScoreBadge
│   │   └── search/              # SearchLoading (progress step indicator)
│   ├── lib/                     # api.ts (thin HTTP caller), types.ts
│   └── store/                   # useChatStore (Zustand, 3 live state values)
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
```text

## Architecture

### Two-Agent Recommendation Pipeline

```text
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

`load_dotenv()` is handled by uvicorn at startup (reads `.env` automatically).

**Never** call `load_dotenv()` in imported library modules (e.g., `db/session.py`, agent files, `core/config.py`). The entry point loads env vars; library modules read `os.getenv()` values that are already in the environment.

### Important Convention: Agent Instantiation

Agents are created via **factory functions** decorated with `functools.cache` (e.g. `get_intent_parser_agent()`, `get_recommendation_agent()`). This ensures a single cached instance per process without eagerly initializing at import time.

### Important Convention: LLM Configuration

Environment variables in `.env`:

| Variable | Required | Default | Notes |
| --- | --- | --- | --- |
| `OPENROUTER_API_KEY` | yes | — | API key for OpenRouter |
| `DATABASE_URL` | yes | — | PostgreSQL connection string |
| `LLM_PROVIDER` | no | `openrouter` | Must be the literal string `openrouter` |
| `LLM_MODEL_NAME` | no | `openai/gpt-4o` | **Must include provider prefix**, e.g. `openai/gpt-4o`, `anthropic/claude-sonnet-4-20250514` |
| `TMDB_READ_ACCESS_TOKEN` | no | — | TMDB Read Access Token (for enrichment script) |
| `NEXT_PUBLIC_API_BASE_URL` | no | `http://localhost:8000` | Used by frontend to reach backend (Docker: `http://api:8000`) |
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
5. **Frontend LPD cleanup** — removed 7 dead component files, 9 unused npm packages, dead CSS, duplicate `MovieRecommendation` interface. Consolidated data transformation to single layer in `api/chat/route.ts`. Fixed stale results bug and zero-result state.
6. **`matchDetails`/`similarity` removed** — computed through 3 layers but never rendered in UI. Deleted from types, route, and schema.

---

## Lean Product Development (LPD) Guidelines

All frontend and backend work follows Lean Product Development principles. These rules are not optional — they are the working standards for this codebase.

### Core Philosophy

> Build the smallest thing that delivers value. Learn fast. Iterate continuously.

The goal is to **maximize learning per unit time** while **minimizing wasted effort**.

### Rules

1. **Value First** — Every feature must tie directly to user value. Ask: *What is the user trying to achieve?* If a change doesn't make the user's task easier or clearer, don't build it.

2. **Minimize Waste** — Over-engineering, unused features, premature optimization, excess abstraction, and long development cycles without feedback are all waste. If it isn't validated, it is waste.

3. **Inline Before Modularizing** — Prefer simple, direct implementations. Hardcode before abstracting. Extract components or functions only when duplication is painful (same code in 3+ places with active divergence). Never extract to "prepare for the future."

4. **One Transformation Layer** — Data should be reshaped in exactly one place. If the same data passes through multiple layers that each rename, restructure, or derive fields, pick one layer and make it responsible. Don't split transformations across the proxy route, the client library, and the component — that's three bug surfaces for one job.

5. **No Dead Code** — Unused imports, unreferenced components, unused dependencies, and dead CSS are not "safety nets." Delete them. A file that isn't imported doesn't belong in the source tree. A package that isn't used doesn't belong in `package.json`.

6. **No Stale State** — When a user action produces an error or empty result, the UI must reflect that, not show results from the previous action. `hasResults` must check `!error`, not just `latestResult.movies?.length`.

7. **Ship Over Polish** — The first version should work, not be beautiful. CSS transitions are enough for animations; framer-motion is justified only when CSS can't do the job (e.g., staggered card entrance). Reduce bundle size before adding effects.

8. **Decision Shortcuts Over Paragraphs** — Users scan before they read. Tags, match scores, and editorial labels are the highest-value information on a card. Give them visual prominence. Don't bury useful information under generically worded explanations.

9. **Fix the Root Cause** — Don't paper over symptoms. If a field always shows "N/A", remove the field. If a button renders with no handler, hide the button. Don't add guards around broken design — fix the design.

10. **Measure, Don't Guess** — Before adding complexity, identify the bottleneck. Profile before optimizing. Collect logs and user feedback before building features you think users want.

### Anti-Patterns (Avoid These)

- Designing for scale before validation
- Over-abstracting early (components with 6+ props passed to exactly 2 call sites in the same file)
- Building full systems before testing a hypothesis
- Keeping "just in case" fallback code (46-line regex tag derivation for a field the backend already provides)
- Shipping broken affordances (clickable buttons that do nothing)
- Duplicating types across files (create the type once, import it everywhere)
- Accumulating state that's never read (messages array growing without bound when only the last pair is shown)

### Decision Framework

Before implementing anything, ask:

1. What hypothesis am I testing?
2. What is the smallest way to test it?
3. How will I measure success?
4. How fast can I get feedback?

> Speed of learning > sophistication of design
