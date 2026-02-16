from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

class UserUpdate(SQLModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class ApiKey(SQLModel, table=True):
    """User API keys for programmatic access"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    key_prefix: str = Field(max_length=12)      # First 8 chars for identification
    key_hash: str                                 # SHA-256 hash of full key
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    last_used_at: Optional[datetime] = None


class ApiKeyRead(SQLModel):
    key_prefix: str
    created_at: datetime
    is_active: bool
