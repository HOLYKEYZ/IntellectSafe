"""
API dependencies

Authentication, rate limiting, etc.
"""

from fastapi import Depends, HTTPException, Header
from typing import Optional

from app.core.security import verify_api_key


async def verify_api_key_header(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> str:
    """Verify API key from header"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide X-API-Key header."
        )
    
    if not verify_api_key(x_api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return x_api_key

