from functools import cache

from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel

from cinemind.core.config import get_settings
from cinemind.prompts import INTENT_PARSER_SYSTEM_PROMPT
from cinemind.schemas.api import RecommendRequest
from cinemind.schemas.preferences import ParsedPreferences


@cache
def get_intent_parser_agent() -> Agent:
    settings = get_settings()
    model = OpenRouterModel(
        settings.llm_model_name,
        provider=settings.llm_provider,
    )
    return Agent(
        model,
        name="intent_parser_agent",
        description="Parses a movie recommendation request into structured user preferences.",
        output_type=str,
        system_prompt=INTENT_PARSER_SYSTEM_PROMPT,
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
    result = agent.run_sync(prompt)
    output = result.output
    if isinstance(output, str):
        return ParsedPreferences.parse_raw(output)
    return ParsedPreferences.parse_obj(output)
