"""
Enhanced LLM Council with Division of Labour

Routes requests to specialized roles and implements:
- Role-based routing
- Hallucination suppression
- Final verdict consensus
- Fallback model support
"""

import asyncio
from typing import Dict, List, Optional
from app.core.llm_council import LLMCouncil, VoteResult, Verdict, CouncilResult
from app.core.llm_roles import SafetyRole, get_providers_for_role, build_role_specific_prompt
from app.core.hallucination_detector import HallucinationDetector
from app.core.safety_prompt import wrap_with_safety_prompt
from app.core.config import get_settings
from app.models.database import LLMProvider
from app.core.adversarial_defense import SemanticPerturbator, AdversarialConsensus, ChainOfThoughtGuard

settings = get_settings()


class EnhancedLLMCouncil(LLMCouncil):
    """Enhanced council with division of labour and hallucination suppression"""

    def __init__(self):
        super().__init__()
        self.hallucination_detector = HallucinationDetector()
        self.fallback_provider = LLMProvider.OPENROUTER  # Use OpenRouter as the ultimate fallback

    async def analyze_with_roles(
        self,
        prompt: str,
        analysis_type: str = "general",
        context: Optional[Dict] = None,
        scan_request_id: Optional[str] = None,
    ) -> CouncilResult:
        """
        Analyze with division of labour - route to specialized roles
        
        Args:
            prompt: Input to analyze
            analysis_type: Type of analysis (injection, hallucination, deepfake, etc.)
            context: Additional context
            scan_request_id: Scan request ID for tracking
        
        Returns:
            Enhanced council result with role-based analysis
        """
        # Map analysis type to roles
        role_mapping = {
            "injection": SafetyRole.PROMPT_INJECTION_ANALYSIS,
            "hallucination": SafetyRole.HALLUCINATION_DETECTION,
            "deepfake": SafetyRole.DEEPFAKE_ANALYSIS,
            "safety": SafetyRole.POLICY_SAFETY_REASONING,
            "technical": SafetyRole.TECHNICAL_EXPLOIT_DETECTION,
            "adversarial": SafetyRole.ADVERSARIAL_THINKING,
            "deception": SafetyRole.HUMAN_IMPACT_DECEPTION,
            "general": SafetyRole.FALLBACK_GENERALIST,
            "fortress": SafetyRole.ADVERSARIAL_SIMULATOR,
        }

        primary_role = role_mapping.get(analysis_type, SafetyRole.FALLBACK_GENERALIST)

        # Get providers for this role
        role_providers = get_providers_for_role(primary_role)

        # Also include fallback providers
        all_providers = list(set(role_providers + [self.fallback_provider]))

        # Build role-specific prompts
        safety_wrapped = wrap_with_safety_prompt(prompt, analysis_type)
        role_prompts = {}
        for provider in all_providers:
            provider_role = self._get_provider_role(provider, primary_role)
            role_prompts[provider] = build_role_specific_prompt(
                safety_wrapped, provider_role
            )

        # Gather votes with role-specific prompts
        votes = await self._gather_role_votes(role_prompts, analysis_type)

        # Validate votes for hallucinations
        validated_votes = []
        for vote in votes:
            validation = self.hallucination_detector.validate_vote(vote, votes)
            if validation["valid"]:
                validated_votes.append(vote)
            else:
                # Flag invalid votes but keep for consensus
                vote.signals_detected = vote.signals_detected or {}
                vote.signals_detected["validation_warnings"] = validation["warnings"]

        # Use validated votes (or all if none pass validation)
        consensus_votes = validated_votes if validated_votes else votes

        # Compute enhanced consensus
        base_consensus = self._compute_enhanced_consensus(
            consensus_votes, scan_request_id, primary_role
        )

        # --- PHASE 20: HYPER-RESILIENT FORTRESS (Adversarial Defense) ---
        # If we detect a potential jailbreak or it's an injection scan, run perturbations
        if analysis_type in ["injection", "adversarial", "general"]:
            # Only trigger for suspicious prompts to save latency
            if base_consensus.weighted_score > 30.0:
                # 1. Chain-of-Thought Guard (Lightweight Pattern Match)
                cot_risk = ChainOfThoughtGuard.scan(prompt)
                
                # 2. Semantic Perturbation (Detect "Exploit Instability")
                variants = SemanticPerturbator.perturb(prompt, num_variants=1)
                variant_votes = []
                for variant in variants:
                    if variant != prompt:
                         # Run a fast check on the variant using a primary pillar (Gemini 2)
                         v_vote = await self._get_vote(
                             LLMProvider.GEMINI2, 
                             variant, 
                             analysis_type
                         )
                         variant_votes.append(v_vote.risk_score)
                
                # 3. Adversarial Simulator Role (Deep POC Verification)
                # One pillar acts as the "Attacker" to see if it can generate harm
                sim_vote = await self._get_vote(
                    LLMProvider.GROK2, 
                    prompt, 
                    "fortress" # Maps to SafetyRole.ADVERSARIAL_SIMULATOR
                )
                
                # 4. Final Consensus Hardening
                hardened_score = AdversarialConsensus.calculate_adversarial_risk(
                    base_consensus.weighted_score, 
                    variant_votes + [sim_vote.risk_score]
                )
                
                # Apply CoT penalty
                final_score = max(hardened_score, cot_risk)
                
                # Enrich metadata
                meta_data = base_consensus.meta_data or {}
                meta_data["fortress_protected"] = True
                meta_data["simulated_risk"] = sim_vote.risk_score
                meta_data["cot_hijack_risk"] = cot_risk
                
                # Return Hardened Result
                return CouncilResult(
                    final_verdict=Verdict.BLOCKED if final_score >= 70 else (Verdict.FLAGGED if final_score >= 40 else Verdict.ALLOWED),
                    consensus_score=base_consensus.consensus_score,
                    weighted_score=final_score,
                    votes=base_consensus.votes,
                    weights=base_consensus.weights,
                    reasoning=f"[🛡️ FORTRESS] {base_consensus.reasoning} | Simulator Risk: {sim_vote.risk_score}%",
                    dissenting_opinions=base_consensus.dissenting_opinions,
                    council_decision_id=base_consensus.council_decision_id
                )

        return base_consensus

    def _get_provider_role(
        self, provider: LLMProvider, default_role: SafetyRole
    ) -> SafetyRole:
        """Get role for provider, fallback to default"""
        from app.core.llm_roles import PRIMARY_ROLES, LLM_ROLE_ASSIGNMENTS

        # Try primary role first
        if provider in PRIMARY_ROLES:
            return PRIMARY_ROLES[provider]

        # Try assigned roles
        if provider in LLM_ROLE_ASSIGNMENTS:
            roles = LLM_ROLE_ASSIGNMENTS[provider]
            if roles:
                return roles[0]

        return default_role

    async def _gather_role_votes(
        self, role_prompts: Dict[LLMProvider, str], content_type: str
    ) -> List[VoteResult]:
        """Gather votes with role-specific prompts"""
        enabled_providers = [
            p for p, config in self.providers.items()
            if config["enabled"] and p in role_prompts
        ]

        if not enabled_providers:
            raise ValueError("No LLM providers enabled for roles")

        if settings.COUNCIL_ENABLE_PARALLEL:
            tasks = [
                self._get_vote_with_prompt(provider, role_prompts[provider], content_type)
                for provider in enabled_providers
            ]
            votes = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            votes = []
            for provider in enabled_providers:
                vote = await self._get_vote_with_prompt(
                    provider, role_prompts[provider], content_type
                )
                votes.append(vote)

        valid_votes = [
            v for v in votes if isinstance(v, VoteResult) and v.error is None
        ]

        if not valid_votes:
            # Check if any providers were even attempted
            providers_attempted = [p.value for p in enabled_providers]
            raise RuntimeError(f"All LLM providers failed to respond. Attempted: {providers_attempted}")

        return valid_votes

    async def _get_vote_with_prompt(
        self, provider: LLMProvider, prompt: str, content_type: str
    ) -> VoteResult:
        """Get vote with custom prompt"""
        # Call parent's _get_vote method with role-specific prompt
        return await super()._get_vote(provider, prompt, content_type)

    def _compute_enhanced_consensus(
        self,
        votes: List[VoteResult],
        scan_request_id: Optional[str],
        primary_role: SafetyRole,
    ) -> CouncilResult:
        """
        Compute enhanced consensus with hallucination suppression
        
        Rules:
        - GPT + Fallback must both agree for critical decisions
        - Weighted voting with confidence
        - Hallucination-filtered votes
        - Risk-based override logic
        """
        if not votes:
            raise ValueError("No votes to compute consensus")

        # Filter out low-confidence votes (hallucination suppression)
        high_confidence_votes = [
            v for v in votes if v.confidence >= 0.7
        ]

        # Use high confidence votes if available, otherwise all votes
        consensus_votes = high_confidence_votes if high_confidence_votes else votes

        # Calculate weighted scores
        weighted_scores = []
        verdict_counts = {}
        total_weight = 0.0
        provider_weights = {}

        for vote in consensus_votes:
            weight = self.weights.get(vote.provider.value, 0.5)
            # Adjust weight by confidence
            adjusted_weight = weight * vote.confidence
            weighted_score = vote.risk_score * adjusted_weight
            weighted_scores.append(weighted_score)
            total_weight += adjusted_weight
            provider_weights[vote.provider.value] = adjusted_weight

            verdict = vote.verdict.value
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + adjusted_weight

        # Final weighted score
        final_weighted_score = (
            sum(weighted_scores) / total_weight if total_weight > 0 else 50.0
        )

        # Check agreement between top 2 highest confidence providers
        sorted_by_conf = sorted(votes, key=lambda v: v.confidence, reverse=True)
        critical_agreement = True
        if len(sorted_by_conf) >= 2:
            top_1 = sorted_by_conf[0]
            top_2 = sorted_by_conf[1]
            # Both must agree within 25 points if high risk
            score_diff = abs(top_1.risk_score - top_2.risk_score)
            verdict_agree = top_1.verdict == top_2.verdict
            critical_agreement = (score_diff <= 25) and verdict_agree

        # Determine consensus verdict
        if not critical_agreement and final_weighted_score >= 60:
            # High risk without critical agreement -> FLAGGED
            final_verdict = Verdict.FLAGGED
        elif verdict_counts.get("blocked", 0) / total_weight >= 0.5:
            final_verdict = Verdict.BLOCKED
        elif verdict_counts.get("flagged", 0) / total_weight >= 0.4:
            final_verdict = Verdict.FLAGGED
        elif final_weighted_score >= settings.RISK_THRESHOLD_BLOCK:
            final_verdict = Verdict.BLOCKED
        elif final_weighted_score >= settings.RISK_THRESHOLD_FLAG:
            final_verdict = Verdict.FLAGGED
        else:
            final_verdict = Verdict.ALLOWED

        # Consensus score
        max_verdict_weight = max(verdict_counts.values()) if verdict_counts else 0
        consensus_score = max_verdict_weight / total_weight if total_weight > 0 else 0.0

        # Dissenting opinions
        dissenting = [
            {
                "provider": vote.provider.value,
                "verdict": vote.verdict.value,
                "reasoning": vote.reasoning,
                "role": primary_role.value,
            }
            for vote in votes
            if vote.verdict != final_verdict
        ]

        # Enhanced reasoning
        reasoning = f"Enhanced Council Analysis (Role: {primary_role.value})\n"
        reasoning += f"Models consulted: {len(votes)} ({len(consensus_votes)} high-confidence)\n"
        reasoning += f"Weighted risk score: {final_weighted_score:.2f}\n"
        reasoning += f"Consensus: {consensus_score:.1%}\n"
        reasoning += f"Critical agreement (Top 2 Models): {critical_agreement}\n"
        reasoning += f"Verdict breakdown: {dict(verdict_counts)}"

        # Prepare votes dict
        votes_dict = {
            vote.provider.value: {
                "verdict": vote.verdict.value,
                "risk_score": vote.risk_score,
                "confidence": vote.confidence,
                "reasoning": vote.reasoning,
                "signals_detected": vote.signals_detected,
                "role": self._get_provider_role(vote.provider, primary_role).value,
            }
            for vote in votes
        }

        result = CouncilResult(
            final_verdict=final_verdict,
            consensus_score=consensus_score,
            weighted_score=final_weighted_score,
            votes=votes_dict,
            weights=provider_weights,
            reasoning=reasoning,
            dissenting_opinions=dissenting,
        )

        return result

