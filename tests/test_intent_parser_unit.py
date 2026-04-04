from types import SimpleNamespace

import pytest
from cinemind.agents.intent_parser_agent import parse_preferences
from pydantic import ValidationError

from cinemind.schemas.api import RecommendRequest
from cinemind.schemas.preferences import ParsedPreferences


def test_recommend_request_accepts_optional_max_results():
    request = RecommendRequest(query="Recommend a thriller", max_results=3)
    assert request.query == "Recommend a thriller"
    assert request.max_results == 3


def test_recommend_request_allows_missing_max_results():
    request = RecommendRequest(query="Recommend a thriller")
    assert request.max_results is None


def test_recommend_request_rejects_invalid_max_results():
    with pytest.raises(ValidationError):
        RecommendRequest(query="Recommend a thriller", max_results=11)


def test_parse_preferences_returns_agent_output(monkeypatch):
    expected = ParsedPreferences(
        genre="comedy",
        min_year=1990,
        max_year=1999,
    )

    def fake_run_sync(prompt: str):
        assert "User query: Recommend a good comedy movie from the 90s." in prompt
        return SimpleNamespace(output=expected)

    monkeypatch.setattr(
        "cinemind.agents.intent_parser_agent.intent_parser_agent.run_sync",
        fake_run_sync,
    )

    request = RecommendRequest(query="Recommend a good comedy movie from the 90s.")
    result = parse_preferences(request)

    assert result == expected


def test_parse_preferences_includes_api_max_results_in_prompt(monkeypatch):
    expected = ParsedPreferences(genre="sci-fi", desired_results=10)

    def fake_run_sync(prompt: str):
        assert "Explicit API max_results override: 4" in prompt
        assert (
            "Only set desired_results if the user query itself explicitly asks"
            in prompt
        )
        return SimpleNamespace(output=expected)

    monkeypatch.setattr(
        "cinemind.agents.intent_parser_agent.intent_parser_agent.run_sync",
        fake_run_sync,
    )

    request = RecommendRequest(
        query="What are the top ten sci-fi movies?",
        max_results=4,
    )
    result = parse_preferences(request)

    assert result.genre == "sci-fi"
    assert result.desired_results == 10
