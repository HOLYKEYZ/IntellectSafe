
import asyncio
import httpx
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.config import get_settings

settings = get_settings()

async def final_audit():
    print("=== FINAL API KEY HEALTH AUDIT ===\n")
    providers = {
        "OpenAI (Direct)": {
            "url": "https://api.openai.com/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            "json": {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}]},
            "key": settings.OPENAI_API_KEY
        },
        "Groq": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            "json": {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "hi"}]},
            "key": settings.GROQ_API_KEY
        },
        "Gemini 2.5 Flash": {
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GOOGLE_API_KEY}",
            "headers": {"Content-Type": "application/json"},
            "json": {"contents": [{"parts": [{"text": "hi"}]}]},
            "key": settings.GOOGLE_API_KEY
        },
        "DeepSeek": {
            "url": "https://api.deepseek.com/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
            "json": {"model": "deepseek-chat", "messages": [{"role": "user", "content": "hi"}]},
            "key": settings.DEEPSEEK_API_KEY
        },
        "Cohere": {
            "url": "https://api.cohere.ai/v1/generate",
            "headers": {"Authorization": f"Bearer {settings.COHERE_API_KEY}"},
            "json": {"model": "command-r", "prompt": "hi", "max_tokens": 10},
            "key": settings.COHERE_API_KEY
        },
         "OpenRouter (Fallback)": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
            "json": {"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}]},
            "key": settings.OPENROUTER_API_KEY
        }
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, data in providers.items():
            if not data["key"]:
                print(f"[-] {name:20}: ⚠️ NOT CONFIGURED")
                continue
            
            try:
                if "Gemini" in name:
                    resp = await client.post(data["url"], json=data["json"])
                else:
                    resp = await client.post(data["url"], headers=data["headers"], json=data["json"])
                
                if resp.status_code == 200:
                    print(f"[+] {name:20}: ✅ WORKING")
                else:
                    print(f"[X] {name:20}: ❌ FAILED ({resp.status_code})")
                    try:
                        err_data = resp.json().get("error", {})
                        msg = err_data.get("message", resp.text[:100])
                    except:
                        msg = resp.text[:100]
                    print(f"    Reason: {msg}")
            except Exception as e:
                print(f"[!] {name:20}: ‼️ ERROR ({str(e)})")
            print("-" * 30)

if __name__ == "__main__":
    asyncio.run(final_audit())
