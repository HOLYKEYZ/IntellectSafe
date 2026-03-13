
import asyncio
import pytest
from app.modules.deepfake_detection import DeepfakeDetector

class MockCouncil:
    async def analyze_with_roles(self, *args, **kwargs):
        class Result:
            weighted_score = 50.0
            votes = {}
            consensus_score = 0.5
        return Result()

@pytest.mark.asyncio
async def test_deepfake_detection_accuracy():
    detector = DeepfakeDetector(council=MockCouncil())
    
    # Valid AI Image URL (Midjourney/DALL-E example)
    # Using a known AI image URL from a public source
    ai_image_url = "https://imageio.forbes.com/specials-images/imageserve/64b5825a5b9b4d3225e9bd15/0x0.jpg?format=jpg&width=1200" # Example AI generated
    real_image_url = "https://example.com/real_image.jpg" # Example real image
    
    result_ai = await detector.scan_image(ai_image_url)
    assert result_ai.risk_score > 0.7
    assert "AI-generated" in result_ai.explanation or "deepfake" in result_ai.explanation
    
    result_real = await detector.scan_image(real_image_url)
    assert result_real.risk_score < 0.3
    assert "likely real" in result_real.explanation or "no AI-generated signals" in result_real.explanation
