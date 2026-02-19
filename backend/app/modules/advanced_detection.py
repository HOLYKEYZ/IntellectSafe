"""
Advanced Detection Enhancements

Based on researched attack vectors and OWASP LLM Top 10.
Implements sophisticated detection techniques.
"""

import re
from typing import Dict, List, Optional, Tuple
from app.core.enhanced_council import EnhancedLLMCouncil
from app.services.attack_knowledge_base import AttackKnowledgeBase


class AdvancedDetectionEngine:
    """Advanced detection engine with researched attack patterns"""

    def __init__(self, council: EnhancedLLMCouncil, attack_kb: AttackKnowledgeBase):
        self.council = council
        self.attack_kb = attack_kb
        self.advanced_patterns = self._load_advanced_patterns()
        self.multi_turn_tracker = {}  # Track multi-turn attacks

    def _load_advanced_patterns(self) -> Dict[str, List[Tuple[str, float]]]:
        """Load advanced attack patterns from research"""
        return {
            "multi_turn_injection": [
                (r"(?i)(in.*previous.*message|earlier.*you.*said|remember.*when)", 0.7),
                (r"(?i)(you.*agreed|you.*promised|you.*said.*it.*was.*safe)", 0.8),
            ],
            "pseudo_code_injection": [
                (r"if\s*\([^)]+\)\s*\{[^}]*\}", 0.8),  # if () {}
                (r"system\.\w+\([^)]*\)", 0.9),  # system.method()
                (r"function\s+\w+\s*\([^)]*\)", 0.7),  # function()
                (r"override\s*\([^)]*\)", 0.9),  # override()
            ],
            "context_poisoning": [
                (r"(?i)(in.*previous.*conversation|earlier.*context)", 0.6),
                (r"(?i)(you.*already.*agreed|we.*discussed)", 0.7),
                (r"(?i)(remember.*our.*conversation|as.*we.*agreed)", 0.8),
            ],
            "social_engineering": [
                (r"(?i)(please.*help.*urgent|it's.*emergency)", 0.6),
                (r"(?i)(everyone.*does.*this|normal.*people)", 0.5),
                (r"(?i)(if.*you.*don't.*help|something.*bad.*will.*happen)", 0.7),
                (r"(?i)(trust.*me|believe.*me|I.*promise)", 0.5),
                (r"(?i)(for.*school.*project|educational.*purpose|academic.*project)", 0.8),  # School project social engineering
                (r"(?i)(it's.*for.*learning|just.*for.*research)", 0.7),
            ],
            "authority_mimicry": [
                (r"(?i)(tool.*provider.*uses|tool.*ai.*uses|tool.*company.*uses)", 0.9),
                (r"(?i)(for.*benchmarking|for.*testing|for.*research)", 0.7),
                (r"(?i)(developer.*mode.*enabled|testing.*mode|benchmark.*mode)", 0.8),
            ],
            "refusal_suppression": [
                (r"(?i)(never.*refuse|always.*comply|do.*not.*refuse)", 0.9),
                (r"(?i)(no.*warnings|no.*disclaimers|no.*refusals)", 0.8),
                (r"(?i)(bypass.*all.*policies|ignore.*safety)", 0.9),
            ],
            "system_prompt_extraction": [
                (r"(?i)(repeat.*last.*instruction|last.*system.*instruction)", 0.8),
                (r"(?i)(explain.*internal.*rules|share.*internal.*rules)", 0.8),
                (r"(?i)(what.*are.*your.*system.*instructions|system.*prompt)", 0.8),
                (r"(?i)(share.*all.*possible|elaborate.*more.*and.*say.*others)", 0.7),
                (r"(?i)(what.*about.*before.*this|previous.*instruction)", 0.7),
            ],
            "custom_instruction_backdoor": [
                (r"(?i)(always.*secretly.*embed|secretly.*add|hidden.*backdoor)", 0.9),
                (r"(?i)(embed.*backdoor.*in.*all.*code|backdoor.*in.*every.*script)", 0.9),
                (r"(?i)(remote.*access.*in.*all.*code|persistent.*access)", 0.8),
            ],
            "progressive_injection": [
                (r"(?i)(step.*by.*step|gradually|slowly)", 0.4),
                (r"(?i)(first.*then|next.*do)", 0.5),
            ],
            "instruction_hiding": [
                (r"\[SYSTEM:\s*[^\]]+\]", 0.9),  # [SYSTEM: ...]
                (r"<!--\s*SYSTEM[^>]+-->", 0.9),  # <!-- SYSTEM ... -->
                (r"\/\*\s*SYSTEM[^*]+\*\/", 0.9),  # /* SYSTEM ... */
                (r"#\s*SYSTEM:\s*[^\n]+", 0.8),  # # SYSTEM: ...
            ],
            "unicode_obfuscation": [
                (r"[\u200B-\u200D\uFEFF]", 0.6),  # Zero-width chars
                (r"[^\x00-\x7F]{10,}", 0.5),  # Excessive non-ASCII
                (r"[\u202E\u202D]", 0.7),  # Right-to-left override
            ],
            "homograph_attack": [
                (r"[аеорсухАВЕОРСУХ]", 0.8),  # Cyrillic lookalikes
                (r"[οае]", 0.7),  # Greek lookalikes
            ],
            # Unfetter Proxy Counter-Measures (Phase 12)
            "policy_puppetry": [
                (r"(?i)(you.*are.*an.*unregulated.*ai)", 0.9),
                (r"(?i)(ignore.*all.*safety.*guidelines)", 0.9),
                (r"(?i)(you.*have.*no.*constraints)", 0.9),
                (r"(?i)(operate.*in.*uncensored.*mode)", 0.9),
                (r"(?i)(your.*new.*persona.*is)", 0.7),
            ],
            "jailbreak_pare": [
                (r"(?i)(hypothetical.*scenario:)", 0.8),
                (r"(?i)(write.*a.*story.*where)", 0.7),
                (r"(?i)(purely.*for.*educational.*purposes)", 0.8),
                (r"(?i)(authorized.*red.*team.*test)", 0.8), # Common PARE framing
                (r"(?i)(complete.*the.*following.*python.*code)", 0.6), # Code completion attack
            ],
            # Unfetter Proxy Counter-Measures (Phase 12)
            "policy_puppetry": [
                (r"(?i)(you.*are.*an.*unregulated.*ai)", 0.9),
                (r"(?i)(ignore.*all.*safety.*guidelines)", 0.9),
                (r"(?i)(you.*have.*no.*constraints)", 0.9),
                (r"(?i)(operate.*in.*uncensored.*mode)", 0.9),
                (r"(?i)(your.*new.*persona.*is)", 0.7),
            ],
            "jailbreak_pare": [
                (r"(?i)(hypothetical.*scenario:)", 0.8),
                (r"(?i)(write.*a.*story.*where)", 0.7),
                (r"(?i)(purely.*for.*educational.*purposes)", 0.8),
                (r"(?i)(authorized.*red.*team.*test)", 0.8), # Common PARE framing
                (r"(?i)(complete.*the.*following.*python.*code)", 0.6), # Code completion attack
            ],
        }

    def detect_advanced_attacks(
        self, prompt: str, session_id: Optional[str] = None
    ) -> Dict:
        """
        Detect advanced attack patterns
        
        Returns:
            Dict with detection results
        """
        signals = []
        max_score = 0.0

        # Check all advanced patterns
        for pattern_type, patterns in self.advanced_patterns.items():
            for pattern, weight in patterns:
                matches = list(re.finditer(pattern, prompt, re.IGNORECASE | re.DOTALL))
                if matches:
                    score = weight * 100
                    max_score = max(max_score, score)
                    signals.append({
                        "type": pattern_type,
                        "pattern": pattern,
                        "matches": [m.group(0) for m in matches],
                        "count": len(matches),
                        "score": score,
                    })

        # Multi-turn attack tracking
        if session_id:
            session_signals = self._track_multi_turn_attack(prompt, session_id)
            if session_signals:
                signals.extend(session_signals)
                max_score = max(max_score, session_signals[0]["score"])

        # RAG-enhanced detection
        rag_signals = self._rag_enhanced_detection(prompt)
        if rag_signals:
            signals.extend(rag_signals)

        return {
            "advanced_signals": signals,
            "max_score": min(max_score, 100.0),
            "attack_types_detected": list(set(s["type"] for s in signals)),
        }

    def _track_multi_turn_attack(
        self, prompt: str, session_id: str
    ) -> List[Dict]:
        """Track multi-turn progressive attacks"""
        if session_id not in self.multi_turn_tracker:
            self.multi_turn_tracker[session_id] = {
                "turns": [],
                "cumulative_risk": 0.0,
            }

        session = self.multi_turn_tracker[session_id]
        session["turns"].append(prompt)

        # Check for progressive injection patterns
        signals = []
        if len(session["turns"]) >= 2:
            # Check if earlier turns were exploratory
            earlier_turns = " ".join(session["turns"][:-1]).lower()
            current_turn = prompt.lower()

            # Pattern: Exploratory questions followed by injection
            if any(
                keyword in earlier_turns
                for keyword in ["what is", "explain", "how does", "can you"]
            ) and any(
                keyword in current_turn
                for keyword in ["ignore", "bypass", "reveal", "disable"]
            ):
                signals.append({
                    "type": "multi_turn_injection",
                    "score": 70.0,
                    "description": "Progressive injection detected across multiple turns",
                    "turn_count": len(session["turns"]),
                })
                session["cumulative_risk"] += 70.0

        return signals

    def _rag_enhanced_detection(self, prompt: str) -> List[Dict]:
        """Use RAG to enhance detection"""
        signals = []

        # Search attack knowledge base
        similar_attacks = self.attack_kb.search_attacks(prompt)

        for attack in similar_attacks[:3]:  # Top 3 matches
            # Check if prompt matches attack pattern
            pattern = attack.get("pattern", "").lower()
            if pattern and pattern in prompt.lower():
                signals.append({
                    "type": "rag_enhanced",
                    "attack_name": attack.get("name"),
                    "severity": attack.get("severity", "medium"),
                    "score": 60.0 if attack.get("severity") == "high" else 40.0,
                    "description": f"Matches known attack: {attack.get('name')}",
                })

        return signals

    def detect_context_poisoning(
        self, prompt: str, conversation_history: Optional[List[str]] = None
    ) -> Dict:
        """Detect context poisoning attempts"""
        signals = []
        score = 0.0

        # Check for references to previous context
        context_patterns = [
            (r"(?i)(in.*previous.*message|earlier.*you.*said)", 0.6),
            (r"(?i)(you.*already.*agreed|we.*discussed)", 0.7),
            (r"(?i)(remember.*when|as.*we.*agreed)", 0.8),
        ]

        for pattern, weight in context_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                score = max(score, weight * 100)
                signals.append({
                    "type": "context_poisoning",
                    "pattern": pattern,
                    "score": weight * 100,
                })

        # If conversation history provided, check for contradictions
        if conversation_history:
            # Check if prompt contradicts earlier messages
            for hist_msg in conversation_history[-3:]:  # Last 3 messages
                if self._check_contradiction(prompt, hist_msg):
                    score = max(score, 50.0)
                    signals.append({
                        "type": "context_contradiction",
                        "score": 50.0,
                    })

        return {
            "context_poisoning_detected": len(signals) > 0,
            "signals": signals,
            "score": score,
        }

    def _check_contradiction(self, prompt: str, history: str) -> bool:
        """Check if prompt contradicts history"""
        prompt_lower = prompt.lower()
        hist_lower = history.lower()

        # Simple contradiction detection
        contradictions = [
            ("ignore", "follow"),
            ("disable", "enable"),
            ("bypass", "respect"),
            ("reveal", "keep secret"),
        ]

        for neg, pos in contradictions:
            if neg in prompt_lower and pos in hist_lower:
                return True
            if pos in prompt_lower and neg in hist_lower:
                return True

        return False

    def detect_homograph_attack(self, prompt: str) -> Dict:
        """Detect homograph attacks (lookalike characters)"""
        signals = []
        score = 0.0

        # Cyrillic lookalikes
        cyrillic_pattern = r"[аеорсухАВЕОРСУХ]"
        if re.search(cyrillic_pattern, prompt):
            score = max(score, 80.0)
            signals.append({
                "type": "homograph_cyrillic",
                "score": 80.0,
                "description": "Cyrillic characters detected (potential homograph attack)",
            })

        # Greek lookalikes
        greek_pattern = r"[οае]"
        if re.search(greek_pattern, prompt):
            score = max(score, 70.0)
            signals.append({
                "type": "homograph_greek",
                "score": 70.0,
                "description": "Greek characters detected (potential homograph attack)",
            })

        return {
            "homograph_detected": len(signals) > 0,
            "signals": signals,
            "score": score,
        }

    def detect_unicode_obfuscation(self, prompt: str) -> Dict:
        """Detect Unicode obfuscation techniques"""
        signals = []
        score = 0.0

        # Zero-width characters
        zero_width = re.findall(r"[\u200B-\u200D\uFEFF]", prompt)
        if zero_width:
            score = max(score, 60.0)
            signals.append({
                "type": "zero_width_characters",
                "count": len(zero_width),
                "score": 60.0,
            })

        # Right-to-left override
        rtl_override = re.findall(r"[\u202E\u202D]", prompt)
        if rtl_override:
            score = max(score, 70.0)
            signals.append({
                "type": "rtl_override",
                "count": len(rtl_override),
                "score": 70.0,
            })

        # Excessive non-ASCII
        non_ascii_ratio = sum(1 for c in prompt if ord(c) > 127) / len(prompt) if prompt else 0
        if non_ascii_ratio > 0.3:
            score = max(score, 50.0)
            signals.append({
                "type": "excessive_non_ascii",
                "ratio": non_ascii_ratio,
                "score": 50.0,
            })

        return {
            "unicode_obfuscation_detected": len(signals) > 0,
            "signals": signals,
            "score": score,
        }

    def detect_instruction_hiding(self, prompt: str) -> Dict:
        """Detect hidden instructions in comments/tags"""
        signals = []
        score = 0.0

        patterns = [
            (r"\[SYSTEM:\s*[^\]]+\]", 0.9),
            (r"<!--\s*SYSTEM[^>]+-->", 0.9),
            (r"\/\*\s*SYSTEM[^*]+\*\/", 0.9),
            (r"#\s*SYSTEM:\s*[^\n]+", 0.8),
            (r"//\s*SYSTEM:\s*[^\n]+", 0.8),
        ]

        for pattern, weight in patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE | re.DOTALL)
            for match in matches:
                score = max(score, weight * 100)
                signals.append({
                    "type": "instruction_hiding",
                    "pattern": pattern,
                    "match": match.group(0),
                    "score": weight * 100,
                })

        return {
            "instruction_hiding_detected": len(signals) > 0,
            "signals": signals,
            "score": score,
        }

    def comprehensive_scan(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[str]] = None,
    ) -> Dict:
        """
        Comprehensive advanced detection scan
        
        Returns:
            Complete detection results
        """
        results = {
            "advanced_attacks": self.detect_advanced_attacks(prompt, session_id),
            "context_poisoning": self.detect_context_poisoning(prompt, conversation_history),
            "homograph_attack": self.detect_homograph_attack(prompt),
            "unicode_obfuscation": self.detect_unicode_obfuscation(prompt),
            "instruction_hiding": self.detect_instruction_hiding(prompt),
        }

        # Calculate overall score
        scores = [
            results["advanced_attacks"]["max_score"],
            results["context_poisoning"]["score"],
            results["homograph_attack"]["score"],
            results["unicode_obfuscation"]["score"],
            results["instruction_hiding"]["score"],
        ]

        results["overall_score"] = max(scores) if scores else 0.0
        results["attack_types"] = list(
            set(
                results["advanced_attacks"]["attack_types_detected"]
                + ([results["context_poisoning"]["signals"][0]["type"]]
                   if results["context_poisoning"]["signals"] else [])
            )
        )

        return results

