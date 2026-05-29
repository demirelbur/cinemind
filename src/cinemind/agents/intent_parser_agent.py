from functools import cache

from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from cinemind.core.config import get_settings
from cinemind.prompts import INTENT_PARSER_SYSTEM_PROMPT
from cinemind.schemas.api import RecommendRequest
from cinemind.schemas.preferences import ParsedPreferences


@cache
def get_intent_parser_agent() -> Agent:
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
        output_type=str,
        system_prompt=INTENT_PARSER_SYSTEM_PROMPT,
    )


def _extract_json(text: str) -> str:
    """Strip markdown code fences from LLM JSON output."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


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
        cleaned = _extract_json(output)
        return ParsedPreferences.model_validate_json(cleaned)
    return ParsedPreferences.model_validate(output)
