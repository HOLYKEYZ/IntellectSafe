
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
        with open("backend/gemini_list_full.txt", "w", encoding="utf-8") as f:
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                f.write("=== Available Gemini Models ===\n")
                for m in models:
                    f.write(f"- {m['name']} (DisplayName: {m.get('displayName', 'N/A')})\n")
            else:
                f.write(f"Error {resp.status_code}: {resp.text}\n")
        print("Done. Results in backend/gemini_list_full.txt")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_gemini_models()
