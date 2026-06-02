"""enrich_movies_with_tmdb_metadata

Revision ID: edcb5f493f33
Revises: c34025e1aff2
Create Date: 2026-05-31 23:15:47.851278

Drops the movies table and recreates it with the enriched schema,
preserving existing row data via a temp staging approach.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'edcb5f493f33'
down_revision: Union[str, Sequence[str], None] = 'c34025e1aff2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create staging table with new schema
    op.execute("""
        CREATE TABLE movies_new (
            id INTEGER PRIMARY KEY,
            imdb_title TEXT,
            imdb_year INTEGER,
            imdb_rating FLOAT,
            tmdb_id INTEGER,
            title TEXT,
            release_year INTEGER,
            overview TEXT,
            genres TEXT[],
            runtime_minutes INTEGER,
            tmdb_rating FLOAT,
            vote_count INTEGER,
            poster_url TEXT,
            backdrop_url TEXT,
            trailer_url TEXT,
            director VARCHAR(255),
            lead_actor VARCHAR(100),
            lead_actor_2 VARCHAR(100),
            lead_actor_3 VARCHAR(100),
            recommended_for VARCHAR(20),
            audience VARCHAR(20),
            popularity FLOAT,
            editorial_tags TEXT[],
            enriched_at TIMESTAMP,
            embedding VECTOR(1536),
            CHECK (tmdb_rating IS NULL OR (tmdb_rating BETWEEN 0.0 AND 10.0)),
            CHECK (popularity IS NULL OR popularity >= 0.0),
            CHECK (recommended_for IS NULL OR recommended_for IN ('family', 'teens', 'adults'))
        )
    """)

    # Migrate existing data
    op.execute("""
        INSERT INTO movies_new (
            id, imdb_title, imdb_year, imdb_rating, director, lead_actor, recommended_for
        )
        SELECT
            id, title, year, rating, director, lead_actor, recommended_for
        FROM movies
    """)

    # Drop old table and rename new
    op.execute("DROP TABLE movies")
    op.execute("ALTER TABLE movies_new RENAME TO movies")

    # Create indexes
    op.execute("CREATE INDEX ix_movies_tmdb_id ON movies (tmdb_id)")
    op.execute("CREATE INDEX ix_movies_imdb_title ON movies (imdb_title)")
    op.execute("CREATE INDEX ix_movies_release_year ON movies (release_year)")
    op.execute("CREATE INDEX ix_movies_recommended_for ON movies (recommended_for)")
    op.execute("CREATE INDEX vec_movies_embedding ON movies USING ivfflat (embedding vector_cosine_ops)")
    


def downgrade() -> None:
    op.execute("DROP TABLE movies")

    op.execute("""
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            title VARCHAR(100) NOT NULL,
            genre VARCHAR(20) NOT NULL,
            year INTEGER NOT NULL,
            rating DOUBLE PRECISION NOT NULL,
            synopsis TEXT NOT NULL,
            director VARCHAR(100),
            lead_actor VARCHAR(100),
            recommended_for VARCHAR(20),
            CHECK (genre IN ('action', 'comedy', 'drama', 'sci-fi', 'thriller', 'horror', 'romance')),
            CHECK (recommended_for IS NULL OR recommended_for IN ('family', 'teens', 'adults')),
            CHECK (char_length(synopsis) BETWEEN 10 AND 500),
            CHECK (char_length(title) BETWEEN 1 AND 100),
            CHECK (rating BETWEEN 0.0 AND 10.0),
            CHECK (year BETWEEN 1900 AND 2025)
        )
    """)

    op.execute("CREATE INDEX ix_movies_genre ON movies (genre)")
    op.execute("CREATE INDEX ix_movies_rating ON movies (rating)")
    op.execute("CREATE INDEX ix_movies_recommended_for ON movies (recommended_for)")
    op.execute("CREATE INDEX ix_movies_title ON movies (title)")
    op.execute("CREATE INDEX ix_movies_year ON movies (year)")
