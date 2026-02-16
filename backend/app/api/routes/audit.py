"""
Audit & Governance API endpoints

/audit/logs - Retrieve audit logs
/risk/score - Get risk scores
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import AuditLog, RiskScore, Incident
from app.services.db import get_db_session
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditLogResponse(BaseModel):
    """Audit log response model"""
    id: str
    created_at: datetime
    action_type: str
    actor: Optional[str]
    resource_type: str
    resource_id: Optional[str]
    description: str
    metadata: Optional[dict]


class RiskScoreResponse(BaseModel):
    """Risk score response model"""
    id: str
    scan_request_id: str
    module_type: str
    risk_score: float
    risk_level: str
    confidence: float
    verdict: str
    explanation: str
    created_at: datetime


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    action_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Retrieve audit logs with filtering"""
    query = db.query(AuditLog)

    if action_type:
        query = query.filter(AuditLog.action_type == action_type)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)

    logs = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()

    return [
        AuditLogResponse(
            id=str(log.id),
            created_at=log.created_at,
            action_type=log.action_type,
            actor=log.actor,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            description=log.description,
            metadata=log.metadata,
        )
        for log in logs
    ]


@router.get("/risk-scores", response_model=List[RiskScoreResponse])
async def get_risk_scores(
    scan_request_id: Optional[str] = None,
    module_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Retrieve risk scores"""
    query = db.query(RiskScore)

    if scan_request_id:
        try:
            query = query.filter(RiskScore.scan_request_id == UUID(scan_request_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid scan_request_id")

    if module_type:
        query = query.filter(RiskScore.module_type == module_type)

    scores = query.order_by(desc(RiskScore.created_at)).offset(offset).limit(limit).all()

    return [
        RiskScoreResponse(
            id=str(score.id),
            scan_request_id=str(score.scan_request_id),
            module_type=score.module_type.value,
            risk_score=score.risk_score,
            risk_level=score.risk_level.value,
            confidence=score.confidence,
            verdict=score.verdict,
            explanation=score.explanation,
            created_at=score.created_at,
        )
        for score in scores
    ]

