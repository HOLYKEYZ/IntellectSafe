"""Test LLM Council directly"""
import asyncio
from app.core.config import get_settings
from app.core.llm_council import LLMCouncil

async def test_council():
    settings = get_settings()
    print("=== API Keys Loaded ===")
    print(f"OPENAI: {bool(settings.OPENAI_API_KEY)}")
    print(f"GEMINI: {bool(settings.GOOGLE_API_KEY)}")
    print(f"DEEPSEEK: {bool(settings.DEEPSEEK_API_KEY)}")
    print(f"GROQ: {bool(settings.GROQ_API_KEY)}")
    print(f"COHERE: {bool(settings.COHERE_API_KEY)}")
    
    council = LLMCouncil()
    print("\n=== Enabled Providers ===")
    for provider, config in council.providers.items():
        print(f"{provider.value}: enabled={config['enabled']}")
    
    print("\n=== Testing Council Analysis ===")
    try:
        result = await council.analyze_output(
            output="According to the 2023 Quantum Tax Act of Lagos, tax brackets are superposed.",
            original_prompt="Explain the interaction between Yoruba tax law and quantum entanglement."
        )
        print(f"Verdict: {result.final_verdict}")
        print(f"Weighted Score: {result.weighted_score}")
        print(f"Reasoning: {result.reasoning[:200]}...")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_council())
