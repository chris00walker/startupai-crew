"""
Pytest Configuration and Fixtures.

Provides reusable fixtures for testing the Modal-based validation flow.
"""

import pytest
from typing import Dict, Any
from datetime import datetime
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import os
from pathlib import Path
from uuid import uuid4

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

# Import from new Modal-based state models
from src.state.models import (
    ValidationRunState,
    ValidationSignal,
    PivotRecommendation,
    FoundersBrief,
    TheIdea,
    ProblemHypothesis,
    CustomerHypothesis,
    SolutionHypothesis,
    CustomerProfile,
    ValueMap,
    FitAssessment,
    DesirabilityEvidence,
    FeasibilityEvidence,
    ViabilityEvidence,
    HITLCheckpoint,
)


# ===========================================================================
# STATE FIXTURES
# ===========================================================================

@pytest.fixture
def run_id() -> str:
    """Generate a unique run ID for testing."""
    return str(uuid4())


@pytest.fixture
def project_id() -> str:
    """Generate a unique project ID for testing."""
    return str(uuid4())


@pytest.fixture
def user_id() -> str:
    """Generate a unique user ID for testing."""
    return str(uuid4())


@pytest.fixture
def base_state(run_id, project_id, user_id) -> ValidationRunState:
    """Create a minimal base state for testing."""
    return ValidationRunState(
        run_id=run_id,
        project_id=project_id,
        user_id=user_id,
        entrepreneur_input="A B2B SaaS platform for supply chain optimization",
        current_phase=0,
        status="pending",
    )


@pytest.fixture
def minimal_founders_brief() -> FoundersBrief:
    """Create a minimal valid Founder's Brief."""
    return FoundersBrief(
        the_idea=TheIdea(
            one_liner="AI-powered supply chain optimizer",
            description="A platform that uses ML to optimize logistics.",
        ),
        problem_hypothesis=ProblemHypothesis(
            problem_statement="Supply chain managers waste time on manual forecasting",
            who_has_this_problem="Logistics managers at mid-size retailers",
        ),
        customer_hypothesis=CustomerHypothesis(
            primary_segment="Mid-size retailers",
            segment_description="Retailers with 10-500 stores",
        ),
        solution_hypothesis=SolutionHypothesis(
            proposed_solution="AI demand forecasting dashboard",
        ),
    )


@pytest.fixture
def phase_1_state(base_state, minimal_founders_brief) -> ValidationRunState:
    """Create a state in Phase 1 with Founder's Brief complete."""
    base_state.current_phase = 1
    base_state.status = "running"
    base_state.founders_brief = minimal_founders_brief
    return base_state


@pytest.fixture
def phase_2_state(phase_1_state) -> ValidationRunState:
    """Create a state in Phase 2 with VPC complete."""
    phase_1_state.current_phase = 2
    phase_1_state.customer_profile = CustomerProfile(
        segment_name="Mid-size retailers",
        segment_description="Retailers with 10-500 stores",
    )
    phase_1_state.value_map = ValueMap()
    phase_1_state.fit_assessment = FitAssessment(
        fit_score=75,
        fit_status="strong",
        profile_completeness=0.9,
        value_map_coverage=0.85,
        evidence_strength="strong",
        gate_ready=True,
    )
    return phase_1_state


@pytest.fixture
def phase_3_state(phase_2_state) -> ValidationRunState:
    """Create a state in Phase 3 with Desirability validated."""
    phase_2_state.current_phase = 3
    phase_2_state.desirability_evidence = DesirabilityEvidence(
        problem_resonance=0.55,
        zombie_ratio=0.30,
        signal=ValidationSignal.STRONG_COMMITMENT,
    )
    return phase_2_state


@pytest.fixture
def phase_4_state(phase_3_state) -> ValidationRunState:
    """Create a state in Phase 4 with Feasibility validated."""
    phase_3_state.current_phase = 4
    phase_3_state.feasibility_evidence = FeasibilityEvidence(
        core_features_feasible=True,
        downgrade_required=False,
        signal=ValidationSignal.GREEN,
    )
    return phase_3_state


@pytest.fixture
def validated_state(phase_4_state) -> ValidationRunState:
    """Create a fully validated state."""
    phase_4_state.status = "completed"
    phase_4_state.viability_evidence = ViabilityEvidence(
        cac=100,
        ltv=400,
        ltv_cac_ratio=4.0,
        signal=ValidationSignal.PROFITABLE,
    )
    return phase_4_state


# ===========================================================================
# EVIDENCE FIXTURES
# ===========================================================================

@pytest.fixture
def strong_desirability() -> DesirabilityEvidence:
    """Strong desirability evidence (PROCEED)."""
    return DesirabilityEvidence(
        ad_impressions=1000,
        ad_clicks=150,
        ad_signups=30,
        problem_resonance=0.55,
        zombie_ratio=0.25,
        signal=ValidationSignal.STRONG_COMMITMENT,
    )


@pytest.fixture
def no_interest_desirability() -> DesirabilityEvidence:
    """No interest evidence (SEGMENT_PIVOT)."""
    return DesirabilityEvidence(
        problem_resonance=0.15,
        zombie_ratio=0.40,
        signal=ValidationSignal.NO_INTEREST,
    )


@pytest.fixture
def mild_interest_desirability() -> DesirabilityEvidence:
    """Mild interest evidence - high zombie (VALUE_PIVOT)."""
    return DesirabilityEvidence(
        problem_resonance=0.45,
        zombie_ratio=0.75,
        signal=ValidationSignal.MILD_INTEREST,
    )


@pytest.fixture
def green_feasibility() -> FeasibilityEvidence:
    """Green feasibility evidence (PROCEED)."""
    return FeasibilityEvidence(
        core_features_feasible=True,
        downgrade_required=False,
        signal=ValidationSignal.GREEN,
    )


@pytest.fixture
def orange_feasibility() -> FeasibilityEvidence:
    """Orange feasibility evidence (FEATURE_PIVOT)."""
    return FeasibilityEvidence(
        core_features_feasible=True,
        downgrade_required=True,
        downgrade_features=["Real-time sync", "AI recommendations"],
        signal=ValidationSignal.ORANGE_CONSTRAINED,
    )


@pytest.fixture
def red_feasibility() -> FeasibilityEvidence:
    """Red feasibility evidence (KILL)."""
    return FeasibilityEvidence(
        core_features_feasible=False,
        constraints=["No API available", "Patent blocked"],
        signal=ValidationSignal.RED_IMPOSSIBLE,
    )


@pytest.fixture
def profitable_viability() -> ViabilityEvidence:
    """Profitable viability evidence (PROCEED)."""
    return ViabilityEvidence(
        cac=100,
        ltv=400,
        ltv_cac_ratio=4.0,
        signal=ValidationSignal.PROFITABLE,
    )


@pytest.fixture
def marginal_viability() -> ViabilityEvidence:
    """Marginal viability evidence (PRICE_PIVOT)."""
    return ViabilityEvidence(
        cac=100,
        ltv=200,
        ltv_cac_ratio=2.0,
        signal=ValidationSignal.MARGINAL,
    )


@pytest.fixture
def underwater_viability() -> ViabilityEvidence:
    """Underwater viability evidence (STRATEGIC_PIVOT)."""
    return ViabilityEvidence(
        cac=100,
        ltv=50,
        ltv_cac_ratio=0.5,
        signal=ValidationSignal.UNDERWATER,
    )


# ===========================================================================
# HITL FIXTURES
# ===========================================================================

@pytest.fixture
def pending_hitl_checkpoint() -> HITLCheckpoint:
    """HITL checkpoint awaiting decision."""
    return HITLCheckpoint(
        checkpoint_name="approve_vpc_completion",
        phase=1,
        title="VPC Discovery Complete",
        description="Review the VPC fit score before proceeding.",
        context={"fit_score": 78},
        options=[
            {"id": "approve", "label": "Approve"},
            {"id": "iterate", "label": "Iterate"},
        ],
        recommended_option="approve",
    )


@pytest.fixture
def approved_hitl_checkpoint() -> HITLCheckpoint:
    """HITL checkpoint with approved decision."""
    return HITLCheckpoint(
        checkpoint_name="approve_desirability_gate",
        phase=2,
        title="Desirability Gate",
        description="Approve desirability validation.",
        decision="approved",
        feedback="Looks good, proceed.",
        decided_at=datetime.utcnow(),
    )


# ===========================================================================
# MOCK FIXTURES
# ===========================================================================

@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    with patch("src.state.persistence.create_client") as mock:
        client = Mock()
        client.table.return_value.upsert.return_value.execute.return_value = Mock()
        client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data=None)
        client.table.return_value.insert.return_value.execute.return_value = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    with patch("openai.OpenAI") as mock:
        client = Mock()
        response = Mock()
        response.choices = [Mock(message=Mock(content="Mocked response"))]
        client.chat.completions.create.return_value = response
        mock.return_value = client
        yield mock


# ===========================================================================
# CREW MOCK FIXTURES
# ===========================================================================

@pytest.fixture
def mock_onboarding_crew():
    """Mock OnboardingCrew for testing without execution."""
    with patch("src.crews.onboarding.OnboardingCrew") as mock:
        crew_instance = Mock()
        crew_instance.kickoff.return_value = Mock(raw="mocked", json_dict={})
        mock.return_value.crew.return_value = crew_instance
        yield mock


@pytest.fixture
def mock_discovery_crews():
    """Mock all discovery crews for testing."""
    mocks = {}
    crews = [
        "src.crews.discovery.DiscoveryCrew",
        "src.crews.discovery.CustomerProfileCrew",
        "src.crews.discovery.ValueDesignCrew",
        "src.crews.discovery.WTPCrew",
        "src.crews.discovery.FitAssessmentCrew",
    ]
    with patch.multiple(
        "src.crews.discovery",
        run_discovery_crew=Mock(return_value={}),
        run_customer_profile_crew=Mock(return_value=CustomerProfile(
            segment_name="Test", segment_description="Test"
        )),
        run_value_design_crew=Mock(return_value=ValueMap()),
        run_wtp_crew=Mock(return_value={}),
        run_fit_assessment_crew=Mock(return_value=FitAssessment(
            fit_score=75,
            fit_status="strong",
            profile_completeness=0.8,
            value_map_coverage=0.8,
            evidence_strength="moderate",
            gate_ready=True,
        )),
    ) as mocks:
        yield mocks


@pytest.fixture
def mock_desirability_crews():
    """Mock all desirability crews for testing."""
    with patch.multiple(
        "src.crews.desirability",
        run_build_crew=Mock(return_value={}),
        run_growth_crew=Mock(return_value=DesirabilityEvidence(
            problem_resonance=0.5,
            zombie_ratio=0.3,
            signal=ValidationSignal.STRONG_COMMITMENT,
        )),
        run_governance_crew=Mock(return_value={}),
    ) as mocks:
        yield mocks


@pytest.fixture
def mock_feasibility_crews():
    """Mock all feasibility crews for testing."""
    with patch.multiple(
        "src.crews.feasibility",
        run_feasibility_build_crew=Mock(return_value=FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            signal=ValidationSignal.GREEN,
        )),
        run_feasibility_governance_crew=Mock(return_value={}),
    ) as mocks:
        yield mocks


@pytest.fixture
def mock_viability_crews():
    """Mock all viability crews for testing."""
    with patch.multiple(
        "src.crews.viability",
        run_finance_crew=Mock(return_value=ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )),
        run_synthesis_crew=Mock(return_value={}),
        run_viability_governance_crew=Mock(return_value={}),
    ) as mocks:
        yield mocks


@pytest.fixture
def mock_all_crews(
    mock_onboarding_crew,
    mock_discovery_crews,
    mock_desirability_crews,
    mock_feasibility_crews,
    mock_viability_crews,
):
    """
    Composite fixture that mocks all crews at once.

    Usage:
        def test_flow_with_mocked_crews(mock_all_crews):
            # All crews are mocked, flow can execute without LLM calls
            pass
    """
    return {
        "onboarding": mock_onboarding_crew,
        "discovery": mock_discovery_crews,
        "desirability": mock_desirability_crews,
        "feasibility": mock_feasibility_crews,
        "viability": mock_viability_crews,
    }


# ===========================================================================
# UTILITY FUNCTIONS
# ===========================================================================

def create_test_state(**overrides) -> ValidationRunState:
    """Create a test state with optional overrides."""
    defaults = {
        "run_id": str(uuid4()),
        "project_id": str(uuid4()),
        "user_id": str(uuid4()),
        "entrepreneur_input": "Test business idea",
        "current_phase": 0,
        "status": "pending",
    }
    defaults.update(overrides)
    return ValidationRunState(**defaults)


def create_test_brief(**overrides) -> FoundersBrief:
    """Create a test Founder's Brief with optional overrides."""
    defaults = {
        "the_idea": TheIdea(
            one_liner="Test product",
            description="Test description",
        ),
        "problem_hypothesis": ProblemHypothesis(
            problem_statement="Test problem",
            who_has_this_problem="Test customers",
        ),
        "customer_hypothesis": CustomerHypothesis(
            primary_segment="Test segment",
            segment_description="Test segment description",
        ),
        "solution_hypothesis": SolutionHypothesis(
            proposed_solution="Test solution",
        ),
    }
    defaults.update(overrides)
    return FoundersBrief(**defaults)
