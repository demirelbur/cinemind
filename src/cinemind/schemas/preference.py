from pydantic import Field, field_validator, model_validator

from cinemind.schemas.base import StrictBaseModel
from cinemind.schemas.movie import AudienceLiteral, GenreLiteral


class ParsedPreferences(StrictBaseModel):
    """Structured representation of user preferences extracted from natural language."""

    genre: GenreLiteral | None = Field(
        default=None,
        description="Preferred primary genre, if explicitly or implicitly identified.",
    )
    min_year: int | None = Field(
        default=None,
        ge=1900,
        le=2025,
        description="Minimum preferred release year.",
    )
    max_year: int | None = Field(
        default=None,
        ge=1900,
        le=2025,
        description="Maximum preferred release year.",
    )
    min_rating: float | None = Field(
        default=None,
        ge=0.0,
        le=10.0,
        description="Minimum preferred rating threshold.",
    )
    recommended_for: AudienceLiteral | None = Field(
        default=None,
        description="Preferred audience category, if inferred from the query.",
    )
    mood: str | None = Field(
        default=None,
        description="Free-text mood or tone preference, such as 'dark' or 'uplifting'.",
    )
    themes: list[str] = Field(
        default_factory=list,
        description="Free-text thematic preferences, such as 'space', 'friendship', or 'revenge'.",
    )
    exclude_genres: list[GenreLiteral] = Field(
        default_factory=list,
        description="Genres the user wants to avoid.",
    )

    @field_validator("mood", mode="before")
    @classmethod
    def normalize_mood(cls, value: object) -> object:
        """Collapse repeated whitespace and convert empty strings to None."""
        if value is None:
            return None
        if isinstance(value, str):
            normalized = " ".join(value.split())
            return normalized or None
        return value

    @field_validator("themes", mode="before")
    @classmethod
    def normalize_themes(cls, value: object) -> list[str] | object:
        """Normalize theme strings and drop empty entries."""
        if value is None:
            return []
        if isinstance(value, list):
            cleaned: list[str] = []
            for item in value:
                if isinstance(item, str):
                    normalized = " ".join(item.split())
                    if normalized:
                        cleaned.append(normalized)
            return cleaned
        return value

    @model_validator(mode="after")
    def validate_year_range(self) -> "ParsedPreferences":
        """Ensure the minimum year does not exceed the maximum year."""
        if (
            self.min_year is not None
            and self.max_year is not None
            and self.min_year > self.max_year
        ):
            raise ValueError("min_year cannot be greater than max_year")
        return self
