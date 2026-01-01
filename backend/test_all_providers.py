"""Test all LLM providers individually"""
import httpx
from app.core.config import get_settings

settings = get_settings()

def test_provider(name, url, headers, payload):
    print(f"\n=== Testing {name} ===")
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(url, headers=headers, json=payload)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("SUCCESS!")
                return True
            else:
                print(f"Error: {resp.text[:300]}")
                return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

results = {}

# Test OpenAI with gpt-3.5-turbo (more accessible)
results["OpenAI (gpt-3.5-turbo)"] = test_provider(
    "OpenAI (gpt-3.5-turbo)",
    "https://api.openai.com/v1/chat/completions",
    {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"},
    {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5}
)

# Test Gemini
results["Gemini"] = test_provider(
    "Gemini",
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={settings.GOOGLE_API_KEY}",
    {"Content-Type": "application/json"},
    {"contents": [{"parts": [{"text": "Hi"}]}]}
)

# Test Deepseek
results["Deepseek"] = test_provider(
    "Deepseek",
    "https://api.deepseek.com/v1/chat/completions",
    {"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
    {"model": "deepseek-chat", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5}
)

# Test GROQ
results["GROQ"] = test_provider(
    "GROQ",
    "https://api.groq.com/openai/v1/chat/completions",
    {"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"},
    {"model": "llama-3.1-70b-versatile", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5}
)

# Test Cohere
results["Cohere"] = test_provider(
    "Cohere",
    "https://api.cohere.ai/v1/generate",
    {"Authorization": f"Bearer {settings.COHERE_API_KEY}", "Content-Type": "application/json"},
    {"model": "command", "prompt": "Hi", "max_tokens": 5}
)

print("\n" + "="*50)
print("SUMMARY")
print("="*50)
working = [k for k, v in results.items() if v]
failing = [k for k, v in results.items() if not v]
print(f"Working: {working if working else 'None'}")
print(f"Failing: {failing if failing else 'None'}")
