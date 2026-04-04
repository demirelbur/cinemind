from cinemind.schemas.api import RecommendationResponse, RecommendRequest
from cinemind.schemas.movie import MovieRecommendation, MovieRecord
from cinemind.schemas.preferences import ParsedPreferences
from cinemind.schemas.retrieval import RetrievalResult
from cinemind.services.recommendation_service import run_recommendation_pipeline


def test_run_recommendation_pipeline_returns_clamped_results(monkeypatch):
    retrieval_result = RetrievalResult(
        preferences=ParsedPreferences(genre="sci-fi", desired_results=3),
        candidates=[
            MovieRecord(
                title="Movie A",
                genre="sci-fi",
                year=1982,
                rating=8.0,
                synopsis="A science fiction adventure set in space.",
                director="Director A",
                lead_actor="Actor A",
                recommended_for="teens",
            ),
            MovieRecord(
                title="Movie B",
                genre="sci-fi",
                year=1985,
                rating=7.8,
                synopsis="A time-travel science fiction story with humor.",
                director="Director B",
                lead_actor="Actor B",
                recommended_for="teens",
            ),
            MovieRecord(
                title="Movie C",
                genre="sci-fi",
                year=1988,
                rating=7.5,
                synopsis="A dark futuristic tale about conflict and identity.",
                director="Director C",
                lead_actor="Actor C",
                recommended_for="teens",
            ),
        ],
    )

    monkeypatch.setattr(
        "cinemind.services.recommendation_service.run_intent_retrieval_agent",
        lambda request: retrieval_result,
    )

    monkeypatch.setattr(
        "cinemind.services.recommendation_service.recommend_movies",
        lambda context: RecommendationResponse(
            query=context.query,
            recommendations=[
                MovieRecommendation(
                    movie=context.candidates[0],
                    reason="Strong sci-fi fit.",
                    match_score=0.95,
                ),
                MovieRecommendation(
                    movie=context.candidates[1],
                    reason="Good teen-friendly sci-fi option.",
                    match_score=0.90,
                ),
                MovieRecommendation(
                    movie=context.candidates[2],
                    reason="Another relevant sci-fi choice.",
                    match_score=0.85,
                ),
            ],
        ),
    )

    response = run_recommendation_pipeline(
        RecommendRequest(query="Give me 2 sci-fi movies.", max_results=2)
    )

    assert len(response.recommendations) == 2
    assert response.query == "Give me 2 sci-fi movies."
