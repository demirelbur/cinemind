from pydantic import Field

from cinemind.schemas.base import StrictBaseModel
from cinemind.schemas.movie import MovieRecord
from cinemind.schemas.preferences import ParsedPreferences


class RecommendationContext(StrictBaseModel):
    """Internal context passed into Agent 2 for grounded movie recommendation."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Original natural-language user query.",
    )
    preferences: ParsedPreferences = Field(
        ...,
        description="Structured preferences extracted from the user query.",
    )
    candidates: list[MovieRecord] = Field(
        default_factory=list,
        description="Grounded candidate movies retrieved from PostgreSQL.",
    )
    max_results: int = Field(
        ...,
        ge=1,
        le=10,
        description="Maximum number of recommendations to return.",
    )
