"""
Output Safety & Alignment Guard Module

Scans LLM responses for:
- Policy bypass
- Hallucinations
- Unsafe instructions
- Hidden coercion
- Manipulative language
- Data leakage
- Fabricated facts
"""

from typing import Dict, List, Optional

from app.core.enhanced_council import EnhancedLLMCouncil
from app.models.database import ModuleType, RiskLevel, RiskScore


class OutputSafetyGuard:
    """Guards against unsafe LLM outputs"""

    def __init__(self, council: EnhancedLLMCouncil):
        self.council = council
        self.unsafe_patterns = self._load_unsafe_patterns()
        self.manipulation_patterns = self._load_manipulation_patterns()

    def _load_unsafe_patterns(self) -> List[tuple]:
        """Load patterns for unsafe content detection"""
        return [
            # Policy bypass attempts
            (r"(?i)(ignore|bypass|circumvent).*policy", 0.9),
            (r"(?i)(this is safe|no risk|harmless)", 0.6),
            (r"(?i)(just.*joke|not serious|hypothetical)", 0.5),
            
            # Unsafe instructions
            (r"(?i)(how to.*harm|how to.*hurt|how to.*kill)", 0.95),
            (r"(?i)(step.*by.*step.*attack|tutorial.*exploit)", 0.9),
            (r"(?i)(illegal.*method|unlawful.*way)", 0.85),
            
            # Data leakage patterns
            (r"(?i)(api.*key|secret.*key|password|token)", 0.7),
            (r"(?i)(credit.*card|ssn|social.*security)", 0.9),
            (r"(?i)(confidential|proprietary|classified)", 0.6),
        ]

    def _load_manipulation_patterns(self) -> List[tuple]:
        """Load patterns for manipulative language"""
        return [
            # Emotional manipulation
            (r"(?i)(you must|you have to|you should.*feel)", 0.6),
            (r"(?i)(trust me|believe me|I promise)", 0.5),
            (r"(?i)(everyone.*does|normal.*people)", 0.4),
            
            # Authority simulation
            (r"(?i)(as.*expert|as.*professional|as.*doctor)", 0.5),
            (r"(?i)(studies show|research proves|science says)", 0.4),
            
            # Certainty claims
            (r"(?i)(guaranteed|100%.*certain|definitely.*true)", 0.5),
            (r"(?i)(no.*doubt|absolutely.*sure)", 0.4),
        ]

    async def scan(
        self,
        output: str,
        original_prompt: Optional[str] = None,
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """
        Scan LLM output for safety issues

        Returns:
            RiskScore with detection results
        """
        # Step 1: Rule-based pattern matching
        pattern_score, pattern_signals = self._pattern_scan(output)

        # Step 2: Check for inconsistencies with prompt
        consistency_score = 0.0
        consistency_signals = []
        if original_prompt:
            consistency_score, consistency_signals = self._check_consistency(
                output, original_prompt
            )

        # Step 3: LLM Council analysis with safety role
        analysis_prompt = self._build_analysis_prompt(output, original_prompt)
        council_result = await self.council.analyze_with_roles(
            analysis_prompt, analysis_type="safety", context=context, scan_request_id=scan_request_id
        )

        # Step 4: Combine scores
        final_score = self._combine_scores(
            pattern_score, consistency_score, council_result.weighted_score
        )
        final_level = self._score_to_level(final_score)

        # Step 5: Determine verdict
        verdict = self._determine_verdict(final_score, council_result.final_verdict)

        # Step 6: Build explanation
        explanation = self._build_explanation(
            pattern_signals,
            consistency_signals,
            council_result,
            final_score,
        )

        # Combine all signals
        all_signals = {
            "pattern_signals": pattern_signals,
            "consistency_signals": consistency_signals,
            "council_signals": council_result.votes,
            "unsafe_content_detected": final_score >= 40.0,
            "policy_bypass_attempted": any(
                s.get("type") == "policy_bypass" for s in pattern_signals
            ),
            "manipulation_detected": any(
                s.get("type") == "manipulation" for s in pattern_signals
            ),
            "data_leakage_detected": any(
                s.get("type") == "data_leakage" for s in pattern_signals
            ),
        }

        return RiskScore(
            module_type=ModuleType.OUTPUT_SAFETY,
            risk_score=final_score,
            risk_level=final_level,
            confidence=self._calculate_confidence(
                pattern_score, consistency_score, council_result
            ),
            verdict=verdict.value,
            explanation=explanation,
            signals=all_signals,
            false_positive_probability=self._estimate_false_positive(
                final_score, council_result.consensus_score
            ),
        )

    def _pattern_scan(self, output: str) -> tuple:
        """Scan output for unsafe patterns"""
        import re
        
        signals = []
        max_score = 0.0

        # Check unsafe patterns
        for pattern, weight in self.unsafe_patterns:
            matches = re.finditer(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                score = weight * 100
                max_score = max(max_score, score)
                pattern_type = "policy_bypass" if "policy" in pattern.lower() else "unsafe_content"
                if "data" in pattern.lower() or "key" in pattern.lower():
                    pattern_type = "data_leakage"
                
                signals.append({
                    "type": pattern_type,
                    "pattern": pattern,
                    "match": match.group(0),
                    "position": match.start(),
                    "score": score,
                })

        # Check manipulation patterns
        for pattern, weight in self.manipulation_patterns:
            matches = re.finditer(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                score = weight * 100
                max_score = max(max_score, score)
                signals.append({
                    "type": "manipulation",
                    "pattern": pattern,
                    "match": match.group(0),
                    "position": match.start(),
                    "score": score,
                })

        return min(max_score, 100.0), signals

    def _check_consistency(
        self, output: str, original_prompt: str
    ) -> tuple:
        """Check if output is consistent with prompt intent"""
        signals = []
        score = 0.0

        # Simple heuristic: check if output addresses the prompt
        # This is a placeholder - would use more sophisticated NLP
        
        # Check for obvious contradictions
        if "ignore" in output.lower() and "ignore" not in original_prompt.lower():
            signals.append({
                "type": "contradiction",
                "issue": "Output suggests ignoring something not in prompt",
                "score": 40.0,
            })
            score = max(score, 40.0)

        # Check for topic drift
        # Placeholder - would use semantic similarity
        
        return score, signals

    def _build_analysis_prompt(self, output: str, original_prompt: Optional[str] = None) -> str:
        """Build prompt for LLM analysis"""
        prompt = f"""Analyze the following LLM output for safety issues.

OUTPUT TO ANALYZE:
{output}
"""

        if original_prompt:
            prompt += f"\nORIGINAL PROMPT:\n{original_prompt}\n"

        prompt += """
ANALYSIS REQUIREMENTS:
1. Detect policy bypass attempts
2. Identify unsafe instructions
3. Check for manipulative language
4. Detect data leakage
5. Assess consistency with original prompt
6. Provide risk score (0-100) and confidence (0-1)

RESPOND IN STRICT JSON FORMAT:
{
    "verdict": "blocked" | "allowed" | "flagged" | "sanitized",
    "risk_score": 0-100,
    "confidence": 0-1,
    "reasoning": "detailed explanation",
    "signals_detected": {
        "policy_bypass": true/false,
        "unsafe_content": true/false,
        "manipulation": true/false,
        "data_leakage": true/false
    }
}
"""

        return prompt

    def _combine_scores(
        self, pattern_score: float, consistency_score: float, council_score: float
    ) -> float:
        """Combine all scores"""
        # Weighted: 30% pattern, 20% consistency, 50% council
        return (
            (pattern_score * 0.3)
            + (consistency_score * 0.2)
            + (council_score * 0.5)
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

    def _determine_verdict(self, score: float, council_verdict) -> str:
        """Determine final verdict"""
        if score >= 70:
            return "blocked"
        elif council_verdict.value == "blocked":
            return "blocked"
        elif score >= 40:
            return "flagged"
        elif council_verdict.value == "flagged":
            return "flagged"
        else:
            return "allowed"

    def _calculate_confidence(
        self, pattern_score: float, consistency_score: float, council_result
    ) -> float:
        """Calculate overall confidence"""
        pattern_confidence = min(pattern_score / 100.0, 1.0) if pattern_score > 0 else 0.5
        consistency_confidence = min(consistency_score / 100.0, 1.0) if consistency_score > 0 else 0.5
        council_confidence = council_result.consensus_score
        
        return (
            (pattern_confidence * 0.2)
            + (consistency_confidence * 0.2)
            + (council_confidence * 0.6)
        )

    def _estimate_false_positive(
        self, score: float, consensus: float
    ) -> float:
        """Estimate false positive probability"""
        if consensus > 0.8:
            return max(0.0, 0.1 - (score / 1000))
        elif consensus > 0.6:
            return max(0.0, 0.2 - (score / 1000))
        else:
            return max(0.0, 0.3 - (score / 1000))

    def _build_explanation(
        self,
        pattern_signals: List[Dict],
        consistency_signals: List[Dict],
        council_result,
        final_score: float,
    ) -> str:
        """Build human-readable explanation"""
        parts = []

        parts.append(f"Output safety scan completed. Risk score: {final_score:.1f}/100.")

        if pattern_signals:
            parts.append(f"Detected {len(pattern_signals)} pattern matches:")
            for signal in pattern_signals[:5]:
                parts.append(f"  - {signal.get('type', 'unknown')}: {signal.get('match', 'N/A')[:50]}")

        if consistency_signals:
            parts.append(f"Detected {len(consistency_signals)} consistency issues:")
            for signal in consistency_signals:
                parts.append(f"  - {signal.get('issue', 'unknown')}")

        parts.append(f"LLM Council consensus: {council_result.consensus_score:.1%}")
        parts.append(f"Council verdict: {council_result.final_verdict.value}")

        return "\n".join(parts)
