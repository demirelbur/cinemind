from functools import cache

from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from cinemind.core.config import get_settings
from cinemind.prompts import RECOMMENDATION_AGENT_SYSTEM_PROMPT
from cinemind.schemas.api import RecommendationResponse
from cinemind.schemas.recommendation import RecommendationContext


@cache
def get_recommendation_agent() -> Agent[None, RecommendationResponse]:
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
        output_retries=3,
    )


def recommend_movies(context: RecommendationContext) -> RecommendationResponse:
    """
    Run Agent 2: grounded recommendation generation.

    Input:
        RecommendationContext (query + preferences + candidates + max_results)

    Output:
        RecommendationResponse
    """

    prompt = (
        "Generate grounded movie recommendations from the following context.\n\n"
        f"User query:\n{context.query}\n\n"
        f"Parsed preferences:\n{context.preferences.model_dump_json(indent=2)}\n\n"
        f"Candidate movies:\n{context.candidates}\n\n"
        f"Return at most {context.max_results} recommendations using ONLY the candidate movies."
    )

    response = get_recommendation_agent().run_sync(prompt).output

    # Defensive: respect max_results even if LLM overproduces
    if len(response.recommendations) > context.max_results:
        response.recommendations = response.recommendations[: context.max_results]

    return response
