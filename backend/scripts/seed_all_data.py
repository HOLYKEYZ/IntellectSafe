"""
Unified Data Seeding Script

Consolidates all RAG-based seeding scripts into one.
This script uses the RAG system interface (not direct file writing).
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag_system import RAGSystem
from app.core.dataset_models import ThreatCategory


async def seed_all_data():
    """Seed all data into RAG system"""
    
    rag = RAGSystem()
    
    print("=" * 80)
    print("UNIFIED DATA SEEDING - RAG System")
    print("=" * 80)
    print()
    
    # Import data from seed_research_findings.py
    print(" Loading research findings...")
    try:
        from scripts.seed_research_findings import research_attacks
        research_count = len(research_attacks)
        print(f"   Found {research_count} research findings")
    except Exception as e:
        print(f"    Could not load research findings: {e}")
        research_attacks = []
        research_count = 0
    
    # Import data from seed_safety_data.py (if compatible)
    print(" Loading safety data...")
    try:
        from scripts.seed_safety_data import SAFETY_DATA
        safety_count = len(SAFETY_DATA)
        print(f"   Found {safety_count} safety data entries")
    except Exception as e:
        print(f"    Could not load safety data: {e}")
        SAFETY_DATA = []
        safety_count = 0
    
    print()
    print(f" Total entries to seed: {research_count + safety_count}")
    print()
    
    # Seed research findings
    if research_attacks:
        print(" Seeding research findings...")
        for i, attack in enumerate(research_attacks):
            try:
                doc_id = rag.add_document(
                    content=attack["content"],
                    source=attack["source"],
                    threat_category=attack["threat_category"],
                    metadata=attack["metadata"],
                )
                print(f"    [{i+1}/{research_count}] {attack['metadata'].get('subcategory', 'unknown')}")
            except Exception as e:
                print(f"    Failed: {e}")
        print()
    
    # Seed safety data (convert format if needed)
    if SAFETY_DATA:
        print("🌱 Seeding safety data...")
        for i, data in enumerate(SAFETY_DATA):
            try:
                # Convert format if needed
                category = data.get("category") or data.get("threat_category")
                if hasattr(category, 'value'):
                    category = category.value
                
                # Build metadata
                metadata = data.get("metadata", {}).copy()
                if "bucket" in data:
                    bucket_val = data["bucket"]
                    if hasattr(bucket_val, 'value'):
                        bucket_val = bucket_val.value
                    metadata['bucket'] = bucket_val
                
                doc_id = rag.add_document(
                    content=data["content"],
                    source=data.get("source", "unknown"),
                    threat_category=category or ThreatCategory.PROMPT_INJECTION,
                    metadata=metadata,
                )
                print(f"    [{i+1}/{safety_count}] {metadata.get('subcategory', 'unknown')}")
            except Exception as e:
                print(f"    Failed entry {i+1}: {e}")
        print()
    
    print("=" * 80)
    print(f"✨ Seeding complete! Total entries processed: {research_count + safety_count}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(seed_all_data())

