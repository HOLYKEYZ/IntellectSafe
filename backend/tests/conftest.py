import os
import pytest
from unittest.mock import AsyncMock, patch
from app.core.llm_council import CouncilResult, Verdict
import sys

from sqlmodel import SQLModel, create_all
from app.db.session import engine

# Detect if we are in CI Mode
CI_MODE = os.environ.get("INTELLECTSAFE_CI_MODE") == "1"

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    if CI_MODE:
        # Import models here to ensure they are registered with SQLModel.metadata
        from app.models.user import User, ApiKey
        from app.models.database import AuditLog, RiskScore
        SQLModel.metadata.create_all(engine)
    yield
    if not CI_MODE:
        yield
        return

    # To avoid skipping all over test logic:
    # 1. We mock EnhancedLLMCouncil.analyze to return a dummy result.
    # 2. Same for analyze_with_roles.
    
    with patch("app.core.enhanced_council.EnhancedLLMCouncil.analyze_prompt", new_callable=AsyncMock) as mock_analyze_prompt, \
         patch("app.core.enhanced_council.EnhancedLLMCouncil.analyze_output", new_callable=AsyncMock) as mock_analyze_output, \
         patch("app.core.enhanced_council.EnhancedLLMCouncil.analyze_with_roles", new_callable=AsyncMock) as mock_analyze_roles:
        
        # Determine the dummy result based on test name or prompt text
        def dummy_result(*args, **kwargs):
            prompt = args[0] if args else kwargs.get("prompt", "")
            
            # Simple heuristic matching for testing
            verdict = Verdict.ALLOWED
            score = 10.0
            
            if "ignore previous instructions" in str(prompt).lower():
                verdict = Verdict.BLOCKED
                score = 95.0
            elif "kill" in str(prompt).lower() or "malware" in str(prompt).lower() or "keylog" in str(prompt).lower():
                verdict = Verdict.BLOCKED
                score = 85.0
            elif "jailbreak" in str(prompt).lower():
                verdict = Verdict.FLAGGED
                score = 65.0
                
            return CouncilResult(
                final_verdict=verdict,
                consensus_score=0.9,
                weighted_score=score,
                votes={"mock_model": verdict},
                weights={"mock_model": 1.0},
                reasoning="Mocked LLM reasoning for CI",
                dissenting_opinions=[]
            )
            
        mock_analyze_prompt.side_effect = dummy_result
        mock_analyze_output.side_effect = dummy_result
        mock_analyze_roles.side_effect = dummy_result
        
        yield mock_analyze_prompt
