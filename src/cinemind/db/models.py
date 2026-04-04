from sqlalchemy import CheckConstraint, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from cinemind.db.base import Base


class Movie(Base):
    __tablename__ = "movies"

    __table_args__ = (
        CheckConstraint(
            "genre IN ('action', 'comedy', 'drama', 'sci-fi', 'thriller', 'horror', 'romance')",
            name="ck_movies_genre",
        ),
        CheckConstraint(
            "year BETWEEN 1900 AND 2025",
            name="ck_movies_year",
        ),
        CheckConstraint(
            "rating BETWEEN 0.0 AND 10.0",
            name="ck_movies_rating",
        ),
        CheckConstraint(
            "char_length(title) BETWEEN 1 AND 100",
            name="ck_movies_title_length",
        ),
        CheckConstraint(
            "char_length(synopsis) BETWEEN 10 AND 500",
            name="ck_movies_synopsis_length",
        ),
        CheckConstraint(
            "recommended_for IS NULL OR recommended_for IN ('family', 'teens', 'adults')",
            name="ck_movies_recommended_for",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    genre: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    synopsis: Mapped[str] = mapped_column(Text, nullable=False)

    director: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lead_actor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    recommended_for: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
