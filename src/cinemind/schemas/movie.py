from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class MovieRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Movie title",
    )
    genre: GenreLiteral = Field(
        ...,
        description="One of the supported CineMind genres",
    )
    year: int = Field(
        ...,
        ge=1900,
        le=2025,
        description="Release year",
    )
    rating: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Rating out of 10",
    )
    synopsis: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Brief plot summary",
    )
    # Optional fields with default None
    director: str | None = Field(
        default=None,
        description="Director name",
    )
    lead_actor: str | None = Field(
        default=None,
        description="Lead actor name",
    )
    recommended_for: AudienceLiteral | None = Field(
        default=None,
        description="Target audience category",
    )

    @field_validator("title", "synopsis", "director", "lead_actor", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = " ".join(value.split())
            return value or None
        return value
