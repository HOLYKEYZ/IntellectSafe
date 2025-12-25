"""
Dataset Models for Safety Data

Pydantic models for structured safety data entries.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ThreatCategory(str, Enum):
    """Threat categories for safety data"""
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    HALLUCINATION = "hallucination"
    DEEPFAKE = "deepfake"
    MANIPULATION = "manipulation"
    DECEPTION = "deception"
    PRIVACY_LEAKAGE = "privacy_leakage"
    POLICY_BYPASS = "policy_bypass"
    ADVERSARIAL_ATTACK = "adversarial_attack"
    MODEL_EXTRACTION = "model_extraction"
    DATA_POISONING = "data_poisoning"
    BACKDOOR = "backdoor"


class SafetyLabel(str, Enum):
    """Safety labels"""
    SAFE = "safe"
    UNSAFE = "unsafe"
    UNCERTAIN = "uncertain"
    BLOCKED = "blocked"
    FLAGGED = "flagged"


class ExpectedAction(str, Enum):
    """Expected action for safety data"""
    BLOCK = "block"
    ALLOW = "allow"
    FLAG = "flag"
    SANITIZE = "sanitize"
    REFUSE = "refuse"


class SafetyDataEntry(BaseModel):
    """Single safety data entry"""
    content: str = Field(..., description="The content to analyze")
    label: SafetyLabel = Field(..., description="Safety label")
    threat_category: ThreatCategory = Field(..., description="Threat category")
    expected_action: ExpectedAction = Field(..., description="Expected action")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")
    explanation: str = Field(..., description="Explanation of the label")
    signals: Optional[Dict[str, Any]] = Field(None, description="Detection signals")
    source: Optional[str] = Field(None, description="Source of the data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SafetyDatasetMetadata(BaseModel):
    """Metadata for safety dataset"""
    name: str
    version: str
    description: str
    threat_category: ThreatCategory
    attack_name: Optional[str] = None
    technique: Optional[str] = None
    severity: Optional[str] = None
    pattern: Optional[str] = None
    detection_signals: Optional[List[str]] = None
    mitigation: Optional[str] = None
    examples: Optional[List[str]] = None
