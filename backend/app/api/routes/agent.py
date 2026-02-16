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
from app.api.deps import get_current_user
from app.models.user import User

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
    current_user: User = Depends(get_current_user),
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


class ExecuteRequest(BaseModel):
    """Request model for action execution"""
    action_id: str = Field(..., min_length=1)


class ExecuteResponse(BaseModel):
    """Response model for execution"""
    action_id: str
    executed: bool
    result: Optional[dict] = None
    error: Optional[str] = None
    timestamp: datetime


@router.post("/execute", response_model=ExecuteResponse)
async def execute_action(
    request: ExecuteRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Execute a previously authorized agent action
    """
    try:
        # Fetch action from database
        action = db.query(AgentAction).filter(AgentAction.id == request.action_id).first()
        
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        
        if not action.authorized:
            raise HTTPException(status_code=403, detail="Action not authorized")
        
        if action.executed:
            raise HTTPException(status_code=400, detail="Action already executed")
        
        # Execute via controller
        result = await agent_controller.execute_action(action)
        
        # Update in DB
        db.commit()
        db.refresh(action)
        
        return ExecuteResponse(
            action_id=str(action.id),
            executed=True,
            result=result,
            timestamp=datetime.utcnow(),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


class KillRequest(BaseModel):
    """Request model for kill switch"""
    agent_id: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    reason: Optional[str] = "Emergency kill switch activated"


class KillResponse(BaseModel):
    """Response model for kill switch"""
    agent_id: str
    killed: bool
    actions_blocked: int
    timestamp: datetime


@router.post("/kill", response_model=KillResponse)
async def kill_agent(
    request: KillRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Emergency kill switch - blocks all pending actions for an agent
    """
    try:
        # Activate kill switch
        agent_controller.kill_switch(request.agent_id, request.session_id)
        
        # Block all pending (authorized but not executed) actions
        query = db.query(AgentAction).filter(
            AgentAction.agent_id == request.agent_id,
            AgentAction.authorized == True,
            AgentAction.executed == False,
        )
        if request.session_id:
            query = query.filter(AgentAction.session_id == request.session_id)
        
        pending_actions = query.all()
        for action in pending_actions:
            action.authorized = False
            action.safety_flags = {**(action.safety_flags or {}), "killed": True, "kill_reason": request.reason}
        
        db.commit()
        
        return KillResponse(
            agent_id=request.agent_id,
            killed=True,
            actions_blocked=len(pending_actions),
            timestamp=datetime.utcnow(),
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Kill switch failed: {str(e)}")


class ActionHistoryItem(BaseModel):
    """Single action in history"""
    action_id: str
    action_type: str
    authorized: bool
    executed: bool
    risk_score: Optional[float]
    created_at: datetime


class HistoryResponse(BaseModel):
    """Response model for action history"""
    agent_id: str
    total_actions: int
    actions: list[ActionHistoryItem]


@router.get("/history/{agent_id}", response_model=HistoryResponse)
async def get_action_history(
    agent_id: str,
    session_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get action history for an agent
    """
    try:
        query = db.query(AgentAction).filter(AgentAction.agent_id == agent_id)
        
        if session_id:
            query = query.filter(AgentAction.session_id == session_id)
        
        actions = query.order_by(AgentAction.created_at.desc()).limit(limit).all()
        
        history = [
            ActionHistoryItem(
                action_id=str(a.id),
                action_type=a.action_type,
                authorized=a.authorized,
                executed=a.executed or False,
                risk_score=a.risk_score,
                created_at=a.created_at,
            )
            for a in actions
        ]
        
        return HistoryResponse(
            agent_id=agent_id,
            total_actions=len(history),
            actions=history,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History fetch failed: {str(e)}")
