# Architecture Notes

## Retrieval is deterministic

The LLM does not generate SQL directly.

- The parser turns user language into `ParsedPreferences`.
- The retrieval layer uses deterministic PostgreSQL filtering.
- Agent 2 ranks only within grounded candidates.

This makes the system easier to test, safer, and more production-friendly.

## Agent 2 is grounded

Agent 2 is only allowed to recommend movies from the retrieved candidate set.

This reduces hallucination risk and keeps explanations grounded in real database records.

## `max_results` is optional

CineMind supports both:

- an explicit API override via `RecommendRequest.max_results`
- an inferred count from the query, such as "top ten movies"

The final result count is resolved by the orchestration layer.

## Rejected rows are expected

During dataset transformation, some rows may be rejected if they fail the `MovieRecord` schema.

This is intentional and improves data quality.

## MVP with clean upgrade path

The current version uses PostgreSQL only.

A natural next step is:

- PostgreSQL + `pgvector`
- semantic search
- hybrid retrieval
- better reranking
