from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import ValidationError

from cinemind.schemas.movie import MovieRecord


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

MOVIES_FILE = RAW_DIR / "tmdb_5000_movies.csv"
CREDITS_FILE = RAW_DIR / "tmdb_5000_credits.csv"

OUTPUT_CSV = PROCESSED_DIR / "movies_clean.csv"
OUTPUT_JSONL = PROCESSED_DIR / "movies_clean.jsonl"
REJECTED_CSV = PROCESSED_DIR / "rejected_rows.csv"


GENRE_MAP: dict[str, str] = {
    "Action": "action",
    "Comedy": "comedy",
    "Drama": "drama",
    "Science Fiction": "sci-fi",
    "Thriller": "thriller",
    "Horror": "horror",
    "Romance": "romance",
}

GENRE_PRIORITY: list[str] = [
    "Science Fiction",
    "Thriller",
    "Horror",
    "Action",
    "Drama",
    "Comedy",
    "Romance",
]


def parse_json_like(value: Any) -> list[dict[str, Any]]:
    """Parse TMDB CSV stringified JSON/list-like fields into Python lists."""
    if value is None or pd.isna(value):
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []

        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            return []
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(value)
                if isinstance(parsed, list):
                    return parsed
                return []
            except (ValueError, SyntaxError):
                return []

    return []


def normalize_text(value: Any) -> str | None:
    """Normalize whitespace and convert empty-like values to None."""
    if value is None or pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    normalized = " ".join(text.split())
    return normalized or None


def extract_year(release_date: Any) -> int | None:
    """Extract release year from a YYYY-MM-DD-like string."""
    if release_date is None or pd.isna(release_date):
        return None

    text = str(release_date).strip()
    if len(text) < 4:
        return None

    try:
        year = int(text[:4])
    except ValueError:
        return None

    if 1900 <= year <= 2025:
        return year

    return None


def map_genre(genres_raw: Any) -> str | None:
    """Map TMDB genre list to one normalized CineMind genre."""
    genres = parse_json_like(genres_raw)
    genre_names = {
        item.get("name")
        for item in genres
        if isinstance(item, dict) and item.get("name")
    }

    for genre_name in GENRE_PRIORITY:
        if genre_name in genre_names:
            return GENRE_MAP[genre_name]

    return None


def extract_director(crew_raw: Any) -> str | None:
    """Extract the director name from crew metadata."""
    crew = parse_json_like(crew_raw)

    for member in crew:
        if not isinstance(member, dict):
            continue
        if member.get("job") == "Director":
            return normalize_text(member.get("name"))

    return None


def extract_lead_actor(cast_raw: Any) -> str | None:
    """Extract the lead actor, preferring the lowest cast order."""
    cast = parse_json_like(cast_raw)
    if not cast:
        return None

    best_name: str | None = None
    best_order = float("inf")

    for member in cast:
        if not isinstance(member, dict):
            continue

        name = normalize_text(member.get("name"))
        if not name:
            continue

        order = member.get("order")
        if isinstance(order, int):
            if order < best_order:
                best_name = name
                best_order = order
        elif best_name is None:
            best_name = name

    return best_name


def infer_audience(genres_raw: Any) -> str | None:
    """
    Infer recommended audience from genre heuristics.

    This is intentionally simple for the MVP and can be improved later.
    """
    genres = parse_json_like(genres_raw)
    genre_names = {
        item.get("name")
        for item in genres
        if isinstance(item, dict) and item.get("name")
    }

    if "Horror" in genre_names or "Thriller" in genre_names:
        return "adults"

    if "Action" in genre_names or "Science Fiction" in genre_names or "Drama" in genre_names:
        return "teens"

    if "Comedy" in genre_names or "Romance" in genre_names:
        return "family"

    return "teens"


def clean_synopsis(overview: Any) -> str | None:
    """Clean and bound the synopsis to the MovieRecord constraints."""
    text = normalize_text(overview)
    if text is None:
        return None

    if len(text) < 10:
        return None

    if len(text) > 500:
        text = text[:497].rstrip() + "..."

    return text


def clean_title(title: Any) -> str | None:
    """Clean and bound the title to the MovieRecord constraints."""
    text = normalize_text(title)
    if text is None:
        return None

    if len(text) > 100:
        text = text[:100].rstrip()

    return text if text else None


def clean_rating(value: Any) -> float | None:
    """Convert rating to float and enforce bounds."""
    if value is None or pd.isna(value):
        return None

    try:
        rating = float(value)
    except (TypeError, ValueError):
        return None

    if 0.0 <= rating <= 10.0:
        return rating

    return None


def transform_row(row: pd.Series) -> dict[str, Any]:
    """Transform one merged TMDB row into the CineMind movie schema."""
    return {
        "title": clean_title(row.get("title")),
        "genre": map_genre(row.get("genres")),
        "year": extract_year(row.get("release_date")),
        "rating": clean_rating(row.get("vote_average")),
        "synopsis": clean_synopsis(row.get("overview")),
        "director": extract_director(row.get("crew")),
        "lead_actor": extract_lead_actor(row.get("cast")),
        "recommended_for": infer_audience(row.get("genres")),
    }


def build_rejection_record(row: pd.Series, error: ValidationError) -> dict[str, Any]:
    """Create a rejection record for auditing failed rows."""
    return {
        "source_id": row.get("id"),
        "title": row.get("title"),
        "errors": error.json(),
    }


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not MOVIES_FILE.exists():
        raise FileNotFoundError(f"Missing movies file: {MOVIES_FILE}")

    if not CREDITS_FILE.exists():
        raise FileNotFoundError(f"Missing credits file: {CREDITS_FILE}")

    movies_df = pd.read_csv(MOVIES_FILE)
    credits_df = pd.read_csv(CREDITS_FILE)

    merged_df = movies_df.merge(
        credits_df[["movie_id", "cast", "crew"]],
        left_on="id",
        right_on="movie_id",
        how="left",
    )

    valid_records: list[dict[str, Any]] = []
    rejected_records: list[dict[str, Any]] = []

    for _, row in merged_df.iterrows():
        transformed = transform_row(row)

        try:
            record = MovieRecord(**transformed)
            valid_records.append(record.model_dump())
        except ValidationError as exc:
            rejected_records.append(build_rejection_record(row, exc))

    valid_df = pd.DataFrame(valid_records)
    rejected_df = pd.DataFrame(rejected_records)

    valid_df.to_csv(OUTPUT_CSV, index=False)

    with OUTPUT_JSONL.open("w", encoding="utf-8") as file:
        for record in valid_records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    rejected_df.to_csv(REJECTED_CSV, index=False)

    print(f"Valid records: {len(valid_records)}")
    print(f"Rejected records: {len(rejected_records)}")
    print(f"Saved CSV: {OUTPUT_CSV}")
    print(f"Saved JSONL: {OUTPUT_JSONL}")
    print(f"Saved rejected rows: {REJECTED_CSV}")


if __name__ == "__main__":
    main()
