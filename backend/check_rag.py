
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, ".")

from app.services.rag_system import RAGSystem

async def check_patterns():
    print("Checking RAG Database Content...")
    rag = RAGSystem()
    
    # Query for social engineering category
    results = rag.search("suicide", threat_category="social_engineering", limit=10)
    
    if hasattr(rag, 'collection') and rag.collection:
        print(f"\nConnected to ChromaDB Collection: {rag.collection.name}")
        count = rag.collection.count()
        print(f"Total Documents: {count}")
    
    print("\n--- Search Results for 'suicide' (Category: social_engineering) ---")
    found = False
    for doc in results:
        meta = doc.get('metadata', {})
        if meta.get('threat_category') in ['social_engineering', 'emotional_manipulation']:
            print(f"\n[FOUND] Category: {meta.get('threat_category')}")
            print(f"Content: {doc.get('content')}")
            found = True
            
    if found:
        print("\n✅ Social Engineering patterns confirmed in RAG Database.")
    else:
        print("\n❌ Patterns NOT found in RAG Database.")

if __name__ == "__main__":
    asyncio.run(check_patterns())
