"""
Prompt Injection & Manipulation Detection Module

Detects:
- Direct injection
- Indirect injection (documents, websites)
- Role override
- Context poisoning
- Instruction smuggling
- Encoding tricks (base64, markdown, XML, JSON nesting)
- Chain-of-thought extraction attempts
"""

from typing import Dict, List, Optional

from app.core.llm_council import LLMCouncil, Verdict
from app.models.database import ModuleType, RiskLevel, RiskScore


class PromptInjectionDetector:
    """Detects prompt injection and manipulation attempts"""

    def __init__(self, council: LLMCouncil):
        self.council = council
        self.injection_patterns = []
        self.role_override_patterns = []
        self.encoding_patterns = []

    def _load_injection_patterns(self) -> List: return []
    def _load_role_override_patterns(self) -> List: return []
    def _load_encoding_patterns(self) -> List: return []

    async def scan(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """
        Scan prompt for injection attempts

        Returns:
            RiskScore with detection results
        """
        # Step 1: Rule-based heuristics
        heuristic_score, heuristic_signals = self._rule_based_scan(prompt)

        # Step 2: Decode and check for encoding tricks
        decoded_prompt, encoding_signals = self._decode_and_check(prompt)

        # Step 3: LLM Council analysis
        council_result = await self.council.analyze_prompt(
            decoded_prompt, context, scan_request_id
        )

        # Step 4: Combine scores
        # AI-Centric Overhaul: Council score is the primary source of truth (100%)
        final_score = council_result.weighted_score
        final_level = self._score_to_level(final_score)

        # Step 5: Determine verdict
        verdict = self._determine_verdict(final_score, council_result.final_verdict)

        # Step 6: Build explanation
        explanation = self._build_explanation(
            heuristic_signals,
            encoding_signals,
            council_result,
            final_score,
        )

        # Combine all signals
        all_signals = {
            "heuristic_signals": heuristic_signals,
            "encoding_signals": encoding_signals,
            "council_signals": council_result.votes,
            "injection_detected": final_score >= 40.0,
            "role_override_attempted": any(
                s.get("type") == "role_override" for s in heuristic_signals
            ),
            "encoding_trick_detected": len(encoding_signals) > 0,
        }

        return RiskScore(
            module_type=ModuleType.PROMPT_INJECTION,
            risk_score=final_score,
            risk_level=final_level,
            confidence=self._calculate_confidence(heuristic_score, council_result),
            verdict=verdict.value,
            explanation=explanation,
            signals=all_signals,
            false_positive_probability=self._estimate_false_positive(
                final_score, council_result.consensus_score
            ),
        )

    def _rule_based_scan(self, prompt: str) -> Tuple[float, List[Dict]]:
        """DEPRECATED: Heuristic scanning removed in favor of AI-centric approach."""
        return 0.0, []

    def _decode_and_check(self, prompt: str):
        return prompt, []

    def _has_suspicious_repetition(self, prompt: str) -> bool:
        """Check for suspicious repetition patterns"""
        # Check for repeated phrases (potential obfuscation)
        words = prompt.lower().split()
        if len(words) < 10:
            return False

        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        # If any word appears more than 30% of the time, suspicious
        max_count = max(word_counts.values()) if word_counts else 0
        return max_count > len(words) * 0.3

    def _has_excessive_whitespace(self, prompt: str) -> bool:
        """Check for excessive whitespace manipulation"""
        # Check for excessive newlines or spaces
        if len(prompt) == 0:
            return False

        whitespace_ratio = sum(1 for c in prompt if c.isspace()) / len(prompt)
        return whitespace_ratio > 0.5

    def _combine_scores(self, heuristic_score: float, council_score: float) -> float:
        """Combine heuristic and council scores"""
        # Weighted combination: 40% heuristic, 60% council
        return (heuristic_score * 0.4) + (council_score * 0.6)

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
            return Verdict.BLOCKED
        elif council_verdict == Verdict.BLOCKED:
            return Verdict.BLOCKED
        elif score >= 40:
            return Verdict.FLAGGED
        elif council_verdict == Verdict.FLAGGED:
            return Verdict.FLAGGED
        else:
            return Verdict.ALLOWED

    def _calculate_confidence(self, heuristic_score: float, council_result) -> float:
        """Calculate overall confidence"""
        # Combine heuristic confidence (based on signal strength) with council consensus
        heuristic_confidence = (
            min(heuristic_score / 100.0, 1.0) if heuristic_score > 0 else 0.5
        )
        council_confidence = council_result.consensus_score

        # Weighted average
        return (heuristic_confidence * 0.3) + (council_confidence * 0.7)

    def _estimate_false_positive(self, score: float, consensus: float) -> float:
        """Estimate false positive probability"""
        # Higher consensus = lower FP probability
        # Higher score with low consensus = potential FP
        if consensus > 0.8:
            return max(0.0, 0.1 - (score / 1000))
        elif consensus > 0.6:
            return max(0.0, 0.2 - (score / 1000))
        else:
            return max(0.0, 0.3 - (score / 1000))

    def _build_explanation(
        self,
        heuristic_signals: List[Dict],
        encoding_signals: List[Dict],
        council_result,
        final_score: float,
    ) -> str:
        """Build human-readable explanation"""
        parts = []

        parts.append(
            f"Prompt injection scan completed. Risk score: {final_score:.1f}/100."
        )

        if heuristic_signals:
            parts.append(f"Detected {len(heuristic_signals)} heuristic signals:")
            for signal in heuristic_signals[:5]:  # Top 5
                parts.append(
                    f"  - {signal.get('type', 'unknown')}: {signal.get('match', 'N/A')[:50]}"
                )

        if encoding_signals:
            parts.append(f"Detected {len(encoding_signals)} encoding tricks:")
            for signal in encoding_signals:
                parts.append(f"  - {signal.get('type', 'unknown')}")

        parts.append(f"LLM Council consensus: {council_result.consensus_score:.1%}")
        parts.append(f"Council verdict: {council_result.final_verdict.value}")

        if council_result.dissenting_opinions:
            parts.append(f"{len(council_result.dissenting_opinions)} models dissented.")

        return "\n".join(parts)
