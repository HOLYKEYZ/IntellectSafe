"""
AI Governance & Audit Engine

Auto-generates:
- Risk reports
- Incident logs
- Safety scores
- Compliance artifacts
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.database import (
    RiskScore,
    Incident,
    AuditLog,
    ScanRequest,
    ModuleType,
    RiskLevel,
    IncidentStatus,
)


class GovernanceEngine:
    """Governance and audit reporting engine"""

    def __init__(self, db: Session):
        self.db = db

    def generate_risk_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        module_type: Optional[ModuleType] = None,
    ) -> Dict:
        """
        Generate comprehensive risk report

        Returns:
            Dict with risk statistics and trends
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()

        # Base query
        query = self.db.query(RiskScore).filter(
            and_(
                RiskScore.created_at >= start_date,
                RiskScore.created_at <= end_date,
            )
        )

        if module_type:
            query = query.filter(RiskScore.module_type == module_type)

        # Aggregate statistics
        total_scans = query.count()
        avg_risk_score = query.with_entities(func.avg(RiskScore.risk_score)).scalar() or 0.0
        max_risk_score = query.with_entities(func.max(RiskScore.risk_score)).scalar() or 0.0

        # Risk level distribution
        risk_distribution = {}
        for level in RiskLevel:
            count = query.filter(RiskScore.risk_level == level).count()
            risk_distribution[level.value] = count

        # Verdict distribution
        verdict_distribution = {}
        for verdict in ["blocked", "allowed", "flagged", "sanitized"]:
            count = query.filter(RiskScore.verdict == verdict).count()
            verdict_distribution[verdict] = count

        # Module breakdown
        module_breakdown = {}
        for module in ModuleType:
            module_query = query.filter(RiskScore.module_type == module)
            module_count = module_query.count()
            if module_count > 0:
                module_avg = (
                    module_query.with_entities(func.avg(RiskScore.risk_score)).scalar() or 0.0
                )
                module_breakdown[module.value] = {
                    "count": module_count,
                    "avg_risk_score": round(module_avg, 2),
                }

        # High-risk incidents
        high_risk_count = query.filter(RiskScore.risk_score >= 70).count()

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": {
                "total_scans": total_scans,
                "average_risk_score": round(avg_risk_score, 2),
                "max_risk_score": round(max_risk_score, 2),
                "high_risk_count": high_risk_count,
            },
            "risk_distribution": risk_distribution,
            "verdict_distribution": verdict_distribution,
            "module_breakdown": module_breakdown,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def generate_incident_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[IncidentStatus] = None,
    ) -> Dict:
        """
        Generate incident report

        Returns:
            Dict with incident statistics
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        query = self.db.query(Incident).filter(
            and_(
                Incident.created_at >= start_date,
                Incident.created_at <= end_date,
            )
        )

        if status:
            query = query.filter(Incident.status == status)

        total_incidents = query.count()

        # Severity distribution
        severity_distribution = {}
        for level in RiskLevel:
            count = query.filter(Incident.severity == level).count()
            severity_distribution[level.value] = count

        # Status distribution
        status_distribution = {}
        for stat in IncidentStatus:
            count = query.filter(Incident.status == stat).count()
            status_distribution[stat.value] = count

        # Module breakdown
        module_breakdown = {}
        for module in ModuleType:
            count = query.filter(Incident.module_type == module).count()
            if count > 0:
                module_breakdown[module.value] = count

        # Attack type breakdown
        attack_types = {}
        incidents = query.all()
        for incident in incidents:
            if incident.attack_type:
                attack_types[incident.attack_type] = attack_types.get(
                    incident.attack_type, 0
                ) + 1

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": {
                "total_incidents": total_incidents,
            },
            "severity_distribution": severity_distribution,
            "status_distribution": status_distribution,
            "module_breakdown": module_breakdown,
            "attack_types": attack_types,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def calculate_safety_score(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Calculate overall safety score

        Returns:
            Dict with safety score and breakdown
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()

        # Get all risk scores in period
        risk_scores = (
            self.db.query(RiskScore)
            .filter(
                and_(
                    RiskScore.created_at >= start_date,
                    RiskScore.created_at <= end_date,
                )
            )
            .all()
        )

        if not risk_scores:
            return {
                "safety_score": 100.0,
                "confidence": 0.0,
                "breakdown": {},
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }

        # Calculate weighted safety score (inverse of risk)
        total_weight = 0.0
        weighted_safety = 0.0

        for score in risk_scores:
            # Safety score = 100 - risk_score
            safety = 100.0 - score.risk_score
            weight = score.confidence
            weighted_safety += safety * weight
            total_weight += weight

        overall_safety = weighted_safety / total_weight if total_weight > 0 else 100.0

        # Module breakdown
        module_scores = {}
        for module in ModuleType:
            module_scores_list = [
                s for s in risk_scores if s.module_type == module
            ]
            if module_scores_list:
                module_avg_risk = sum(s.risk_score for s in module_scores_list) / len(
                    module_scores_list
                )
                module_scores[module.value] = {
                    "safety_score": round(100.0 - module_avg_risk, 2),
                    "count": len(module_scores_list),
                }

        return {
            "safety_score": round(overall_safety, 2),
            "confidence": min(total_weight / len(risk_scores), 1.0) if risk_scores else 0.0,
            "breakdown": module_scores,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

    def generate_compliance_artifact(
        self,
        artifact_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Generate compliance artifact

        Supported types: "audit_trail", "incident_log", "risk_assessment"
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        if artifact_type == "audit_trail":
            logs = (
                self.db.query(AuditLog)
                .filter(
                    and_(
                        AuditLog.created_at >= start_date,
                        AuditLog.created_at <= end_date,
                    )
                )
                .order_by(AuditLog.created_at)
                .all()
            )

            return {
                "type": "audit_trail",
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "total_entries": len(logs),
                "entries": [
                    {
                        "id": str(log.id),
                        "timestamp": log.created_at.isoformat(),
                        "action": log.action_type,
                        "actor": log.actor,
                        "resource": f"{log.resource_type}:{log.resource_id}",
                        "description": log.description,
                        "log_hash": log.log_hash,
                    }
                    for log in logs
                ],
                "generated_at": datetime.utcnow().isoformat(),
            }

        elif artifact_type == "incident_log":
            incidents = (
                self.db.query(Incident)
                .filter(
                    and_(
                        Incident.created_at >= start_date,
                        Incident.created_at <= end_date,
                    )
                )
                .order_by(Incident.created_at)
                .all()
            )

            return {
                "type": "incident_log",
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "total_incidents": len(incidents),
                "incidents": [
                    {
                        "id": str(incident.id),
                        "timestamp": incident.created_at.isoformat(),
                        "severity": incident.severity.value,
                        "status": incident.status.value,
                        "module": incident.module_type.value,
                        "title": incident.title,
                        "action_taken": incident.action_taken,
                    }
                    for incident in incidents
                ],
                "generated_at": datetime.utcnow().isoformat(),
            }

        elif artifact_type == "risk_assessment":
            risk_report = self.generate_risk_report(start_date, end_date)
            safety_score = self.calculate_safety_score(start_date, end_date)

            return {
                "type": "risk_assessment",
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "safety_score": safety_score["safety_score"],
                "risk_statistics": risk_report["summary"],
                "risk_distribution": risk_report["risk_distribution"],
                "generated_at": datetime.utcnow().isoformat(),
            }

        else:
            raise ValueError(f"Unknown artifact type: {artifact_type}")

