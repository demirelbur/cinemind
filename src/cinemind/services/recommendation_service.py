from cinemind.agents.intent_retrieval_agent import (
    resolve_final_result_count,
    run_intent_retrieval_agent,
)
from cinemind.agents.recommendation_agent import recommend_movies
from cinemind.schemas.api import RecommendationResponse, RecommendRequest
from cinemind.schemas.recommendation import RecommendationContext


def run_recommendation_pipeline(request: RecommendRequest) -> RecommendationResponse:
    """
    End-to-end CineMind recommendation pipeline:
    1. Parse user intent and retrieve grounded candidates.
    2. Resolve final recommendation count.
    3. Run grounded recommendation generation.
    """
    retrieval_result = run_intent_retrieval_agent(request)

    if not retrieval_result.candidates:
        return RecommendationResponse(
            query=request.query,
            recommendations=[],
        )

    final_result_count = resolve_final_result_count(
        request=request,
        desired_results_from_query=retrieval_result.preferences.desired_results,
    )
    final_result_count = min(final_result_count, len(retrieval_result.candidates))

    context = RecommendationContext(
        query=request.query,
        preferences=retrieval_result.preferences,
        candidates=retrieval_result.candidates,
        max_results=final_result_count,
    )

    response = recommend_movies(context)

    if len(response.recommendations) > final_result_count:
        response = RecommendationResponse(
            query=response.query,
            recommendations=response.recommendations[:final_result_count],
        )

    return response
