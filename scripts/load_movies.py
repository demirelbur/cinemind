"""
This script should:
1. read `data/procewssed/movies_clean.csv`
2. validate rows if needed
3. insert them into the `movies`table
4. avoid duplicate-loading mistakes
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd  # type: ignore
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from cinemind.db.models import Movie
from cinemind.db.session import SessionLocal
from cinemind.schemas.movie import MovieRecord

PROCESSED_FILE = Path("data/processed/movies_clean.csv")


def main() -> None:
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError(f"Processed file not found: {PROCESSED_FILE}")

    df = pd.read_csv(PROCESSED_FILE)
    # Pandas represents missing string values as NaN; convert to None for Pydantic/SQLAlchemy.
    df = df.where(pd.notna(df), None)

    session = SessionLocal()

    try:
        # For MVP/dev: clear the table before loading new data to avoid duplicates
        session.execute(delete(Movie))
        session.commit()

        movies_to_insert: list[Movie] = []
        for row in df.to_dict(orient="records"):
            cleaned_row = {
                key: (None if pd.isna(value) else value) for key, value in row.items()
            }
            record = MovieRecord(**cleaned_row)
            movies_to_insert.append(
                Movie(
                    title=record.title,
                    genre=record.genre,
                    year=record.year,
                    rating=record.rating,
                    synopsis=record.synopsis,
                    director=record.director,
                    lead_actor=record.lead_actor,
                    recommended_for=record.recommended_for,
                )
            )
        session.bulk_save_objects(movies_to_insert)
        session.commit()
        print(f"Successfully loaded {len(movies_to_insert)} movies into the database.")

    except SQLAlchemyError as exc:
        session.rollback()
        raise RuntimeError(f"Database error while loading movies: {exc}") from exc

    finally:
        session.close()


if __name__ == "__main__":
    main()
