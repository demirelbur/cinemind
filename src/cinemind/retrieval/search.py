from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from cinemind.db.models import Movie
from cinemind.schemas.movie import MovieRecord
from cinemind.schemas.preferences import ParsedPreferences


@dataclass(frozen=True)
class RetrievalConfig:
    """Internal configuration for PostgreSQL candidate retrieval."""

    candidate_limit: int = 25


def _apply_hard_filters(
    statement: Select[tuple[Movie]],
    preferences: ParsedPreferences,
) -> Select[tuple[Movie]]:
    """Apply deterministic SQL filters based on structured preferences."""
    if preferences.genre is not None:
        statement = statement.where(Movie.genre == preferences.genre)

    if preferences.min_year is not None:
        statement = statement.where(Movie.year >= preferences.min_year)

    if preferences.max_year is not None:
        statement = statement.where(Movie.year <= preferences.max_year)

    if preferences.min_rating is not None:
        statement = statement.where(Movie.rating >= preferences.min_rating)

    if preferences.recommended_for is not None:
        statement = statement.where(
            Movie.recommended_for == preferences.recommended_for
        )

    if preferences.exclude_genres:
        statement = statement.where(Movie.genre.notin_(preferences.exclude_genres))

    return statement


def _base_statement() -> Select[tuple[Movie]]:
    """Create the base movie selection statement."""
    return select(Movie).order_by(
        Movie.rating.desc(), Movie.year.desc(), Movie.title.asc()
    )


def _rows_to_movie_records(rows: list[Movie]) -> list[MovieRecord]:
    """Convert ORM rows into validated domain models."""
    return [
        MovieRecord(
            title=row.title,
            genre=row.genre,
            year=row.year,
            rating=row.rating,
            synopsis=row.synopsis,
            director=row.director,
            lead_actor=row.lead_actor,
            recommended_for=row.recommended_for,
        )
        for row in rows
    ]


def _run_query(
    session: Session,
    statement: Select[tuple[Movie]],
    limit: int,
) -> list[MovieRecord]:
    rows = session.execute(statement.limit(limit)).scalars().all()
    return _rows_to_movie_records(rows)


def retrieve_candidate_movies(
    session: Session,
    preferences: ParsedPreferences,
    config: RetrievalConfig | None = None,
) -> list[MovieRecord]:
    """
    Retrieve candidate movies from PostgreSQL.

    Strategy:
    1. Apply full hard filters.
    2. If no results, relax `min_rating`.
    3. If still no results, relax `recommended_for`.
    4. If still no results, fall back to broader query with genre/year/exclusions only.
    """
    config = config or RetrievalConfig()

    # Attempt 1: full filter set
    statement = _apply_hard_filters(_base_statement(), preferences)
    candidates = _run_query(session, statement, config.candidate_limit)
    if candidates:
        return candidates

    # Attempt 2: relax min_rating
    relaxed_min_rating = preferences.model_copy(update={"min_rating": None})
    statement = _apply_hard_filters(_base_statement(), relaxed_min_rating)
    candidates = _run_query(session, statement, config.candidate_limit)
    if candidates:
        return candidates

    # Attempt 3: relax recommended_for too
    relaxed_audience = relaxed_min_rating.model_copy(update={"recommended_for": None})
    statement = _apply_hard_filters(_base_statement(), relaxed_audience)
    candidates = _run_query(session, statement, config.candidate_limit)
    if candidates:
        return candidates

    # Attempt 4: broad fallback with only genre/year/exclusions
    broad_preferences = ParsedPreferences(
        genre=preferences.genre,
        min_year=preferences.min_year,
        max_year=preferences.max_year,
        exclude_genres=preferences.exclude_genres,
    )
    statement = _apply_hard_filters(_base_statement(), broad_preferences)
    candidates = _run_query(session, statement, config.candidate_limit)
    if candidates:
        return candidates

    # Final fallback: top-rated movies respecting only exclusions
    final_fallback = ParsedPreferences(exclude_genres=preferences.exclude_genres)
    statement = _apply_hard_filters(_base_statement(), final_fallback)
    return _run_query(session, statement, config.candidate_limit)
