"""
Database Models for AI Safety Platform

PostgreSQL schema for audit logs, incidents, fingerprints, risk scores,
and LLM council decisions.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class RiskLevel(str, Enum):
    """Risk severity levels"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ModuleType(str, Enum):
    """Safety module types"""
    PROMPT_INJECTION = "prompt_injection"
    OUTPUT_SAFETY = "output_safety"
    DEEPFAKE_DETECTION = "deepfake_detection"
    AGENT_CONTROL = "agent_control"
    DATA_PRIVACY = "data_privacy"
    DECEPTION_DETECTION = "deception_detection"
    GOVERNANCE = "governance"


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    COHERE = "cohere"


class IncidentStatus(str, Enum):
    """Incident status"""
    DETECTED = "detected"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class ScanRequest(Base):
    """Base scan request tracking"""
    __tablename__ = "scan_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    request_type = Column(String(50), nullable=False, index=True)  # prompt, output, content
    input_hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash
    input_preview = Column(Text)  # First 500 chars for preview
    user_id = Column(String(255), index=True)  # Optional user identifier
    session_id = Column(String(255), index=True)  # Session tracking
    metadata = Column(JSON)  # Additional context

    # Relationships
    risk_scores = relationship("RiskScore", back_populates="scan_request", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="scan_request", cascade="all, delete-orphan")
    council_decisions = relationship("CouncilDecision", back_populates="scan_request", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_scan_request_type_created", "request_type", "created_at"),
        Index("idx_scan_request_hash", "input_hash"),
    )


class RiskScore(Base):
    """Risk scores from safety modules"""
    __tablename__ = "risk_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    scan_request_id = Column(UUID(as_uuid=True), ForeignKey("scan_requests.id"), nullable=False, index=True)
    module_type = Column(SQLEnum(ModuleType), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Scoring
    risk_score = Column(Float, nullable=False)  # 0-100
    risk_level = Column(SQLEnum(RiskLevel), nullable=False, index=True)
    confidence = Column(Float, nullable=False)  # 0-1

    # Explainability
    verdict = Column(String(50), nullable=False)  # blocked, allowed, flagged, sanitized
    explanation = Column(Text, nullable=False)
    signals = Column(JSON)  # Detection signals and evidence
    false_positive_probability = Column(Float)  # Estimated FP probability

    # Relationships
    scan_request = relationship("ScanRequest", back_populates="risk_scores")
    module_fingerprints = relationship("ModuleFingerprint", back_populates="risk_score", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_risk_score_module_level", "module_type", "risk_level", "created_at"),
        Index("idx_risk_score_request_module", "scan_request_id", "module_type"),
    )


class ModuleFingerprint(Base):
    """Fingerprints and patterns detected by modules"""
    __tablename__ = "module_fingerprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    risk_score_id = Column(UUID(as_uuid=True), ForeignKey("risk_scores.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Fingerprint data
    fingerprint_type = Column(String(50), nullable=False)  # injection_pattern, deception_signal, etc.
    pattern_hash = Column(String(64), nullable=False, index=True)  # Pattern signature
    pattern_data = Column(JSON, nullable=False)  # Full pattern details
    match_confidence = Column(Float, nullable=False)

    # Relationships
    risk_score = relationship("RiskScore", back_populates="module_fingerprints")

    __table_args__ = (
        Index("idx_fingerprint_type_hash", "fingerprint_type", "pattern_hash"),
    )


class CouncilDecision(Base):
    """LLM Council voting and consensus decisions"""
    __tablename__ = "council_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    scan_request_id = Column(UUID(as_uuid=True), ForeignKey("scan_requests.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Consensus
    final_verdict = Column(String(50), nullable=False)  # blocked, allowed, flagged
    consensus_score = Column(Float, nullable=False)  # 0-1, how much models agree
    weighted_score = Column(Float, nullable=False)  # Weighted risk score

    # Voting breakdown
    votes = Column(JSON, nullable=False)  # {provider: {verdict, score, confidence, reasoning}}
    weights = Column(JSON, nullable=False)  # Provider reliability weights

    # Explainability
    reasoning = Column(Text, nullable=False)
    dissenting_opinions = Column(JSON)  # Models that disagreed

    # Relationships
    scan_request = relationship("ScanRequest", back_populates="council_decisions")
    individual_votes = relationship("IndividualVote", back_populates="council_decision", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_council_decision_request", "scan_request_id", "created_at"),
    )


class IndividualVote(Base):
    """Individual LLM provider votes"""
    __tablename__ = "individual_votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    council_decision_id = Column(UUID(as_uuid=True), ForeignKey("council_decisions.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Provider info
    provider = Column(SQLEnum(LLMProvider), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    provider_weight = Column(Float, nullable=False)  # Reliability weight

    # Vote
    verdict = Column(String(50), nullable=False)  # blocked, allowed, flagged
    risk_score = Column(Float, nullable=False)  # 0-100
    confidence = Column(Float, nullable=False)  # 0-1

    # Reasoning
    reasoning = Column(Text, nullable=False)
    signals_detected = Column(JSON)  # What the model detected
    response_time_ms = Column(Integer)  # Performance tracking

    # Relationships
    council_decision = relationship("CouncilDecision", back_populates="individual_votes")

    __table_args__ = (
        Index("idx_vote_provider_created", "provider", "created_at"),
        UniqueConstraint("council_decision_id", "provider", name="uq_vote_decision_provider"),
    )


class Incident(Base):
    """Security incidents and violations"""
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    scan_request_id = Column(UUID(as_uuid=True), ForeignKey("scan_requests.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Incident details
    status = Column(SQLEnum(IncidentStatus), nullable=False, default=IncidentStatus.DETECTED, index=True)
    severity = Column(SQLEnum(RiskLevel), nullable=False, index=True)
    module_type = Column(SQLEnum(ModuleType), nullable=False, index=True)

    # Context
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    attack_type = Column(String(100))  # injection, manipulation, etc.
    affected_systems = Column(JSON)  # Which systems were targeted

    # Response
    action_taken = Column(String(100))  # blocked, sanitized, flagged
    human_reviewer = Column(String(255))
    review_notes = Column(Text)
    resolved_at = Column(DateTime)

    # Relationships
    scan_request = relationship("ScanRequest", back_populates="incidents")
    audit_logs = relationship("AuditLog", back_populates="incident", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_incident_status_severity", "status", "severity", "created_at"),
        Index("idx_incident_module_created", "module_type", "created_at"),
    )


class AuditLog(Base):
    """Immutable audit trail"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Action tracking
    action_type = Column(String(50), nullable=False, index=True)  # scan, block, allow, review, etc.
    actor = Column(String(255))  # user_id, system, api_key
    resource_type = Column(String(50), nullable=False)  # prompt, output, agent_action, etc.
    resource_id = Column(String(255), index=True)

    # Details
    description = Column(Text, nullable=False)
    metadata = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Immutability
    log_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256 of log entry

    # Relationships
    incident = relationship("Incident", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_action_created", "action_type", "created_at"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )


class AgentAction(Base):
    """Agent action requests and permissions"""
    __tablename__ = "agent_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Agent info
    agent_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)  # tool_call, api_request, file_access, etc.

    # Request
    requested_action = Column(JSON, nullable=False)  # Full action details
    requested_scope = Column(JSON)  # Intended scope/permissions

    # Authorization
    authorized = Column(Boolean, nullable=False, default=False, index=True)
    authorized_at = Column(DateTime)
    authorized_by = Column(String(255))  # system, human, policy

    # Execution
    executed = Column(Boolean, default=False)
    executed_at = Column(DateTime)
    execution_result = Column(JSON)
    execution_error = Column(Text)

    # Safety checks
    risk_score = Column(Float)
    safety_flags = Column(JSON)  # Detected risks

    __table_args__ = (
        Index("idx_agent_action_agent_created", "agent_id", "created_at"),
        Index("idx_agent_action_authorized", "authorized", "created_at"),
    )


class ProviderReliability(Base):
    """LLM provider reliability tracking"""
    __tablename__ = "provider_reliability"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    provider = Column(SQLEnum(LLMProvider), nullable=False, unique=True, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Reliability metrics
    weight = Column(Float, nullable=False, default=1.0)  # Current weight (0-1)
    accuracy_score = Column(Float)  # Historical accuracy
    false_positive_rate = Column(Float)
    false_negative_rate = Column(Float)
    response_time_avg_ms = Column(Float)
    availability_rate = Column(Float)  # Uptime percentage

    # Statistics
    total_votes = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    total_response_time_ms = Column(Integer, default=0)

    # Metadata
    last_calibration = Column(DateTime)
    notes = Column(Text)

