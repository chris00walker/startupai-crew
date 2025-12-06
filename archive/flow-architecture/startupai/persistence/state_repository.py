"""
State Repository Pattern for Validation Flow.

Provides an abstract interface for state persistence with a concrete
Supabase implementation.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from startupai.flows.state_schemas import StartupValidationState
from startupai.persistence.events import ValidationEvent, EventType
from startupai.persistence.connection import get_supabase_client


class StateRepository(ABC):
    """
    Abstract base class for state persistence.

    This allows swapping storage backends (e.g., Supabase, local file, etc.)
    without changing the flow logic.
    """

    @abstractmethod
    async def save_state(self, state: StartupValidationState) -> str:
        """
        Save or update the validation state.

        Args:
            state: The current state to persist

        Returns:
            The project_id of the saved state
        """
        pass

    @abstractmethod
    async def load_state(self, project_id: str) -> Optional[StartupValidationState]:
        """
        Load a validation state by project ID.

        Args:
            project_id: The unique identifier for the project

        Returns:
            The loaded state or None if not found
        """
        pass

    @abstractmethod
    async def save_event(self, event: ValidationEvent) -> str:
        """
        Save a validation event.

        Args:
            event: The event to persist

        Returns:
            The event_id of the saved event
        """
        pass

    @abstractmethod
    async def get_events(
        self,
        project_id: str,
        event_types: Optional[List[EventType]] = None,
        limit: int = 100,
    ) -> List[ValidationEvent]:
        """
        Get events for a project.

        Args:
            project_id: The project to get events for
            event_types: Optional filter by event type
            limit: Maximum number of events to return

        Returns:
            List of validation events
        """
        pass

    @abstractmethod
    async def list_projects(
        self,
        phase: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List projects with optional filtering.

        Args:
            phase: Optional filter by current phase
            limit: Maximum number of projects to return

        Returns:
            List of project summaries
        """
        pass


class SupabaseStateRepository(StateRepository):
    """
    Supabase implementation of the StateRepository.

    Uses two tables:
    - flow_executions: Stores the full state with indexed columns
    - validation_events: Stores the event log for audit/replay
    """

    def __init__(self):
        """Initialize with Supabase client."""
        self._client = get_supabase_client()

    async def save_state(self, state: StartupValidationState) -> str:
        """Save or update the validation state in Supabase."""
        # Convert state to dict for storage
        state_dict = state.dict()

        # Prepare the record with indexed columns
        record = {
            "project_id": state.project_id,
            "phase": state.phase.value if hasattr(state.phase, 'value') else str(state.phase),
            "current_risk_axis": state.current_risk_axis.value if hasattr(state.current_risk_axis, 'value') else str(state.current_risk_axis),
            "iteration": state.iteration,
            "desirability_signal": state.desirability_signal.value if hasattr(state.desirability_signal, 'value') else str(state.desirability_signal),
            "feasibility_signal": state.feasibility_signal.value if hasattr(state.feasibility_signal, 'value') else str(state.feasibility_signal),
            "viability_signal": state.viability_signal.value if hasattr(state.viability_signal, 'value') else str(state.viability_signal),
            "full_state": state_dict,
            "updated_at": datetime.now().isoformat(),
        }

        # Upsert (insert or update based on project_id)
        result = self._client.table("flow_executions").upsert(
            record,
            on_conflict="project_id"
        ).execute()

        return state.project_id

    async def load_state(self, project_id: str) -> Optional[StartupValidationState]:
        """Load a validation state from Supabase."""
        result = self._client.table("flow_executions").select(
            "full_state"
        ).eq(
            "project_id", project_id
        ).single().execute()

        if not result.data:
            return None

        # Reconstruct the state from the JSON
        return StartupValidationState(**result.data["full_state"])

    async def save_event(self, event: ValidationEvent) -> str:
        """Save a validation event to Supabase."""
        record = event.to_db_record()

        self._client.table("validation_events").insert(record).execute()

        return event.event_id

    async def get_events(
        self,
        project_id: str,
        event_types: Optional[List[EventType]] = None,
        limit: int = 100,
    ) -> List[ValidationEvent]:
        """Get events for a project from Supabase."""
        query = self._client.table("validation_events").select("*").eq(
            "project_id", project_id
        ).order("timestamp", desc=True).limit(limit)

        if event_types:
            type_values = [et.value for et in event_types]
            query = query.in_("event_type", type_values)

        result = query.execute()

        return [ValidationEvent.from_db_record(r) for r in result.data]

    async def list_projects(
        self,
        phase: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List projects from Supabase."""
        query = self._client.table("flow_executions").select(
            "project_id, phase, current_risk_axis, iteration, desirability_signal, "
            "feasibility_signal, viability_signal, created_at, updated_at"
        ).order("updated_at", desc=True).limit(limit)

        if phase:
            query = query.eq("phase", phase)

        result = query.execute()

        return result.data


class InMemoryStateRepository(StateRepository):
    """
    In-memory implementation for testing.

    Stores state and events in dictionaries for fast testing without
    database dependencies.
    """

    def __init__(self):
        """Initialize empty storage."""
        self._states: Dict[str, StartupValidationState] = {}
        self._events: Dict[str, List[ValidationEvent]] = {}

    async def save_state(self, state: StartupValidationState) -> str:
        """Save state in memory."""
        self._states[state.project_id] = state
        return state.project_id

    async def load_state(self, project_id: str) -> Optional[StartupValidationState]:
        """Load state from memory."""
        return self._states.get(project_id)

    async def save_event(self, event: ValidationEvent) -> str:
        """Save event in memory."""
        if event.project_id not in self._events:
            self._events[event.project_id] = []
        self._events[event.project_id].append(event)
        return event.event_id

    async def get_events(
        self,
        project_id: str,
        event_types: Optional[List[EventType]] = None,
        limit: int = 100,
    ) -> List[ValidationEvent]:
        """Get events from memory."""
        events = self._events.get(project_id, [])

        if event_types:
            events = [e for e in events if e.event_type in event_types]

        # Sort by timestamp descending and apply limit
        events = sorted(events, key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    async def list_projects(
        self,
        phase: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List projects from memory."""
        projects = []
        for project_id, state in self._states.items():
            phase_value = state.phase.value if hasattr(state.phase, 'value') else str(state.phase)
            if phase and phase_value != phase:
                continue
            projects.append({
                "project_id": project_id,
                "phase": phase_value,
                "iteration": state.iteration,
            })

        return projects[:limit]

    def clear(self) -> None:
        """Clear all stored data (for testing)."""
        self._states.clear()
        self._events.clear()
