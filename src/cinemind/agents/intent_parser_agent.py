from dotenv import load_dotenv
from pydantic_ai import Agent

from cinemind.prompts import INTENT_PARSER_SYSTEM_PROMPT
from cinemind.schemas.api import RecommendRequest
from cinemind.schemas.preferences import ParsedPreferences

load_dotenv()

intent_parser_agent = Agent(
    "openrouter:openai/gpt-4o",
    name="intent_parser_agent",
    description="Parses a movie recommendation request into structured user preferences.",
    output_type=ParsedPreferences,
    defer_model_check=True,
    system_prompt=INTENT_PARSER_SYSTEM_PROMPT,
)


def parse_preferences(request: RecommendRequest) -> ParsedPreferences:
    prompt = (
        "Parse the following movie recommendation request into structured preferences.\n\n"
        f"User query: {request.query}\n"
        f"Explicit API max_results override: {request.max_results}\n\n"
        "Important: the explicit API max_results override is not the same as user intent. "
        "Only set desired_results if the user query itself explicitly asks for a specific number."
    )

    result = intent_parser_agent.run_sync(prompt)
    return result.output
