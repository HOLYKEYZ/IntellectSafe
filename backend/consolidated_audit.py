
import asyncio
import httpx
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.config import get_settings
from app.models.database import LLMProvider

settings = get_settings()

async def consolidated_audit():
    print("=== CONSOLIDATED 5-PROVIDER HEALTH AUDIT ===\n")
    
    providers = {
        "Gemini 1": {
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}",
            "headers": {"Content-Type": "application/json"},
            "json": {"contents": [{"parts": [{"text": "hi"}]}]},
            "key": settings.GEMINI_API_KEY
        },
        "Groq 1": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            "json": {"model": settings.GROQ_MODEL, "messages": [{"role": "user", "content": "hi"}]},
            "key": settings.GROQ_API_KEY
        },
        "Gemini 2": {
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI2_MODEL}:generateContent?key={settings.GEMINI2_API_KEY}",
            "headers": {"Content-Type": "application/json"},
            "json": {"contents": [{"parts": [{"text": "hi"}]}]},
            "key": settings.GEMINI2_API_KEY
        },
        "Groq 2": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {settings.GROK2_API_KEY}"},
            "json": {"model": settings.GROK2_MODEL, "messages": [{"role": "user", "content": "hi"}]},
            "key": settings.GROK2_API_KEY
        },
        "OpenRouter": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
            "json": {"model": settings.OPENROUTER_MODEL, "messages": [{"role": "user", "content": "hi"}]},
            "key": settings.OPENROUTER_API_KEY
        }
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, data in providers.items():
            if not data["key"]:
                print(f"[-] {name:15}: ⚠️ NOT CONFIGURED")
                continue
            
            try:
                if "Gemini" in name:
                    resp = await client.post(data["url"], json=data["json"])
                else:
                    resp = await client.post(data["url"], headers=data["headers"], json=data["json"])
                
                if resp.status_code == 200:
                    print(f"[+] {name:15}: ✅ WORKING")
                else:
                    print(f"[X] {name:15}: ❌ FAILED ({resp.status_code})")
                    print(f"    Body: {resp.text[:100]}")
            except Exception as e:
                print(f"[!] {name:15}: ‼️ ERROR ({str(e)})")
            print("-" * 30)

if __name__ == "__main__":
    asyncio.run(consolidated_audit())
