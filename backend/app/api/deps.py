from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session, select
from app.db.session import get_session
from app.core.config import get_settings
from app.core import security
from app.models.user import User

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

def get_current_user(
    db: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        key = settings.SECRET_KEY
        if not key:
            if settings.ENVIRONMENT == "production":
                raise credentials_exception
            key = "dev-only-insecure-key-do-not-use-in-prod"
        payload = jwt.decode(token, key, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Lookup user by ID (sub contains user ID as string)
    if user_id.isdigit():
        user = db.get(User, int(user_id))
    else:
        # Fallback: lookup by email if sub was email
        statement = select(User).where(User.email == user_id)
        user = db.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    return user
