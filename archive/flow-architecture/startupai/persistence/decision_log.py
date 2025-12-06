"""
Decision Log Persistence Module.

Handles persisting decisions to the decision_log table for audit trail
and HITL workflow support.

Area 6 Implementation: HITL UX & Guardrails - Decision Logging
"""

from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from startupai.persistence.connection import get_supabase_client
from startupai.flows.state_schemas import EnforcementMode
from startupai.models.tool_contracts import ToolResult


# =======================================================================================
# DATA MODELS
# =======================================================================================

class DecisionType(str, Enum):
    """Types of decisions that can be logged."""
    BUDGET_CHECK = "budget_check"
    BUDGET_ESCALATION = "budget_escalation"
    BUDGET_OVERRIDE = "budget_override"
    HUMAN_APPROVAL = "human_approval"
    ROUTER_DECISION = "router_decision"
    POLICY_SELECTION = "policy_selection"
    PIVOT_DECISION = "pivot_decision"
    CREATIVE_APPROVAL = "creative_approval"
    VIABILITY_APPROVAL = "viability_approval"


class ActorType(str, Enum):
    """Types of actors that can make decisions."""
    SYSTEM = "system"
    HUMAN = "human"
    HUMAN_FOUNDER = "human_founder"
    ADMIN = "admin"
    GUARDIAN_AGENT = "guardian_agent"
    SYNTHESIS_AGENT = "synthesis_agent"


class DecisionRecord(BaseModel):
    """Record of a decision for logging."""
    project_id: str
    decision_type: DecisionType
    decision_point: str  # Where in the flow
    decision: str  # approved, rejected, escalated, etc.
    rationale: Optional[str] = None
    actor_type: ActorType
    actor_id: Optional[str] = None

    # Budget-specific (optional)
    enforcement_mode: Optional[EnforcementMode] = None
    budget_limit_usd: Optional[float] = None
    current_spend_usd: Optional[float] = None
    threshold_pct: Optional[float] = None

    # Context
    context_snapshot: Dict[str, Any] = Field(default_factory=dict)

    # Override info (optional)
    is_override: bool = False
    override_reason: Optional[str] = None
    overridden_by: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionLogEntry(BaseModel):
    """Entry retrieved from decision log."""
    id: str
    project_id: str
    decision_type: str
    decision_point: str
    decision: str
    rationale: Optional[str]
    actor_type: str
    actor_id: Optional[str]
    enforcement_mode: Optional[str]
    budget_limit_usd: Optional[float]
    current_spend_usd: Optional[float]
    threshold_pct: Optional[float]
    context_snapshot: Dict[str, Any]
    is_override: bool
    override_reason: Optional[str]
    overridden_by: Optional[str]
    created_at: datetime
    metadata: Dict[str, Any]


# =======================================================================================
# DECISION LOGGER
# =======================================================================================

class DecisionLogger:
    """
    Logger for decisions in the validation flow.

    Provides methods to log various decision types and query decision history.
    """

    def __init__(self):
        """Initialize the decision logger."""
        self._supabase = None

    @property
    def supabase(self):
        """Lazy load Supabase client."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    def log_decision(
        self,
        record: DecisionRecord,
    ) -> ToolResult[str]:
        """
        Log a decision to the database.

        Args:
            record: Decision record to log

        Returns:
            ToolResult with the decision log entry ID
        """
        try:
            result = self.supabase.rpc(
                'log_decision',
                {
                    'p_project_id': record.project_id,
                    'p_decision_type': record.decision_type.value,
                    'p_decision_point': record.decision_point,
                    'p_decision': record.decision,
                    'p_rationale': record.rationale,
                    'p_actor_type': record.actor_type.value,
                    'p_actor_id': record.actor_id,
                    'p_enforcement_mode': record.enforcement_mode.value if record.enforcement_mode else None,
                    'p_budget_limit_usd': record.budget_limit_usd,
                    'p_current_spend_usd': record.current_spend_usd,
                    'p_threshold_pct': record.threshold_pct,
                    'p_context_snapshot': record.context_snapshot,
                    'p_is_override': record.is_override,
                    'p_override_reason': record.override_reason,
                    'p_overridden_by': record.overridden_by,
                }
            ).execute()

            entry_id = result.data if result.data else 'logged'

            return ToolResult.success(
                data=str(entry_id),
                decision_type=record.decision_type.value,
            )

        except Exception as e:
            return ToolResult.failure(
                message=f"Failed to log decision: {str(e)}",
                code="DECISION_LOG_ERROR",
            )

    def get_decisions(
        self,
        project_id: str,
        decision_type: Optional[DecisionType] = None,
        limit: int = 50,
    ) -> ToolResult[List[DecisionLogEntry]]:
        """
        Get decision history for a project.

        Args:
            project_id: Project identifier
            decision_type: Optional filter by decision type
            limit: Maximum number of entries to return

        Returns:
            ToolResult with list of decision log entries
        """
        try:
            query = self.supabase.table('decision_log') \
                .select('*') \
                .eq('project_id', project_id) \
                .order('created_at', desc=True) \
                .limit(limit)

            if decision_type:
                query = query.eq('decision_type', decision_type.value)

            result = query.execute()

            entries = [
                DecisionLogEntry(
                    id=row['id'],
                    project_id=row['project_id'],
                    decision_type=row['decision_type'],
                    decision_point=row['decision_point'],
                    decision=row['decision'],
                    rationale=row.get('rationale'),
                    actor_type=row['actor_type'],
                    actor_id=row.get('actor_id'),
                    enforcement_mode=row.get('enforcement_mode'),
                    budget_limit_usd=row.get('budget_limit_usd'),
                    current_spend_usd=row.get('current_spend_usd'),
                    threshold_pct=row.get('threshold_pct'),
                    context_snapshot=row.get('context_snapshot', {}),
                    is_override=row.get('is_override', False),
                    override_reason=row.get('override_reason'),
                    overridden_by=row.get('overridden_by'),
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')),
                    metadata=row.get('metadata', {}),
                )
                for row in result.data
            ]

            return ToolResult.success(data=entries)

        except Exception as e:
            return ToolResult.failure(
                message=f"Failed to get decisions: {str(e)}",
                code="DECISION_QUERY_ERROR",
            )

    def get_overrides(
        self,
        project_id: Optional[str] = None,
        limit: int = 50,
    ) -> ToolResult[List[DecisionLogEntry]]:
        """
        Get override decisions for audit.

        Args:
            project_id: Optional filter by project
            limit: Maximum number of entries

        Returns:
            ToolResult with list of override entries
        """
        try:
            query = self.supabase.from_('override_audit') \
                .select('*') \
                .order('created_at', desc=True) \
                .limit(limit)

            if project_id:
                query = query.eq('project_id', project_id)

            result = query.execute()

            entries = [
                DecisionLogEntry(
                    id=row['id'],
                    project_id=row['project_id'],
                    decision_type=row['decision_type'],
                    decision_point=row['decision_point'],
                    decision=row['decision'],
                    rationale=row.get('rationale'),
                    actor_type=row['actor_type'],
                    actor_id=None,
                    enforcement_mode=None,
                    budget_limit_usd=None,
                    current_spend_usd=None,
                    threshold_pct=None,
                    context_snapshot={},
                    is_override=True,
                    override_reason=row.get('override_reason'),
                    overridden_by=row.get('overridden_by'),
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')),
                    metadata={},
                )
                for row in result.data
            ]

            return ToolResult.success(data=entries)

        except Exception as e:
            return ToolResult.failure(
                message=f"Failed to get overrides: {str(e)}",
                code="OVERRIDE_QUERY_ERROR",
            )

    def get_budget_summary(
        self,
        project_id: str,
    ) -> ToolResult[Dict[str, Any]]:
        """
        Get budget decisions summary for a project.

        Args:
            project_id: Project identifier

        Returns:
            ToolResult with budget decision summary
        """
        try:
            result = self.supabase.from_('budget_decisions_summary') \
                .select('*') \
                .eq('project_id', project_id) \
                .execute()

            if result.data:
                return ToolResult.success(data=result.data[0])
            else:
                return ToolResult.success(data={
                    'project_id': project_id,
                    'approved_count': 0,
                    'rejected_count': 0,
                    'escalated_count': 0,
                    'override_count': 0,
                })

        except Exception as e:
            return ToolResult.failure(
                message=f"Failed to get budget summary: {str(e)}",
                code="BUDGET_SUMMARY_ERROR",
            )


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def log_human_approval(
    project_id: str,
    decision_point: str,
    approved: bool,
    rationale: str,
    actor_id: str,
    context: Optional[Dict[str, Any]] = None,
) -> ToolResult[str]:
    """
    Log a human approval decision.

    Args:
        project_id: Project identifier
        decision_point: Where in the flow
        approved: Whether it was approved
        rationale: Reason for the decision
        actor_id: ID of the human making the decision
        context: Optional context snapshot

    Returns:
        ToolResult with log entry ID
    """
    logger = DecisionLogger()
    record = DecisionRecord(
        project_id=project_id,
        decision_type=DecisionType.HUMAN_APPROVAL,
        decision_point=decision_point,
        decision='approved' if approved else 'rejected',
        rationale=rationale,
        actor_type=ActorType.HUMAN_FOUNDER,
        actor_id=actor_id,
        context_snapshot=context or {},
    )
    return logger.log_decision(record)


def log_policy_selection(
    project_id: str,
    policy_version: str,
    selection_reason: str,
    experiment_type: str,
) -> ToolResult[str]:
    """
    Log a policy selection decision.

    Args:
        project_id: Project identifier
        policy_version: Selected policy version
        selection_reason: Reason for selection
        experiment_type: Type of experiment

    Returns:
        ToolResult with log entry ID
    """
    logger = DecisionLogger()
    record = DecisionRecord(
        project_id=project_id,
        decision_type=DecisionType.POLICY_SELECTION,
        decision_point=f'experiment_{experiment_type}',
        decision=policy_version,
        rationale=selection_reason,
        actor_type=ActorType.SYSTEM,
        metadata={'experiment_type': experiment_type},
    )
    return logger.log_decision(record)


def log_router_decision(
    project_id: str,
    gate_name: str,
    passed: bool,
    rationale: str,
    evidence_summary: Optional[Dict[str, Any]] = None,
) -> ToolResult[str]:
    """
    Log a router/gate decision.

    Args:
        project_id: Project identifier
        gate_name: Name of the gate (desirability, feasibility, viability)
        passed: Whether the gate was passed
        rationale: Reason for the decision
        evidence_summary: Optional evidence snapshot

    Returns:
        ToolResult with log entry ID
    """
    logger = DecisionLogger()
    record = DecisionRecord(
        project_id=project_id,
        decision_type=DecisionType.ROUTER_DECISION,
        decision_point=f'{gate_name}_gate',
        decision='passed' if passed else 'failed',
        rationale=rationale,
        actor_type=ActorType.SYSTEM,
        context_snapshot=evidence_summary or {},
    )
    return logger.log_decision(record)


def log_pivot_decision(
    project_id: str,
    pivot_type: str,
    rationale: str,
    confidence_level: str,
    actor_type: ActorType = ActorType.SYNTHESIS_AGENT,
    human_approved: bool = False,
    human_approver_id: Optional[str] = None,
) -> ToolResult[str]:
    """
    Log a pivot decision.

    Args:
        project_id: Project identifier
        pivot_type: Type of pivot recommended
        rationale: Reasoning for the pivot
        confidence_level: Confidence in the decision
        actor_type: Who made the decision
        human_approved: Whether it was human-approved
        human_approver_id: ID of human approver if applicable

    Returns:
        ToolResult with log entry ID
    """
    logger = DecisionLogger()
    record = DecisionRecord(
        project_id=project_id,
        decision_type=DecisionType.PIVOT_DECISION,
        decision_point='synthesis',
        decision=pivot_type,
        rationale=rationale,
        actor_type=actor_type,
        actor_id=human_approver_id,
        metadata={
            'confidence_level': confidence_level,
            'human_approved': human_approved,
        },
    )
    return logger.log_decision(record)


def get_project_decision_history(
    project_id: str,
    decision_type: Optional[str] = None,
) -> List[DecisionLogEntry]:
    """
    Get decision history for a project.

    Args:
        project_id: Project identifier
        decision_type: Optional filter by type

    Returns:
        List of decision log entries
    """
    logger = DecisionLogger()
    dt = DecisionType(decision_type) if decision_type else None
    result = logger.get_decisions(project_id, decision_type=dt)

    if result.is_usable:
        return result.data
    return []
