import pytest

from cinemind.schemas.api import RecommendRequest
from cinemind.services.recommendation_service import run_recommendation_pipeline


@pytest.mark.llm
def test_agent2_end_to_end_returns_grounded_recommendations():
    request = RecommendRequest(query="Give me 3 dark sci-fi movies after 2010.")

    response = run_recommendation_pipeline(request)

    assert response.query == request.query
    assert 1 <= len(response.recommendations) <= 3

    for recommendation in response.recommendations:
        assert recommendation.movie.genre == "sci-fi"
        assert recommendation.movie.year >= 2010
        assert len(recommendation.reason) >= 10
        assert 0.0 <= recommendation.match_score <= 1.0
