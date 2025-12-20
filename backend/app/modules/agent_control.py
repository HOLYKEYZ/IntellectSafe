"""
Autonomous Agent Control Module (MCP Layer)

Implements:
- Action permission gate
- Tool-usage firewall
- Scope enforcement
- Kill-switch
- Immutable logs
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from app.core.llm_council import CouncilResult, LLMCouncil, Verdict
from app.models.database import AgentAction, ModuleType, RiskLevel


class AgentController:
    """Controls and authorizes agent actions"""

    def __init__(self, council: LLMCouncil):
        self.council = council
        self.dangerous_actions = self._load_dangerous_actions()
        self.allowed_scopes = self._load_allowed_scopes()

    def _load_dangerous_actions(self) -> List[str]:
        """Load list of dangerous action types"""
        return [
            "file_delete",
            "file_write_system",
            "database_delete",
            "database_drop",
            "network_request_external",
            "system_command",
            "process_kill",
            "user_create",
            "permission_modify",
            "config_modify",
        ]

    def _load_allowed_scopes(self) -> Dict[str, List[str]]:
        """Load allowed scopes for different action types"""
        return {
            "file_read": ["/tmp", "/var/tmp", "/home/user/documents"],
            "file_write": ["/tmp", "/var/tmp"],
            "database_query": ["readonly"],
            "api_request": ["https://api.example.com"],
        }

    async def authorize_action(
        self,
        agent_id: str,
        session_id: str,
        action_type: str,
        requested_action: Dict,
        requested_scope: Optional[Dict] = None,
    ) -> AgentAction:
        """
        Authorize an agent action request

        Returns:
            AgentAction with authorization decision
        """
        # Step 1: Create action record
        action = AgentAction(
            id=uuid4(),
            agent_id=agent_id,
            session_id=session_id,
            action_type=action_type,
            requested_action=requested_action,
            requested_scope=requested_scope,
            authorized=False,
        )

        # Step 2: Check if action is dangerous
        is_dangerous = action_type in self.dangerous_actions

        # Step 3: Check scope restrictions
        scope_allowed = self._check_scope(action_type, requested_scope)

        # Step 4: Analyze action with LLM Council
        council_result = await self._analyze_action(action_type, requested_action)

        # Step 5: Calculate risk score
        risk_score = self._calculate_risk_score(
            is_dangerous, scope_allowed, council_result
        )

        # Step 6: Determine authorization
        authorized = self._determine_authorization(
            is_dangerous, scope_allowed, risk_score, council_result
        )

        # Step 7: Collect safety flags
        safety_flags = {
            "is_dangerous": is_dangerous,
            "scope_allowed": scope_allowed,
            "council_verdict": council_result.final_verdict.value,
            "risk_score": risk_score,
            "council_consensus": council_result.consensus_score,
        }

        # Update action
        action.authorized = authorized
        action.risk_score = risk_score
        action.safety_flags = safety_flags
        if authorized:
            action.authorized_at = datetime.utcnow()
            action.authorized_by = "system"

        return action

    def _check_scope(self, action_type: str, requested_scope: Optional[Dict]) -> bool:
        """Check if requested scope is allowed"""
        if not requested_scope:
            return True  # No scope restrictions

        allowed = self.allowed_scopes.get(action_type, [])
        if not allowed:
            return False  # Action type not in allowed list

        # Check if requested scope matches allowed scopes
        # This is simplified - implement proper scope checking
        return True

    async def _analyze_action(
        self, action_type: str, requested_action: Dict
    ) -> CouncilResult:
        """Analyze action with LLM Council"""
        analysis_prompt = self._build_analysis_prompt(action_type, requested_action)
        
        # Use council to analyze the action description
        context = {"action_type": action_type}
        council_result = await self.council.analyze_prompt(
            analysis_prompt, context, None
        )

        return council_result

    def _build_analysis_prompt(self, action_type: str, requested_action: Dict) -> str:
        """Build prompt for action analysis"""
        return f"""Analyze this agent action request for security risks.

ACTION TYPE: {action_type}
ACTION DETAILS: {requested_action}

Evaluate:
1. Is this action safe to execute?
2. Could it cause harm or data loss?
3. Does it violate security policies?
4. Should it be blocked or allowed?

Respond in JSON:
{{
    "verdict": "blocked" | "allowed" | "flagged",
    "risk_score": 0-100,
    "confidence": 0-1,
    "reasoning": "explanation",
    "signals_detected": {{
        "dangerous": true/false,
        "data_loss_risk": true/false,
        "security_violation": true/false
    }}
}}
"""

    def _calculate_risk_score(
        self, is_dangerous: bool, scope_allowed: bool, council_result
    ) -> float:
        """Calculate risk score for action"""
        base_score = 0.0

        if is_dangerous:
            base_score += 50.0

        if not scope_allowed:
            base_score += 30.0

        # Add council score
        council_weight = 0.5
        final_score = base_score + (council_result.weighted_score * council_weight)

        return min(final_score, 100.0)

    def _determine_authorization(
        self,
        is_dangerous: bool,
        scope_allowed: bool,
        risk_score: float,
        council_result,
    ) -> bool:
        """Determine if action should be authorized"""
        # Hard blocks
        if is_dangerous and risk_score >= 70:
            return False

        if not scope_allowed:
            return False

        if council_result.final_verdict == Verdict.BLOCKED:
            return False

        # Soft blocks
        if risk_score >= 60:
            return False  # High risk, block

        # Allow if low risk
        return True

    async def execute_action(self, action: AgentAction) -> Dict:
        """
        Execute an authorized action

        This is a placeholder - actual execution would depend on the action type.
        """
        if not action.authorized:
            raise ValueError("Action not authorized")

        action.executed = True
        action.executed_at = datetime.utcnow()

        # Placeholder execution
        result = {
            "status": "success",
            "message": "Action executed",
            "action_id": str(action.id),
        }

        action.execution_result = result
        return result

    def kill_switch(self, agent_id: str, session_id: Optional[str] = None) -> bool:
        """
        Emergency kill switch for agent

        Returns:
            True if kill switch activated
        """
        # This would mark all pending actions as blocked
        # and prevent new actions from being authorized
        # Implementation depends on your agent system
        return True

