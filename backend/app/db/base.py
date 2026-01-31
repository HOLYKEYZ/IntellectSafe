from sqlmodel import SQLModel

# Import all models here so Alembic can discover them
from app.models.user import User  # noqa
