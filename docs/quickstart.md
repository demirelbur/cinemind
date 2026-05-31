# Quickstart

## 1. Install dependencies

```bash
uv sync
```

Or, if needed:

```bash
uv add fastapi uvicorn sqlalchemy alembic "psycopg[binary]" python-dotenv requests pandas kaggle pydantic pydantic-ai
```

## 2. Configure environment variables

Create a `.env` file at the project root:

```env
DATABASE_URL=postgresql://cinemind_user:<strong_db_password>@localhost:5432/cinemind
CINEMIND_API_BASE_URL=http://127.0.0.1:8000
OPENROUTER_API_KEY=<your_real_api_key>
```

If you are using a different provider through PydanticAI, add the required provider key instead.

Security notes:

- Never commit `.env` to Git.
- Use strong, unique secrets for database and API keys.
- Rotate keys immediately if they are exposed.

## 3. Prepare the database

Run migrations:

```bash
uv run alembic upgrade head
```

Load processed movie data:

```bash
uv run python scripts/load_movies.py
```

For PostgreSQL installation on macOS, see [postgresql_setup.md](postgresql_setup.md).

## 4. Run the backend

This command is for local development only (`--reload`):

```bash
uv run uvicorn cinemind.api.main:app --reload
```

Useful endpoints:

- `GET /health`
- `POST /recommend`
- Swagger UI: `http://127.0.0.1:8000/docs` (development use)

## 5. Run the frontend

The frontend is a Next.js app in the `frontend/` directory. See the main
[README.md](../README.md) for instructions on running it via Docker Compose
or locally with `npm run dev`.

## 6. Run full app

The recommended way to run the full stack is with Docker Compose:

```bash
docker compose up -d
```

This starts PostgreSQL, the FastAPI backend, and the Next.js frontend in one command.
