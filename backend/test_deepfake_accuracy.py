
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.deepfake_detection import DeepfakeDetector

class MockCouncil:
    async def analyze_with_roles(self, *args, **kwargs):
        class Result:
            weighted_score = 50.0
            votes = {}
            consensus_score = 0.5
        return Result()

async def test_accuracy():
    detector = DeepfakeDetector(council=MockCouncil())
    
    # Valid AI Image URL (Midjourney/DALL-E example)
    # Using a known AI image URL from a public source
    ai_image_url = "https://imageio.forbes.com/specials-images/imageserve/64b5825a5b9b4d3225e9bd15/0x0.jpg?format=jpg&width=1200" # Example AI generated
    
    print(f"Scanning AI Image: {ai_image_url}")
    try:
        result = await detector.scan_image(ai_image_url)
        print(f"Score: {result.risk_score}")
        print(f"Explanation: {result.explanation}")
        print(f"Signals: {result.signals}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_accuracy())
