from fastapi import APIRouter, HTTPException, status

from cinemind.schemas.api import RecommendationResponse, RecommendRequest
from cinemind.services.recommendation_service import run_recommendation_pipeline

# run_recommendation_engine [better naming]

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["system"],
    summary="Health Check",
    description="Check the health of the API",
)
def health_check() -> dict[str, str]:
    """
    Endpoint to check the health of the API.

    Returns:
        A JSON object indicating the API is healthy.
    """
    return {"status": "healthy"}


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    tags=["recommendation"],
    summary="Generate grounded Movie Recommendations",
    description="Get movie recommendations based on user preferences",
)
def recommend(request: RecommendRequest) -> RecommendationResponse:
    """
    Endpoint to get movie recommendations based on user preferences.

    Args:
        request: A RecommendRequest object containing user preferences.

    Returns:
        A RecommendationResponse object containing a list of recommended movies.

    Raises:
        HTTPException: If the recommendation engine fails, with status code 500.

    Run the full CineMind recommendation pipeline, which includes:
    1. Parse user intent
    2. Retrieve candidate movies
    3. Rank and explain recommendations
    """
    try:
        return run_recommendation_pipeline(request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation engine failed: {exc}",
        ) from exc
