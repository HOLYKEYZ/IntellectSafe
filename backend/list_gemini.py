
import httpx
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.config import get_settings

settings = get_settings()

def list_gemini_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.GOOGLE_API_KEY}"
    try:
        resp = httpx.get(url)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            print("=== Available Gemini Models ===")
            for m in models:
                print(f"- {m['name']} (DisplayName: {m.get('displayName', 'N/A')})")
        else:
            print(f"Error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_gemini_models()
