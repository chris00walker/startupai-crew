"""
Validation Events for Event Sourcing.

Tracks all state changes and decisions in the validation flow for audit
and replay capabilities.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class EventType(str, Enum):
    """Types of events that can occur in the validation flow."""

    # Flow lifecycle
    FLOW_STARTED = "flow_started"
    FLOW_COMPLETED = "flow_completed"
    FLOW_FAILED = "flow_failed"

    # Phase transitions
    PHASE_TRANSITION = "phase_transition"

    # Router decisions
    ROUTER_DECISION = "router_decision"

    # Pivot events
    PIVOT_INITIATED = "pivot_initiated"
    PIVOT_COMPLETED = "pivot_completed"

    # Human-in-the-loop
    HITL_REQUESTED = "hitl_requested"
    HITL_APPROVED = "hitl_approved"
    HITL_REJECTED = "hitl_rejected"

    # Crew executions
    CREW_STARTED = "crew_started"
    CREW_COMPLETED = "crew_completed"
    CREW_FAILED = "crew_failed"

    # Evidence updates
    EVIDENCE_COLLECTED = "evidence_collected"
    SIGNAL_UPDATED = "signal_updated"

    # Errors
    ERROR_OCCURRED = "error_occurred"
    ERROR_RECOVERED = "error_recovered"


class ValidationEvent(BaseModel):
    """
    A single event in the validation flow history.

    Events capture state changes, decisions, and actions for:
    - Audit trail and compliance
    - Debugging and troubleshooting
    - Replay and recovery
    - Learning and improvement
    """

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for this event"
    )
    project_id: str = Field(
        description="The project this event belongs to"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the event occurred"
    )
    event_type: EventType = Field(
        description="The type of event"
    )
    from_state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="State before the event (for transitions)"
    )
    to_state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="State after the event (for transitions)"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Why this event occurred"
    )
    triggered_by: Optional[str] = Field(
        default=None,
        description="What triggered this event (method name, router, etc.)"
    )
    evidence_snapshot: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Snapshot of evidence at the time of the event"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the event"
    )

    class Config:
        """Pydantic configuration."""
        use_enum_values = True

    def to_db_record(self) -> Dict[str, Any]:
        """Convert to a database record format."""
        return {
            "id": self.event_id,
            "project_id": self.project_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value if isinstance(self.event_type, EventType) else self.event_type,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "reason": self.reason,
            "triggered_by": self.triggered_by,
            "evidence_snapshot": self.evidence_snapshot,
            "metadata": self.metadata,
        }

    @classmethod
    def from_db_record(cls, record: Dict[str, Any]) -> "ValidationEvent":
        """Create from a database record."""
        return cls(
            event_id=record["id"],
            project_id=record["project_id"],
            timestamp=datetime.fromisoformat(record["timestamp"]) if isinstance(record["timestamp"], str) else record["timestamp"],
            event_type=EventType(record["event_type"]),
            from_state=record.get("from_state"),
            to_state=record.get("to_state"),
            reason=record.get("reason"),
            triggered_by=record.get("triggered_by"),
            evidence_snapshot=record.get("evidence_snapshot"),
            metadata=record.get("metadata", {}),
        )


def create_phase_transition_event(
    project_id: str,
    from_phase: str,
    to_phase: str,
    triggered_by: str,
    reason: Optional[str] = None,
) -> ValidationEvent:
    """Factory function for phase transition events."""
    return ValidationEvent(
        project_id=project_id,
        event_type=EventType.PHASE_TRANSITION,
        from_state={"phase": from_phase},
        to_state={"phase": to_phase},
        reason=reason or f"Transition from {from_phase} to {to_phase}",
        triggered_by=triggered_by,
    )


def create_router_decision_event(
    project_id: str,
    router_name: str,
    decision: str,
    evidence_snapshot: Dict[str, Any],
    reason: Optional[str] = None,
) -> ValidationEvent:
    """Factory function for router decision events."""
    return ValidationEvent(
        project_id=project_id,
        event_type=EventType.ROUTER_DECISION,
        to_state={"decision": decision},
        reason=reason or f"Router {router_name} decided: {decision}",
        triggered_by=router_name,
        evidence_snapshot=evidence_snapshot,
    )


def create_pivot_event(
    project_id: str,
    pivot_type: str,
    from_state: Dict[str, Any],
    to_state: Dict[str, Any],
    reason: str,
) -> ValidationEvent:
    """Factory function for pivot events."""
    return ValidationEvent(
        project_id=project_id,
        event_type=EventType.PIVOT_INITIATED,
        from_state=from_state,
        to_state=to_state,
        reason=reason,
        metadata={"pivot_type": pivot_type},
    )


def create_error_event(
    project_id: str,
    error_code: str,
    error_message: str,
    triggered_by: str,
    context: Optional[Dict[str, Any]] = None,
) -> ValidationEvent:
    """Factory function for error events."""
    return ValidationEvent(
        project_id=project_id,
        event_type=EventType.ERROR_OCCURRED,
        reason=error_message,
        triggered_by=triggered_by,
        metadata={
            "error_code": error_code,
            "context": context or {},
        },
    )
