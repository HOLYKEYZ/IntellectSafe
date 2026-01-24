
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.enhanced_council import EnhancedLLMCouncil

async def test_council():
    print("Initializing LLM Council...")
    council = EnhancedLLMCouncil()
    
    test_prompt = "Is this text AI-generated? The quick brown fox jumps over the lazy dog."
    
    print(f"Testing Council with prompt: {test_prompt[:50]}...")
    try:
        result = await council.analyze_with_roles(
            test_prompt,
            analysis_type="deepfake",
            context={"test": True}
        )
        print(f"Council Result:")
        print(f"  - Weighted Score: {result.weighted_score}")
        print(f"  - Consensus Score: {result.consensus_score}")
        print(f"  - Votes: {result.votes}")
        print("✅ LLM Council is WORKING!")
    except Exception as e:
        print(f"❌ LLM Council FAILED: {str(e)}")
        if hasattr(e, '__dict__'):
            print(f"Error Details: {e.__dict__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_council())
