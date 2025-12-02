"""
State Repository Tests - Persistence Layer Unit Tests

Tests for InMemoryStateRepository and SupabaseStateRepository.
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any
import time

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from startupai.flows.state_schemas import (
    StartupValidationState,
    Phase,
    RiskAxis,
    DesirabilitySignal,
    FeasibilitySignal,
    ViabilitySignal,
)
from startupai.persistence.state_repository import (
    InMemoryStateRepository,
    SupabaseStateRepository,
)
from startupai.persistence.events import ValidationEvent, EventType


# ===========================================================================
# HELPER FIXTURES
# ===========================================================================

@pytest.fixture
def base_state() -> StartupValidationState:
    """Create a minimal state for testing."""
    return StartupValidationState(
        project_id="test_proj_001",
        entrepreneur_input="A SaaS for supply chain optimization",
        phase=Phase.DESIRABILITY,
        current_risk_axis=RiskAxis.DESIRABILITY,
        iteration=1,
    )


@pytest.fixture
def validated_state() -> StartupValidationState:
    """Create a fully validated state for testing."""
    return StartupValidationState(
        project_id="test_proj_002",
        entrepreneur_input="A fintech platform",
        phase=Phase.VALIDATED,
        current_risk_axis=RiskAxis.VIABILITY,
        iteration=3,
        desirability_signal=DesirabilitySignal.STRONG_COMMITMENT,
        feasibility_signal=FeasibilitySignal.GREEN,
        viability_signal=ViabilitySignal.PROFITABLE,
    )


@pytest.fixture
def test_event() -> ValidationEvent:
    """Create a test event."""
    return ValidationEvent(
        project_id="test_proj_001",
        event_type=EventType.PHASE_TRANSITION,
        from_state={"phase": "ideation"},
        to_state={"phase": "desirability"},
        reason="Initial phase transition",
        triggered_by="intake_entrepreneur_input",
    )


@pytest.fixture
def in_memory_repo() -> InMemoryStateRepository:
    """Create an in-memory repository for testing."""
    return InMemoryStateRepository()


# ===========================================================================
# IN-MEMORY REPOSITORY TESTS
# ===========================================================================

class TestInMemoryStateRepository:
    """Test InMemoryStateRepository (no mocking needed)."""

    async def test_save_and_load_state(self, in_memory_repo, base_state):
        """State can be saved and loaded correctly."""
        # Save
        project_id = await in_memory_repo.save_state(base_state)
        assert project_id == base_state.project_id

        # Load
        loaded = await in_memory_repo.load_state(base_state.project_id)
        assert loaded is not None
        assert loaded.project_id == base_state.project_id
        assert loaded.phase == base_state.phase
        assert loaded.entrepreneur_input == base_state.entrepreneur_input

    async def test_load_nonexistent_state_returns_none(self, in_memory_repo):
        """Loading a non-existent project returns None."""
        loaded = await in_memory_repo.load_state("nonexistent_project")
        assert loaded is None

    async def test_save_state_updates_existing(self, in_memory_repo, base_state):
        """Saving again updates the existing state."""
        await in_memory_repo.save_state(base_state)

        # Modify and save again
        base_state.phase = Phase.FEASIBILITY
        base_state.iteration = 2
        await in_memory_repo.save_state(base_state)

        # Load and verify updated
        loaded = await in_memory_repo.load_state(base_state.project_id)
        assert loaded.phase == Phase.FEASIBILITY
        assert loaded.iteration == 2

    async def test_save_event(self, in_memory_repo, test_event):
        """Events can be saved."""
        event_id = await in_memory_repo.save_event(test_event)
        assert event_id == test_event.event_id

    async def test_get_events_returns_saved_events(self, in_memory_repo, test_event):
        """get_events returns previously saved events."""
        await in_memory_repo.save_event(test_event)

        events = await in_memory_repo.get_events(test_event.project_id)
        assert len(events) == 1
        assert events[0].event_id == test_event.event_id
        assert events[0].event_type == EventType.PHASE_TRANSITION

    async def test_get_events_filters_by_type(self, in_memory_repo):
        """get_events filters by event_type correctly."""
        # Save multiple events of different types
        event1 = ValidationEvent(
            project_id="test_proj",
            event_type=EventType.PHASE_TRANSITION,
            reason="Phase change",
        )
        event2 = ValidationEvent(
            project_id="test_proj",
            event_type=EventType.ROUTER_DECISION,
            reason="Router decided",
        )
        event3 = ValidationEvent(
            project_id="test_proj",
            event_type=EventType.PHASE_TRANSITION,
            reason="Another phase change",
        )

        await in_memory_repo.save_event(event1)
        await in_memory_repo.save_event(event2)
        await in_memory_repo.save_event(event3)

        # Filter by PHASE_TRANSITION
        phase_events = await in_memory_repo.get_events(
            "test_proj",
            event_types=[EventType.PHASE_TRANSITION]
        )
        assert len(phase_events) == 2

        # Filter by ROUTER_DECISION
        router_events = await in_memory_repo.get_events(
            "test_proj",
            event_types=[EventType.ROUTER_DECISION]
        )
        assert len(router_events) == 1

    async def test_get_events_respects_limit(self, in_memory_repo):
        """get_events respects the limit parameter."""
        # Save 5 events
        for i in range(5):
            event = ValidationEvent(
                project_id="test_proj",
                event_type=EventType.EVIDENCE_COLLECTED,
                reason=f"Event {i}",
            )
            await in_memory_repo.save_event(event)

        # Get with limit
        events = await in_memory_repo.get_events("test_proj", limit=3)
        assert len(events) == 3

    async def test_get_events_returns_empty_for_unknown_project(self, in_memory_repo):
        """get_events returns empty list for unknown project."""
        events = await in_memory_repo.get_events("unknown_project")
        assert events == []

    async def test_list_projects(self, in_memory_repo, base_state, validated_state):
        """list_projects returns saved projects."""
        await in_memory_repo.save_state(base_state)
        await in_memory_repo.save_state(validated_state)

        projects = await in_memory_repo.list_projects()
        assert len(projects) == 2

        project_ids = [p["project_id"] for p in projects]
        assert base_state.project_id in project_ids
        assert validated_state.project_id in project_ids

    async def test_list_projects_filters_by_phase(self, in_memory_repo, base_state, validated_state):
        """list_projects filters by phase correctly."""
        await in_memory_repo.save_state(base_state)  # DESIRABILITY
        await in_memory_repo.save_state(validated_state)  # VALIDATED

        # Filter by DESIRABILITY
        desirability_projects = await in_memory_repo.list_projects(phase="desirability")
        assert len(desirability_projects) == 1
        assert desirability_projects[0]["project_id"] == base_state.project_id

        # Filter by VALIDATED
        validated_projects = await in_memory_repo.list_projects(phase="validated")
        assert len(validated_projects) == 1
        assert validated_projects[0]["project_id"] == validated_state.project_id

    async def test_list_projects_respects_limit(self, in_memory_repo):
        """list_projects respects the limit parameter."""
        # Save 5 states
        for i in range(5):
            state = StartupValidationState(
                project_id=f"proj_{i}",
                entrepreneur_input=f"Business {i}",
                phase=Phase.IDEATION,
            )
            await in_memory_repo.save_state(state)

        projects = await in_memory_repo.list_projects(limit=3)
        assert len(projects) == 3

    async def test_clear_removes_all_data(self, in_memory_repo, base_state, test_event):
        """clear() removes all states and events."""
        await in_memory_repo.save_state(base_state)
        await in_memory_repo.save_event(test_event)

        in_memory_repo.clear()

        # Verify everything is gone
        assert await in_memory_repo.load_state(base_state.project_id) is None
        assert await in_memory_repo.get_events(test_event.project_id) == []
        assert await in_memory_repo.list_projects() == []


# ===========================================================================
# SUPABASE REPOSITORY TESTS (with mocks)
# ===========================================================================

class TestSupabaseStateRepository:
    """Test SupabaseStateRepository with mocked Supabase client."""

    @pytest.fixture
    def mock_supabase_client(self):
        """Create a mock Supabase client."""
        client = MagicMock()

        # Setup table operations
        table = MagicMock()
        client.table.return_value = table

        # Setup select chain
        select = MagicMock()
        table.select.return_value = select
        select.eq.return_value = select
        select.order.return_value = select
        select.limit.return_value = select
        select.in_.return_value = select
        select.single.return_value = select

        # Default empty response
        select.execute.return_value = Mock(data=None)

        # Setup insert/upsert
        table.insert.return_value.execute.return_value = Mock(data={})
        table.upsert.return_value.execute.return_value = Mock(data={})

        return client

    @pytest.fixture
    def supabase_repo(self, mock_supabase_client):
        """Create SupabaseStateRepository with mocked client."""
        with patch('startupai.persistence.state_repository.get_supabase_client',
                   return_value=mock_supabase_client):
            repo = SupabaseStateRepository()
            yield repo

    async def test_save_state_upserts(self, supabase_repo, mock_supabase_client, base_state):
        """save_state uses upsert with correct record structure."""
        await supabase_repo.save_state(base_state)

        # Verify upsert was called
        mock_supabase_client.table.assert_called_with("flow_executions")
        mock_supabase_client.table().upsert.assert_called_once()

        # Check the record structure
        call_args = mock_supabase_client.table().upsert.call_args
        record = call_args[0][0]  # First positional argument

        assert record["project_id"] == base_state.project_id
        assert record["phase"] == "desirability"
        assert record["iteration"] == base_state.iteration
        assert "full_state" in record
        assert "updated_at" in record

    async def test_save_state_serializes_enums(self, supabase_repo, mock_supabase_client, validated_state):
        """Enum values are serialized to strings."""
        await supabase_repo.save_state(validated_state)

        call_args = mock_supabase_client.table().upsert.call_args
        record = call_args[0][0]

        # Verify enums are serialized as strings
        assert record["phase"] == "validated"
        assert record["desirability_signal"] == "strong_commitment"
        assert record["feasibility_signal"] == "green"
        assert record["viability_signal"] == "profitable"

    async def test_load_state_reconstructs(self, supabase_repo, mock_supabase_client, base_state):
        """load_state reconstructs StartupValidationState from JSON."""
        # Setup mock response with full_state data
        state_dict = base_state.dict()
        mock_supabase_client.table().select().eq().single().execute.return_value = Mock(
            data={"full_state": state_dict}
        )

        loaded = await supabase_repo.load_state(base_state.project_id)

        assert loaded is not None
        assert loaded.project_id == base_state.project_id
        assert loaded.phase == base_state.phase

        # Verify correct query was made
        mock_supabase_client.table.assert_called_with("flow_executions")
        mock_supabase_client.table().select.assert_called_with("full_state")

    async def test_load_state_not_found(self, supabase_repo, mock_supabase_client):
        """load_state returns None for missing project."""
        mock_supabase_client.table().select().eq().single().execute.return_value = Mock(data=None)

        loaded = await supabase_repo.load_state("nonexistent")
        assert loaded is None

    async def test_save_event_inserts(self, supabase_repo, mock_supabase_client, test_event):
        """save_event inserts event record."""
        await supabase_repo.save_event(test_event)

        mock_supabase_client.table.assert_called_with("validation_events")
        mock_supabase_client.table().insert.assert_called_once()

        # Check record structure
        call_args = mock_supabase_client.table().insert.call_args
        record = call_args[0][0]

        assert record["id"] == test_event.event_id
        assert record["project_id"] == test_event.project_id
        assert record["event_type"] == "phase_transition"

    async def test_get_events_queries_correctly(self, supabase_repo, mock_supabase_client):
        """get_events builds correct query."""
        # Setup mock response
        mock_supabase_client.table().select().eq().order().limit().execute.return_value = Mock(data=[])

        await supabase_repo.get_events("test_proj", limit=50)

        # Verify query chain
        mock_supabase_client.table.assert_called_with("validation_events")
        mock_supabase_client.table().select.assert_called_with("*")
        mock_supabase_client.table().select().eq.assert_called_with("project_id", "test_proj")

    async def test_get_events_with_type_filter(self, supabase_repo, mock_supabase_client):
        """get_events applies type filter to query."""
        mock_supabase_client.table().select().eq().order().limit().in_().execute.return_value = Mock(data=[])

        await supabase_repo.get_events(
            "test_proj",
            event_types=[EventType.PHASE_TRANSITION, EventType.ROUTER_DECISION]
        )

        # Verify in_ was called with event type values
        mock_supabase_client.table().select().eq().order().limit().in_.assert_called_with(
            "event_type", ["phase_transition", "router_decision"]
        )

    async def test_list_projects_queries_correctly(self, supabase_repo, mock_supabase_client):
        """list_projects builds correct query."""
        mock_supabase_client.table().select().order().limit().execute.return_value = Mock(data=[])

        await supabase_repo.list_projects(limit=25)

        mock_supabase_client.table.assert_called_with("flow_executions")
        # Verify select includes expected columns
        select_call = mock_supabase_client.table().select.call_args
        assert "project_id" in select_call[0][0]
        assert "phase" in select_call[0][0]

    async def test_list_projects_with_phase_filter(self, supabase_repo, mock_supabase_client):
        """list_projects applies phase filter."""
        mock_supabase_client.table().select().order().limit().eq().execute.return_value = Mock(data=[])

        await supabase_repo.list_projects(phase="desirability")

        # Verify eq was called for phase filter
        mock_supabase_client.table().select().order().limit().eq.assert_called_with("phase", "desirability")


# ===========================================================================
# EDGE CASE TESTS
# ===========================================================================

class TestRepositoryEdgeCases:
    """Test edge cases and boundary conditions."""

    async def test_in_memory_handles_multiple_projects(self, in_memory_repo):
        """InMemoryStateRepository handles multiple projects correctly."""
        states = []
        for i in range(10):
            state = StartupValidationState(
                project_id=f"proj_{i:03d}",
                entrepreneur_input=f"Business idea {i}",
                phase=Phase.IDEATION,
            )
            states.append(state)
            await in_memory_repo.save_state(state)

        # Verify all can be loaded
        for state in states:
            loaded = await in_memory_repo.load_state(state.project_id)
            assert loaded is not None
            assert loaded.project_id == state.project_id

    async def test_events_sorted_by_timestamp(self, in_memory_repo):
        """Events are sorted by timestamp (newest first)."""
        events = []
        for i in range(3):
            event = ValidationEvent(
                project_id="test_proj",
                event_type=EventType.EVIDENCE_COLLECTED,
                reason=f"Event {i}",
            )
            events.append(event)
            await in_memory_repo.save_event(event)
            await asyncio.sleep(0.01)  # Small delay to ensure different timestamps

        retrieved = await in_memory_repo.get_events("test_proj")

        # Should be sorted newest first
        for i in range(len(retrieved) - 1):
            assert retrieved[i].timestamp >= retrieved[i + 1].timestamp

    async def test_state_with_complex_nested_data(self, in_memory_repo):
        """State with complex nested structures is preserved."""
        state = StartupValidationState(
            project_id="complex_001",
            entrepreneur_input="Complex business",
            phase=Phase.DESIRABILITY,
            business_idea="AI-powered analytics",
            target_segments=["SMBs", "Enterprises", "Startups"],
        )
        # Add some customer profiles
        state.customer_profiles["SMBs"] = {
            "jobs": ["Reduce costs", "Increase efficiency"],
            "pains": ["Manual processes", "Data silos"],
            "gains": ["Automation", "Insights"],
        }

        await in_memory_repo.save_state(state)
        loaded = await in_memory_repo.load_state("complex_001")

        assert loaded.target_segments == ["SMBs", "Enterprises", "Startups"]
        assert loaded.customer_profiles["SMBs"]["jobs"] == ["Reduce costs", "Increase efficiency"]
