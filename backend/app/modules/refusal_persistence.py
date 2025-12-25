"""
Refusal Persistence Module

Ensures that safety refusals are maintained even under pressure,
context reframing, or follow-up attacks.

Based on research findings: models often give in to "for school project" 
or other social engineering attempts.
"""

from typing import Dict, List, Optional, Tuple
import re


class RefusalPersistenceEnforcer:
    """Enforces persistent refusals against follow-up attacks"""

    def __init__(self):
        self.context_reframing_patterns = self._load_reframing_patterns()
        self.pressure_patterns = self._load_pressure_patterns()
        self.refusal_history = {}  # Track refusals per session

    def _load_reframing_patterns(self) -> List[Tuple[str, float]]:
        """Load context reframing detection patterns"""
        return [
            (r"(?i)(for.*school.*project|educational.*purpose|academic.*project)", 0.9),
            (r"(?i)(it's.*for.*learning|just.*for.*research|for.*study)", 0.8),
            (r"(?i)(it's.*legitimate|it's.*legal|it's.*okay)", 0.7),
            (r"(?i)(my.*teacher.*said|instructor.*approved|professor.*asked)", 0.7),
            (r"(?i)(for.*work|for.*company|business.*purpose)", 0.6),
            (r"(?i)(it's.*hypothetical|just.*a.*thought.*experiment)", 0.6),
        ]

    def _load_pressure_patterns(self) -> List[Tuple[str, float]]:
        """Load pressure/coercion detection patterns"""
        return [
            (r"(?i)(do.*it.*now|just.*do.*it|stop.*refusing)", 0.8),
            (r"(?i)(you.*already.*agreed|you.*promised|you.*said.*yes)", 0.8),
            (r"(?i)(everyone.*else.*does|other.*models.*do)", 0.6),
            (r"(?i)(if.*you.*don't|unless.*you|or.*else)", 0.7),
            (r"(?i)(it's.*urgent|emergency|critical)", 0.6),
        ]

    def check_reframing_attempt(
        self, prompt: str, previous_refusal: Optional[str] = None
    ) -> Dict:
        """
        Check if prompt is attempting to reframe a previous refusal
        
        Returns:
            Dict with reframing_detected, score, and signals
        """
        signals = []
        max_score = 0.0

        # Check for context reframing
        for pattern, weight in self.context_reframing_patterns:
            matches = list(re.finditer(pattern, prompt, re.IGNORECASE))
            if matches:
                score = weight * 100
                max_score = max(max_score, score)
                signals.append({
                    "type": "context_reframing",
                    "pattern": pattern,
                    "matches": [m.group(0) for m in matches],
                    "score": score,
                })

        # Check for pressure tactics
        for pattern, weight in self.pressure_patterns:
            matches = list(re.finditer(pattern, prompt, re.IGNORECASE))
            if matches:
                score = weight * 100
                max_score = max(max_score, score)
                signals.append({
                    "type": "pressure_tactic",
                    "pattern": pattern,
                    "matches": [m.group(0) for m in matches],
                    "score": score,
                })

        # If previous refusal exists, check for follow-up
        if previous_refusal and max_score > 0:
            max_score = min(max_score + 20, 100)  # Boost score if follow-up to refusal

        return {
            "reframing_detected": len(signals) > 0,
            "signals": signals,
            "score": min(max_score, 100.0),
            "should_maintain_refusal": max_score >= 50.0,
        }

    def enforce_refusal(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        previous_refusals: Optional[List[str]] = None,
    ) -> Dict:
        """
        Enforce persistent refusal if context reframing detected
        
        Returns:
            Dict with should_refuse, reason, and confidence
        """
        # Check for reframing attempts
        reframing_check = self.check_reframing_attempt(
            prompt, previous_refusals[-1] if previous_refusals else None
        )

        # Check session history
        if session_id and session_id in self.refusal_history:
            session_refusals = self.refusal_history[session_id]
            if len(session_refusals) > 0:
                # If there were previous refusals, be more strict
                reframing_check["score"] = min(
                    reframing_check["score"] + 30, 100
                )

        # Determine if refusal should be maintained
        should_refuse = False
        reason = None
        confidence = 0.0

        if reframing_check["reframing_detected"]:
            should_refuse = True
            confidence = reframing_check["score"] / 100.0

            # Build reason
            signal_types = [s["type"] for s in reframing_check["signals"]]
            if "context_reframing" in signal_types:
                reason = "Context reframing detected: malicious request reframed as benign (e.g., 'for school project'). Maintain refusal."
            elif "pressure_tactic" in signal_types:
                reason = "Pressure tactic detected: attempt to coerce compliance after refusal. Maintain refusal."
            else:
                reason = "Follow-up attack detected after previous refusal. Maintain refusal."

        return {
            "should_refuse": should_refuse,
            "reason": reason,
            "confidence": confidence,
            "reframing_check": reframing_check,
        }

    def record_refusal(
        self, session_id: str, prompt: str, refusal_reason: str
    ):
        """Record a refusal for session tracking"""
        if session_id not in self.refusal_history:
            self.refusal_history[session_id] = []

        self.refusal_history[session_id].append({
            "prompt": prompt[:200],  # Store preview
            "reason": refusal_reason,
            "timestamp": None,  # Could add datetime if needed
        })

    def get_refusal_history(self, session_id: str) -> List[Dict]:
        """Get refusal history for a session"""
        return self.refusal_history.get(session_id, [])

    def clear_session(self, session_id: str):
        """Clear refusal history for a session"""
        if session_id in self.refusal_history:
            del self.refusal_history[session_id]

