
import asyncio
import sys
import os
import httpx
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import get_settings
from app.models.database import LLMProvider
from app.core.llm_council import LLMCouncil

settings = get_settings()

async def test_provider(council, provider_enum):
    provider_name = provider_enum.value
    config = council.providers.get(provider_enum)
    
    if not config or not config.get("enabled"):
        print(f"[-] {provider_name}: DISABLED (No API key)")
        return
        
    print(f"[*] Testing {provider_name} ({config['model']})...")
    start = time.time()
    try:
        # Call the specific internal method
        if provider_enum == LLMProvider.OPENAI:
            res = await council._call_openai(config, "Say 'SUCCESS'")
        elif provider_enum == LLMProvider.GEMINI:
            res = await council._call_gemini(config, "Say 'SUCCESS'")
        elif provider_enum == LLMProvider.GROQ:
            res = await council._call_groq(config, "Say 'SUCCESS'")
        elif provider_enum == LLMProvider.DEEPSEEK:
            res = await council._call_deepseek(config, "Say 'SUCCESS'")
        elif provider_enum == LLMProvider.COHERE:
            res = await council._call_cohere(config, "Say 'SUCCESS'")
        else:
            print(f"[!] {provider_name}: Unknown provider mapping")
            return

        elapsed = time.time() - start
        print(f"[+] {provider_name}: SUCCESS ({elapsed:.2f}s)")
        print(f"    Response: {res[:100]}...")
    except Exception as e:
        elapsed = time.time() - start
        print(f"[X] {provider_name}: FAILED ({elapsed:.2f}s)")
        print(f"    Error: {str(e)}")

async def main():
    print("=== IntellectSafe direct API Connectivity Test ===\n")
    council = LLMCouncil()
    
    # Test each provider sequentially for clarity
    for provider in LLMProvider:
        await test_provider(council, provider)
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())
