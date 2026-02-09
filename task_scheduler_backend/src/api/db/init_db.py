from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.db.base import Base
from src.api.db.session import get_engine


# PUBLIC_INTERFACE
def init_db() -> None:
    """Initialize database schema (create tables if they do not exist).

    This is a lightweight approach suitable for templates. For production,
    consider migrations (Alembic).
    """
    # Import models so they are registered on Base.metadata
    from src.api.models import task  # noqa: F401
    from src.api.models import user  # noqa: F401

    engine = get_engine()

    Base.metadata.create_all(bind=engine)

    # Simple sanity check - verify DB connectivity
    with Session(bind=engine) as s:
        s.execute(text("SELECT 1"))
        s.commit()
