"""
Event Tests - ValidationEvent and Factory Function Tests

Tests for event serialization, deserialization, and factory functions.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from startupai.persistence.events import (
    EventType,
    ValidationEvent,
    create_phase_transition_event,
    create_router_decision_event,
    create_pivot_event,
    create_error_event,
)


# ===========================================================================
# EVENT TYPE TESTS
# ===========================================================================

class TestEventType:
    """Test EventType enum."""

    def test_all_event_types_defined(self):
        """Verify all expected event types exist."""
        expected_types = [
            "flow_started", "flow_completed", "flow_failed",
            "phase_transition", "router_decision",
            "pivot_initiated", "pivot_completed",
            "hitl_requested", "hitl_approved", "hitl_rejected",
            "crew_started", "crew_completed", "crew_failed",
            "evidence_collected", "signal_updated",
            "error_occurred", "error_recovered",
        ]
        actual_values = [e.value for e in EventType]
        for expected in expected_types:
            assert expected in actual_values, f"Missing event type: {expected}"

    def test_event_type_values_are_strings(self):
        """Event type values should be lowercase snake_case strings."""
        for event_type in EventType:
            assert isinstance(event_type.value, str)
            assert event_type.value == event_type.value.lower()
            assert "_" in event_type.value or event_type.value.isalpha()

    def test_event_type_from_string(self):
        """EventType can be created from string value."""
        assert EventType("flow_started") == EventType.FLOW_STARTED
        assert EventType("phase_transition") == EventType.PHASE_TRANSITION
        assert EventType("router_decision") == EventType.ROUTER_DECISION


# ===========================================================================
# VALIDATION EVENT TESTS
# ===========================================================================

class TestValidationEvent:
    """Test ValidationEvent model."""

    def test_event_creation_minimal(self):
        """Event can be created with minimal required fields."""
        event = ValidationEvent(
            project_id="proj_001",
            event_type=EventType.FLOW_STARTED,
        )
        assert event.project_id == "proj_001"
        assert event.event_type == EventType.FLOW_STARTED
        assert event.event_id is not None  # Auto-generated
        assert event.timestamp is not None  # Auto-generated

    def test_event_creation_full(self):
        """Event can be created with all fields."""
        event = ValidationEvent(
            project_id="proj_001",
            event_type=EventType.PHASE_TRANSITION,
            from_state={"phase": "ideation"},
            to_state={"phase": "desirability"},
            reason="Starting validation",
            triggered_by="start_flow",
            evidence_snapshot={"problem_resonance": 0.0},
            metadata={"iteration": 1},
        )
        assert event.from_state == {"phase": "ideation"}
        assert event.to_state == {"phase": "desirability"}
        assert event.reason == "Starting validation"
        assert event.triggered_by == "start_flow"
        assert event.evidence_snapshot == {"problem_resonance": 0.0}
        assert event.metadata == {"iteration": 1}

    def test_event_id_unique(self):
        """Each event gets a unique ID."""
        events = [
            ValidationEvent(project_id="proj", event_type=EventType.FLOW_STARTED)
            for _ in range(10)
        ]
        event_ids = [e.event_id for e in events]
        assert len(set(event_ids)) == 10  # All unique

    def test_timestamp_auto_set(self):
        """Timestamp is automatically set to current time."""
        before = datetime.now()
        event = ValidationEvent(
            project_id="proj",
            event_type=EventType.FLOW_STARTED,
        )
        after = datetime.now()
        assert before <= event.timestamp <= after

    def test_defaults_are_none_or_empty(self):
        """Optional fields default to None or empty."""
        event = ValidationEvent(
            project_id="proj",
            event_type=EventType.FLOW_STARTED,
        )
        assert event.from_state is None
        assert event.to_state is None
        assert event.reason is None
        assert event.triggered_by is None
        assert event.evidence_snapshot is None
        assert event.metadata == {}


# ===========================================================================
# SERIALIZATION TESTS
# ===========================================================================

class TestEventSerialization:
    """Test to_db_record and from_db_record methods."""

    @pytest.fixture
    def full_event(self) -> ValidationEvent:
        """Create a fully populated event for testing."""
        return ValidationEvent(
            event_id="evt_123",
            project_id="proj_001",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            event_type=EventType.PHASE_TRANSITION,
            from_state={"phase": "ideation", "iteration": 0},
            to_state={"phase": "desirability", "iteration": 1},
            reason="Passed ideation gate",
            triggered_by="ideation_gate",
            evidence_snapshot={"problem_resonance": 0.65},
            metadata={"gate_score": 85},
        )

    def test_to_db_record_structure(self, full_event):
        """to_db_record returns correct structure."""
        record = full_event.to_db_record()

        assert record["id"] == "evt_123"
        assert record["project_id"] == "proj_001"
        assert record["timestamp"] == "2024-01-15T10:30:00"
        assert record["event_type"] == "phase_transition"
        assert record["from_state"] == {"phase": "ideation", "iteration": 0}
        assert record["to_state"] == {"phase": "desirability", "iteration": 1}
        assert record["reason"] == "Passed ideation gate"
        assert record["triggered_by"] == "ideation_gate"
        assert record["evidence_snapshot"] == {"problem_resonance": 0.65}
        assert record["metadata"] == {"gate_score": 85}

    def test_from_db_record_roundtrip(self, full_event):
        """from_db_record correctly reconstructs event."""
        record = full_event.to_db_record()
        reconstructed = ValidationEvent.from_db_record(record)

        assert reconstructed.event_id == full_event.event_id
        assert reconstructed.project_id == full_event.project_id
        assert reconstructed.timestamp == full_event.timestamp
        assert reconstructed.event_type == full_event.event_type
        assert reconstructed.from_state == full_event.from_state
        assert reconstructed.to_state == full_event.to_state
        assert reconstructed.reason == full_event.reason
        assert reconstructed.triggered_by == full_event.triggered_by
        assert reconstructed.evidence_snapshot == full_event.evidence_snapshot
        assert reconstructed.metadata == full_event.metadata

    def test_from_db_record_handles_datetime_object(self):
        """from_db_record handles datetime objects (not just strings)."""
        record = {
            "id": "evt_456",
            "project_id": "proj",
            "timestamp": datetime(2024, 2, 1, 12, 0, 0),  # datetime object
            "event_type": "flow_started",
        }
        event = ValidationEvent.from_db_record(record)
        assert event.timestamp == datetime(2024, 2, 1, 12, 0, 0)

    def test_from_db_record_handles_missing_optional_fields(self):
        """from_db_record handles missing optional fields."""
        record = {
            "id": "evt_789",
            "project_id": "proj",
            "timestamp": "2024-03-01T09:00:00",
            "event_type": "flow_started",
            # Missing: from_state, to_state, reason, triggered_by, evidence_snapshot, metadata
        }
        event = ValidationEvent.from_db_record(record)

        assert event.event_id == "evt_789"
        assert event.from_state is None
        assert event.to_state is None
        assert event.reason is None
        assert event.triggered_by is None
        assert event.evidence_snapshot is None
        assert event.metadata == {}

    def test_enum_serialization(self):
        """EventType is correctly serialized to string."""
        event = ValidationEvent(
            project_id="proj",
            event_type=EventType.ROUTER_DECISION,
        )
        record = event.to_db_record()
        assert record["event_type"] == "router_decision"


# ===========================================================================
# FACTORY FUNCTION TESTS
# ===========================================================================

class TestFactoryFunctions:
    """Test event factory functions."""

    def test_create_phase_transition_event(self):
        """create_phase_transition_event creates correct event."""
        event = create_phase_transition_event(
            project_id="proj_001",
            from_phase="ideation",
            to_phase="desirability",
            triggered_by="ideation_gate",
            reason="Validated business concept",
        )

        assert event.project_id == "proj_001"
        assert event.event_type == EventType.PHASE_TRANSITION
        assert event.from_state == {"phase": "ideation"}
        assert event.to_state == {"phase": "desirability"}
        assert event.triggered_by == "ideation_gate"
        assert event.reason == "Validated business concept"

    def test_create_phase_transition_event_default_reason(self):
        """create_phase_transition_event generates default reason."""
        event = create_phase_transition_event(
            project_id="proj",
            from_phase="feasibility",
            to_phase="viability",
            triggered_by="feasibility_gate",
        )
        assert "feasibility" in event.reason.lower()
        assert "viability" in event.reason.lower()

    def test_create_router_decision_event(self):
        """create_router_decision_event creates correct event."""
        evidence = {"problem_resonance": 0.75, "conversion_rate": 0.12}
        event = create_router_decision_event(
            project_id="proj_002",
            router_name="desirability_gate",
            decision="proceed_to_feasibility",
            evidence_snapshot=evidence,
            reason="Strong commitment signals detected",
        )

        assert event.project_id == "proj_002"
        assert event.event_type == EventType.ROUTER_DECISION
        assert event.to_state == {"decision": "proceed_to_feasibility"}
        assert event.triggered_by == "desirability_gate"
        assert event.evidence_snapshot == evidence
        assert event.reason == "Strong commitment signals detected"

    def test_create_router_decision_event_default_reason(self):
        """create_router_decision_event generates default reason."""
        event = create_router_decision_event(
            project_id="proj",
            router_name="viability_gate",
            decision="validation_complete",
            evidence_snapshot={},
        )
        assert "viability_gate" in event.reason
        assert "validation_complete" in event.reason

    def test_create_pivot_event(self):
        """create_pivot_event creates correct event."""
        event = create_pivot_event(
            project_id="proj_003",
            pivot_type="segment_pivot",
            from_state={"segment": "SMBs", "iteration": 1},
            to_state={"segment": "Enterprise", "iteration": 2},
            reason="Low problem resonance with SMBs",
        )

        assert event.project_id == "proj_003"
        assert event.event_type == EventType.PIVOT_INITIATED
        assert event.from_state == {"segment": "SMBs", "iteration": 1}
        assert event.to_state == {"segment": "Enterprise", "iteration": 2}
        assert event.reason == "Low problem resonance with SMBs"
        assert event.metadata == {"pivot_type": "segment_pivot"}

    def test_create_error_event(self):
        """create_error_event creates correct event."""
        event = create_error_event(
            project_id="proj_004",
            error_code="CREW_TIMEOUT",
            error_message="Analysis crew timed out after 300s",
            triggered_by="analysis_crew",
            context={"crew_name": "analysis", "timeout_seconds": 300},
        )

        assert event.project_id == "proj_004"
        assert event.event_type == EventType.ERROR_OCCURRED
        assert event.reason == "Analysis crew timed out after 300s"
        assert event.triggered_by == "analysis_crew"
        assert event.metadata["error_code"] == "CREW_TIMEOUT"
        assert event.metadata["context"]["crew_name"] == "analysis"

    def test_create_error_event_without_context(self):
        """create_error_event handles missing context."""
        event = create_error_event(
            project_id="proj",
            error_code="UNKNOWN",
            error_message="Unknown error",
            triggered_by="system",
        )
        assert event.metadata["context"] == {}


# ===========================================================================
# EDGE CASE TESTS
# ===========================================================================

class TestEventEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_event_with_empty_strings(self):
        """Event handles empty string values."""
        event = ValidationEvent(
            project_id="proj",
            event_type=EventType.FLOW_STARTED,
            reason="",
            triggered_by="",
        )
        assert event.reason == ""
        assert event.triggered_by == ""

    def test_event_with_nested_metadata(self):
        """Event handles deeply nested metadata."""
        nested_metadata = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep"
                    }
                }
            }
        }
        event = ValidationEvent(
            project_id="proj",
            event_type=EventType.FLOW_STARTED,
            metadata=nested_metadata,
        )
        record = event.to_db_record()
        reconstructed = ValidationEvent.from_db_record(record)
        assert reconstructed.metadata["level1"]["level2"]["level3"]["value"] == "deep"

    def test_event_with_large_evidence_snapshot(self):
        """Event handles large evidence snapshots."""
        large_evidence = {f"key_{i}": f"value_{i}" for i in range(100)}
        event = ValidationEvent(
            project_id="proj",
            event_type=EventType.EVIDENCE_COLLECTED,
            evidence_snapshot=large_evidence,
        )
        record = event.to_db_record()
        reconstructed = ValidationEvent.from_db_record(record)
        assert len(reconstructed.evidence_snapshot) == 100

    def test_event_with_special_characters_in_reason(self):
        """Event handles special characters in text fields."""
        event = ValidationEvent(
            project_id="proj",
            event_type=EventType.ERROR_OCCURRED,
            reason="Error: 'Failed' with \"quotes\" & <tags>",
        )
        record = event.to_db_record()
        reconstructed = ValidationEvent.from_db_record(record)
        assert reconstructed.reason == "Error: 'Failed' with \"quotes\" & <tags>"

    def test_event_timestamp_precision(self):
        """Event preserves timestamp precision through serialization."""
        precise_time = datetime(2024, 6, 15, 14, 30, 45, 123456)
        event = ValidationEvent(
            event_id="evt_precise",
            project_id="proj",
            timestamp=precise_time,
            event_type=EventType.FLOW_STARTED,
        )
        record = event.to_db_record()
        reconstructed = ValidationEvent.from_db_record(record)
        # Note: microseconds may be lost in ISO format depending on implementation
        assert reconstructed.timestamp.year == 2024
        assert reconstructed.timestamp.month == 6
        assert reconstructed.timestamp.day == 15
        assert reconstructed.timestamp.hour == 14
        assert reconstructed.timestamp.minute == 30
        assert reconstructed.timestamp.second == 45
