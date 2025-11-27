"""
Resume Webhook Handler for HITL Workflows.

Parses /resume payloads from the product app for:
- Creative approvals (landing pages, ad creatives)
- Viability decisions (price pivot, cost pivot, kill)

The product app sends these payloads when a human makes a decision
on a paused validation flow.

Area 6 Enhancement: Rationale persistence via decision_log table.
"""

import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator

# Import decision logging for rationale persistence (Area 6)
try:
    from startupai.persistence.decision_log import (
        DecisionLogger,
        DecisionRecord,
        DecisionType,
        ActorType,
        log_human_approval,
        log_pivot_decision,
    )
    DECISION_LOG_AVAILABLE = True
except ImportError:
    DECISION_LOG_AVAILABLE = False


# =======================================================================================
# ENUMS
# =======================================================================================

class ApprovalType(str, Enum):
    """Types of approvals that can be sent via /resume."""
    CREATIVE_APPROVAL = "creative_approval"      # LP/ad approval
    VIABILITY_DECISION = "viability_decision"    # Price/cost pivot
    SEGMENT_PIVOT = "segment_pivot"              # Change target segment
    VALUE_PIVOT = "value_pivot"                  # Iterate value prop
    DOWNGRADE_APPROVAL = "downgrade_approval"    # Accept feature cuts


class CreativeStatus(str, Enum):
    """Status for creative artifacts."""
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class ViabilityChoice(str, Enum):
    """Choices for viability decision."""
    PRICE_PIVOT = "price_pivot"     # Increase price to improve margins
    COST_PIVOT = "cost_pivot"       # Reduce costs/features
    KILL = "kill"                   # Terminate the validation
    CONTINUE = "continue"           # Proceed despite warnings


# =======================================================================================
# PAYLOAD MODELS
# =======================================================================================

class CreativeApprovalPayload(BaseModel):
    """Payload for creative (LP/ad) approval decisions."""
    variant_id: str = Field(..., description="ID of the variant being approved")
    status: CreativeStatus = Field(..., description="Approval status")
    feedback: Optional[str] = Field(None, description="Human feedback/notes")
    revision_notes: Optional[str] = Field(None, description="What to fix if revision requested")
    approved_by: Optional[str] = Field(None, description="User ID of approver")
    approved_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Additional context
    variant_type: Optional[str] = Field(None, description="landing_page, ad_creative, etc.")
    experiment_id: Optional[str] = Field(None, description="Associated experiment ID")


class ViabilityDecisionPayload(BaseModel):
    """Payload for viability/strategic pivot decisions."""
    choice: ViabilityChoice = Field(..., description="The human's decision")
    rationale: Optional[str] = Field(None, description="Why this choice was made")
    decided_by: Optional[str] = Field(None, description="User ID of decision maker")
    decided_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # For price_pivot
    new_price_target: Optional[float] = Field(None, description="Target price if price pivot")

    # For cost_pivot
    cost_reduction_target: Optional[float] = Field(None, description="Target cost reduction %")
    features_to_cut: List[str] = Field(default_factory=list, description="Features to remove")

    # For kill
    kill_reason: Optional[str] = Field(None, description="Why validation is being killed")


class SegmentPivotPayload(BaseModel):
    """Payload for segment pivot decisions."""
    approved: bool = Field(..., description="Whether to proceed with pivot")
    new_segment: Optional[str] = Field(None, description="New target segment if pivoting")
    keep_current: bool = Field(False, description="Stay with current segment")
    feedback: Optional[str] = Field(None, description="Human notes")


class ValuePivotPayload(BaseModel):
    """Payload for value proposition iteration decisions."""
    approved: bool = Field(..., description="Whether to proceed with iteration")
    direction: Optional[str] = Field(None, description="Iteration direction")
    # Direction options: intensify_pain_relievers, add_gain_creators, simplify, differentiate
    specific_changes: List[str] = Field(default_factory=list, description="Specific changes requested")
    feedback: Optional[str] = Field(None, description="Human notes")


class DowngradeApprovalPayload(BaseModel):
    """Payload for feature downgrade approval."""
    approved: bool = Field(..., description="Whether to accept the downgrade")
    acceptable_tradeoffs: List[str] = Field(default_factory=list, description="Accepted tradeoffs")
    rejected_tradeoffs: List[str] = Field(default_factory=list, description="Rejected tradeoffs")
    feedback: Optional[str] = Field(None, description="Human notes")


class ResumePayload(BaseModel):
    """
    Main payload structure for /resume webhook.

    The product app sends this when a human makes a decision
    on a paused validation flow.
    """
    # Required fields
    kickoff_id: str = Field(..., description="CrewAI kickoff ID to resume")
    approval_type: ApprovalType = Field(..., description="Type of approval being sent")

    # Context
    project_id: Optional[str] = Field(None, description="Project ID")
    user_id: Optional[str] = Field(None, description="User making the decision")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Type-specific payloads (only one should be populated based on approval_type)
    creative_approval: Optional[CreativeApprovalPayload] = None
    viability_decision: Optional[ViabilityDecisionPayload] = None
    segment_pivot: Optional[SegmentPivotPayload] = None
    value_pivot: Optional[ValuePivotPayload] = None
    downgrade_approval: Optional[DowngradeApprovalPayload] = None

    @field_validator('creative_approval', 'viability_decision', 'segment_pivot',
                     'value_pivot', 'downgrade_approval', mode='before')
    @classmethod
    def validate_payload_type(cls, v, info):
        """Ensure payload matches approval_type."""
        # This is a soft validation - just return the value
        return v

    def get_payload(self) -> Union[
        CreativeApprovalPayload,
        ViabilityDecisionPayload,
        SegmentPivotPayload,
        ValuePivotPayload,
        DowngradeApprovalPayload,
        None
    ]:
        """Get the appropriate payload based on approval_type."""
        type_to_payload = {
            ApprovalType.CREATIVE_APPROVAL: self.creative_approval,
            ApprovalType.VIABILITY_DECISION: self.viability_decision,
            ApprovalType.SEGMENT_PIVOT: self.segment_pivot,
            ApprovalType.VALUE_PIVOT: self.value_pivot,
            ApprovalType.DOWNGRADE_APPROVAL: self.downgrade_approval,
        }
        return type_to_payload.get(self.approval_type)


# =======================================================================================
# RESUME HANDLER
# =======================================================================================

class ResumeHandler:
    """
    Handler for processing /resume webhook payloads.

    This class parses incoming payloads and provides methods to:
    - Validate the payload structure
    - Extract the appropriate decision data
    - Format the decision for flow state updates
    - Persist decision rationale to decision_log table (Area 6)
    """

    def __init__(self, persist_decisions: bool = True):
        """
        Initialize the handler.

        Args:
            persist_decisions: Whether to persist decisions to decision_log table
        """
        self._processed_payloads: List[Dict[str, Any]] = []
        self._persist_decisions = persist_decisions and DECISION_LOG_AVAILABLE
        self._decision_logger = DecisionLogger() if self._persist_decisions else None

    def parse_payload(self, raw_payload: Union[str, Dict[str, Any]]) -> ResumePayload:
        """
        Parse a raw payload into a structured ResumePayload.

        Args:
            raw_payload: JSON string or dict from the webhook

        Returns:
            Validated ResumePayload object

        Raises:
            ValueError: If payload is invalid
        """
        if isinstance(raw_payload, str):
            try:
                data = json.loads(raw_payload)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON payload: {e}")
        else:
            data = raw_payload

        try:
            payload = ResumePayload(**data)
            self._processed_payloads.append({
                "timestamp": datetime.now().isoformat(),
                "kickoff_id": payload.kickoff_id,
                "approval_type": payload.approval_type.value,
            })
            return payload
        except Exception as e:
            raise ValueError(f"Invalid payload structure: {e}")

    def handle_creative_approval(
        self,
        payload: ResumePayload
    ) -> Dict[str, Any]:
        """
        Process a creative approval payload.

        Returns a dict suitable for updating flow state.
        """
        if payload.approval_type != ApprovalType.CREATIVE_APPROVAL:
            raise ValueError(f"Expected creative_approval, got {payload.approval_type}")

        creative = payload.creative_approval
        if not creative:
            raise ValueError("Missing creative_approval data")

        return {
            "variant_id": creative.variant_id,
            "approved": creative.status == CreativeStatus.APPROVED,
            "status": creative.status.value,
            "feedback": creative.feedback,
            "revision_notes": creative.revision_notes,
            "approved_by": creative.approved_by,
            "approved_at": creative.approved_at,
        }

    def handle_viability_decision(
        self,
        payload: ResumePayload
    ) -> Dict[str, Any]:
        """
        Process a viability decision payload.

        Returns a dict suitable for updating flow state and routing.
        """
        if payload.approval_type != ApprovalType.VIABILITY_DECISION:
            raise ValueError(f"Expected viability_decision, got {payload.approval_type}")

        decision = payload.viability_decision
        if not decision:
            raise ValueError("Missing viability_decision data")

        result = {
            "choice": decision.choice.value,
            "rationale": decision.rationale,
            "decided_by": decision.decided_by,
            "decided_at": decision.decided_at,
        }

        # Add choice-specific data
        if decision.choice == ViabilityChoice.PRICE_PIVOT:
            result["new_price_target"] = decision.new_price_target
        elif decision.choice == ViabilityChoice.COST_PIVOT:
            result["cost_reduction_target"] = decision.cost_reduction_target
            result["features_to_cut"] = decision.features_to_cut
        elif decision.choice == ViabilityChoice.KILL:
            result["kill_reason"] = decision.kill_reason

        return result

    def handle_segment_pivot(
        self,
        payload: ResumePayload
    ) -> Dict[str, Any]:
        """Process a segment pivot payload."""
        if payload.approval_type != ApprovalType.SEGMENT_PIVOT:
            raise ValueError(f"Expected segment_pivot, got {payload.approval_type}")

        pivot = payload.segment_pivot
        if not pivot:
            raise ValueError("Missing segment_pivot data")

        return {
            "approved": pivot.approved,
            "new_segment": pivot.new_segment,
            "keep_current": pivot.keep_current,
            "feedback": pivot.feedback,
        }

    def handle_value_pivot(
        self,
        payload: ResumePayload
    ) -> Dict[str, Any]:
        """Process a value pivot payload."""
        if payload.approval_type != ApprovalType.VALUE_PIVOT:
            raise ValueError(f"Expected value_pivot, got {payload.approval_type}")

        pivot = payload.value_pivot
        if not pivot:
            raise ValueError("Missing value_pivot data")

        return {
            "approved": pivot.approved,
            "direction": pivot.direction,
            "specific_changes": pivot.specific_changes,
            "feedback": pivot.feedback,
        }

    def handle_downgrade_approval(
        self,
        payload: ResumePayload
    ) -> Dict[str, Any]:
        """Process a downgrade approval payload."""
        if payload.approval_type != ApprovalType.DOWNGRADE_APPROVAL:
            raise ValueError(f"Expected downgrade_approval, got {payload.approval_type}")

        approval = payload.downgrade_approval
        if not approval:
            raise ValueError("Missing downgrade_approval data")

        return {
            "approved": approval.approved,
            "acceptable_tradeoffs": approval.acceptable_tradeoffs,
            "rejected_tradeoffs": approval.rejected_tradeoffs,
            "feedback": approval.feedback,
        }

    def _persist_decision(
        self,
        payload: ResumePayload,
        result: Dict[str, Any],
    ) -> Optional[str]:
        """
        Persist decision to decision_log table for audit trail.

        Args:
            payload: The parsed resume payload
            result: The processed result dict

        Returns:
            Decision log entry ID if persisted, None otherwise
        """
        if not self._persist_decisions or not self._decision_logger:
            return None

        try:
            # Map approval types to decision types
            decision_type_map = {
                ApprovalType.CREATIVE_APPROVAL: DecisionType.CREATIVE_APPROVAL,
                ApprovalType.VIABILITY_DECISION: DecisionType.VIABILITY_APPROVAL,
                ApprovalType.SEGMENT_PIVOT: DecisionType.PIVOT_DECISION,
                ApprovalType.VALUE_PIVOT: DecisionType.PIVOT_DECISION,
                ApprovalType.DOWNGRADE_APPROVAL: DecisionType.HUMAN_APPROVAL,
            }

            decision_type = decision_type_map.get(
                payload.approval_type, DecisionType.HUMAN_APPROVAL
            )

            # Extract decision and rationale based on type
            if payload.approval_type == ApprovalType.CREATIVE_APPROVAL:
                decision = result.get('status', 'unknown')
                rationale = result.get('feedback') or result.get('revision_notes')
            elif payload.approval_type == ApprovalType.VIABILITY_DECISION:
                decision = result.get('choice', 'unknown')
                rationale = result.get('rationale') or result.get('kill_reason')
            else:
                decision = 'approved' if result.get('approved') else 'rejected'
                rationale = result.get('feedback')

            # Create decision record
            record = DecisionRecord(
                project_id=payload.project_id or payload.kickoff_id,
                decision_type=decision_type,
                decision_point=f"resume_{payload.approval_type.value}",
                decision=decision,
                rationale=rationale,
                actor_type=ActorType.HUMAN_FOUNDER,
                actor_id=payload.user_id,
                context_snapshot={
                    'kickoff_id': payload.kickoff_id,
                    'approval_type': payload.approval_type.value,
                    'result_keys': list(result.keys()),
                },
            )

            log_result = self._decision_logger.log_decision(record)
            if log_result.is_success:
                return log_result.data
            return None

        except Exception as e:
            # Log but don't fail the main operation
            print(f"Warning: Failed to persist decision: {e}")
            return None

    def process(self, raw_payload: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process any resume payload and return the appropriate result.

        This is the main entry point for processing payloads.

        Args:
            raw_payload: JSON string or dict from the webhook

        Returns:
            Dict with processed decision data and metadata
        """
        payload = self.parse_payload(raw_payload)

        handlers = {
            ApprovalType.CREATIVE_APPROVAL: self.handle_creative_approval,
            ApprovalType.VIABILITY_DECISION: self.handle_viability_decision,
            ApprovalType.SEGMENT_PIVOT: self.handle_segment_pivot,
            ApprovalType.VALUE_PIVOT: self.handle_value_pivot,
            ApprovalType.DOWNGRADE_APPROVAL: self.handle_downgrade_approval,
        }

        handler = handlers.get(payload.approval_type)
        if not handler:
            raise ValueError(f"No handler for approval type: {payload.approval_type}")

        result = handler(payload)

        # Persist decision to decision_log (Area 6)
        decision_log_id = self._persist_decision(payload, result)

        result["_meta"] = {
            "kickoff_id": payload.kickoff_id,
            "project_id": payload.project_id,
            "user_id": payload.user_id,
            "approval_type": payload.approval_type.value,
            "timestamp": payload.timestamp,
            "decision_log_id": decision_log_id,  # Track persisted decision
        }

        return result


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def parse_resume_payload(raw_payload: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to parse and process a resume payload.

    Args:
        raw_payload: JSON string or dict from the /resume webhook

    Returns:
        Processed decision data with metadata
    """
    handler = ResumeHandler()
    return handler.process(raw_payload)
