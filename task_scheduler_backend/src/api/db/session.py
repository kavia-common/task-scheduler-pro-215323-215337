from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.core.config import get_settings

settings = get_settings()

# Engine for synchronous SQLAlchemy usage (FastAPI endpoints are sync by default here).
engine = create_engine(
    settings.postgres_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy Session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
