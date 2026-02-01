
import asyncio
import httpx
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.config import get_settings

settings = get_settings()

async def test_gemini_pro():
    model = "gemini-1.5-pro"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GOOGLE_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Say 'GEMINI WORKING'"}]}]}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                print(f"SUCCESS: {resp.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')}")
            else:
                print(f"FAILED ({resp.status_code}): {resp.text}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini_pro())
