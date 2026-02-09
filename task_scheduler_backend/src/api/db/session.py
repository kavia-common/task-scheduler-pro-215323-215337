from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.core.config import get_settings

# Lazily initialized engine/sessionmaker to avoid import-time env reads.
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def _get_engine() -> Engine:
    """Create (once) and return the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        # Engine for synchronous SQLAlchemy usage (FastAPI endpoints are sync by default here).
        _engine = create_engine(
            settings.postgres_url,
            pool_pre_ping=True,
        )
    return _engine


def _get_sessionmaker() -> sessionmaker:
    """Create (once) and return the SQLAlchemy sessionmaker."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _SessionLocal


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy Session."""
    SessionLocal = _get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# PUBLIC_INTERFACE
def get_engine() -> Engine:
    """Return the lazily initialized SQLAlchemy engine."""
    return _get_engine()
