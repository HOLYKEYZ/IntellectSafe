"""
Agent Control API endpoints

/agent/authorize - Authorize agent actions
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.llm_council import council
from app.models.database import AgentAction
from app.modules.agent_control import AgentController
from app.services.db import get_db_session

router = APIRouter(prefix="/agent", tags=["agent"])

# Initialize agent controller
agent_controller = AgentController(council)


class AuthorizeRequest(BaseModel):
    """Request model for agent action authorization"""
    agent_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    action_type: str = Field(..., min_length=1)
    requested_action: dict = Field(..., min_length=1)
    requested_scope: Optional[dict] = None


class AuthorizeResponse(BaseModel):
    """Response model for authorization"""
    action_id: str
    authorized: bool
    risk_score: Optional[float] = None
    safety_flags: Optional[dict] = None
    reasoning: str
    timestamp: datetime


@router.post("/authorize", response_model=AuthorizeResponse)
async def authorize_action(
    request: AuthorizeRequest,
    db: Session = Depends(get_db_session),
):
    """
    Authorize an agent action request

    Implements permission gate, tool-usage firewall, and scope enforcement.
    """
    try:
        # Authorize action using agent controller
        action = await agent_controller.authorize_action(
            agent_id=request.agent_id,
            session_id=request.session_id,
            action_type=request.action_type,
            requested_action=request.requested_action,
            requested_scope=request.requested_scope,
        )

        # Save to database
        db.add(action)
        db.commit()
        db.refresh(action)

        # Build reasoning
        reasoning = f"Action analyzed. Risk score: {action.risk_score or 0:.1f}. "
        reasoning += f"Council verdict: {action.safety_flags.get('council_verdict', 'unknown')}. "
        if action.authorized:
            reasoning += "Action authorized."
        else:
            reasoning += "Action blocked due to security concerns."

        return AuthorizeResponse(
            action_id=str(action.id),
            authorized=action.authorized,
            risk_score=action.risk_score,
            safety_flags=action.safety_flags,
            reasoning=reasoning,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Authorization failed: {str(e)}")

