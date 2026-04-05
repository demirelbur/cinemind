# Testing

## Run deterministic tests only

```bash
uv run pytest -m "not llm"
```

## Run live LLM integration tests

```bash
uv run pytest -m llm -s
```

The test campaign is intentionally split into:

- deterministic schema and wrapper tests
- live LLM integration tests

This keeps testing practical for an LLM-based system.
