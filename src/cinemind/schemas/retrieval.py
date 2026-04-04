from pydantic import Field

from cinemind.schemas.base import StrictBaseModel
from cinemind.schemas.movie import MovieRecord
from cinemind.schemas.preferences import ParsedPreferences


class RetrievalResult(StrictBaseModel):
    """Structured output from the retrieval component, containing relevant movies and extracted preferences."""

    preferences: ParsedPreferences = Field(
        ...,
        description="Structured movie preferences extracted from the user's query.",
    )
    candidates: list[MovieRecord] = Field(
        default_factory=list,
        description="Candidate movies retrieved from PostgreSQL based on the extracted preferences.",
    )
