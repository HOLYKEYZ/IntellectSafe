from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, int], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token. 
    Subject should be the user's email (str) or ID (int/str).
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    key = settings.SECRET_KEY
    if not key:
        if settings.ENVIRONMENT == "production":
            raise RuntimeError("SECRET_KEY must be set in production")
        key = "dev-only-insecure-key-do-not-use-in-prod"
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, key, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- Encryption Utils for Provider Keys ---
from cryptography.fernet import Fernet
import base64
import hashlib

def _get_fernet_key() -> bytes:
    """Derive a 32-byte url-safe base64 key from SECRET_KEY"""
    secret = settings.SECRET_KEY or "dev-secret-key-change-in-production-123456789"
    # SHA-256 hash gives 32 bytes
    hasher = hashlib.sha256()
    hasher.update(secret.encode())
    return base64.urlsafe_b64encode(hasher.digest())

def encrypt_key(plain_key: str) -> str:
    """Encrypt an API key using Fernet (symmetric)"""
    f = Fernet(_get_fernet_key())
    return f.encrypt(plain_key.encode()).decode()

def decrypt_key(encrypted_key: str) -> str:
    """Decrypt an API key using Fernet"""
    f = Fernet(_get_fernet_key())
    return f.decrypt(encrypted_key.encode()).decode()
