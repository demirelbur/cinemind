"""
Load movies from processed CSV into the enriched movies table.
Maps old schema (title, genre, year, rating, synopsis, ...) to new schema
(imdb_title, imdb_year, imdb_rating, ...).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import delete

from cinemind.db.models import Movie
from cinemind.db.session import SessionLocal
from cinemind.schemas.movie import MovieRecord

PROCESSED_FILE = Path("data/processed/movies_clean.csv")


def main() -> None:
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError(f"Processed file not found: {PROCESSED_FILE}")

    df = pd.read_csv(PROCESSED_FILE)
    df = df.where(pd.notna(df), None)

    session = SessionLocal()
    try:
        session.execute(delete(Movie))
        session.commit()

        movies_to_insert = []
        for row in df.to_dict(orient="records"):
            cleaned = {k: (None if pd.isna(v) else v) for k, v in row.items()}
            record = MovieRecord(**cleaned)
            movies_to_insert.append(
                Movie(
                    imdb_title=record.title,
                    imdb_year=record.year,
                    imdb_rating=record.rating,
                    director=record.director,
                    lead_actor=record.lead_actor,
                    recommended_for=record.recommended_for,
                )
            )

        session.bulk_save_objects(movies_to_insert)
        session.commit()
        print(f"Loaded {len(movies_to_insert)} movies.")

    finally:
        session.close()


if __name__ == "__main__":
    main()

