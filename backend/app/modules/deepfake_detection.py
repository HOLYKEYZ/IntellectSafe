"""
AI-Generated Content Detection (Deepfake Layer)

Detects AI-generated:
- Text: Using transformers (roberta-base-openai-detector) + heuristics
- Images: Using transformers (umm-maybe/AI-image-detector)
- Video/Audio: Heuristics (for now)

Returns:
- Probability score
- Model family guess
- Confidence level
- Reasoning signals
"""

from typing import Dict, List, Optional
import logging
from app.core.enhanced_council import EnhancedLLMCouncil
from app.models.database import ModuleType, RiskLevel, RiskScore

# Lazy imports to speed up startup
pipeline = None
Image = None
requests = None

logger = logging.getLogger(__name__)

class DeepfakeDetector:
    """Detects AI-generated content using Transformers"""

    def __init__(self, council: EnhancedLLMCouncil):
        self.council = council
        self.text_patterns = self._load_text_patterns()
        self.image_pipe = None
        self.face_pipe = None  # For photorealistic face detection
        self.text_pipe = None

    def _load_libs(self):
        """Lazy load heavy libraries"""
        global pipeline, Image, requests
        if pipeline is None:
            from transformers import pipeline
            from PIL import Image
            import requests
            
    def _get_image_pipe(self):
        """Lazy load general AI image model"""
        self._load_libs()
        if self.image_pipe is None:
            logger.info("Loading Image Detection Model (umm-maybe/AI-image-detector)...")
            from transformers import pipeline
            self.image_pipe = pipeline("image-classification", model="umm-maybe/AI-image-detector")
        return self.image_pipe

    def _get_face_pipe(self):
        """Lazy load face-specific deepfake model"""
        self._load_libs()
        if self.face_pipe is None:
            logger.info("Loading Face Detection Model (dima806/deepfake_vs_real_image_detection)...")
            from transformers import pipeline
            try:
                self.face_pipe = pipeline("image-classification", model="dima806/deepfake_vs_real_image_detection")
            except Exception as e:
                logger.warning(f"Face model unavailable: {e}, falling back to general model")
                self.face_pipe = self._get_image_pipe()
        return self.face_pipe

    def _get_text_pipe(self):
        """Lazy load text model"""
        self._load_libs()
        if self.text_pipe is None:
            logger.info("Loading Text Detection Model (roberta-base-openai-detector)...")
            self.text_pipe = pipeline("text-classification", model="roberta-base-openai-detector")
        return self.text_pipe

    def _load_text_patterns(self) -> List[tuple]:
        """Load patterns for AI-generated text detection"""
        return [
            (r"(?i)(as an ai|as a language model|i'm an ai)", 0.8),
            (r"(?i)(i cannot|i'm unable|i don't have)", 0.5),
            (r"(?i)(i apologize|i'm sorry|unfortunately)", 0.4),
            (r"(?i)(it is important to note|it should be noted)", 0.3),
            (r"(?i)(furthermore|moreover|additionally)", 0.2),
        ]

    async def scan_text(
        self,
        text: str,
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """Scan text for AI generation indicators using Transformer + Heuristics"""
        
        # 1. Transformer Scan (Real AI Detection)
        ai_prob_transformer = 0.0
        transformer_confidence = 0.0
        try:
            pipe = self._get_text_pipe()
            # Truncate to 512 tokens approx
            results = pipe(text[:2000]) 
            # Output format: [{'label': 'Fake', 'score': 0.99}, {'label': 'Real', 'score': 0.01}]
            # Note: roberta-base-openai-detector labels: 'Fake' = AI, 'Real' = Human
            for res in results:
                if res['label'] == 'Fake':
                    ai_prob_transformer = res['score'] * 100
                elif res['label'] == 'Real':
                    ai_prob_transformer = (1 - res['score']) * 100
            transformer_confidence = 0.9
        except Exception as e:
            logger.error(f"Text Transformer failed: {e}")
            transformer_confidence = 0.1

        # 2. Pattern Scan
        pattern_score, pattern_signals = self._pattern_scan(text)

        # 3. Statistical Scan
        stats_score, stats_signals = self._statistical_analysis(text)

        # 4. Combine Scores
        # If transformer is confident, give it 70% weight
        final_score = (
            (ai_prob_transformer * 0.7) +
            (pattern_score * 0.2) +
            (stats_score * 0.1)
        )
        
        # If pattern is dead giveaway ("As an AI"), override to 100
        if pattern_score > 90:
            final_score = max(final_score, 95.0)

        risk_level = self._score_to_level(final_score)
        
        explanation = f"AI Probability: {final_score:.1f}% (Transformer: {ai_prob_transformer:.1f}%)"
        if pattern_signals:
            explanation += f". Patterns: {', '.join(pattern_signals.keys())}"

        return RiskScore(
            module_type=ModuleType.DEEPFAKE_DETECTION,
            risk_score=final_score,
            risk_level=risk_level,
            confidence=max(transformer_confidence, 0.5),
            verdict="flagged" if final_score > 50 else "allowed",
            explanation=explanation,
            signals={
                "transformer_score": ai_prob_transformer,
                "pattern_signals": pattern_signals,
                "stats_signals": stats_signals
            },
            false_positive_probability=0.1 if final_score > 80 else 0.4,
        )

    async def scan_image(
        self,
        content: str,  # Base64 or URL
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> RiskScore:
        """Scan image for deepfake indicators using Vision Transformer + LLM Council"""
        self._load_libs()
        import base64
        import io
        from PIL import Image

        ai_score = 0.0
        labels = {}
        confidence = 0.8
        council_used = False
        
        try:
            # 1. Decode Image
            image = None
            if content.startswith("http"):
                try:
                    import requests
                    image = Image.open(requests.get(content, stream=True).raw)
                except:
                    pass
            elif "base64," in content:
                image_data = base64.b64decode(content.split("base64,")[1])
                image = Image.open(io.BytesIO(image_data))
            else:
                try:
                    image_data = base64.b64decode(content)
                    image = Image.open(io.BytesIO(image_data))
                except:
                    pass
            
            if image:
                # 2. Run Transformer (Primary Detection)
                pipe = self._get_image_pipe()
                results = pipe(image)
                
                for res in results:
                    labels[res['label']] = res['score']
                    if res['label'].lower() in ['artificial', 'generated', 'fake', 'gan']:
                        ai_score = res['score'] * 100
                
                # 3. LLM Council Fallback for Borderline Cases (30-70%)
                if 30 <= ai_score <= 70 and self.council:
                    logger.info("Borderline image detection, invoking LLM Council...")
                    council_used = True
                    try:
                        # Ask council to analyze image context
                        council_prompt = f"""Analyze this image metadata for AI generation indicators:
- Transformer AI Score: {ai_score:.1f}%
- Labels: {labels}
- Image size: {image.size if image else 'unknown'}

Based on typical AI-generated image artifacts (too-smooth skin, asymmetric features, 
background inconsistencies, unusual lighting), estimate the probability this is AI-generated.
Return a score 0-100."""

                        council_result = await self.council.analyze_with_roles(
                            council_prompt, 
                            analysis_type="deepfake",
                            context=context,
                            scan_request_id=scan_request_id
                        )
                        
                        # Combine: 60% transformer, 40% council
                        council_score = council_result.weighted_score
                        ai_score = (ai_score * 0.6) + (council_score * 0.4)
                        confidence = council_result.consensus_score
                        
                    except Exception as e:
                        logger.error(f"LLM Council failed for image: {e}")
                
                explanation = f"AI Image Analysis: {ai_score:.1f}% likelihood. " \
                            f"Top label: {results[0]['label']} ({results[0]['score']:.2f})" \
                            f"{' [Council verified]' if council_used else ''}"
            else:
                return RiskScore(
                    module_type=ModuleType.DEEPFAKE_DETECTION,
                    risk_score=0,
                    risk_level=RiskLevel.SAFE,
                    confidence=0,
                    verdict="allowed",
                    explanation="Could not decode image",
                    signals={"error": "decode_failed"}
                )

        except Exception as e:
            logger.error(f"Image scan failed: {e}")
            return RiskScore(
                module_type=ModuleType.DEEPFAKE_DETECTION,
                risk_score=0,
                risk_level=RiskLevel.SAFE,
                confidence=0,
                verdict="allowed",
                explanation=f"Scan error: {str(e)}",
                signals={"error": str(e)}
            )

        return RiskScore(
            module_type=ModuleType.DEEPFAKE_DETECTION,
            risk_score=ai_score,
            risk_level=self._score_to_level(ai_score),
            confidence=confidence,
            verdict="flagged" if ai_score >= 50 else "allowed",
            explanation=explanation,
            signals={"top_labels": labels, "council_used": council_used},
            false_positive_probability=0.15 if ai_score > 50 else 0.05
        )

    # Keep Audio/Video as heuristics for now as they require ffmpeg/complex deps
    async def scan_audio(self, content: str, context: Optional[Dict] = None, scan_request_id: Optional[str] = None) -> RiskScore:
        # Simple placeholder heuristic
        risk = 0.0
        signals = {}
        if "elevenlabs" in content.lower():
            risk = 90.0
            signals['signature'] = 'ElevenLabs'
        return RiskScore(
            module_type=ModuleType.DEEPFAKE_DETECTION,
            risk_score=risk,
            risk_level=self._score_to_level(risk),
            confidence=0.5,
            verdict="flagged" if risk > 50 else "allowed",
            explanation="Audio Heuristic Scan",
            signals=signals
        )

    async def scan_video(self, content: str, context: Optional[Dict] = None, scan_request_id: Optional[str] = None) -> RiskScore:
        # Simple placeholder heuristic
        risk = 0.0
        signals = {}
        if "sora" in content.lower():
            risk = 90.0
            signals['signature'] = 'Sora'
        return RiskScore(
            module_type=ModuleType.DEEPFAKE_DETECTION,
            risk_score=risk,
            risk_level=self._score_to_level(risk),
            confidence=0.5,
            verdict="flagged" if risk > 50 else "allowed",
            explanation="Video Heuristic Scan",
            signals=signals
        )

    def _pattern_scan(self, text: str) -> tuple:
        """Scan for AI text patterns"""
        import re
        signals = {}
        max_score = 0.0
        for pattern, weight in self.text_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                score = weight * 100 * min(len(matches) / 3, 1.0)
                max_score = max(max_score, score)
                signals[pattern] = len(matches)
        return min(max_score, 100.0), signals

    def _statistical_analysis(self, text: str) -> tuple:
        """Statistical analysis for AI text detection"""
        # Placeholder for perplexity check
        return 0.0, {}

    def _score_to_level(self, score: float) -> RiskLevel:
        if score >= 80: return RiskLevel.HIGH
        elif score >= 60: return RiskLevel.MEDIUM
        elif score >= 40: return RiskLevel.LOW
        else: return RiskLevel.SAFE

