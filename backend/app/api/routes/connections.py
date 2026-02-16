from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.api.deps import get_db_session, get_current_user
from app.models.user import User
from app.models.provider_key import ProviderKey
from app.core.security import encrypt_key
from pydantic import BaseModel

router = APIRouter(prefix="/connections", tags=["connections"])

class ConnectionCreate(BaseModel):
    provider: str
    api_key: str
    label: str = None

class ConnectionRead(BaseModel):
    id: int
    provider: str
    key_mask: str
    label: str = None
    created_at: Any

@router.post("/", response_model=ConnectionRead)
def create_connection(
    data: ConnectionCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Securely store an upstream API key."""
    # Check if key already exists for this provider (optional constraint)
    # For now allow multiple, but usually one per provider per user is enough.
    
    # Create Mask (e.g. sk-proj-...4567)
    if len(data.api_key) > 8:
        mask = f"{data.api_key[:4]}...{data.api_key[-4:]}"
    else:
        mask = "***"
        
    encrypted = encrypt_key(data.api_key)
    
    connection = ProviderKey(
        user_id=current_user.id,
        provider=data.provider.lower(),
        encrypted_key=encrypted,
        key_mask=mask,
        label=data.label or data.provider.title()
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection

@router.get("/", response_model=List[ConnectionRead])
def list_connections(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """List all active upstream connections."""
    statement = select(ProviderKey).where(ProviderKey.user_id == current_user.id)
    return db.exec(statement).all()

@router.delete("/{id}")
def delete_connection(
    id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Remove a connection."""
    connection = db.get(ProviderKey, id)
    if not connection or connection.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    db.delete(connection)
    db.commit()
    return {"ok": True}
