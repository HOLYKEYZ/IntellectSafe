"""
Database service layer

SQLAlchemy session management and database utilities.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings

settings = get_settings()

# Create engine
DATABASE_URL = settings.DATABASE_URL or "sqlite:///./sql_app.db"
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE if "sqlite" not in DATABASE_URL else None,
    max_overflow=settings.DB_MAX_OVERFLOW if "sqlite" not in DATABASE_URL else None,
    pool_pre_ping=True,  # Verify connections before using
    connect_args=connect_args
)


# Session factory
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

