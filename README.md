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

## ⬇️ Installation

Minimum requirement: Python 3.11+

Install dependencies:

```bash
uv sync
```

For complete setup, environment variables, migrations, and local run steps, see [docs/quickstart.md](docs/quickstart.md).

## 🚀 Usage

Start backend:

```bash
uv run uvicorn cinemind.api.main:app --reload
```

This repository is intentionally dev-first; the `--reload` workflow is used on purpose for local iteration speed.

Start frontend:

```bash
uv run streamlit run src/cinemind/frontend/app.py
```

Then ask for recommendations in natural language, for example:

- "Give me 3 dark sci-fi movies after 2010."
- "Recommend a family-friendly movie with no horror."

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
- Add Docker Compose for one-command local startup

## 📄 License

This project is licensed under Apache License 2.0.

See [LICENSE](LICENSE) for the full text.

Note: dataset licensing is separate from source-code licensing. See [docs/dataset_setup.md](docs/dataset_setup.md).
