# Dataset Setup

CineMind uses a TMDB-based dataset that is transformed into a normalized internal schema.

## Data licensing note

This repository's code license does not automatically apply to movie data.

- TMDB/Kaggle data remains subject to the original dataset/provider terms.
- You are responsible for complying with TMDB, Kaggle, and any downstream usage restrictions.
- Review and follow attribution/redistribution requirements before publishing derived datasets.

## Download the dataset

You can use a Kaggle TMDB dataset such as `tmdb/tmdb-movie-metadata`.

```bash
uv run kaggle datasets download -d tmdb/tmdb-movie-metadata
unzip tmdb-movie-metadata.zip -d data/raw
```

Make sure your Kaggle CLI credentials are configured before running this.

## Transform the raw data

```bash
uv run python scripts/transform_tmdb.py
```

This produces cleaned output such as:

- `data/processed/movies_clean.csv`
- `data/processed/movies_clean.jsonl`
- `data/processed/rejected_rows.csv`
