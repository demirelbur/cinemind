# Quickstart

## 1. Install dependencies

```bash
uv sync
```

Or, if needed:

```bash
uv add fastapi uvicorn sqlalchemy alembic "psycopg[binary]" python-dotenv streamlit requests pandas kaggle pydantic pydantic-ai
```

## 2. Configure environment variables

Create a `.env` file at the project root:

```env
DATABASE_URL=postgresql://cinemind_user:password@localhost:5432/cinemind
CINEMIND_API_BASE_URL=http://127.0.0.1:8000
OPENROUTER_API_KEY=your_key_here
```

If you are using a different provider through PydanticAI, add the required provider key instead.

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

```bash
uv run uvicorn cinemind.api.main:app --reload
```

Useful endpoints:

- `GET /health`
- `POST /recommend`
- Swagger UI: `http://127.0.0.1:8000/docs`

## 5. Run the frontend

```bash
uv run streamlit run src/cinemind/frontend/app.py
```

Then open the local Streamlit URL shown in the terminal.

## 6. Run full app (two terminals)

Terminal 1:

```bash
uv run uvicorn cinemind.api.main:app --reload
```

Terminal 2:

```bash
uv run streamlit run src/cinemind/frontend/app.py
```
