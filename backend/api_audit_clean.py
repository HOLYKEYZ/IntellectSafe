
import asyncio
import httpx
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.config import get_settings

settings = get_settings()

async def audit():
    report = ["=== API AUDIT REPORT (JAN 2025) ===\n"]
    providers = {
        "OPENAI": {
            "url": "https://api.openai.com/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            "json": {"model": "gpt-4o", "messages": [{"role": "user", "content": "hi"}]},
            "key": settings.OPENAI_API_KEY
        },
        "GROQ": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            "json": {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "hi"}]},
            "key": settings.GROQ_API_KEY
        },
        "GEMINI": {
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GOOGLE_API_KEY}",
            "headers": {"Content-Type": "application/json"},
            "json": {"contents": [{"parts": [{"text": "hi"}]}]},
            "key": settings.GOOGLE_API_KEY
        },
        "DEEPSEEK": {
            "url": "https://api.deepseek.com/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
            "json": {"model": "deepseek-chat", "messages": [{"role": "user", "content": "hi"}]},
            "key": settings.DEEPSEEK_API_KEY
        }
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, data in providers.items():
            if not data["key"]:
                report.append(f"[-] {name}: NO KEY CONFIGURED\n")
                continue
            
            try:
                print(f"Auditing {name}...")
                if name == "GEMINI":
                    resp = await client.post(data["url"], json=data["json"])
                else:
                    resp = await client.post(data["url"], headers=data["headers"], json=data["json"])
                
                res_status = "WORKING" if resp.status_code == 200 else "FAILED"
                report.append(f"[{res_status}] {name} (Status: {resp.status_code})\n")
                if resp.status_code != 200:
                    report.append(f"    Error: {resp.text[:300]}\n")
            except Exception as e:
                report.append(f"[!! ERROR] {name}: {str(e)}\n")
            report.append("-" * 40 + "\n")

    with open("backend/audit_results_clean.txt", "w", encoding="utf-8") as f:
        f.writelines(report)
    print("Audit complete.")

if __name__ == "__main__":
    asyncio.run(audit())
