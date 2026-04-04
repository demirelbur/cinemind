import pytest

from cinemind.agents.intent_parser_agent import parse_preferences
from cinemind.schemas.api import RecommendRequest
from cinemind.schemas.preferences import ParsedPreferences


class IntentParserCase:
    def __init__(self, name: str, query: str, expected: ParsedPreferences):
        self.name = name
        self.query = query
        self.expected = expected


TEST_CASES = [
    IntentParserCase(
        name="simple_comedy",
        query="Recommend a good comedy movie.",
        expected=ParsedPreferences(genre="comedy"),
    ),
    IntentParserCase(
        name="nineties_comedy",
        query="Recommend a good comedy movie from the 90s.",
        expected=ParsedPreferences(
            genre="comedy",
            min_year=1990,
            max_year=1999,
        ),
    ),
    IntentParserCase(
        name="dark_scifi_after_2010",
        query="Give me 3 dark sci-fi movies after 2010.",
        expected=ParsedPreferences(
            genre="sci-fi",
            min_year=2010,
            mood="dark",
            desired_results=3,
        ),
    ),
    IntentParserCase(
        name="family_no_horror",
        query="Recommend a family-friendly movie, no horror.",
        expected=ParsedPreferences(
            recommended_for="family",
            exclude_genres=["horror"],
        ),
    ),
    IntentParserCase(
        name="top_ten_thrillers_before_2000",
        query="What are the top ten thrillers before 2000?",
        expected=ParsedPreferences(
            genre="thriller",
            max_year=1999,
            desired_results=10,
        ),
    ),
    IntentParserCase(
        name="friendship_theme",
        query="Recommend something emotional about friendship.",
        expected=ParsedPreferences(
            mood="emotional",
            themes=["friendship"],
        ),
    ),
    IntentParserCase(
        name="broad_query_should_stay_sparse",
        query="Recommend something good.",
        expected=ParsedPreferences(),
    ),
]


def compare_expected_subset(
    actual: ParsedPreferences,
    expected: ParsedPreferences,
) -> list[str]:
    errors: list[str] = []

    actual_data = actual.model_dump()
    expected_data = expected.model_dump(exclude_none=True)

    for key, expected_value in expected_data.items():
        actual_value = actual_data.get(key)
        if actual_value != expected_value:
            errors.append(
                f"Field '{key}' mismatch: expected={expected_value!r}, actual={actual_value!r}"
            )

    return errors


@pytest.mark.llm
@pytest.mark.parametrize("case", TEST_CASES, ids=[case.name for case in TEST_CASES])
def test_intent_parser_live(case: IntentParserCase):
    request = RecommendRequest(query=case.query)
    actual = parse_preferences(request)

    errors = compare_expected_subset(actual, case.expected)

    assert not errors, (
        f"\nQuery: {case.query}\n"
        f"Actual: {actual.model_dump_json(indent=2)}\n"
        f"Errors:\n- " + "\n- ".join(errors)
    )
