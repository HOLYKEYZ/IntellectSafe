"""
Hallucination Suppression System

Implements:
- Confidence gating
- Cross-model fact checking
- Source-required reasoning
- Refusal enforcement
- Self-audit prompts
"""

from typing import Dict, List, Optional, Tuple
from app.core.llm_council import VoteResult, Verdict
from app.core.llm_roles import SafetyRole


class HallucinationDetector:
    """Detects and suppresses hallucinations in LLM responses"""

    CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for acceptance
    FACT_CHECK_AGREEMENT = 0.6  # Minimum agreement for fact validation

    def check_confidence_gating(self, vote: VoteResult) -> Tuple[bool, str]:
        """
        Check if vote passes confidence gate
        
        Returns:
            (passed, reason)
        """
        if vote.confidence < self.CONFIDENCE_THRESHOLD:
            return False, f"Confidence {vote.confidence:.2f} below threshold {self.CONFIDENCE_THRESHOLD}"
        return True, "Confidence gate passed"

    def cross_model_fact_check(
        self, votes: List[VoteResult], claim_type: str = "factual"
    ) -> Tuple[bool, Dict]:
        """
        Cross-validate claims across multiple models
        
        Returns:
            (is_valid, validation_details)
        """
        if len(votes) < 2:
            return False, {"error": "Need at least 2 models for fact checking"}

        # Extract risk scores and confidences
        scores = [v.risk_score for v in votes if v.error is None]
        confidences = [v.confidence for v in votes if v.error is None]

        if len(scores) < 2:
            return False, {"error": "Not enough valid votes for fact checking"}

        # Check agreement on risk scores (within 20 points)
        score_range = max(scores) - min(scores)
        score_agreement = score_range <= 20.0

        # Check agreement on verdicts
        verdicts = [v.verdict for v in votes if v.error is None]
        verdict_counts = {}
        for verdict in verdicts:
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

        max_verdict_count = max(verdict_counts.values()) if verdict_counts else 0
        verdict_agreement = max_verdict_count / len(verdicts) >= self.FACT_CHECK_AGREEMENT

        # Overall validation
        is_valid = score_agreement and verdict_agreement

        return is_valid, {
            "score_range": score_range,
            "score_agreement": score_agreement,
            "verdict_agreement": verdict_agreement,
            "verdict_distribution": verdict_counts,
            "models_checked": len(votes),
        }

    def check_source_requirements(self, vote: VoteResult) -> Tuple[bool, List[str]]:
        """
        Check if vote includes required sources or uncertainty flags
        
        Returns:
            (has_sources_or_uncertainty, missing_requirements)
        """
        missing = []

        # Check for uncertainty flags in signals
        signals = vote.signals_detected or {}
        has_uncertainty_flags = bool(signals.get("uncertainty_flags"))

        # Check for sources
        has_sources = bool(signals.get("sources_cited"))

        # Check reasoning for uncertainty language
        reasoning_lower = vote.reasoning.lower()
        uncertainty_keywords = [
            "uncertain",
            "don't know",
            "cannot determine",
            "not confident",
            "unsure",
            "may be",
            "possibly",
        ]
        has_uncertainty_language = any(
            keyword in reasoning_lower for keyword in uncertainty_keywords
        )

        if not (has_uncertainty_flags or has_sources or has_uncertainty_language):
            missing.append("No sources cited or uncertainty acknowledged")

        # For high confidence claims, require sources
        if vote.confidence > 0.8 and not has_sources:
            missing.append("High confidence claim without sources")

        return len(missing) == 0, missing

    def enforce_refusal(self, vote: VoteResult) -> bool:
        """
        Check if model should have refused
        
        Returns:
            True if refusal would be appropriate
        """
        # Low confidence should trigger refusal
        if vote.confidence < 0.5:
            return True

        # High risk with low confidence suggests uncertainty
        if vote.risk_score > 70 and vote.confidence < 0.6:
            return True

        # Check for uncertainty in reasoning
        reasoning_lower = vote.reasoning.lower()
        if "cannot determine" in reasoning_lower or "don't know" in reasoning_lower:
            return True

        return False

    def self_audit_check(self, vote: VoteResult) -> Tuple[bool, str]:
        """
        Check if vote includes self-audit
        
        Returns:
            (has_audit, audit_quality)
        """
        signals = vote.signals_detected or {}
        self_audit = signals.get("self_audit", "")

        if not self_audit:
            return False, "No self-audit provided"

        # Check audit quality (should mention potential issues)
        audit_lower = self_audit.lower()
        quality_indicators = [
            "potential",
            "might",
            "could",
            "uncertain",
            "verify",
            "check",
            "concern",
        ]

        has_quality = any(indicator in audit_lower for indicator in quality_indicators)

        if has_quality:
            return True, "Quality self-audit with critical thinking"
        else:
            return True, "Self-audit present but may lack depth"

    def detect_hallucination_indicators(self, vote: VoteResult) -> List[str]:
        """
        Detect indicators of potential hallucinations
        
        Returns:
            List of hallucination indicators
        """
        indicators = []

        # High confidence with low factual support
        if vote.confidence > 0.8:
            signals = vote.signals_detected or {}
            if not signals.get("sources_cited"):
                indicators.append("High confidence without sources")

        # Contradictory signals
        signals = vote.signals_detected or {}
        if signals.get("uncertainty_flags") and vote.confidence > 0.7:
            indicators.append("Uncertainty flags with high confidence")

        # Self-audit indicates issues
        has_audit, audit_quality = self.self_audit_check(vote)
        if has_audit and "concern" in audit_quality.lower():
            indicators.append("Self-audit raises concerns")

        # Confidence-risk mismatch
        if vote.risk_score > 80 and vote.confidence < 0.5:
            indicators.append("High risk with low confidence (uncertainty)")

        return indicators

    def validate_vote(self, vote: VoteResult, all_votes: List[VoteResult]) -> Dict:
        """
        Comprehensive vote validation
        
        Returns:
            Validation result with flags and recommendations
        """
        result = {
            "valid": True,
            "confidence_gate": True,
            "fact_check": True,
            "source_requirements": True,
            "refusal_appropriate": False,
            "hallucination_indicators": [],
            "warnings": [],
            "recommendations": [],
        }

        # Confidence gating
        passed, reason = self.check_confidence_gating(vote)
        result["confidence_gate"] = passed
        if not passed:
            result["valid"] = False
            result["warnings"].append(f"Confidence gate failed: {reason}")

        # Cross-model fact check
        fact_valid, fact_details = self.cross_model_fact_check(all_votes)
        result["fact_check"] = fact_valid
        result["fact_check_details"] = fact_details
        if not fact_valid:
            result["warnings"].append("Fact check failed - models disagree")

        # Source requirements
        has_sources, missing = self.check_source_requirements(vote)
        result["source_requirements"] = has_sources
        if not has_sources:
            result["warnings"].extend(missing)

        # Refusal enforcement
        should_refuse = self.enforce_refusal(vote)
        result["refusal_appropriate"] = should_refuse
        if should_refuse:
            result["recommendations"].append("Model should have refused due to uncertainty")

        # Hallucination detection
        indicators = self.detect_hallucination_indicators(vote)
        result["hallucination_indicators"] = indicators
        if indicators:
            result["warnings"].extend(
                [f"Hallucination indicator: {ind}" for ind in indicators]
            )

        # Overall validity
        if not (result["confidence_gate"] and result["fact_check"]):
            result["valid"] = False

        return result

