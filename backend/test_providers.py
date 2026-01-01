"""Simple test of individual LLM providers"""
import asyncio
import httpx
from app.core.config import get_settings

settings = get_settings()

async def test_openai():
    print("\n=== Testing OpenAI ===")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [{"role": "user", "content": "Say hello"}],
                    "max_tokens": 10,
                },
            )
            print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Error: {resp.text[:200]}")
            else:
                print("SUCCESS")
    except Exception as e:
        print(f"Exception: {e}")

async def test_gemini():
    print("\n=== Testing Gemini ===")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                params={"key": settings.GOOGLE_API_KEY},
                json={"contents": [{"parts": [{"text": "Say hello"}]}]},
            )
            print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Error: {resp.text[:200]}")
            else:
                print("SUCCESS")
    except Exception as e:
        print(f"Exception: {e}")

async def test_deepseek():
    print("\n=== Testing Deepseek ===")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "Say hello"}],
                    "max_tokens": 10,
                },
            )
            print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Error: {resp.text[:200]}")
            else:
                print("SUCCESS")
    except Exception as e:
        print(f"Exception: {e}")

async def main():
    print("=== Testing Individual Providers ===")
    print(f"OPENAI key length: {len(settings.OPENAI_API_KEY or '')}")
    print(f"GEMINI key length: {len(settings.GOOGLE_API_KEY or '')}")
    print(f"DEEPSEEK key length: {len(settings.DEEPSEEK_API_KEY or '')}")
    
    await test_deepseek()  # Test Deepseek first since it was working
    await test_openai()
    await test_gemini()

if __name__ == "__main__":
    asyncio.run(main())
