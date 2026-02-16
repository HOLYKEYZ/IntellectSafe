from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_current_user, get_db_session
from app.models.user import User, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=UserRead)
def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> Any:
    """
    Update own user.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return current_user
