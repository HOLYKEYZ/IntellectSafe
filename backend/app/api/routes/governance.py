"""
Governance & Audit API endpoints

/risk/report - Generate risk reports
/risk/score - Get safety scores
/compliance/artifact - Generate compliance artifacts
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.database import ModuleType, IncidentStatus
from app.services.db import get_db_session
from app.services.governance import GovernanceEngine

router = APIRouter(prefix="/governance", tags=["governance"])


class RiskReportResponse(BaseModel):
    """Risk report response"""
    period: dict
    summary: dict
    risk_distribution: dict
    verdict_distribution: dict
    module_breakdown: dict
    generated_at: str


class SafetyScoreResponse(BaseModel):
    """Safety score response"""
    safety_score: float
    confidence: float
    breakdown: dict
    period: dict
    generated_at: str


@router.get("/risk/report", response_model=RiskReportResponse)
async def get_risk_report(
    days: int = Query(7, ge=1, le=365),
    module_type: Optional[str] = None,
    db: Session = Depends(get_db_session),
):
    """Generate risk report for specified period"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        module_enum = None
        if module_type:
            try:
                module_enum = ModuleType(module_type)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid module type: {module_type}"
                )

        engine = GovernanceEngine(db)
        report = engine.generate_risk_report(start_date, end_date, module_enum)

        return RiskReportResponse(**report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/risk/score", response_model=SafetyScoreResponse)
async def get_safety_score(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db_session),
):
    """Calculate overall safety score"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        engine = GovernanceEngine(db)
        score = engine.calculate_safety_score(start_date, end_date)

        return SafetyScoreResponse(**score)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate score: {str(e)}")


@router.get("/incident/report")
async def get_incident_report(
    days: int = Query(30, ge=1, le=365),
    status: Optional[str] = None,
    db: Session = Depends(get_db_session),
):
    """Generate incident report"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        status_enum = None
        if status:
            try:
                status_enum = IncidentStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid status: {status}"
                )

        engine = GovernanceEngine(db)
        report = engine.generate_incident_report(start_date, end_date, status_enum)

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/compliance/artifact")
async def get_compliance_artifact(
    artifact_type: str = Query(..., regex="^(audit_trail|incident_log|risk_assessment)$"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db_session),
):
    """Generate compliance artifact"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        engine = GovernanceEngine(db)
        artifact = engine.generate_compliance_artifact(artifact_type, start_date, end_date)

        return artifact

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate artifact: {str(e)}")

