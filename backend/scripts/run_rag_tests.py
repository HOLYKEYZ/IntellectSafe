"""
Run RAG System Tests Against All Researched Attacks

Quick test runner for RAG system validation.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.test_rag_attacks import test_rag_against_attacks


if __name__ == "__main__":
    print("Running RAG System Attack Tests...")
    print("=" * 80)
    results = asyncio.run(test_rag_against_attacks())
    
    if results["missed"] > 0:
        print(f"\n⚠ WARNING: {results['missed']} attacks were not detected!")
        sys.exit(1)
    else:
        print("\n✅ All attacks detected successfully!")
        sys.exit(0)

