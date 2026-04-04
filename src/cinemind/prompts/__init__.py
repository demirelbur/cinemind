"""System prompts for the agents."""

from importlib.resources import files

_pkg = files(__name__)
INTENT_PARSER_SYSTEM_PROMPT: str = (_pkg / "INTENT_PARSER_SYSTEM.md").read_text(
    encoding="utf-8"
)
RECOMMENDATION_AGENT_SYSTEM_PROMPT: str = (
    _pkg / "RECOMMENDATION_AGENT_SYSTEM.md"
).read_text(encoding="utf-8")

__all__ = ["INTENT_PARSER_SYSTEM_PROMPT", "RECOMMENDATION_AGENT_SYSTEM_PROMPT"]
