from __future__ import annotations

from dataclasses import dataclass

from cinemind.agents.intent_parser_agent import parse_preferences
from cinemind.db.session import SessionLocal
from cinemind.retrieval.search import RetrievalConfig, retrieve_candidate_movies
from cinemind.schemas.api import RecommendRequest
from cinemind.schemas.retrieval import RetrievalResult


@dataclass(frozen=True)
class IntentRetrievalConfig:
    """Configuration for Agent 1 orchestration."""

    default_final_results: int = 5
    candidate_limit: int = 25
    max_final_results_cap: int = 10


def resolve_final_result_count(
    request: RecommendRequest,
    desired_results_from_query: int | None,
    config: IntentRetrievalConfig | None = None,
) -> int:
    """
    Resolve the final number of recommendations to return later in the pipeline.

    Priority:
    1. Explicit API override from RecommendRequest.max_results
    2. desired_results inferred from user language
    3. system default
    """
    config = config or IntentRetrievalConfig()

    resolved = (
        request.max_results
        or desired_results_from_query
        or config.default_final_results
    )
    return min(resolved, config.max_final_results_cap)


def run_intent_retrieval_agent(
    request: RecommendRequest,
    config: IntentRetrievalConfig | None = None,
) -> RetrievalResult:
    """
    Run Agent 1 end-to-end:
    - parse user intent into ParsedPreferences
    - retrieve grounded movie candidates from PostgreSQL
    - return RetrievalResult
    """
    config = config or IntentRetrievalConfig()

    preferences = parse_preferences(request)

    session = SessionLocal()
    try:
        candidates = retrieve_candidate_movies(
            session=session,
            preferences=preferences,
            config=RetrievalConfig(candidate_limit=config.candidate_limit),
        )
    finally:
        session.close()

    return RetrievalResult(
        preferences=preferences,
        candidates=candidates,
    )
