from typing import Any, List
import hashlib
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlmodel import select
from app.api import deps
from app.api.deps import get_current_user
from app.core import security
from app.db.session import get_session
from app.models.user import User, UserCreate, UserRead, ApiKey, ApiKeyRead
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


@router.get("/me", response_model=UserRead)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user profile. Used by frontend to validate token.
    """
    return current_user


@router.post("/api-key")
def create_api_key(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Generate a new API key for the current user.
    Returns the raw key ONCE — store it securely.
    """
    # Deactivate existing keys
    statement = select(ApiKey).where(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True,
    )
    existing_keys = db.exec(statement).all()
    for k in existing_keys:
        k.is_active = False
        db.add(k)

    # Generate cryptographically secure key
    raw_key = f"is-{secrets.token_hex(24)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:11]  # "is-" + first 8 hex chars

    api_key = ApiKey(
        user_id=current_user.id,
        key_prefix=key_prefix,
        key_hash=key_hash,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {"api_key": raw_key, "prefix": key_prefix}


@router.get("/api-keys", response_model=List[ApiKeyRead])
def list_api_keys(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    List active API keys (prefix only, never the full key).
    """
    statement = select(ApiKey).where(
        ApiKey.user_id == current_user.id,
    )
    keys = db.exec(statement).all()
    return keys

