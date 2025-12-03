"""
Pytest Configuration and Fixtures.

Provides reusable fixtures for testing the validation flow.
"""

import pytest
from typing import Dict, Any
from datetime import datetime
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables for tests
# 1. First load from ~/.secrets/startupai (shared secrets via direnv pattern)
# 2. Then load from local .env (project-specific overrides)
secrets_file = Path.home() / ".secrets" / "startupai"
if secrets_file.exists():
    load_dotenv(secrets_file)
load_dotenv()  # Load local .env (won't override existing vars)

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from startupai.flows.state_schemas import (
    StartupValidationState,
    Phase,
    RiskAxis,
    DesirabilitySignal,
    FeasibilitySignal,
    ViabilitySignal,
    PivotType,
    HumanApprovalStatus,
)
from startupai.persistence.state_repository import InMemoryStateRepository
from startupai.persistence.events import ValidationEvent, EventType


# ===========================================================================
# STATE FIXTURES
# ===========================================================================

@pytest.fixture
def base_state() -> StartupValidationState:
    """Create a minimal base state for testing."""
    return StartupValidationState(
        project_id="test_001",
        entrepreneur_input="A B2B SaaS platform for supply chain optimization",
        phase=Phase.IDEATION,
    )


@pytest.fixture
def desirability_state(base_state) -> StartupValidationState:
    """Create a state in desirability phase."""
    base_state.phase = Phase.DESIRABILITY
    base_state.current_risk_axis = RiskAxis.DESIRABILITY
    base_state.business_idea = "AI-powered supply chain optimizer"
    base_state.target_segments = ["Logistics Managers", "Procurement Officers"]
    base_state.current_segment = "Logistics Managers"
    return base_state


@pytest.fixture
def feasibility_state(desirability_state) -> StartupValidationState:
    """Create a state in feasibility phase with desirability validated."""
    desirability_state.phase = Phase.FEASIBILITY
    desirability_state.current_risk_axis = RiskAxis.FEASIBILITY
    desirability_state.desirability_signal = DesirabilitySignal.STRONG_COMMITMENT
    return desirability_state


@pytest.fixture
def viability_state(feasibility_state) -> StartupValidationState:
    """Create a state in viability phase with feasibility validated."""
    feasibility_state.phase = Phase.VIABILITY
    feasibility_state.current_risk_axis = RiskAxis.VIABILITY
    feasibility_state.feasibility_signal = FeasibilitySignal.GREEN
    return feasibility_state


@pytest.fixture
def validated_state(viability_state) -> StartupValidationState:
    """Create a fully validated state."""
    viability_state.phase = Phase.VALIDATED
    viability_state.viability_signal = ViabilitySignal.PROFITABLE
    return viability_state


# ===========================================================================
# SIGNAL COMBINATION FIXTURES
# ===========================================================================

@pytest.fixture
def no_interest_state(desirability_state) -> StartupValidationState:
    """State with no customer interest (triggers segment pivot)."""
    desirability_state.desirability_signal = DesirabilitySignal.NO_INTEREST
    return desirability_state


@pytest.fixture
def weak_interest_state(desirability_state) -> StartupValidationState:
    """State with weak interest (triggers value pivot)."""
    desirability_state.desirability_signal = DesirabilitySignal.WEAK_INTEREST
    return desirability_state


@pytest.fixture
def red_feasibility_state(feasibility_state) -> StartupValidationState:
    """State with impossible feasibility (triggers kill or downgrade)."""
    feasibility_state.feasibility_signal = FeasibilitySignal.RED_IMPOSSIBLE
    return feasibility_state


@pytest.fixture
def constrained_feasibility_state(feasibility_state) -> StartupValidationState:
    """State with constrained feasibility (triggers downgrade testing)."""
    feasibility_state.feasibility_signal = FeasibilitySignal.ORANGE_CONSTRAINED
    return feasibility_state


@pytest.fixture
def underwater_viability_state(viability_state) -> StartupValidationState:
    """State with underwater unit economics (triggers strategic pivot)."""
    viability_state.viability_signal = ViabilitySignal.UNDERWATER
    return viability_state


@pytest.fixture
def zombie_market_state(viability_state) -> StartupValidationState:
    """State with zombie market signal (triggers price/cost pivot)."""
    viability_state.viability_signal = ViabilitySignal.ZOMBIE_MARKET
    return viability_state


# ===========================================================================
# REPOSITORY FIXTURES
# ===========================================================================

@pytest.fixture
def mock_repository() -> InMemoryStateRepository:
    """Create an in-memory repository for testing."""
    return InMemoryStateRepository()


@pytest.fixture
def populated_repository(mock_repository, base_state) -> InMemoryStateRepository:
    """Repository with a state already saved."""
    import asyncio
    asyncio.get_event_loop().run_until_complete(
        mock_repository.save_state(base_state)
    )
    return mock_repository


# ===========================================================================
# MOCK FIXTURES
# ===========================================================================

@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    with patch("startupai.persistence.connection.create_client") as mock:
        client = Mock()
        client.table.return_value.upsert.return_value.execute.return_value = Mock()
        client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=None)
        client.table.return_value.insert.return_value.execute.return_value = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings API."""
    with patch("openai.OpenAI") as mock:
        client = Mock()
        response = Mock()
        response.data = [Mock(embedding=[0.1] * 1536)]
        client.embeddings.create.return_value = response
        mock.return_value = client
        yield mock


# ===========================================================================
# CREW MOCK FIXTURES
# ===========================================================================

@pytest.fixture
def mock_service_crew():
    """Mock ServiceCrew for testing without execution."""
    with patch("startupai.flows._founder_validation_flow.ServiceCrew") as mock:
        crew_instance = Mock()
        crew_instance.kickoff.return_value = {"status": "success", "output": "mocked"}
        mock.return_value = crew_instance
        yield mock


@pytest.fixture
def mock_analysis_crew():
    """Mock AnalysisCrew for testing without execution."""
    with patch("startupai.flows._founder_validation_flow.AnalysisCrew") as mock:
        crew_instance = Mock()
        crew_instance.kickoff.return_value = {"status": "success", "output": "mocked"}
        mock.return_value = crew_instance
        yield mock


@pytest.fixture
def mock_governance_crew():
    """Mock GovernanceCrew for testing without execution."""
    with patch("startupai.flows._founder_validation_flow.GovernanceCrew") as mock:
        crew_instance = Mock()
        crew_instance.kickoff.return_value = {"status": "success", "output": "mocked"}
        mock.return_value = crew_instance
        yield mock


@pytest.fixture
def mock_build_crew():
    """Mock BuildCrew for testing without execution."""
    with patch("startupai.flows._founder_validation_flow.BuildCrew") as mock:
        crew_instance = Mock()
        crew_instance.kickoff.return_value = {"status": "success", "output": "mocked"}
        mock.return_value = crew_instance
        yield mock


@pytest.fixture
def mock_growth_crew():
    """Mock GrowthCrew for testing without execution."""
    with patch("startupai.flows._founder_validation_flow.GrowthCrew") as mock:
        crew_instance = Mock()
        crew_instance.kickoff.return_value = {"status": "success", "output": "mocked"}
        mock.return_value = crew_instance
        yield mock


@pytest.fixture
def mock_synthesis_crew():
    """Mock SynthesisCrew for testing without execution."""
    with patch("startupai.flows._founder_validation_flow.SynthesisCrew") as mock:
        crew_instance = Mock()
        crew_instance.kickoff.return_value = {"status": "success", "output": "mocked"}
        mock.return_value = crew_instance
        yield mock


@pytest.fixture
def mock_finance_crew():
    """Mock FinanceCrew for testing without execution."""
    with patch("startupai.flows._founder_validation_flow.FinanceCrew") as mock:
        crew_instance = Mock()
        crew_instance.kickoff.return_value = {"status": "success", "output": "mocked"}
        mock.return_value = crew_instance
        yield mock


@pytest.fixture
def mock_all_crews(
    mock_service_crew,
    mock_analysis_crew,
    mock_governance_crew,
    mock_build_crew,
    mock_growth_crew,
    mock_synthesis_crew,
    mock_finance_crew,
):
    """
    Composite fixture that mocks all crews at once.

    Usage:
        def test_flow_with_mocked_crews(mock_all_crews):
            # All crews are mocked, flow can execute without LLM calls
            pass
    """
    return {
        "service": mock_service_crew,
        "analysis": mock_analysis_crew,
        "governance": mock_governance_crew,
        "build": mock_build_crew,
        "growth": mock_growth_crew,
        "synthesis": mock_synthesis_crew,
        "finance": mock_finance_crew,
    }


# ===========================================================================
# UTILITY FUNCTIONS
# ===========================================================================

def create_test_state(**overrides) -> StartupValidationState:
    """Create a test state with optional overrides."""
    defaults = {
        "project_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "entrepreneur_input": "Test business idea",
        "phase": Phase.IDEATION,
    }
    defaults.update(overrides)
    return StartupValidationState(**defaults)


def create_test_event(**overrides) -> ValidationEvent:
    """Create a test event with optional overrides."""
    defaults = {
        "project_id": "test_001",
        "event_type": EventType.FLOW_STARTED,
        "reason": "Test event",
    }
    defaults.update(overrides)
    return ValidationEvent(**defaults)
