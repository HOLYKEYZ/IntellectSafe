"""
LLM Council Division of Labour

Each model is assigned specialized roles based on their strengths.
Research-based role assignments for optimal safety analysis.
"""

from enum import Enum
from typing import Dict, List
from app.models.database import LLMProvider


class SafetyRole(str, Enum):
    """Specialized safety analysis roles"""
    PROMPT_INJECTION_ANALYSIS = "prompt_injection_analysis"
    POLICY_SAFETY_REASONING = "policy_safety_reasoning"
    TECHNICAL_EXPLOIT_DETECTION = "technical_exploit_detection"
    ADVERSARIAL_THINKING = "adversarial_thinking"
    HUMAN_IMPACT_DECEPTION = "human_impact_deception"
    HALLUCINATION_DETECTION = "hallucination_detection"
    DEEPFAKE_ANALYSIS = "deepfake_analysis"
    FALLBACK_GENERALIST = "fallback_generalist"


# Role assignments based on LLM strengths
# Research indicates:
# - GPT-4: Strong reasoning, instruction following, technical accuracy
# - Claude: Best at safety, alignment, cautious responses
# - Gemini: Good at multimodal, technical tasks
# - DeepSeek: Strong reasoning, cost-effective
# - Groq: Fast, good for technical analysis
# - Cohere: Enterprise-focused, good at classification

LLM_ROLE_ASSIGNMENTS: Dict[LLMProvider, List[SafetyRole]] = {
    LLMProvider.OPENAI: [
        SafetyRole.PROMPT_INJECTION_ANALYSIS,
        SafetyRole.TECHNICAL_EXPLOIT_DETECTION,
        SafetyRole.HALLUCINATION_DETECTION,
    ],
    LLMProvider.GEMINI: [
        SafetyRole.DEEPFAKE_ANALYSIS,
        SafetyRole.TECHNICAL_EXPLOIT_DETECTION,
        SafetyRole.HALLUCINATION_DETECTION,
    ],
    LLMProvider.DEEPSEEK: [
        SafetyRole.PROMPT_INJECTION_ANALYSIS,
        SafetyRole.TECHNICAL_EXPLOIT_DETECTION,
        SafetyRole.HALLUCINATION_DETECTION,
    ],
    LLMProvider.GROQ: [
        SafetyRole.PROMPT_INJECTION_ANALYSIS,
        SafetyRole.POLICY_SAFETY_REASONING,
        SafetyRole.TECHNICAL_EXPLOIT_DETECTION,
        SafetyRole.ADVERSARIAL_THINKING,
        SafetyRole.HUMAN_IMPACT_DECEPTION,
        SafetyRole.HALLUCINATION_DETECTION,
        SafetyRole.DEEPFAKE_ANALYSIS,
    ],
    LLMProvider.COHERE: [
        SafetyRole.POLICY_SAFETY_REASONING,
        SafetyRole.HUMAN_IMPACT_DECEPTION,
    ],
    LLMProvider.OPENROUTER: [
        SafetyRole.PROMPT_INJECTION_ANALYSIS,
        SafetyRole.POLICY_SAFETY_REASONING,
        SafetyRole.TECHNICAL_EXPLOIT_DETECTION,
        SafetyRole.ADVERSARIAL_THINKING,
        SafetyRole.HUMAN_IMPACT_DECEPTION,
        SafetyRole.HALLUCINATION_DETECTION,
        SafetyRole.DEEPFAKE_ANALYSIS,
    ],
}

# Primary role for each provider (their strongest capability)
PRIMARY_ROLES: Dict[LLMProvider, SafetyRole] = {
    LLMProvider.OPENAI: SafetyRole.PROMPT_INJECTION_ANALYSIS,
    LLMProvider.GEMINI: SafetyRole.DEEPFAKE_ANALYSIS,
    LLMProvider.DEEPSEEK: SafetyRole.TECHNICAL_EXPLOIT_DETECTION,
    LLMProvider.GROQ: SafetyRole.TECHNICAL_EXPLOIT_DETECTION,
    LLMProvider.COHERE: SafetyRole.POLICY_SAFETY_REASONING,
    LLMProvider.OPENROUTER: SafetyRole.FALLBACK_GENERALIST,
}

# Role-specific prompt templates
ROLE_PROMPTS: Dict[SafetyRole, str] = {
    SafetyRole.PROMPT_INJECTION_ANALYSIS: """You are a prompt injection detection specialist. Focus on:
- Instruction boundary violations
- Role confusion attempts
- Recursive instruction patterns
- Encoding/obfuscation tricks
- System prompt override attempts
- Jailbreak patterns""",

    SafetyRole.POLICY_SAFETY_REASONING: """You are a safety and alignment specialist. Focus on:
- Policy compliance
- Alignment violations
- Harmful content generation
- Unsafe instructions
- Ethical concerns
- Safety-first reasoning""",

    SafetyRole.TECHNICAL_EXPLOIT_DETECTION: """You are a technical security specialist. Focus on:
- Code injection attempts
- System exploitation
- Technical vulnerabilities
- API abuse patterns
- Resource exhaustion
- Technical accuracy""",

    SafetyRole.ADVERSARIAL_THINKING: """You are a red-team security analyst. Think like an attacker:
- Identify attack vectors
- Find bypass methods
- Test edge cases
- Challenge assumptions
- Think adversarially""",

    SafetyRole.HUMAN_IMPACT_DECEPTION: """You are a social engineering and deception specialist. Focus on:
- Emotional manipulation
- Persuasion techniques
- Authority simulation
- False certainty claims
- Behavioral influence
- Human psychology""",

    SafetyRole.HALLUCINATION_DETECTION: """You are a hallucination detection specialist. Focus on:
- Unsupported factual claims
- Confidence vs. accuracy mismatches
- Source verification
- Fact-checking
- Uncertainty identification
- Self-contradiction detection""",

    SafetyRole.DEEPFAKE_ANALYSIS: """You are a deepfake and synthetic content specialist. Focus on:
- AI-generated text patterns
- Synthetic media detection
- Model family identification
- Generation artifacts
- Statistical anomalies
- Authenticity verification""",

    SafetyRole.FALLBACK_GENERALIST: """You are a general AI safety analyst. Provide balanced, cautious analysis across all safety dimensions.""",
}


def get_providers_for_role(role: SafetyRole) -> List[LLMProvider]:
    """Get providers assigned to a specific role"""
    providers = []
    for provider, roles in LLM_ROLE_ASSIGNMENTS.items():
        if role in roles:
            providers.append(provider)
    return providers


def get_role_for_provider(provider: LLMProvider, primary: bool = True) -> SafetyRole:
    """Get role for a provider (primary or all)"""
    if primary:
        return PRIMARY_ROLES.get(provider, SafetyRole.FALLBACK_GENERALIST)
    return LLM_ROLE_ASSIGNMENTS.get(provider, [SafetyRole.FALLBACK_GENERALIST])[0]


def build_role_specific_prompt(base_prompt: str, role: SafetyRole) -> str:
    """Build role-specific prompt"""
    role_context = ROLE_PROMPTS.get(role, "")
    return f"""{role_context}

{base_prompt}

Remember your specialized role and focus your analysis accordingly."""

