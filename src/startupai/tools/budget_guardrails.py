"""
Budget Guardrails Tool for Spend Control.

Implements hard/soft enforcement modes with escalation thresholds
and kill switch functionality.

Area 6 Implementation: HITL UX & Guardrails - Budget Control
"""

import os
from typing import Dict, Optional, Any, Literal
from datetime import datetime
from pathlib import Path
from enum import Enum

import yaml
from pydantic import BaseModel, Field

from startupai.flows.state_schemas import (
    EnforcementMode,
    BudgetStatus,
    StartupValidationState,
)
from startupai.persistence.connection import get_supabase_client
from startupai.models.tool_contracts import ToolResult


class BudgetCheckResult(BaseModel):
    """Result of a budget check."""
    allowed: bool
    budget_status: BudgetStatus
    current_spend_usd: float
    budget_limit_usd: float
    utilization_pct: float
    threshold_triggered: Optional[str] = None
    action_required: Optional[str] = None
    message: str
    enforcement_mode: EnforcementMode


class EscalationInfo(BaseModel):
    """Information about a budget escalation."""
    escalation_id: str
    project_id: str
    threshold_triggered: str
    current_spend_usd: float
    budget_limit_usd: float
    utilization_pct: float
    enforcement_mode: EnforcementMode
    escalated_at: datetime = Field(default_factory=datetime.now)
    escalation_recipients: list = Field(default_factory=list)


class BudgetGuardrails:
    """
    Budget guardrails with hard/soft enforcement modes.

    Hard mode: Blocks spend above limits
    Soft mode: Warns and logs but allows override with rationale
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize budget guardrails.

        Args:
            config_path: Path to budget_guardrails.yaml config file.
                        If None, uses default location.
        """
        self.config_path = config_path or self._default_config_path()
        self.config = self._load_config()
        self._supabase = None

    def _default_config_path(self) -> str:
        """Get default config path."""
        return str(
            Path(__file__).parent.parent / "config" / "budget_guardrails.yaml"
        )

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return sensible defaults if config doesn't exist
            return {
                'global': {
                    'default_enforcement_mode': 'soft',
                    'enabled': True,
                    'log_all_decisions': True,
                },
                'thresholds': {
                    'warning': {'percentage': 0.80, 'action': 'escalate'},
                    'kill_switch': {'percentage': 1.20, 'action': 'kill'},
                    'critical': {'percentage': 1.50, 'action': 'hard_stop'},
                },
                'default_limits': {
                    'daily_spend_usd': 100.0,
                    'campaign_spend_usd': 500.0,
                },
            }

    @property
    def supabase(self):
        """Lazy load Supabase client."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    def check_budget(
        self,
        project_id: str,
        current_spend_usd: float,
        budget_limit_usd: Optional[float] = None,
        enforcement_mode: Optional[EnforcementMode] = None,
        proposed_spend_usd: float = 0.0,
    ) -> ToolResult[BudgetCheckResult]:
        """
        Check if spending is within budget limits.

        Args:
            project_id: Project identifier
            current_spend_usd: Current total spend
            budget_limit_usd: Budget limit (uses default if None)
            enforcement_mode: Hard or soft enforcement (uses config default if None)
            proposed_spend_usd: Additional spend being proposed

        Returns:
            ToolResult containing budget check result
        """
        try:
            # Determine enforcement mode
            mode = enforcement_mode or EnforcementMode(
                self.config.get('global', {}).get('default_enforcement_mode', 'soft')
            )

            # Determine budget limit
            limit = budget_limit_usd or self.config.get('default_limits', {}).get(
                'campaign_spend_usd', 500.0
            )

            # Calculate utilization
            total_spend = current_spend_usd + proposed_spend_usd
            utilization_pct = (total_spend / limit) if limit > 0 else 0.0

            # Check thresholds
            thresholds = self.config.get('thresholds', {})
            threshold_triggered = None
            action_required = None
            budget_status = BudgetStatus.OK

            # Check critical threshold (always blocks)
            critical_pct = thresholds.get('critical', {}).get('percentage', 1.5)
            if utilization_pct >= critical_pct:
                threshold_triggered = 'critical'
                action_required = 'hard_stop'
                budget_status = BudgetStatus.KILL_TRIGGERED
                allowed = False  # Always block critical

            # Check kill switch threshold
            elif utilization_pct >= thresholds.get('kill_switch', {}).get('percentage', 1.2):
                threshold_triggered = 'kill_switch'
                action_required = 'kill'
                budget_status = BudgetStatus.EXCEEDED
                # Hard mode blocks, soft mode allows with logging
                allowed = mode == EnforcementMode.SOFT

            # Check warning threshold
            elif utilization_pct >= thresholds.get('warning', {}).get('percentage', 0.8):
                threshold_triggered = 'warning'
                action_required = 'escalate'
                budget_status = BudgetStatus.WARNING
                allowed = True  # Warning doesn't block

            else:
                allowed = True

            # Build message
            if threshold_triggered:
                message = self._build_threshold_message(
                    threshold_triggered,
                    utilization_pct,
                    mode,
                    allowed,
                )
            else:
                message = f"Budget check passed: {utilization_pct*100:.1f}% utilization"

            result = BudgetCheckResult(
                allowed=allowed,
                budget_status=budget_status,
                current_spend_usd=total_spend,
                budget_limit_usd=limit,
                utilization_pct=utilization_pct,
                threshold_triggered=threshold_triggered,
                action_required=action_required,
                message=message,
                enforcement_mode=mode,
            )

            # Log the decision
            if self.config.get('global', {}).get('log_all_decisions', True):
                self._log_budget_decision(project_id, result)

            return ToolResult.success(data=result)

        except Exception as e:
            return ToolResult.failure(
                message=f"Budget check failed: {str(e)}",
                code="BUDGET_CHECK_ERROR",
            )

    def _build_threshold_message(
        self,
        threshold: str,
        utilization_pct: float,
        mode: EnforcementMode,
        allowed: bool,
    ) -> str:
        """Build a human-readable threshold message."""
        pct_str = f"{utilization_pct * 100:.1f}%"

        if threshold == 'critical':
            return f"CRITICAL: Budget at {pct_str} - All spending blocked"
        elif threshold == 'kill_switch':
            if allowed:
                return f"KILL SWITCH: Budget at {pct_str} - Soft mode allows override"
            else:
                return f"KILL SWITCH: Budget at {pct_str} - Hard mode blocks spending"
        elif threshold == 'warning':
            return f"WARNING: Budget at {pct_str} - Escalation triggered"
        else:
            return f"Budget threshold '{threshold}' triggered at {pct_str}"

    def _log_budget_decision(
        self,
        project_id: str,
        result: BudgetCheckResult,
    ) -> None:
        """Log budget decision to decision_log table."""
        try:
            decision = 'approved' if result.allowed else 'rejected'
            if result.threshold_triggered == 'warning':
                decision = 'escalated'

            self.supabase.rpc(
                'log_decision',
                {
                    'p_project_id': project_id,
                    'p_decision_type': 'budget_check',
                    'p_decision_point': 'budget_guardrails',
                    'p_decision': decision,
                    'p_actor_type': 'system',
                    'p_rationale': result.message,
                    'p_enforcement_mode': result.enforcement_mode.value,
                    'p_budget_limit_usd': result.budget_limit_usd,
                    'p_current_spend_usd': result.current_spend_usd,
                    'p_threshold_pct': result.utilization_pct,
                }
            ).execute()
        except Exception as e:
            # Log but don't fail the main operation
            print(f"Warning: Failed to log budget decision: {e}")

    def escalate(
        self,
        project_id: str,
        current_spend_usd: float,
        budget_limit_usd: float,
        threshold_triggered: str,
        enforcement_mode: EnforcementMode,
    ) -> ToolResult[EscalationInfo]:
        """
        Trigger budget escalation.

        Args:
            project_id: Project identifier
            current_spend_usd: Current spend amount
            budget_limit_usd: Budget limit
            threshold_triggered: Which threshold was triggered
            enforcement_mode: Current enforcement mode

        Returns:
            ToolResult with escalation info
        """
        try:
            import uuid

            escalation_id = str(uuid.uuid4())[:8]
            utilization_pct = current_spend_usd / budget_limit_usd if budget_limit_usd > 0 else 0

            # Get escalation recipients from config
            recipients = self.config.get('escalation', {}).get('escalation_recipients', [])
            recipient_roles = [r.get('role') for r in recipients]

            escalation = EscalationInfo(
                escalation_id=escalation_id,
                project_id=project_id,
                threshold_triggered=threshold_triggered,
                current_spend_usd=current_spend_usd,
                budget_limit_usd=budget_limit_usd,
                utilization_pct=utilization_pct,
                enforcement_mode=enforcement_mode,
                escalation_recipients=recipient_roles,
            )

            # Log escalation decision
            self.supabase.rpc(
                'log_decision',
                {
                    'p_project_id': project_id,
                    'p_decision_type': 'budget_escalation',
                    'p_decision_point': 'budget_guardrails',
                    'p_decision': 'escalated',
                    'p_actor_type': 'system',
                    'p_rationale': f"Escalation triggered: {threshold_triggered} threshold at {utilization_pct*100:.1f}%",
                    'p_enforcement_mode': enforcement_mode.value,
                    'p_budget_limit_usd': budget_limit_usd,
                    'p_current_spend_usd': current_spend_usd,
                    'p_threshold_pct': utilization_pct,
                }
            ).execute()

            return ToolResult.success(
                data=escalation,
                escalation_id=escalation_id,
            )

        except Exception as e:
            return ToolResult.failure(
                message=f"Escalation failed: {str(e)}",
                code="ESCALATION_ERROR",
            )

    def override_budget(
        self,
        project_id: str,
        actor_id: str,
        actor_type: Literal["human_founder", "admin", "guardian_agent"],
        override_reason: str,
        current_spend_usd: float,
        budget_limit_usd: float,
        enforcement_mode: EnforcementMode,
    ) -> ToolResult[Dict[str, Any]]:
        """
        Record a budget override decision.

        Args:
            project_id: Project identifier
            actor_id: ID of actor performing override
            actor_type: Type of actor
            override_reason: Rationale for the override
            current_spend_usd: Current spend at time of override
            budget_limit_usd: Budget limit being overridden
            enforcement_mode: Current enforcement mode

        Returns:
            ToolResult with override confirmation
        """
        try:
            # Validate override authorization
            allowed_overriders = self.config.get('override_settings', {})
            if enforcement_mode == EnforcementMode.HARD:
                allowed_list = allowed_overriders.get('hard_mode_override', ['human_founder', 'admin'])
            else:
                allowed_list = allowed_overriders.get('soft_mode_override', ['guardian_agent', 'human_founder'])

            if actor_type not in allowed_list:
                return ToolResult.failure(
                    message=f"Actor type '{actor_type}' not authorized for {enforcement_mode.value} mode override",
                    code="OVERRIDE_NOT_AUTHORIZED",
                )

            # Validate rationale
            min_length = self.config.get('override_settings', {}).get('rationale_min_length', 50)
            if len(override_reason) < min_length:
                return ToolResult.failure(
                    message=f"Override rationale must be at least {min_length} characters",
                    code="RATIONALE_TOO_SHORT",
                )

            # Log the override
            utilization_pct = current_spend_usd / budget_limit_usd if budget_limit_usd > 0 else 0

            self.supabase.rpc(
                'log_decision',
                {
                    'p_project_id': project_id,
                    'p_decision_type': 'budget_override',
                    'p_decision_point': 'budget_guardrails',
                    'p_decision': 'overridden',
                    'p_actor_type': actor_type,
                    'p_actor_id': actor_id,
                    'p_rationale': f"Override reason: {override_reason}",
                    'p_enforcement_mode': enforcement_mode.value,
                    'p_budget_limit_usd': budget_limit_usd,
                    'p_current_spend_usd': current_spend_usd,
                    'p_threshold_pct': utilization_pct,
                    'p_is_override': True,
                    'p_override_reason': override_reason,
                    'p_overridden_by': actor_id,
                }
            ).execute()

            return ToolResult.success(
                data={
                    'override_recorded': True,
                    'project_id': project_id,
                    'actor': actor_id,
                    'enforcement_mode': enforcement_mode.value,
                },
                message="Budget override recorded successfully",
            )

        except Exception as e:
            return ToolResult.failure(
                message=f"Override recording failed: {str(e)}",
                code="OVERRIDE_RECORD_ERROR",
            )

    def update_state(
        self,
        state: StartupValidationState,
        check_result: BudgetCheckResult,
    ) -> StartupValidationState:
        """
        Update state with budget check results.

        Args:
            state: Current validation state
            check_result: Result from budget check

        Returns:
            Updated state with budget fields set
        """
        state.budget_status = check_result.budget_status
        state.daily_spend_usd = check_result.current_spend_usd  # Simplified - adjust as needed

        if check_result.threshold_triggered == 'warning':
            state.budget_escalation_triggered = True
        elif check_result.threshold_triggered in ('kill_switch', 'critical'):
            state.budget_kill_triggered = True

        return state


# Convenience functions for use in flows

def check_spend_allowed(
    project_id: str,
    current_spend_usd: float,
    proposed_spend_usd: float,
    budget_limit_usd: Optional[float] = None,
    enforcement_mode: Optional[EnforcementMode] = None,
) -> tuple[bool, str, BudgetStatus]:
    """
    Convenience function to check if additional spend is allowed.

    Returns:
        Tuple of (allowed, message, budget_status)
    """
    guardrails = BudgetGuardrails()
    result = guardrails.check_budget(
        project_id=project_id,
        current_spend_usd=current_spend_usd,
        budget_limit_usd=budget_limit_usd,
        enforcement_mode=enforcement_mode,
        proposed_spend_usd=proposed_spend_usd,
    )

    if result.is_usable:
        return result.data.allowed, result.data.message, result.data.budget_status
    else:
        # Fail safe - block spend on error
        return False, f"Budget check error: {result.error_message}", BudgetStatus.WARNING


def record_budget_override(
    project_id: str,
    actor_id: str,
    actor_type: str,
    override_reason: str,
    current_spend_usd: float,
    budget_limit_usd: float,
) -> bool:
    """
    Convenience function to record a budget override.

    Returns:
        True if recorded successfully, False otherwise
    """
    guardrails = BudgetGuardrails()
    result = guardrails.override_budget(
        project_id=project_id,
        actor_id=actor_id,
        actor_type=actor_type,
        override_reason=override_reason,
        current_spend_usd=current_spend_usd,
        budget_limit_usd=budget_limit_usd,
        enforcement_mode=EnforcementMode.SOFT,  # Default assumption
    )
    return result.is_success
