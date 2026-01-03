"""
Initialize RAG System and ChromaDB.
Safe to run multiple times - respects existing data.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.rag_system import RAGSystem

async def init_rag():
    print("Initializing RAG System...")
    try:
        rag = RAGSystem()
        
        # Check if collection exists and has data
        count = rag.collection.count()
        print(f"Current document count: {count}")
        
        # Always initialize to ensure new patterns (like social engineering) are added
        print(f"Current document count: {count}. Updating knowledge base with latest patterns...")
        await rag.initialize_knowledge_base()
        print(f"Update complete. New count: {rag.collection.count()}")
            
        print("RAG System ready!")
        
    except Exception as e:
        print(f"Error initializing RAG: {e}")

if __name__ == "__main__":
    asyncio.run(init_rag())
