from functools import cache

from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from cinemind.core.config import get_settings
from cinemind.prompts import RECOMMENDATION_AGENT_SYSTEM_PROMPT
from cinemind.schemas.api import RecommendationResponse
from cinemind.schemas.recommendation import RecommendationContext


@cache
def get_recommendation_agent() -> Agent:
    settings = get_settings()
    provider = OpenRouterProvider(api_key=settings.openrouter_api_key)
    model = OpenRouterModel(
        settings.llm_model_name,
        provider=provider,
    )
    return Agent(
        model,
        name="recommendation_agent",
        description="Ranks and explains movie recommendations from candidate movies.",
        output_type=RecommendationResponse,
        system_prompt=RECOMMENDATION_AGENT_SYSTEM_PROMPT,
        retries=2,
    )


def recommend_movies(context: RecommendationContext) -> RecommendationResponse:
    """
    Run Agent 2: grounded recommendation generation.

    Input:
        RecommendationContext (query + preferences + candidates + max_results)

    Output:
        RecommendationResponse
    """

    # Convert candidates into clean JSON-like structure
    candidates_payload = [movie.model_dump() for movie in context.candidates]

    prompt = (
        "Generate grounded movie recommendations from the following context.\n\n"
        f"User query:\n{context.query}\n\n"
        f"Parsed preferences:\n{context.preferences.model_dump_json(indent=2)}\n\n"
        f"Maximum recommendations to return:\n{context.max_results}\n\n"
        f"Candidate movies:\n{candidates_payload}\n\n"
        "Return a RecommendationResponse using ONLY the candidate movies."
    )

    result = get_recommendation_agent().run_sync(prompt)

    response: RecommendationResponse = result.output

    # ✅ Defensive post-processing (important in production)
    if len(response.recommendations) > context.max_results:
        response = RecommendationResponse(
            query=response.query,
            recommendations=response.recommendations[: context.max_results],
        )

    return response
