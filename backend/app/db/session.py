from typing import Generator
from sqlmodel import create_engine, Session
from app.core.config import get_settings

settings = get_settings()

# Use SQLite for local development if DATABASE_URL is not set
DATABASE_URL = settings.DATABASE_URL or "sqlite:///./sql_app.db"

# connect_args={"check_same_thread": False} is needed only for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL, 
    echo=settings.DB_ECHO, 
    connect_args=connect_args
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
