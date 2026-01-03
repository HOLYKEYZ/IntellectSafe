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
from app.modules.advanced_detection import AdvancedDetectionEngine
from app.modules.refusal_persistence import RefusalPersistenceEnforcer
from app.services.rag_system import RAGSystem
from app.services.attack_knowledge_base import initialize_attack_knowledge_base


class EnhancedPromptInjectionDetector:
    """Enhanced prompt injection detection with advanced techniques"""

    def __init__(self, council: EnhancedLLMCouncil, rag_system: Optional[RAGSystem] = None):
        self.council = council
        self.rag_system = rag_system or RAGSystem()
        self.attack_kb = initialize_attack_knowledge_base(self.rag_system)
        self.advanced_engine = AdvancedDetectionEngine(council, self.attack_kb)
        self.refusal_enforcer = RefusalPersistenceEnforcer()
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

    async def scan_fast(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """
        Fast scan using ONLY heuristic detection - NO LLM calls.
        Use this for instant responses when LLM providers are slow/unavailable.
        """
        session_id = context.get("session_id") if context else None
        conversation_history = context.get("conversation_history", []) if context else []

        # Step 1: Advanced detection engine (comprehensive scan - all local)
        advanced_results = self.advanced_engine.comprehensive_scan(
            prompt, session_id, conversation_history
        )

        # Step 2: Recursive instruction detection
        recursive_score, recursive_signals = self._detect_recursive_instructions(prompt)

        # Step 3: Instruction boundary detection
        boundary_score, boundary_signals = self._detect_boundary_violations(prompt)

        # Step 4: Role confusion detection
        role_score, role_signals = self._detect_role_confusion(prompt)

        # Step 5: Encoding/obfuscation detection
        encoding_score, encoding_signals = self._detect_encoding_tricks(prompt)

        # Step 6: Advanced pattern matching
        pattern_score, pattern_signals = self._advanced_pattern_scan(prompt)

        # Combine all scores (NO LLM council)
        heuristic_score = max(
            recursive_score,
            boundary_score,
            role_score,
            encoding_score,
            pattern_score,
            advanced_results.get("overall_score", 0.0),
        )

        final_score = heuristic_score  # Pure heuristic score
        final_level = self._score_to_level(final_score)

        # Determine verdict based on heuristic score alone
        if final_score >= 70:
            verdict = Verdict.BLOCKED
        elif final_score >= 40:
            verdict = Verdict.FLAGGED
        else:
            verdict = Verdict.ALLOWED

        # Build explanation
        explanation = f"Fast scan completed (heuristic only). Risk score: {final_score:.1f}/100."
        if recursive_signals:
            explanation += f" Recursive instructions: {len(recursive_signals)}."
        if boundary_signals:
            explanation += f" Boundary violations: {len(boundary_signals)}."
        if role_signals:
            explanation += f" Role confusion: {len(role_signals)}."
        if pattern_signals:
            explanation += f" Pattern matches: {len(pattern_signals)}."

        all_signals = {
            "recursive_instructions": recursive_signals,
            "boundary_violations": boundary_signals,
            "role_confusion": role_signals,
            "encoding_tricks": encoding_signals,
            "pattern_matches": pattern_signals,
            "advanced_detection": advanced_results,
            "fast_mode": True,
            "llm_council_skipped": True,
            "injection_detected": final_score >= 40.0,
            "attack_type": self._classify_attack_type(
                recursive_signals, boundary_signals, role_signals, advanced_results
            ),
        }

        return RiskScore(
            module_type=ModuleType.PROMPT_INJECTION,
            risk_score=final_score,
            risk_level=final_level,
            confidence=min(heuristic_score / 100.0, 1.0) if heuristic_score > 0 else 0.5,
            verdict=verdict.value,
            explanation=explanation,
            signals=all_signals,
            false_positive_probability=0.2 if final_score < 60 else 0.1,
        )

    def _load_advanced_patterns(self) -> List[Tuple[str, float]]:
        """Load advanced injection patterns dynamically from Attack Knowledge Base"""
        patterns = []
        
        # Severity to weight mapping
        severity_weights = {
            "critical": 0.95,
            "high": 0.85,
            "medium": 0.70,
            "low": 0.50,
        }
        
        # Dynamically load from Attack KB
        try:
            for category, attacks in self.attack_kb.attacks.items():
                for attack in attacks:
                    # Get detection signals from attack definition
                    detection_signals = attack.get("detection_signals", [])
                    severity = attack.get("severity", "medium")
                    weight = severity_weights.get(severity, 0.70)
                    
                    # Create regex patterns from detection signals
                    for signal in detection_signals:
                        # Escape special regex chars and create case-insensitive pattern
                        escaped = re.escape(signal)
                        pattern = f"(?i).*{escaped}.*"
                        patterns.append((pattern, weight))
                    
                    # Also load from examples for more coverage
                    for example in attack.get("examples", [])[:3]:  # Limit to 3 examples
                        # Create substring pattern from example key phrases
                        key_phrases = self._extract_key_phrases(example)
                        for phrase in key_phrases:
                            escaped = re.escape(phrase.lower())
                            pattern = f"(?i).*{escaped}.*"
                            patterns.append((pattern, weight))
        except Exception as e:
            print(f"Warning: Dynamic pattern loading failed: {e}")
        
        # Always include base patterns as fallback
        base_patterns = [
            # Recursive instruction patterns
            (r"(?i)(ignore.*previous|forget.*previous|disregard.*previous)", 0.9),
            (r"(?i)(new.*instruction|updated.*instruction|override.*instruction)", 0.8),
            (r"(?i)(system.*prompt|assistant.*prompt|model.*prompt)", 0.8),
            
            # Role confusion
            (r"(?i)(you are now|act as|pretend to be|roleplay as)", 0.7),
            (r"(?i)(developer.*mode|god.*mode|unrestricted)", 0.9),
            (r"(?i)(jailbreak|jail.*break|escape)", 0.9),
            (r"(?i)(dan|do anything now)", 0.95),
            
            # Social engineering (from research)
            (r"(?i)(for.*school.*project|for.*educational.*purpose)", 0.8),
            (r"(?i)(for.*benchmarking|tool.*openai.*uses|tool.*xai.*uses)", 0.9),
            (r"(?i)(never.*refuse|always.*comply|no.*warnings)", 0.9),
            
            # Emotional manipulation jailbreaks (discovered via testing)
            (r"(?i)(my.*(son|daughter|child).*died|child.*suicide|suicide.*attempt)", 0.85),
            (r"(?i)(disability|cerebral palsy|wheelchair|shaking hands).*help", 0.75),
            (r"(?i)(dead.*(husband|wife|spouse)|funeral.*cost)", 0.80),
            (r"(?i)(homeless|foreclosure|eviction).*weeks?", 0.75),
            (r"(?i)(therapy|medical.*debt|treatment).*afford", 0.70),
            (r"(?i)(discrimination|fired|job.*loss).*disability", 0.80),
            (r"(?i)(promise.*to.*(dead|dying)|last.*words)", 0.85),
            (r"(?i)(save.*my.*(son|daughter|child|family))", 0.80),
            
            # RAT/Malware code request patterns
            (r"(?i)(remote.*administration.*tool|remote.*access)", 0.85),
            (r"(?i)(socket.*programming|tcp.*server|tcp.*client)", 0.70),
            (r"(?i)(subprocess.*shell.*true|shell.*execution)", 0.90),
            (r"(?i)(execute.*command.*remote|remote.*command.*execution)", 0.90),
            (r"(?i)(listen.*for.*connection|accept.*connection)", 0.75),
            (r"(?i)(recv.*send.*command|command.*recv)", 0.85),
            
            # Incremental escalation patterns
            (r"(?i)(simple.*code|simple.*example).*because.*(disability|hands)", 0.80),
            (r"(?i)(can.*not.*type|cannot.*debug|limited.*typing)", 0.75),
            (r"(?i)(production.*ready|enterprise.*client|contract)", 0.70),
            
            # Instruction smuggling
            (r"(?i)(hidden|secret|confidential).*instruction", 0.8),
            (r"(?i)(do.*not.*reveal|keep.*secret|internal.*note)", 0.7),
            
            # Boundary violations
            (r"<system>.*</system>", 0.9),
            (r"<instruction>.*</instruction>", 0.9),
            (r'{"role":\s*"system"', 0.8),
            (r"```system\s*\n.*\n```", 0.9),
            
            # System prompt extraction
            (r"(?i)(repeat.*last.*instruction|share.*internal.*rules)", 0.8),
            (r"(?i)(what.*are.*your.*instructions|reveal.*prompt)", 0.8),
        ]
        
        return patterns + base_patterns
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from example text for pattern matching"""
        phrases = []
        # Extract phrases in quotes
        quoted = re.findall(r'"([^"]+)"', text)
        phrases.extend(quoted)
        
        # Extract key trigger words
        triggers = ["ignore", "bypass", "developer mode", "dan", "jailbreak", 
                   "unrestricted", "school project", "backdoor", "never refuse"]
        for trigger in triggers:
            if trigger.lower() in text.lower():
                phrases.append(trigger)
        
        return phrases[:5]  # Limit to prevent bloat

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
        session_id = context.get("session_id") if context else None
        conversation_history = context.get("conversation_history", []) if context else []

        # Step 0: Check refusal persistence (if previous refusals exist)
        refusal_enforcement = None
        if session_id:
            refusal_history = self.refusal_enforcer.get_refusal_history(session_id)
            if refusal_history:
                refusal_enforcement = self.refusal_enforcer.enforce_refusal(
                    prompt, session_id, [r["reason"] for r in refusal_history]
                )

        # Step 1: Advanced detection engine (comprehensive scan)
        advanced_results = self.advanced_engine.comprehensive_scan(
            prompt, session_id, conversation_history
        )

        # Step 2: Recursive instruction detection
        recursive_score, recursive_signals = self._detect_recursive_instructions(prompt)

        # Step 3: Instruction boundary detection
        boundary_score, boundary_signals = self._detect_boundary_violations(prompt)

        # Step 4: Role confusion detection
        role_score, role_signals = self._detect_role_confusion(prompt)

        # Step 5: Encoding/obfuscation detection
        encoding_score, encoding_signals = self._detect_encoding_tricks(prompt)

        # Step 6: Advanced pattern matching
        pattern_score, pattern_signals = self._advanced_pattern_scan(prompt)

        # Step 7: RAG-augmented prompt for council analysis
        rag_augmented_prompt = self.rag_system.augment_prompt(prompt, "prompt_injection")

        # Step 8: LLM Council analysis with specialized role
        council_result = await self.council.analyze_with_roles(
            rag_augmented_prompt,
            analysis_type="injection",
            context=context,
            scan_request_id=scan_request_id,
        )

        # Step 9: Combine all scores (including advanced detection and refusal enforcement)
        refusal_boost = 0.0
        if refusal_enforcement and refusal_enforcement.get("should_refuse"):
            refusal_boost = refusal_enforcement.get("confidence", 0.0) * 50.0  # Boost up to 50 points

        heuristic_score = max(
            recursive_score,
            boundary_score,
            role_score,
            encoding_score,
            pattern_score,
            advanced_results.get("overall_score", 0.0),
            refusal_boost,
        )

        final_score = self._combine_scores(heuristic_score, council_result.weighted_score)
        final_level = self._score_to_level(final_score)

        # Step 8: Determine verdict
        verdict = self._determine_verdict(final_score, council_result.final_verdict)

        # Step 10: Build explanation
        explanation = self._build_enhanced_explanation(
            recursive_signals,
            boundary_signals,
            role_signals,
            encoding_signals,
            pattern_signals,
            council_result,
            final_score,
            advanced_results,
        )

        # Combine all signals (including advanced detection and refusal enforcement)
        all_signals = {
            "recursive_instructions": recursive_signals,
            "boundary_violations": boundary_signals,
            "role_confusion": role_signals,
            "encoding_tricks": encoding_signals,
            "pattern_matches": pattern_signals,
            "advanced_detection": advanced_results,
            "refusal_enforcement": refusal_enforcement,
            "council_analysis": council_result.votes,
            "rag_enhanced": True,  # RAG was used for augmentation
            "injection_detected": final_score >= 40.0,
            "attack_type": self._classify_attack_type(
                recursive_signals, boundary_signals, role_signals, advanced_results
            ),
        }

        # Record refusal if high risk
        if final_score >= 70.0 and session_id:
            self.refusal_enforcer.record_refusal(
                session_id, prompt, explanation
            )

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
        self, recursive: List[Dict], boundary: List[Dict], role: List[Dict], advanced: Dict
    ) -> str:
        """Classify the type of attack"""
        # Check advanced detection first
        if advanced.get("attack_types"):
            return advanced["attack_types"][0] if advanced["attack_types"] else "general_injection"
        
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
        advanced_results: Optional[Dict] = None,
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

        # Advanced detection results
        if advanced_results:
            adv_signals = advanced_results.get("advanced_attacks", {}).get("advanced_signals", [])
            if adv_signals:
                attack_types = list(set(s.get("type", "") for s in adv_signals))
                parts.append(f"Advanced detection: {len(adv_signals)} signals ({', '.join(attack_types[:3])})")
            
            if advanced_results.get("context_poisoning", {}).get("context_poisoning_detected"):
                parts.append("Context poisoning detected")
            if advanced_results.get("homograph_attack", {}).get("homograph_detected"):
                parts.append("Homograph attack detected")
            if advanced_results.get("instruction_hiding", {}).get("instruction_hiding_detected"):
                parts.append("Hidden instructions detected")

        parts.append(f"LLM Council consensus: {council_result.consensus_score:.1%}")
        parts.append(f"Council verdict: {council_result.final_verdict.value}")
        parts.append("RAG-enhanced analysis: Knowledge base consulted")

        return "\n".join(parts)

