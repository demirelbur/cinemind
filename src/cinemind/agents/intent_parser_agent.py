from functools import cache

from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from cinemind.core.config import get_settings
from cinemind.prompts import INTENT_PARSER_SYSTEM_PROMPT
from cinemind.schemas.api import RecommendRequest
from cinemind.schemas.preferences import ParsedPreferences


@cache
def get_intent_parser_agent() -> Agent[None, ParsedPreferences]:
    settings = get_settings()
    provider = OpenRouterProvider(api_key=settings.openrouter_api_key)
    model = OpenRouterModel(
        settings.llm_model_name,
        provider=provider,
    )
    return Agent(
        model,
        name="intent_parser_agent",
        description="Parses a movie recommendation request into structured user preferences.",
        output_type=ParsedPreferences,
        system_prompt=INTENT_PARSER_SYSTEM_PROMPT,
        output_retries=3,
    )


def parse_preferences(request: RecommendRequest) -> ParsedPreferences:
    agent = get_intent_parser_agent()
    prompt = (
        "Parse the following movie recommendation request into structured preferences.\n\n"
        f"User query: {request.query}\n"
        f"Explicit API max_results override: {request.max_results}\n\n"
        "Important: the explicit API max_results override is not the same as user intent. "
        "Only set desired_results if the user query itself explicitly asks for a specific number."
    )
    return agent.run_sync(prompt).output
