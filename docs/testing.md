# Testing

## Run deterministic tests only

```bash
uv run pytest -m "not llm"
```

## Run live LLM integration tests

```bash
uv run pytest -m llm -s
```

The test suite is split into:

- **Deterministic** — schema validation, retrieval logic, pipeline wrappers (fast, no API calls)
- **Live LLM** — end-to-end tests that call OpenRouter (tagged `@pytest.mark.llm`)

## Test files

| File | What it tests |
|---|---|
| `test_intent_parser_unit.py` | Monkeypatches `get_intent_parser_agent` factory |
| `test_intent_parser_integration.py` | Live LLM intent parsing (tagged `llm`) |
| `test_agent2_integration.py` | Full pipeline with Agent 2 |
| `test_preferences_schema.py` | ParsedPreferences validation and normalization |
| `test_recommendation_services.py` | Pipeline service, monkeypatches retrieval |
