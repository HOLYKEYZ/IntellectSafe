from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlmodel import select
from app.api import deps
from app.core import security
from app.db.session import get_session
from app.models.user import User, UserCreate, UserRead
from datetime import timedelta
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

@router.post("/login", response_model=dict)
def login_access_token(
    db: Session = Depends(get_session), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # 1. Try to find user by email
    statement = select(User).where(User.email == form_data.username)
    user = db.exec(statement).first()
    
    # 2. Verify user and password
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect email or password"
        )
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # 3. Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=UserRead)
def register_user(
    *,
    db: Session = Depends(get_session),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    # 1. Check if user already exists
    statement = select(User).where(User.email == user_in.email)
    user = db.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # 2. Create new user
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=security.get_password_hash(user_in.password),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
