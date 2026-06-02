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
    from sqlalchemy import or_, text as sa_text

    if preferences.genre is not None:
        GENRE_TO_TMDB = {
            "action": "Action", "comedy": "Comedy", "drama": "Drama",
            "sci-fi": "Science Fiction", "thriller": "Thriller",
            "horror": "Horror", "romance": "Romance",
        }
        tmdb_genre = GENRE_TO_TMDB.get(preferences.genre, preferences.genre)
        statement = statement.where(
            sa_text(f"genres @> ARRAY['{tmdb_genre}']")
        )

    if preferences.min_year is not None:
        statement = statement.where(
            or_(
                Movie.imdb_year >= preferences.min_year,
                Movie.release_year >= preferences.min_year,
            )
        )

    if preferences.max_year is not None:
        statement = statement.where(
            or_(
                Movie.imdb_year <= preferences.max_year,
                Movie.release_year <= preferences.max_year,
            )
        )

    if preferences.min_rating is not None:
        statement = statement.where(
            or_(
                Movie.tmdb_rating >= preferences.min_rating,
                Movie.imdb_rating >= preferences.min_rating,
            )
        )

    if preferences.recommended_for is not None:
        statement = statement.where(
            or_(
                Movie.recommended_for == preferences.recommended_for,
                Movie.audience == preferences.recommended_for,
            )
        )

    if preferences.exclude_genres:
        # Exclude movies that contain ANY of the excluded genres
        eg_list = ",".join(f"'{g}'" for g in preferences.exclude_genres)
        statement = statement.where(
            sa_text(f"NOT (genres && ARRAY[{eg_list}])")
        )

    return statement


def _base_statement() -> Select[tuple[Movie]]:
    """Create the base movie selection statement."""
    from sqlalchemy import or_
    stmt = select(Movie).where(
        or_(
            Movie.imdb_title.isnot(None),
            Movie.title.isnot(None),
        )
    ).order_by(
        Movie.tmdb_rating.desc(), Movie.imdb_rating.desc(),
        Movie.release_year.desc(),
        Movie.title.asc()
    )
    return stmt


def _rows_to_movie_records(rows: list[Movie]) -> list[MovieRecord]:
    """Convert ORM rows into validated domain models."""
    records = []
    for row in rows:
        # Use TMDB-enriched data if available, fall back to IMDb source
        title = row.title or row.imdb_title or "Unknown"
        year = row.release_year or row.imdb_year
        rating = row.tmdb_rating if row.tmdb_rating is not None else (row.imdb_rating or 0.0)
        synopsis = row.overview or "No synopsis available."

        if not title or not year or not synopsis:
            continue

        # Derive a single allowed genre from the TMDB genres array
        GENRE_MAP = {
            "Action": "action", "Comedy": "comedy", "Drama": "drama",
            "Science Fiction": "sci-fi", "Thriller": "thriller",
            "Horror": "horror", "Romance": "romance",
        }
        genre_str = None
        if row.genres:
            for g in row.genres:
                mapped = GENRE_MAP.get(g)
                if mapped:
                    genre_str = mapped
                    break

        if genre_str is None:
            continue

        records.append(MovieRecord(
            title=title,
            genre=genre_str,
            year=year,
            rating=rating,
            synopsis=synopsis,
            director=row.director,
            lead_actor=row.lead_actor,
            recommended_for=row.recommended_for or row.audience,
            poster_url=row.poster_url,
            backdrop_url=row.backdrop_url,
            trailer_url=row.trailer_url,
            editorial_tags=row.editorial_tags,
            vote_count=row.vote_count,
            lead_actor_2=row.lead_actor_2,
            lead_actor_3=row.lead_actor_3,
        ))
    return records


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
