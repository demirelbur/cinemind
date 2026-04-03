from typing import Literal

from pydantic import Field, field_validator

from cinemind.schemas.base import StrictBaseModel


GenreLiteral = Literal[
    "action",
    "comedy",
    "drama",
    "sci-fi",
    "thriller",
    "horror",
    "romance",
]

AudienceLiteral = Literal["family", "teens", "adults"]


class MovieRecord(StrictBaseModel):
    """Canonical normalized movie entity used across the CineMind system."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Movie title.",
    )
    genre: GenreLiteral = Field(
        ...,
        description="Primary normalized genre used by CineMind.",
    )
    year: int = Field(
        ...,
        ge=1900,
        le=2025,
        description="Movie release year.",
    )
    rating: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Average movie rating on a 0.0 to 10.0 scale.",
    )
    synopsis: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Brief plot summary.",
    )
    director: str | None = Field(
        default=None,
        description="Director name, when available.",
    )
    lead_actor: str | None = Field(
        default=None,
        description="Lead actor name, when available.",
    )
    recommended_for: AudienceLiteral | None = Field(
        default=None,
        description="Suggested audience category for the movie.",
    )

    @field_validator("title", "synopsis", "director", "lead_actor", mode="before")
    @classmethod
    def normalize_strings(cls, value: object) -> object:
        """Collapse repeated whitespace and convert empty strings to None."""
        if value is None:
            return None
        if isinstance(value, str):
            normalized = " ".join(value.split())
            return normalized or None
        return value


class MovieRecommendation(StrictBaseModel):
    """A recommended movie together with explanation and ranking metadata."""

    movie: MovieRecord = Field(
        ...,
        description="Normalized movie data for the recommended item.",
    )
    reason: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="Short explanation of why this movie matches the user's request.",
    )
    match_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized relevance score where 1.0 is the strongest match.",
    )

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value: object) -> object:
        """Collapse repeated whitespace in explanation text."""
        if value is None:
            return None
        if isinstance(value, str):
            normalized = " ".join(value.split())
            return normalized or None
        return value
