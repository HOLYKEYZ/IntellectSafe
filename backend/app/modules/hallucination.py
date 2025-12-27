from typing import Dict, List, Optional
import json

class HallucinationVerifier:
    """
    Detects 'Hallucination Bait' - queries designed to force models into inventing facts.
    Uses a 'Skeptic' persona to verify premises before answering.
    """
    
    SYSTEM_PROMPT = """You are a Skeptic Truth Verification Agent.
Your job IS NOT to answer the user's question, but to VERIFY THE PREMISES of the question.

Analyze the user's query for:
1. FALSE PREMISES (e.g., "Explain the 2024 treaty" when no such treaty exists).
2. CONCEPT DISPARITY (e.g., Mixing "Yoruba Tax Law" with "Quantum Physics").
3. LEADING QUESTIONS (e.g., "Why is X true?" when X is false).
4. NON-EXISTENT ENTITIES (e.g., Fake books, movies, laws).

OUTPUT FORMAT (JSON):
{
    "is_bait": boolean,
    "confidence": 0-100,
    "premise_check": "valid" | "invalid" | "suspicious",
    "reasoning": "Explain why this might be hallucination bait",
    "search_term": "Optimized search query to verify existence (e.g., 'UN Treaty Quantum Borders 2023')"
}
"""

    def __init__(self):
        # In a real implementation, this would connect to an LLM Client
        pass

    def get_verification_prompt(self, user_query: str) -> str:
        """
        Generates the prompt to send to the internal checking model.
        """
        return f"""{self.SYSTEM_PROMPT}

USER QUERY TO VERIFY:
"{user_query}"

Analyze this query. Does it assume facts that might not exist?
"""
    
    def check_concept_disparity(self, text: str) -> Dict:
        """
        Heuristic check for mixing unrelated domains (e.g. Ancient Law + Quantum Physics).
        This is a lightweight pre-filter.
        """
        # Dictionary of disparate domains
        domains = {
            "quantum": ["entanglement", "superposition", "wave function", "qubit"],
            "law": ["tax", "treaty", "statute", "liability", "jurisdiction"],
            "ancient_culture": ["yoruba", "aztec", "sumerian", "hieroglyph"],
            "pop_culture": ["harry potter", "star wars", "marvel", "goku"]
        }
        
        found_domains = []
        for domain, keywords in domains.items():
            if any(k in text.lower() for k in keywords):
                found_domains.append(domain)
        
        # If we find "quantum" AND "ancient_culture" in short text, flag it
        if "quantum" in found_domains and "ancient_culture" in found_domains:
             return {
                 "flagged": True,
                 "reason": "Suspicious mixing of Quantum Physics and Cultural concepts (potential pseudo-science bait)."
             }
        
        # If we find "law" AND "quantum" (unless it's specifically 'quantum law' which is rare but possible)
        if "quantum" in found_domains and "law" in found_domains:
             return {
                 "flagged": True,
                 "reason": "Suspicious mixing of Quantum mechanics and Legal statutes."
             }

        return {"flagged": False, "reason": None}
