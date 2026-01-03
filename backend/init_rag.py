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
        
        if count == 0:
            print("Database is empty. Populating with initial knowledge base...")
            await rag.initialize_knowledge_base()
            print(f"Population complete. New count: {rag.collection.count()}")
        else:
            print("Database already contains data. Skipping initialization to preserve data.")
            
        print("RAG System ready!")
        
    except Exception as e:
        print(f"Error initializing RAG: {e}")

if __name__ == "__main__":
    asyncio.run(init_rag())
