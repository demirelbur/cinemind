from pydantic import Field, field_validator, model_validator

from cinemind.schemas.base import StrictBaseModel
from cinemind.schemas.movie import AudienceLiteral, GenreLiteral


class ParsedPreferences(StrictBaseModel):
    """
    Structured representation of user intent extracted from natural-language queries.

    This model is produced by the intent parser agent and used by the retrieval layer.
    """

    # Core filters (directly used for SQL filtering)
    genre: GenreLiteral | None = Field(
        default=None,
        description="Preferred primary genre explicitly or implicitly requested by the user.",
    )

    min_year: int | None = Field(
        default=None,
        ge=1900,
        le=2025,
        description="Minimum preferred release year inferred from the query (e.g., 'after 2010').",
    )

    max_year: int | None = Field(
        default=None,
        ge=1900,
        le=2025,
        description="Maximum preferred release year inferred from the query (e.g., 'before 2000').",
    )

    min_rating: float | None = Field(
        default=None,
        ge=0.0,
        le=10.0,
        description="Minimum rating threshold inferred from phrases like 'highly rated'.",
    )

    recommended_for: AudienceLiteral | None = Field(
        default=None,
        description="Target audience inferred from the query (e.g., 'family movie', 'for kids').",
    )

    exclude_genres: list[GenreLiteral] = Field(
        default_factory=list,
        description="Genres the user explicitly wants to avoid.",
    )

    # Soft / semantic preferences (not directly used in SQL yet)
    mood: str | None = Field(
        default=None,
        description="Tone or mood preference such as 'dark', 'light-hearted', or 'emotional'.",
    )

    themes: list[str] = Field(
        default_factory=list,
        description="Free-text thematic preferences such as 'space', 'friendship', or 'revenge'.",
    )

    # Result control (inferred from user language, not API input)
    desired_results: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description=(
            "Desired number of recommendations inferred from the user's query "
            "(e.g., 'top ten movies', 'give me 3 options')."
        ),
    )

    # -------------------------
    # Validators
    # -------------------------

    @field_validator("mood", mode="before")
    @classmethod
    def normalize_mood(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = " ".join(value.split())
            return value or None
        return value

    @field_validator("themes", mode="before")
    @classmethod
    def normalize_themes(cls, value):
        if value is None:
            return []
        if isinstance(value, list):
            cleaned: list[str] = []
            for item in value:
                if isinstance(item, str):
                    item = " ".join(item.split())
                    if item:
                        cleaned.append(item)
            return cleaned
        return value

    @field_validator("exclude_genres", mode="before")
    @classmethod
    def normalize_exclude_genres(cls, value):
        if value is None:
            return []
        if isinstance(value, list):
            return list(dict.fromkeys(value))  # remove duplicates, preserve order
        return value

    @model_validator(mode="after")
    def validate_year_range(self):
        """
        Ensure min_year <= max_year when both are provided.
        """
        if (
            self.min_year is not None
            and self.max_year is not None
            and self.min_year > self.max_year
        ):
            raise ValueError("min_year cannot be greater than max_year")
        return self
