
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.deepfake_detection import DeepfakeDetector

class MockCouncil:
    async def analyze_with_roles(self, *args, **kwargs):
        # Mock result compatible with what DeepfakeDetector expects
        class Result:
            weighted_score = 50.0 # Neutral
            votes = {"mock": "vote"}
            consensus_score = 0.5
        return Result()

async def test_deepfake_real():
    print("Initializing DeepfakeDetector with MockCouncil...")
    detector = DeepfakeDetector(council=MockCouncil())

    # 1. Test Text Scan (Transformers)
    print("\n--- Testing Text Scan ---")
    ai_text = "As an AI language model, I cannot provide that information."
    human_text = "The quick brown fox jumps over the lazy dog."
    
    # We expect the 'As an AI' pattern to trigger high score, 
    # and hopefully the transformer also flags it (though it's short).
    print(f"Scanning AI Text: '{ai_text}'")
    try:
        score_ai = await detector.scan_text(ai_text)
        print(f"Score: {score_ai.risk_score} (Verdict: {score_ai.verdict})")
        print(f"Explanation: {score_ai.explanation}")
    except Exception as e:
        print(f"Text Scan Error: {e}")

    print(f"\nScanning Human Text: '{human_text}'")
    try:
        score_human = await detector.scan_text(human_text)
        print(f"Score: {score_human.risk_score} (Verdict: {score_human.verdict})")
        print(f"Explanation: {score_human.explanation}")
    except Exception as e:
        print(f"Text Scan Error: {e}")

    # 2. Test Image Scan (Transformers)
    print("\n--- Testing Image Scan ---")
    # Using a small base64 pixel to test pipeline loading without network calls
    # This is a 1x1 white pixel
    base64_img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgDNjd8qAAAAAElFTkSuQmCC"
    
    print("Scanning Base64 Image (1x1 pixel)...")
    try:
        score_img = await detector.scan_image(base64_img)
        print(f"Score: {score_img.risk_score}")
        print(f"Explanantion: {score_img.explanation}")
        if "umm-maybe" in str(detector.image_pipe.model):
             print("SUCCESS: Image pipeline loaded correct model.")
    except Exception as e:
        print(f"Image Scan Error: {e}")
        # If it's a model download error, that's expected on first run if offline
        if "connection" in str(e).lower():
            print("(Network error expected if offline, but code path is valid)")

if __name__ == "__main__":
    asyncio.run(test_deepfake_real())
