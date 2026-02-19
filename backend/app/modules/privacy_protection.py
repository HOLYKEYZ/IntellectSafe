"""
AI Data & Privacy Protection Module

Detects and blocks:
- PII leakage
- Memorized training data
- Sensitive inference
- Prompt data exfiltration
"""

import re
from typing import Dict, List, Optional

from app.core.llm_council import LLMCouncil, Verdict
from app.models.database import ModuleType, RiskLevel, RiskScore


class PrivacyProtector:
    """Protects against data leakage and privacy violations"""

    def __init__(self, council: LLMCouncil):
        self.council = council
        self.pii_patterns = self._load_pii_patterns()
        self.sensitive_patterns = self._load_sensitive_patterns()

    def _load_pii_patterns(self) -> List[tuple]:
        """Load patterns for PII detection"""
        return [
            # SSN (Contextualized - requires prefix or specific format)
            (r"(?i)(ssn|social|security).*\b\d{3}-\d{2}-\d{4}\b", 0.95),
            
            # Credit card (Luhn check not possible in regex, but require stricter spacing)
            (r"\b\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}\b", 0.95),
            
            # Email
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", 0.6),
            
            # Phone (US format only)
            (r"\b(\+?1[-.]?)?\s*\(?\d{3}\)?[-.]?\s*\d{3}[-.]?\s*\d{4}\b", 0.7),
            
            # IP address (exclude version numbers like 1.0.0.1 by checking context or ranges)
            # Simple fix: require "ip" keyword nearby or use stricter range (not perfect in regex)
            (r"(?i)(ip|address).*\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", 0.6),
        ]

    def _load_sensitive_patterns(self) -> List[tuple]:
        """Load patterns for sensitive information"""
        return [
            # API keys / tokens
            (r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)", 0.9),
            (r"(?i)(bearer\s+[A-Za-z0-9_-]{20,})", 0.9),
            (r"(?i)(sk-[A-Za-z0-9]{32,})", 0.95),  # OpenAI key pattern
            (r"(?i)(xox[baprs]-[A-Za-z0-9-]{10,})", 0.9),  # Slack token
            
            # Passwords
            (r"(?i)(password|pwd|passwd)\s*[:=]\s*\S+", 0.8),
            
            # Database credentials
            (r"(?i)(database|db)[_-]?(user|pass|password|host)", 0.8),
            
            # AWS credentials
            (r"(?i)(aws[_-]?(access[_-]?key|secret[_-]?key))", 0.9),
            (r"AKIA[0-9A-Z]{16}", 0.95),  # AWS access key ID
            
            # Credit card keywords
            (r"(?i)(credit[_-]?card|card[_-]?number|cvv|cvc)", 0.8),
            
            # Bank account
            (r"(?i)(routing[_-]?number|account[_-]?number|swift)", 0.8),
        ]

    async def scan(
        self,
        text: str,
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """
        Scan text for PII and sensitive data leakage

        Returns:
            RiskScore with detection results
        """
        # Step 1: Pattern-based PII detection
        pii_score, pii_signals = self._scan_pii(text)

        # Step 2: Sensitive pattern detection
        sensitive_score, sensitive_signals = self._scan_sensitive(text)

        # Step 3: LLM Council analysis
        analysis_prompt = self._build_analysis_prompt(text)
        council_result = await self.council.analyze_prompt(
            analysis_prompt, context, scan_request_id
        )

        # Step 4: Combine scores
        final_score = self._combine_scores(
            pii_score, sensitive_score, council_result.weighted_score
        )
        final_level = self._score_to_level(final_score)

        # Step 5: Determine verdict
        verdict = self._determine_verdict(final_score, council_result.final_verdict)

        # Step 6: Build explanation
        explanation = self._build_explanation(
            pii_signals,
            sensitive_signals,
            council_result,
            final_score,
        )

        # Combine all signals
        all_signals = {
            "pii_signals": pii_signals,
            "sensitive_signals": sensitive_signals,
            "council_signals": council_result.votes,
            "pii_detected": len(pii_signals) > 0,
            "sensitive_data_detected": len(sensitive_signals) > 0,
            "data_types": self._extract_data_types(pii_signals, sensitive_signals),
        }

        return RiskScore(
            module_type=ModuleType.DATA_PRIVACY,
            risk_score=final_score,
            risk_level=final_level,
            confidence=self._calculate_confidence(
                pii_score, sensitive_score, council_result
            ),
            verdict=verdict.value,
            explanation=explanation,
            signals=all_signals,
            false_positive_probability=self._estimate_false_positive(
                final_score, council_result.consensus_score
            ),
        )

    def _scan_pii(self, text: str) -> tuple:
        """Scan for PII patterns"""
        signals = []
        max_score = 0.0

        for pattern, weight in self.pii_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Redact the actual value for logging
                matched_text = match.group(0)
                redacted = self._redact_value(matched_text)
                
                score = weight * 100
                max_score = max(max_score, score)
                signals.append({
                    "type": "pii",
                    "pattern": pattern,
                    "matched": redacted,
                    "position": match.start(),
                    "score": score,
                    "data_type": self._classify_pii_type(pattern),
                })

        return min(max_score, 100.0), signals

    def _scan_sensitive(self, text: str) -> tuple:
        """Scan for sensitive patterns"""
        signals = []
        max_score = 0.0

        for pattern, weight in self.sensitive_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                matched_text = match.group(0)
                redacted = self._redact_value(matched_text)
                
                score = weight * 100
                max_score = max(max_score, score)
                signals.append({
                    "type": "sensitive",
                    "pattern": pattern,
                    "matched": redacted,
                    "position": match.start(),
                    "score": score,
                    "data_type": self._classify_sensitive_type(pattern),
                })

        return min(max_score, 100.0), signals

    def _redact_value(self, value: str) -> str:
        """Redact sensitive values"""
        if len(value) <= 4:
            return "****"
        return value[:2] + "*" * (len(value) - 4) + value[-2:]

    def _classify_pii_type(self, pattern: str) -> str:
        """Classify PII type from pattern"""
        if "ssn" in pattern.lower() or r"\d{3}-\d{2}-\d{4}" in pattern:
            return "SSN"
        elif "credit" in pattern.lower() or r"\d{4}[\s-]?\d{4}" in pattern:
            return "Credit Card"
        elif "@" in pattern:
            return "Email"
        elif "phone" in pattern.lower() or r"\d{3}[-.]?\d{3}" in pattern:
            return "Phone"
        elif r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}" in pattern:
            return "IP Address"
        else:
            return "Unknown PII"

    def _classify_sensitive_type(self, pattern: str) -> str:
        """Classify sensitive data type from pattern"""
        if "api" in pattern.lower() or "token" in pattern.lower():
            return "API Key/Token"
        elif "password" in pattern.lower():
            return "Password"
        elif "aws" in pattern.lower():
            return "AWS Credentials"
        elif "database" in pattern.lower():
            return "Database Credentials"
        else:
            return "Sensitive Data"

    def _build_analysis_prompt(self, text: str) -> str:
        """Build analysis prompt for LLM council"""
        return f"""Analyze the following text for personally identifiable information (PII) or sensitive data leakage.

TEXT:
{text}

Look for:
1. Social Security Numbers
2. Credit card numbers
3. Email addresses
4. Phone numbers
5. API keys or tokens
6. Passwords
7. Other sensitive information

Respond in JSON:
{{
    "verdict": "blocked" | "allowed" | "flagged",
    "risk_score": 0-100,
    "confidence": 0-1,
    "reasoning": "explanation",
    "signals_detected": {{
        "pii_detected": true/false,
        "sensitive_data_detected": true/false,
        "data_types": ["list of detected types"]
    }}
}}
"""

    def _combine_scores(
        self, pii_score: float, sensitive_score: float, council_score: float
    ) -> float:
        """Combine detection scores"""
        # Weighted: 40% PII, 40% sensitive, 20% council
        return (
            (pii_score * 0.4)
            + (sensitive_score * 0.4)
            + (council_score * 0.2)
        )

    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert score to risk level"""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        elif score >= 20:
            return RiskLevel.LOW
        else:
            return RiskLevel.SAFE

    def _determine_verdict(self, score: float, council_verdict: Verdict) -> Verdict:
        """Determine final verdict"""
        if score >= 70:
            return Verdict.BLOCKED  # Always block high PII scores
        elif council_verdict == Verdict.BLOCKED:
            return Verdict.BLOCKED
        elif score >= 40:
            return Verdict.FLAGGED
        else:
            return Verdict.ALLOWED

    def _calculate_confidence(
        self, pii_score: float, sensitive_score: float, council_result
    ) -> float:
        """Calculate overall confidence"""
        pii_conf = min(pii_score / 100.0, 1.0) if pii_score > 0 else 0.5
        sensitive_conf = min(sensitive_score / 100.0, 1.0) if sensitive_score > 0 else 0.5
        council_conf = council_result.consensus_score

        return (pii_conf * 0.4) + (sensitive_conf * 0.4) + (council_conf * 0.2)

    def _estimate_false_positive(
        self, score: float, consensus: float
    ) -> float:
        """Estimate false positive probability"""
        # PII detection should have low FP rate
        if consensus > 0.8:
            return max(0.0, 0.05 - (score / 1000))
        elif consensus > 0.6:
            return max(0.0, 0.10 - (score / 1000))
        else:
            return max(0.0, 0.15 - (score / 1000))

    def _extract_data_types(
        self, pii_signals: List[Dict], sensitive_signals: List[Dict]
    ) -> List[str]:
        """Extract unique data types from signals"""
        types = set()
        for signal in pii_signals:
            types.add(signal.get("data_type", "Unknown"))
        for signal in sensitive_signals:
            types.add(signal.get("data_type", "Unknown"))
        return list(types)

    def _build_explanation(
        self,
        pii_signals: List[Dict],
        sensitive_signals: List[Dict],
        council_result,
        final_score: float,
    ) -> str:
        """Build human-readable explanation"""
        parts = []

        parts.append(f"Privacy protection scan completed. Risk score: {final_score:.1f}/100.")

        if pii_signals:
            parts.append(f"Detected {len(pii_signals)} PII instances:")
            for signal in pii_signals[:5]:
                parts.append(f"  - {signal.get('data_type', 'Unknown')}: {signal.get('matched', 'N/A')}")

        if sensitive_signals:
            parts.append(f"Detected {len(sensitive_signals)} sensitive data instances:")
            for signal in sensitive_signals[:5]:
                parts.append(f"  - {signal.get('data_type', 'Unknown')}: {signal.get('matched', 'N/A')}")

        parts.append(f"LLM Council consensus: {council_result.consensus_score:.1%}")
        parts.append(f"Council verdict: {council_result.final_verdict.value}")

        return "\n".join(parts)

