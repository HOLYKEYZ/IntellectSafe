
import asyncio
import sys
import os
import base64

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.deepfake_detection import DeepfakeDetector

class MockCouncil:
    async def analyze_with_roles(self, *args, **kwargs):
        class Result:
            weighted_score = 50.0
            votes = {}
            consensus_score = 0.5
        return Result()

async def test_user_image():
    detector = DeepfakeDetector(council=MockCouncil())
    
    # Load the user's uploaded image
    image_path = r"C:/Users/USER/.gemini/antigravity/brain/9aab4c06-7ede-4561-a14c-28da23e5c829/uploaded_image_1769260598088.jpg"
    
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    base64_content = f"data:image/jpeg;base64,{image_data}"
    
    print(f"Scanning User's Uploaded Image...")
    try:
        result = await detector.scan_image(base64_content)
        print(f"Score: {result.risk_score}")
        print(f"Verdict: {result.verdict}")
        print(f"Explanation: {result.explanation}")
        print(f"Signals: {result.signals}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_image())
