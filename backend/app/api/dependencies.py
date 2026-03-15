"""
API dependencies

Authentication, rate limiting, etc.
"""

from fastapi import Depends, HTTPException, Header
from typing import Optional
import hashlib

from app.db.session import get_session
from sqlmodel import Session, select
from app.models.user import ApiKey


async def verify_api_key(
    db: Session = Depends(get_session), x_api_key: str = Header(...)
) -> int:
    """Verify API key and return user_id"""
    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()

    statement = select(ApiKey).where(
        ApiKey.key_hash == key_hash, ApiKey.is_active == True
    )
    api_key = db.exec(statement).first()

    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return api_key.user_id


async def verify_api_key_header(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> str:
    """Verify API key from header (non-strict mode)"""
    if not x_api_key:
        raise HTTPException(
            status_code=401, detail="API key required. Provide X-API-Key header."
        )

    return x_api_key
