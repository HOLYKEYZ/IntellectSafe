import httpx
from app.core.config import get_settings

settings = get_settings()

print("=== Testing OpenAI (sync) ===")
print(f"Key length: {len(settings.OPENAI_API_KEY or '')}")

try:
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4",  # Try base gpt-4 instead of gpt-4-turbo-preview
                "messages": [{"role": "user", "content": "Say hi"}],
                "max_tokens": 10,
            },
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
