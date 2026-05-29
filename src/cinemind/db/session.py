from cinemind.core.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


_settings = get_settings()
database_url = _settings.database_url
if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(database_url, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
