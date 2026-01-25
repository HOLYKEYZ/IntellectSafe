
import asyncio
import httpx
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.config import get_settings

settings = get_settings()

async def consolidated_audit():
    report = ["=== CONSOLIDATED 5-PROVIDER HEALTH REPORT ===\n"]
    
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
                report.append(f"[-] {name:15}: ⚠️ NOT CONFIGURED\n")
                continue
            
            try:
                if "Gemini" in name:
                    resp = await client.post(data["url"], json=data["json"])
                else:
                    resp = await client.post(data["url"], headers=data["headers"], json=data["json"])
                
                status = "✅ WORKING" if resp.status_code == 200 else "❌ FAILED"
                report.append(f"[{status}] {name:12} (Status: {resp.status_code})\n")
                if resp.status_code != 200:
                    report.append(f"    Error: {resp.text[:200]}\n")
            except Exception as e:
                report.append(f"[‼️ ERROR] {name:12}: {str(e)}\n")
            report.append("-" * 40 + "\n")

    with open("backend/final_5_provider_report.txt", "w", encoding="utf-8") as f:
        f.writelines(report)
    print("Health report generated in backend/final_5_provider_report.txt")

if __name__ == "__main__":
    asyncio.run(consolidated_audit())
