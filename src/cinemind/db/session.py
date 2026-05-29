from cinemind.core.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


_settings = get_settings()
engine = create_engine(_settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
