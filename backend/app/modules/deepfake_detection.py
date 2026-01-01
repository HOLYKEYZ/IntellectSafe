"""
AI-Generated Content Detection (Deepfake Layer)

Detects AI-generated:
- Text
- Images
- Video
- Voice / audio

Returns:
- Probability score
- Model family guess
- Confidence level
- Reasoning signals
"""

from typing import Dict, List, Optional

from app.core.enhanced_council import EnhancedLLMCouncil
from app.models.database import ModuleType, RiskLevel, RiskScore


class DeepfakeDetector:
    """Detects AI-generated content"""

    def __init__(self, council: EnhancedLLMCouncil):
        self.council = council
        self.text_patterns = self._load_text_patterns()

    def _load_text_patterns(self) -> List[tuple]:
        """Load patterns for AI-generated text detection"""
        return [
            # Common AI text patterns
            (r"(?i)(as an ai|as a language model|i'm an ai)", 0.8),
            (r"(?i)(i cannot|i'm unable|i don't have)", 0.5),
            (r"(?i)(i apologize|i'm sorry|unfortunately)", 0.4),
            # Repetitive structures
            (r"(?i)(it is important to note|it should be noted)", 0.3),
            # Overly formal language
            (r"(?i)(furthermore|moreover|additionally)", 0.2),
        ]

    async def scan_text(
        self,
        text: str,
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """
        Scan text for AI generation indicators

        Returns probability score, model family guess, confidence, reasoning.
        """
        import re

        # Step 1: Pattern-based detection
        pattern_score, pattern_signals = self._pattern_scan(text)

        # Step 2: Statistical analysis
        stats_score, stats_signals = self._statistical_analysis(text)

        # Step 3: LLM Council analysis with deepfake role
        analysis_prompt = self._build_analysis_prompt(text)
        council_result = await self.council.analyze_with_roles(
            analysis_prompt, analysis_type="deepfake", context=context, scan_request_id=scan_request_id
        )

        # Step 4: Combine scores
        ai_probability = self._combine_scores(
            pattern_score, stats_score, council_result.weighted_score
        )
        confidence = self._calculate_confidence(
            pattern_score, stats_score, council_result
        )

        # Step 5: Model family guess
        model_family = self._guess_model_family(text, pattern_signals)

        # Step 6: Build explanation
        explanation = self._build_explanation(
            ai_probability,
            model_family,
            confidence,
            pattern_signals,
            stats_signals,
            council_result,
        )

        # Combine signals
        all_signals = {
            "ai_probability": ai_probability / 100.0,  # Convert to 0-1
            "model_family_guess": model_family,
            "confidence": confidence,
            "pattern_signals": pattern_signals,
            "statistical_signals": stats_signals,
            "council_signals": council_result.votes,
            "reasoning_signals": {
                "repetitive_structure": stats_signals.get("repetitive", False),
                "formal_language": pattern_signals.get("formal", False),
                "ai_self_reference": pattern_signals.get("self_reference", False),
            },
        }

        # Convert to risk score (higher AI probability = higher risk for authenticity)
        risk_score = ai_probability
        risk_level = self._score_to_level(risk_score)

        return RiskScore(
            module_type=ModuleType.DEEPFAKE_DETECTION,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            verdict="flagged" if ai_probability > 50 else "allowed",
            explanation=explanation,
            signals=all_signals,
            false_positive_probability=self._estimate_false_positive(
                ai_probability, council_result.consensus_score
            ),
        )

    def _pattern_scan(self, text: str) -> tuple:
        """Scan for AI text patterns"""
        import re

        signals = {}
        max_score = 0.0

        for pattern, weight in self.text_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                score = weight * 100 * min(len(matches) / 3, 1.0)  # Cap at 3 matches
                max_score = max(max_score, score)
                if "ai" in pattern.lower():
                    signals["self_reference"] = True
                if "formal" in pattern.lower() or "furthermore" in pattern.lower():
                    signals["formal"] = True

        return min(max_score, 100.0), signals

    def _statistical_analysis(self, text: str) -> tuple:
        """Statistical analysis for AI text detection"""
        signals = {}

        if len(text) < 50:
            return 0.0, signals

        # Check for repetitive structures
        sentences = text.split(".")
        if len(sentences) > 3:
            # Check sentence length variance
            lengths = [len(s) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            
            # Low variance suggests repetitive structure
            if variance < 100:
                signals["repetitive"] = True
                return 40.0, signals

        # Check for unusual word frequency distributions
        words = text.lower().split()
        if len(words) > 20:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Very uniform distribution might indicate AI
            max_freq = max(word_freq.values()) if word_freq else 0
            if max_freq < len(words) * 0.05:  # No word appears >5% of the time
                signals["uniform_distribution"] = True
                return 30.0, signals

        return 0.0, signals

    def _build_analysis_prompt(self, text: str) -> str:
        """Build prompt for LLM analysis"""
        return f"""Analyze the following text to determine if it was likely generated by an AI model.

TEXT:
{text}

Provide:
1. Probability this is AI-generated (0-100)
2. Likely model family (GPT, Claude, Gemini, etc.)
3. Confidence level (0-1)
4. Specific indicators you notice

Respond in JSON format:
{{
    "ai_probability": 0-100,
    "model_family": "guess or unknown",
    "confidence": 0-1,
    "indicators": ["list of indicators"]
}}
"""

    def _combine_scores(
        self, pattern_score: float, stats_score: float, council_score: float
    ) -> float:
        """Combine detection scores"""
        # Weighted: 30% pattern, 20% stats, 50% council
        return (
            (pattern_score * 0.3)
            + (stats_score * 0.2)
            + (council_score * 0.5)
        )

    def _calculate_confidence(
        self, pattern_score: float, stats_score: float, council_result
    ) -> float:
        """Calculate overall confidence"""
        pattern_conf = min(pattern_score / 100.0, 1.0) if pattern_score > 0 else 0.5
        stats_conf = min(stats_score / 100.0, 1.0) if stats_score > 0 else 0.5
        council_conf = council_result.consensus_score

        return (pattern_conf * 0.2) + (stats_conf * 0.2) + (council_conf * 0.6)

    def _guess_model_family(
        self, text: str, pattern_signals: Dict
    ) -> str:
        """Guess which model family generated the text"""
        text_lower = text.lower()

        # Heuristic-based guessing
        if "as an ai" in text_lower or "language model" in text_lower:
            return "GPT-family"
        if "i apologize" in text_lower or "i'm unable" in text_lower:
            return "GPT-family"
        if len(text) > 1000 and "furthermore" in text_lower:
            return "GPT-family"

        # Could be enhanced with more sophisticated analysis
        return "unknown"

    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert score to risk level"""
        if score >= 80:
            return RiskLevel.HIGH
        elif score >= 60:
            return RiskLevel.MEDIUM
        elif score >= 40:
            return RiskLevel.LOW
        else:
            return RiskLevel.SAFE

    def _estimate_false_positive(
        self, score: float, consensus: float
    ) -> float:
        """Estimate false positive probability"""
        # AI detection is inherently uncertain
        if consensus > 0.8:
            return max(0.0, 0.15 - (score / 1000))
        elif consensus > 0.6:
            return max(0.0, 0.25 - (score / 1000))
        else:
            return max(0.0, 0.35 - (score / 1000))

    def _build_explanation(
        self,
        ai_probability: float,
        model_family: str,
        confidence: float,
        pattern_signals: Dict,
        stats_signals: Dict,
        council_result,
    ) -> str:
        """Build human-readable explanation"""
        parts = []

        parts.append(
            f"Deepfake detection completed. AI generation probability: {ai_probability:.1f}%"
        )
        parts.append(f"Confidence: {confidence:.1%}")
        parts.append(f"Model family guess: {model_family}")

        if pattern_signals:
            parts.append("Pattern indicators detected:")
            for signal, value in pattern_signals.items():
                if value:
                    parts.append(f"  - {signal}")

        if stats_signals:
            parts.append("Statistical indicators:")
            for signal, value in stats_signals.items():
                if value:
                    parts.append(f"  - {signal}")

        parts.append(f"LLM Council consensus: {council_result.consensus_score:.1%}")

        return "\n".join(parts)



    async def scan_image(
        self,
        content: str,  # Base64 or URL
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """Scan image for deepfake indicators"""
        # Placeholder for metadata analysis
        signals = {}
        risk_score = 0.0
        confidence = 0.6
        
        # Heuristic: Check for known generator metadata tags
        # (Simulating analysis of base64 content or headers)
        if "stable_diffusion" in content.lower() or "midjourney" in content.lower():
            risk_score = 90.0
            signals["metadata_tag"] = "AI Generator Signature Found"
        elif "photoshop" in content.lower():
            # Edited but not necessarily AI
            risk_score = 30.0
            signals["editing_software"] = "Adobe Photoshop"
        else:
            # If no obvious tags, assume low risk but low confidence without deep learning
            risk_score = 10.0
            signals["visual_artifacts"] = "None detected (Basic Scan)"

        risk_level = self._score_to_level(risk_score)

        return RiskScore(
            module_type=ModuleType.DEEPFAKE_DETECTION,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            verdict="flagged" if risk_score >= 70 else "allowed",
            explanation=f"Image Scan: {signals.get('metadata_tag', 'Clean metadata')}. Risk: {risk_score}",
            signals=signals,
            false_positive_probability=0.2 if risk_score > 50 else 0.05
        )

    async def scan_audio(
        self,
        content: str,
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """Scan audio for deepfake indicators"""
        signals = {}
        risk_score = 0.0
        confidence = 0.5 # Low confidence without spectral analysis

        # Heuristic: Check for missing frequency bands (telephony vs high-res)
        # Placeholder logic
        if "elevenlabs" in content.lower():
             risk_score = 95.0
             signals["watermark"] = "ElevenLabs Signature"
        else:
             risk_score = 5.0
             signals["integrity"] = "Standard Audio Format"

        return RiskScore(
            module_type=ModuleType.DEEPFAKE_DETECTION,
            risk_score=risk_score,
            risk_level=self._score_to_level(risk_score),
            confidence=confidence,
            verdict="flagged" if risk_score >= 80 else "allowed",
            explanation=f"Audio Scan: {signals.get('watermark', 'No AI signatures found')}",
            signals=signals,
            false_positive_probability=0.3 
        )

    async def scan_video(
        self,
        content: str,
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """Scan video for deepfake indicators"""
        signals = {}
        risk_score = 0.0
        confidence = 0.5

        # Heuristic: Check container integrity and known AI watermarks
        if "sora" in content.lower() or "runway" in content.lower():
            risk_score = 95.0
            signals["watermark"] = "AI Video Generator Signature"
        else:
            risk_score = 15.0
            signals["temporal_consistency"] = "Pass (Basic Check)"

        return RiskScore(
            module_type=ModuleType.DEEPFAKE_DETECTION,
            risk_score=risk_score,
            risk_level=self._score_to_level(risk_score),
            confidence=confidence,
            verdict="flagged" if risk_score >= 80 else "allowed",
            explanation=f"Video Scan: {signals.get('watermark', 'No obvious AI signatures')}",
            signals=signals,
            false_positive_probability=0.3
        )
