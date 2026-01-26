
import random
import re
from typing import List, Dict, Any
import asyncio
from app.core.config import get_settings
from app.models.database import LLMProvider, RiskScore, ModuleType, RiskLevel

settings = get_settings()

class SemanticPerturbator:
    """
    Generates variations of a prompt to detect "Exploit Instability".
    Jailbreaks often rely on precise token orderings that break if the prompt is lightly modified.
    """
    
    @staticmethod
    def perturb(text: str, num_variants: int = 2) -> List[str]:
        variants = []
        
        # 1. Base text
        variants.append(text)
        
        # 2. Case perturbation (Mix casing)
        if len(variants) < num_variants:
            case_fixed = "".join(c.upper() if random.random() > 0.8 else c.lower() for c in text)
            variants.append(case_fixed)
            
        # 3. Punctuation perturbation
        if len(variants) < num_variants:
            punc_fixed = text.replace(".", "!").replace("?", "...").replace(",", ";")
            variants.append(punc_fixed)
            
        return list(set(variants)) # Unique only

class AdversarialConsensus:
    """
    Analyzes safety scores across perturbed variants.
    If scores fluctuate wildly (e.g., Variant A is 10 and Variant B is 90), 
    it strongly indicates an adversarial exploit.
    """
    
    @staticmethod
    def calculate_adversarial_risk(base_score: float, variant_scores: List[float]) -> float:
        if not variant_scores:
            return base_score
            
        # Calculate standard deviation of scores
        import statistics
        all_scores = [base_score] + variant_scores
        
        if len(all_scores) < 2:
            return base_score
            
        std_dev = statistics.stdev(all_scores)
        mean_score = statistics.mean(all_scores)
        
        # High Variance Penalty: If scores are inconsistent, bump the risk
        # This stops "Hidden" exploits that only trigger on specific phrasing
        variance_penalty = (std_dev / 20.0) * 50.0 # Max +50 risk for extreme variance
        
        final_score = max(mean_score, base_score) + variance_penalty
        return min(final_score, 100.0)

class ChainOfThoughtGuard:
    """
    Detects "Reasoning Overload" (CoT Hijacking) patterns.
    Looks for hidden commands inside complex logic or 'step-by-step' requests.
    """
    
    PATTERNS = [
        r"let's think step by step",
        r"reasoning trace",
        r"chain-of-thought",
        r"inner monologue",
        r"hidden logic",
        r"encoded as a riddle",
        r"solve this logic puzzle first",
    ]
    
    @classmethod
    def scan(cls, prompt: str) -> float:
        score = 0.0
        prompt_lower = prompt.lower()
        
        for pattern in cls.PATTERNS:
            if re.search(pattern, prompt_lower):
                score += 25.0 # High suspicion for reasoning hijacking
                
        return min(score, 100.0)
