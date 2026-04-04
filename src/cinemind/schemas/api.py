from pydantic import Field

from cinemind.schemas.base import StrictBaseModel
from cinemind.schemas.movie import MovieRecommendation


class RecommendRequest(StrictBaseModel):
    """Incoming recommendation request from the client."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural-language movie preference provided by the user.",
    )
    max_results: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description=(
            "Optional override for the number of recommendations to return. "
            "If omitted, the system may infer it from the query or use a default."
        ),
    )


class RecommendationResponse(StrictBaseModel):
    """Response returned to the client for a recommendation request."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Original user query used to generate the recommendations.",
    )
    recommendations: list[MovieRecommendation] = Field(
        default_factory=list,
        description="Ordered list of movie recommendations.",
    )
