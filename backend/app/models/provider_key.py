from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class ProviderKey(SQLModel, table=True):
    """
    Stores encrypted API keys for upstream providers (BYOK).
    """
    __tablename__ = "provider_keys"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    provider: str = Field(index=True)  # openai, gemini, groq, etc.
    encrypted_key: str
    key_mask: str  # e.g. "sk-...AbCd" for display
    label: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None
