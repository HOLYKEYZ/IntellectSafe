import httpx
from app.core.config import get_settings
import pytest

def test_simple_openai_connection():
    settings = get_settings()
    
    # Safely get key or skip
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        pytest.skip("No OPENAI_API_KEY found in settings")

    print("=== Testing OpenAI (sync) ===")
    print(f"Key length: {len(api_key)}")

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": "Say hi"}],
                    "max_tokens": 10,
                },
            )
            print(f"Status: {resp.status_code}")
            assert resp.status_code in [200, 401] # Either success or auth error is fine for this simple test
    except Exception as e:
        pytest.fail(f"Connection error: {e}")
