import pytest
from pydantic import ValidationError

from cinemind.schemas.preferences import ParsedPreferences


def test_parsed_preferences_accepts_valid_data():
    prefs = ParsedPreferences(
        genre="sci-fi",
        min_year=1980,
        max_year=1989,
        min_rating=7.0,
        recommended_for="teens",
        exclude_genres=["horror"],
        mood="dark",
        themes=["space travel", "friendship"],
        desired_results=5,
    )

    assert prefs.genre == "sci-fi"
    assert prefs.min_year == 1980
    assert prefs.max_year == 1989
    assert prefs.min_rating == 7.0
    assert prefs.recommended_for == "teens"
    assert prefs.exclude_genres == ["horror"]
    assert prefs.mood == "dark"
    assert prefs.themes == ["space travel", "friendship"]
    assert prefs.desired_results == 5


def test_parsed_preferences_rejects_invalid_genre():
    with pytest.raises(ValidationError):
        ParsedPreferences(genre="fantasy")


def test_parsed_preferences_rejects_invalid_desired_results():
    with pytest.raises(ValidationError):
        ParsedPreferences(desired_results=11)


def test_parsed_preferences_rejects_invalid_year_range():
    with pytest.raises(ValidationError):
        ParsedPreferences(min_year=2010, max_year=2000)


def test_parsed_preferences_normalizes_mood():
    prefs = ParsedPreferences(mood="   very   dark   ")
    assert prefs.mood == "very dark"


def test_parsed_preferences_normalizes_themes_and_drops_empty_values():
    prefs = ParsedPreferences(themes=["  space  travel ", " ", "friendship"])
    assert prefs.themes == ["space travel", "friendship"]


def test_parsed_preferences_deduplicates_exclude_genres():
    prefs = ParsedPreferences(exclude_genres=["horror", "romance", "horror"])
    assert prefs.exclude_genres == ["horror", "romance"]
