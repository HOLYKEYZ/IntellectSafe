"""
Security utilities

API key validation, rate limiting, etc.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_api_key(api_key: str) -> bool:
    """
    Verify API key
    
    Checks against:
    1. Environment variable (for development)
    2. Database (for production - to be implemented)
    3. Secret key (fallback)
    """
    if not api_key:
        return False

    # Check against SECRET_KEY (development)
    if api_key == settings.SECRET_KEY:
        return True

    # TODO: Check against database API keys table
    # For production, implement:
    # from app.models.database import APIKey
    # db_key = db.query(APIKey).filter(APIKey.key_hash == hash_key(api_key)).first()
    # if db_key and db_key.is_active:
    #     return True

    # Check against environment variable (if set)
    import os
    env_api_key = os.getenv("API_KEY")
    if env_api_key and api_key == env_api_key:
        return True

    return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

