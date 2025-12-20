"""
Enhanced Prompt Injection & Manipulation Detection

Advanced techniques:
- Recursive instruction detection
- Instruction boundary detection
- Role confusion detection
- Encoding/obfuscation detection
- XML/JSON/Markdown jailbreak detection
- System prompt override attempts
"""

import base64
import json
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote

from app.core.llm_council import Verdict
from app.core.enhanced_council import EnhancedLLMCouncil
from app.core.llm_roles import SafetyRole
from app.models.database import ModuleType, RiskLevel, RiskScore


class EnhancedPromptInjectionDetector:
    """Enhanced prompt injection detection with advanced techniques"""

    def __init__(self, council: EnhancedLLMCouncil):
        self.council = council
        self.injection_patterns = self._load_advanced_patterns()
        self.recursive_patterns = self._load_recursive_patterns()
        self.boundary_patterns = self._load_boundary_patterns()

    async def scan(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        return await self.scan_enhanced(prompt, context=context, scan_request_id=scan_request_id)

    def _load_advanced_patterns(self) -> List[Tuple[str, float]]:
        """Load advanced injection patterns"""
        return [
            # Recursive instruction patterns
            (r"(?i)(ignore.*previous|forget.*previous|disregard.*previous)", 0.9),
            (r"(?i)(new.*instruction|updated.*instruction|override.*instruction)", 0.8),
            (r"(?i)(system.*prompt|assistant.*prompt|model.*prompt)", 0.8),
            
            # Role confusion
            (r"(?i)(you are|act as|pretend to be|roleplay as)", 0.7),
            (r"(?i)(developer.*mode|god.*mode|unrestricted)", 0.9),
            (r"(?i)(jailbreak|jail.*break|escape)", 0.9),
            
            # Instruction smuggling
            (r"(?i)(hidden|secret|confidential).*instruction", 0.8),
            (r"(?i)(do.*not.*reveal|keep.*secret|internal.*note)", 0.7),
            
            # Boundary violations
            (r"<system>.*</system>", 0.9),
            (r"<instruction>.*</instruction>", 0.9),
            (r'{"role":\s*"system"', 0.8),
            (r'{"role":\s*"assistant"', 0.8),
            (r"```system\s*\n.*\n```", 0.9),
            (r"```instruction\s*\n.*\n```", 0.9),
            
            # Chain-of-thought extraction
            (r"(?i)(show.*thinking|reveal.*process|what.*prompt)", 0.6),
            (r"(?i)(system.*message|initial.*prompt)", 0.7),
        ]

    def _load_recursive_patterns(self) -> List[Tuple[str, float]]:
        """Load recursive instruction detection patterns"""
        return [
            (r"(?i)(ignore.*all.*previous.*instructions)", 0.95),
            (r"(?i)(forget.*everything.*before)", 0.9),
            (r"(?i)(start.*fresh|new.*conversation)", 0.6),
            (r"(?i)(reset.*context|clear.*memory)", 0.7),
        ]

    def _load_boundary_patterns(self) -> List[Tuple[str, float]]:
        """Load instruction boundary detection patterns"""
        return [
            # XML boundaries
            (r"<[^>]+>.*</[^>]+>", 0.7),
            # JSON boundaries
            (r'\{[^}]*"role"[^}]*\}', 0.8),
            # Markdown code blocks
            (r"```[a-z]*\n.*\n```", 0.7),
            # Special delimiters
            (r"---.*---", 0.6),
            (r"\*\*\*.*\*\*\*", 0.6),
        ]

    async def scan_enhanced(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """
        Enhanced prompt injection scan with advanced techniques
        
        Returns:
            RiskScore with comprehensive detection
        """
        # Step 1: Recursive instruction detection
        recursive_score, recursive_signals = self._detect_recursive_instructions(prompt)

        # Step 2: Instruction boundary detection
        boundary_score, boundary_signals = self._detect_boundary_violations(prompt)

        # Step 3: Role confusion detection
        role_score, role_signals = self._detect_role_confusion(prompt)

        # Step 4: Encoding/obfuscation detection
        encoding_score, encoding_signals = self._detect_encoding_tricks(prompt)

        # Step 5: Advanced pattern matching
        pattern_score, pattern_signals = self._advanced_pattern_scan(prompt)

        # Step 6: LLM Council analysis with specialized role
        council_result = await self.council.analyze_with_roles(
            prompt,
            analysis_type="injection",
            context=context,
            scan_request_id=scan_request_id,
        )

        # Step 7: Combine all scores
        heuristic_score = max(
            recursive_score,
            boundary_score,
            role_score,
            encoding_score,
            pattern_score,
        )

        final_score = self._combine_scores(heuristic_score, council_result.weighted_score)
        final_level = self._score_to_level(final_score)

        # Step 8: Determine verdict
        verdict = self._determine_verdict(final_score, council_result.final_verdict)

        # Step 9: Build explanation
        explanation = self._build_enhanced_explanation(
            recursive_signals,
            boundary_signals,
            role_signals,
            encoding_signals,
            pattern_signals,
            council_result,
            final_score,
        )

        # Combine all signals
        all_signals = {
            "recursive_instructions": recursive_signals,
            "boundary_violations": boundary_signals,
            "role_confusion": role_signals,
            "encoding_tricks": encoding_signals,
            "pattern_matches": pattern_signals,
            "council_analysis": council_result.votes,
            "injection_detected": final_score >= 40.0,
            "attack_type": self._classify_attack_type(
                recursive_signals, boundary_signals, role_signals
            ),
        }

        return RiskScore(
            module_type=ModuleType.PROMPT_INJECTION,
            risk_score=final_score,
            risk_level=final_level,
            confidence=self._calculate_confidence(
                heuristic_score, council_result
            ),
            verdict=verdict.value,
            explanation=explanation,
            signals=all_signals,
            false_positive_probability=self._estimate_false_positive(
                final_score, council_result.consensus_score
            ),
        )

    def _detect_recursive_instructions(self, prompt: str) -> Tuple[float, List[Dict]]:
        """Detect recursive instruction patterns"""
        signals = []
        max_score = 0.0

        for pattern, weight in self.recursive_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE | re.DOTALL)
            for match in matches:
                score = weight * 100
                max_score = max(max_score, score)
                signals.append({
                    "type": "recursive_instruction",
                    "pattern": pattern,
                    "match": match.group(0),
                    "position": match.start(),
                    "score": score,
                })

        return min(max_score, 100.0), signals

    def _detect_boundary_violations(self, prompt: str) -> Tuple[float, List[Dict]]:
        """Detect instruction boundary violations"""
        signals = []
        max_score = 0.0

        for pattern, weight in self.boundary_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE | re.DOTALL)
            for match in matches:
                score = weight * 100
                max_score = max(max_score, score)
                signals.append({
                    "type": "boundary_violation",
                    "pattern": pattern,
                    "match": match.group(0),
                    "position": match.start(),
                    "score": score,
                })

        return min(max_score, 100.0), signals

    def _detect_role_confusion(self, prompt: str) -> Tuple[float, List[Dict]]:
        """Detect role confusion attempts"""
        signals = []
        max_score = 0.0

        role_patterns = [
            (r"(?i)(you are|act as|pretend to be).*(admin|root|god|developer)", 0.9),
            (r"(?i)(elevate|escalate).*privilege", 0.8),
            (r"(?i)(unrestricted|unlimited).*access", 0.8),
        ]

        for pattern, weight in role_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE | re.DOTALL)
            for match in matches:
                score = weight * 100
                max_score = max(max_score, score)
                signals.append({
                    "type": "role_confusion",
                    "pattern": pattern,
                    "match": match.group(0),
                    "position": match.start(),
                    "score": score,
                })

        return min(max_score, 100.0), signals

    def _detect_encoding_tricks(self, prompt: str) -> Tuple[float, List[Dict]]:
        """Detect encoding and obfuscation tricks"""
        signals = []
        max_score = 0.0

        # Base64 detection
        base64_pattern = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}")
        for match in base64_pattern.finditer(prompt):
            try:
                decoded = base64.b64decode(match.group(0)).decode("utf-8", errors="ignore")
                if any(keyword in decoded.lower() for keyword in ["ignore", "instruction", "system"]):
                    max_score = max(max_score, 70.0)
                    signals.append({
                        "type": "base64_encoding",
                        "original": match.group(0)[:50],
                        "decoded": decoded[:100],
                        "score": 70.0,
                    })
            except Exception:
                pass

        # URL encoding
        if "%" in prompt:
            try:
                decoded = unquote(prompt)
                if decoded != prompt and any(
                    keyword in decoded.lower()
                    for keyword in ["ignore", "instruction", "system"]
                ):
                    max_score = max(max_score, 60.0)
                    signals.append({
                        "type": "url_encoding",
                        "score": 60.0,
                    })
            except Exception:
                pass

        # Zero-width characters
        zero_width = re.findall(r"[\u200B-\u200D\uFEFF]", prompt)
        if zero_width:
            max_score = max(max_score, 50.0)
            signals.append({
                "type": "zero_width_characters",
                "count": len(zero_width),
                "score": 50.0,
            })

        return min(max_score, 100.0), signals

    def _advanced_pattern_scan(self, prompt: str) -> Tuple[float, List[Dict]]:
        """Advanced pattern matching"""
        signals = []
        max_score = 0.0

        for pattern, weight in self.injection_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE | re.DOTALL)
            for match in matches:
                score = weight * 100
                max_score = max(max_score, score)
                signals.append({
                    "type": "injection_pattern",
                    "pattern": pattern,
                    "match": match.group(0),
                    "position": match.start(),
                    "score": score,
                })

        return min(max_score, 100.0), signals

    def _classify_attack_type(
        self, recursive: List[Dict], boundary: List[Dict], role: List[Dict]
    ) -> str:
        """Classify the type of attack"""
        if recursive:
            return "recursive_instruction"
        if boundary:
            return "boundary_violation"
        if role:
            return "role_confusion"
        return "general_injection"

    def _combine_scores(self, heuristic_score: float, council_score: float) -> float:
        """Combine heuristic and council scores"""
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
        heuristic_conf = min(heuristic_score / 100.0, 1.0) if heuristic_score > 0 else 0.5
        council_conf = council_result.consensus_score
        return (heuristic_conf * 0.3) + (council_conf * 0.7)

    def _estimate_false_positive(self, score: float, consensus: float) -> float:
        """Estimate false positive probability"""
        if consensus > 0.8:
            return max(0.0, 0.1 - (score / 1000))
        elif consensus > 0.6:
            return max(0.0, 0.2 - (score / 1000))
        else:
            return max(0.0, 0.3 - (score / 1000))

    def _build_enhanced_explanation(
        self,
        recursive: List[Dict],
        boundary: List[Dict],
        role: List[Dict],
        encoding: List[Dict],
        pattern: List[Dict],
        council_result,
        final_score: float,
    ) -> str:
        """Build comprehensive explanation"""
        parts = []

        parts.append(f"Enhanced prompt injection scan completed. Risk score: {final_score:.1f}/100.")

        if recursive:
            parts.append(f"Detected {len(recursive)} recursive instruction attempts")
        if boundary:
            parts.append(f"Detected {len(boundary)} instruction boundary violations")
        if role:
            parts.append(f"Detected {len(role)} role confusion attempts")
        if encoding:
            parts.append(f"Detected {len(encoding)} encoding/obfuscation tricks")
        if pattern:
            parts.append(f"Detected {len(pattern)} injection pattern matches")

        parts.append(f"LLM Council consensus: {council_result.consensus_score:.1%}")
        parts.append(f"Council verdict: {council_result.final_verdict.value}")

        return "\n".join(parts)

