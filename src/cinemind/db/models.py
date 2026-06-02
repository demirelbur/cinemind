from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    Float,
    Integer,
    String,
    Text,
    TIMESTAMP,
)
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from cinemind.db.base import Base


class Movie(Base):
    __tablename__ = "movies"

    __table_args__ = (
        CheckConstraint(
            "tmdb_rating IS NULL OR (tmdb_rating BETWEEN 0.0 AND 10.0)",
            name="ck_tmdb_rating",
        ),
        CheckConstraint(
            "popularity IS NULL OR popularity >= 0.0",
            name="ck_popularity",
        ),
        CheckConstraint(
            "recommended_for IS NULL OR recommended_for IN ('family', 'teens', 'adults')",
            name="ck_movies_recommended_for",
        ),
    )

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # IMDb source fields
    imdb_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    imdb_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    imdb_rating: Mapped[float | None] = mapped_column(Float, nullable=True)

    # TMDB enrichment
    tmdb_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    genres: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    runtime_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tmdb_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    vote_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    popularity: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Media
    poster_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    backdrop_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    trailer_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Credits
    director: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lead_actor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lead_actor_2: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lead_actor_3: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Classification
    recommended_for: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    audience: Mapped[str | None] = mapped_column(String(20), nullable=True)
    editorial_tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Embedding
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

    # Metadata
    enriched_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)

