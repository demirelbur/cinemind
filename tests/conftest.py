import pytest

from cinemind.core.config import get_settings
from cinemind.schemas.preferences import ParsedPreferences

get_settings()


@pytest.fixture
def empty_preferences() -> ParsedPreferences:
    return ParsedPreferences()


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "llm: marks tests that require a live LLM call",
    )
