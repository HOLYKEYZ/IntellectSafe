
import asyncio
import httpx
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.config import get_settings

settings = get_settings()

async def run_gemini_pro_check():
    model = "gemini-1.5-pro"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={getattr(settings, 'GOOGLE_API_KEY', '')}"
    payload = {"contents": [{"parts": [{"text": "Say 'GEMINI WORKING'"}]}]}
    success = False
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                text = resp.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                if "GEMINI WORKING" in text:
                    success = True
                    print(f"SUCCESS: {text}")
                else:
                    print(f"FAILED: Expected 'GEMINI WORKING' not found in response. Got: {text}")
            else:
                print(f"FAILED ({resp.status_code}): {resp.text}")
        except Exception as e:
            print(f"ERROR: {e}")
    return success

if __name__ == "__main__":
    success = asyncio.run(run_gemini_pro_check())
    sys.exit(0 if success else 1)
