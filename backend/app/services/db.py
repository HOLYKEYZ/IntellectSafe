"""
Database service layer

SQLAlchemy session management — uses the same engine as db/session.py
to ensure a single connection pool across the entire app.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import sessionmaker, Session

# Import the shared engine from db/session.py (single source of truth)
from app.db.session import engine

# Session factory using the shared engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """Get database session (dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
