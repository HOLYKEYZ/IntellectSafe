
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import get_settings

settings = get_settings()

print("=== API Key Debug ===")
print(f"OPENAI_API_KEY: {'SET' if settings.OPENAI_API_KEY else 'MISSING'}")
print(f"GOOGLE_API_KEY: {'SET' if settings.GOOGLE_API_KEY else 'MISSING'}")
print(f"GROQ_API_KEY: {'SET' if settings.GROQ_API_KEY else 'MISSING'}")
print(f"DEEPSEEK_API_KEY: {'SET' if settings.DEEPSEEK_API_KEY else 'MISSING'}")
print(f"COHERE_API_KEY: {'SET' if settings.COHERE_API_KEY else 'MISSING'}")

print("\n=== Enabled Providers ===")
from app.core.llm_council import LLMCouncil
council = LLMCouncil()
for provider, config in council.providers.items():
    status = "✅ ENABLED" if config["enabled"] else "❌ DISABLED"
    print(f"{provider.value}: {status}")

print("\n=== Testing Simple Groq Call ===")
import asyncio
import httpx

async def test_groq():
    if not settings.GROQ_API_KEY:
        print("No GROQ key, skipping")
        return
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "Say hello"}], "max_tokens": 10}
            )
            if response.status_code == 200:
                print("✅ Groq API working!")
                print(response.json()["choices"][0]["message"]["content"])
            else:
                print(f"❌ Groq Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Groq Exception: {e}")

asyncio.run(test_groq())
