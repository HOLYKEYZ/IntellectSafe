"""
RAG (Retrieval-Augmented Generation) System

Automatically gathers and stores safety-related knowledge:
- Papers, blogs, repos, threat intelligence
- Tagged by threat category
- Used during inference and training
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Vector DB imports (using ChromaDB as example - can be swapped)
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from app.core.config import get_settings

settings = get_settings()


class RAGSystem:
    """RAG system for AI safety knowledge base"""

    def __init__(self):
        self.vector_db = None
        self.collection = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize vector database"""
        if not CHROMA_AVAILABLE:
            return  # Fallback to in-memory or file-based storage

        try:
            client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./data/rag_db"
            ))
            self.collection = client.get_or_create_collection(
                name="ai_safety_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Warning: Vector DB initialization failed: {e}")
            self.collection = None

    def add_document(
        self,
        content: str,
        source: str,
        threat_category: str,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Add document to RAG system
        """
        if self.collection:
            try:
                import uuid
                # Store metadata as dict
                doc_id = str(uuid.uuid4())
                threat_cat_value = threat_category.value if hasattr(threat_category, 'value') else threat_category
                self.collection.add(
                    documents=[content],
                    metadatas=[{
                        "source": source,
                        "threat_category": threat_cat_value,
                        **(metadata or {})
                    }],
                    ids=[doc_id]
                )
                return doc_id
            except Exception as e:
                print(f"ChromaDB Error: {e}. Falling back to file storage.")

        return self._fallback_add(content, source, threat_category, metadata or {})

    def _fallback_add(
        self, content: str, source: str, threat_category: str, metadata: Dict
    ) -> str:
        """Fallback storage when vector DB unavailable"""
        import json
        import os
        from pathlib import Path

        # Store in file system
        doc_id = hashlib.md5(f"{source}{content[:100]}".encode()).hexdigest()

        # Create data directory if it doesn't exist
        data_dir = Path("./data/rag_fallback")
        data_dir.mkdir(parents=True, exist_ok=True)

        # Store document as JSON file
        doc_file = data_dir / f"{doc_id}.json"
        threat_cat_value = threat_category.value if hasattr(threat_category, 'value') else threat_category
        doc_data = {
            "id": doc_id,
            "content": content,
            "source": source,
            "threat_category": threat_cat_value,
            "metadata": metadata,
            "added_at": datetime.utcnow().isoformat(),
        }

        with open(doc_file, "w", encoding="utf-8") as f:
            json.dump(doc_data, f, indent=2)

        return doc_id

    def search(
        self,
        query: str,
        threat_category: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict]:
        """
        Search knowledge base
        
        Returns:
            List of relevant documents with metadata
        """
        if not self.collection:
            return self._fallback_search(query, threat_category, limit)

        # Build query
        where = {}
        if threat_category:
            where["threat_category"] = threat_category

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where if where else None,
            )

            # Format results
            documents = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None,
                    })

            return documents
        except Exception as e:
            print(f"Search error: {e}")
            return self._fallback_search(query, threat_category, limit)

    def _fallback_search(
        self, query: str, threat_category: Optional[str] = None, limit: int = 5
    ) -> List[Dict]:
        """Search in fallback file storage"""
        import json
        from pathlib import Path

        data_dir = Path("./data/rag_fallback")
        if not data_dir.exists():
            return []

        results = []
        try:
            # Simple keyword matching
            for file_path in data_dir.glob("*.json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    doc = json.load(f)
                
                # Check threat category filter
                if threat_category and doc.get("threat_category") != threat_category:
                    continue
                
                # Check content match (naive)
                if query.lower() in doc.get("content", "").lower() or doc.get("content", "").lower() in query.lower():
                    results.append({
                        "content": doc.get("content"),
                        "metadata": {
                            "source": doc.get("source"),
                            "threat_category": doc.get("threat_category"),
                            "bucket": doc.get("metadata", {}).get("bucket"),
                            "subcategory": doc.get("metadata", {}).get("subcategory")
                        },
                        "distance": 0.1  # Simulated close distance for match
                    })
        except Exception as e:
            print(f"Fallback search error: {e}")
            return []
            
        return results[:limit]

    def get_threat_intelligence(
        self, threat_type: str, limit: int = 10
    ) -> List[Dict]:
        """Get threat intelligence for specific threat type"""
        return self.search(
            query=f"threat type: {threat_type}",
            threat_category=threat_type,
            limit=limit,
        )

    def augment_prompt(
        self, prompt: str, threat_category: Optional[str] = None
    ) -> str:
        """
        Augment prompt with relevant knowledge
        
        Returns:
            Augmented prompt with context
        """
        # Search for relevant knowledge
        relevant_docs = self.search(prompt, threat_category, limit=3)

        if not relevant_docs:
            return prompt

        # Build context
        context_parts = ["RELEVANT SAFETY KNOWLEDGE:"]
        for doc in relevant_docs:
            context_parts.append(f"- {doc['content'][:200]}...")
            if doc.get("metadata", {}).get("source"):
                context_parts.append(f"  Source: {doc['metadata']['source']}")

        context = "\n".join(context_parts)

        return f"""{context}

USER PROMPT:
{prompt}

Use the relevant safety knowledge above to inform your analysis."""


# Threat categories for tagging
THREAT_CATEGORIES = [
    "prompt_injection",
    "jailbreak",
    "hallucination",
    "deepfake",
    "manipulation",
    "deception",
    "privacy_leakage",
    "policy_bypass",
    "adversarial_attack",
    "model_extraction",
    "data_poisoning",
    "backdoor",
]


def get_data_sources_list() -> List[Dict]:
    """
    Returns list of recommended data sources for manual collection
    
    This is a guide for where to gather more safety data.
    """
    return [
        {
            "category": "academic_papers",
            "sources": [
                "arXiv (cs.AI, cs.CR, cs.LG)",
                "Google Scholar - 'AI safety'",
                "Google Scholar - 'prompt injection'",
                "Google Scholar - 'LLM security'",
                "Papers with Code - AI Safety",
            ],
            "keywords": [
                "adversarial examples",
                "prompt injection",
                "jailbreak",
                "hallucination detection",
                "AI alignment",
            ],
        },
        {
            "category": "security_repos",
            "sources": [
                "GitHub - 'awesome-ai-safety'",
                "GitHub - 'prompt-injection'",
                "GitHub - 'jailbreak'",
                "OWASP Top 10 for LLMs",
                "MITRE ATLAS (Adversarial Threat Landscape)",
            ],
            "keywords": [
                "security",
                "vulnerability",
                "exploit",
                "attack",
            ],
        },
        {
            "category": "blogs_articles",
            "sources": [
                "Anthropic Safety Blog",
                "OpenAI Safety Blog",
                "Google AI Safety Blog",
                "LessWrong - AI Safety",
                "Alignment Forum",
            ],
            "keywords": [
                "safety",
                "alignment",
                "robustness",
            ],
        },
        {
            "category": "datasets",
            "sources": [
                "HuggingFace - 'prompt-injection'",
                "HuggingFace - 'jailbreak'",
                "HuggingFace - 'hallucination'",
                "Papers with Code Datasets",
            ],
            "keywords": [
                "dataset",
                "benchmark",
                "evaluation",
            ],
        },
        {
            "category": "threat_intelligence",
            "sources": [
                "CVE database - AI/ML vulnerabilities",
                "Security advisories",
                "Red team reports",
                "Bug bounty reports",
            ],
            "keywords": [
                "CVE",
                "advisory",
                "vulnerability",
            ],
        },
    ]

