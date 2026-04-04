import pytest

from cinemind.schemas.preferences import ParsedPreferences


@pytest.fixture
def empty_preferences() -> ParsedPreferences:
    return ParsedPreferences()


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "llm: marks tests that require a live LLM call",
    )
