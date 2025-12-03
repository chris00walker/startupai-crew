"""
Flow Routing Tests - Gate Router Unit Tests

Tests the Innovation Physics routing logic without executing crews.
Each gate router makes decisions based on state signals.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Optional

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
    EvidenceStrength,
    PivotRecommendation,
    DesirabilityEvidence,
    FeasibilityEvidence,
    ViabilityEvidence,
    CommitmentType,
)


# ===========================================================================
# TEST FIXTURES
# ===========================================================================

@pytest.fixture
def mock_flow():
    """Create a flow instance with mocked crews for routing tests.

    Note: We use _state directly because CrewAI Flow's state property is read-only.
    This allows us to inject test state without triggering the full flow execution.
    """
    with patch('startupai.flows.founder_validation_flow.ServiceCrew'), \
         patch('startupai.flows.founder_validation_flow.AnalysisCrew'), \
         patch('startupai.flows.founder_validation_flow.GovernanceCrew'), \
         patch('startupai.flows.founder_validation_flow.BuildCrew'), \
         patch('startupai.flows.founder_validation_flow.GrowthCrew'), \
         patch('startupai.flows.founder_validation_flow.SynthesisCrew'), \
         patch('startupai.flows.founder_validation_flow.FinanceCrew'):
        from startupai.flows._founder_validation_flow import FounderValidationFlow
        flow = FounderValidationFlow.__new__(FounderValidationFlow)
        # Initialize minimal attributes without triggering __init__
        flow._state = None
        yield flow


@pytest.fixture
def desirability_test_state() -> StartupValidationState:
    """State ready for desirability gate testing."""
    state = StartupValidationState(
        project_id="test_desirability_001",
        entrepreneur_input="A B2B SaaS for supply chain",
        phase=Phase.DESIRABILITY,
        current_risk_axis=RiskAxis.DESIRABILITY,
        business_idea="Supply chain optimizer",
        target_segments=["Logistics Managers"],
        current_segment="Logistics Managers",
        max_retries=3,
        retry_count=0,
    )
    # Initialize desirability evidence with default values
    state.desirability_evidence = DesirabilityEvidence(
        problem_resonance=0.5,
        conversion_rate=0.1,
        commitment_depth=CommitmentType.VERBAL,
    )
    return state


@pytest.fixture
def feasibility_test_state() -> StartupValidationState:
    """State ready for feasibility gate testing."""
    state = StartupValidationState(
        project_id="test_feasibility_001",
        entrepreneur_input="A B2B SaaS for supply chain",
        phase=Phase.FEASIBILITY,
        current_risk_axis=RiskAxis.FEASIBILITY,
        business_idea="Supply chain optimizer",
        target_segments=["Logistics Managers"],
        current_segment="Logistics Managers",
        desirability_signal=DesirabilitySignal.STRONG_COMMITMENT,
    )
    state.feasibility_evidence = FeasibilityEvidence(
        core_features_feasible={"feature1": "POSSIBLE"},
    )
    return state


@pytest.fixture
def viability_test_state() -> StartupValidationState:
    """State ready for viability gate testing."""
    state = StartupValidationState(
        project_id="test_viability_001",
        entrepreneur_input="A B2B SaaS for supply chain",
        phase=Phase.VIABILITY,
        current_risk_axis=RiskAxis.VIABILITY,
        business_idea="Supply chain optimizer",
        target_segments=["Logistics Managers"],
        current_segment="Logistics Managers",
        desirability_signal=DesirabilitySignal.STRONG_COMMITMENT,
        feasibility_signal=FeasibilitySignal.GREEN,
        max_retries=3,
        retry_count=0,
    )
    state.viability_evidence = ViabilityEvidence(
        cac=50.0,
        ltv=200.0,
        ltv_cac_ratio=4.0,
        gross_margin=0.7,
    )
    return state


# ===========================================================================
# DESIRABILITY GATE TESTS
# ===========================================================================

class TestDesirabilityGate:
    """Test desirability_gate router decisions."""

    def test_low_problem_resonance_triggers_segment_pivot(self, mock_flow, desirability_test_state):
        """problem_resonance < 0.3 should route to segment_pivot_required."""
        desirability_test_state.desirability_evidence.problem_resonance = 0.2
        mock_flow._state = desirability_test_state

        result = mock_flow.desirability_gate()

        assert result == "segment_pivot_required"
        assert mock_flow._state.pivot_recommendation == PivotRecommendation.SEGMENT_PIVOT
        assert mock_flow._state.human_input_required is True

    def test_high_traffic_low_commitment_triggers_value_pivot(self, mock_flow, desirability_test_state):
        """High traffic + low zombie ratio (< 0.1) should route to value_pivot_required.

        Note: This tests the 'zombie detection' case where there's high interest
        but low commitment (people are interested but not buying).
        """
        # Set up high problem resonance to avoid segment pivot
        desirability_test_state.desirability_evidence.problem_resonance = 0.7
        desirability_test_state.desirability_evidence.traffic_quality = "High"
        mock_flow._state = desirability_test_state

        # Mock calculate_zombie_ratio to return low value (zombie detected)
        with patch.object(StartupValidationState, 'calculate_zombie_ratio', return_value=0.05):
            result = mock_flow.desirability_gate()

        assert result == "value_pivot_required"
        assert mock_flow._state.pivot_recommendation == PivotRecommendation.VALUE_PIVOT
        assert mock_flow._state.human_input_required is True

    def test_weak_signal_with_retries_left_retests(self, mock_flow, desirability_test_state):
        """WEAK evidence with retries available should route to refine_and_retest."""
        desirability_test_state.desirability_evidence.problem_resonance = 0.5
        desirability_test_state.evidence_strength = EvidenceStrength.WEAK
        desirability_test_state.retry_count = 0
        desirability_test_state.max_retries = 3
        mock_flow._state = desirability_test_state

        # Patch calculate_zombie_ratio at class level to bypass traffic_quality check
        with patch.object(StartupValidationState, 'calculate_zombie_ratio', return_value=0.5):
            result = mock_flow.desirability_gate()

        assert result == "refine_and_retest_desirability"
        assert mock_flow._state.retry_count == 1

    def test_weak_signal_exhausted_retries_escalates(self, mock_flow, desirability_test_state):
        """WEAK evidence with no retries left should escalate to Compass."""
        desirability_test_state.desirability_evidence.problem_resonance = 0.5
        desirability_test_state.evidence_strength = EvidenceStrength.WEAK
        desirability_test_state.retry_count = 3
        desirability_test_state.max_retries = 3
        mock_flow._state = desirability_test_state

        with patch.object(StartupValidationState, 'calculate_zombie_ratio', return_value=0.5):
            result = mock_flow.desirability_gate()

        assert result == "compass_synthesis_required"

    def test_strong_signal_proceeds_to_feasibility(self, mock_flow, desirability_test_state):
        """STRONG evidence should proceed to feasibility phase."""
        desirability_test_state.desirability_evidence.problem_resonance = 0.8
        desirability_test_state.evidence_strength = EvidenceStrength.STRONG
        mock_flow._state = desirability_test_state

        with patch.object(StartupValidationState, 'calculate_zombie_ratio', return_value=0.5):
            result = mock_flow.desirability_gate()

        assert result == "proceed_to_feasibility"
        assert mock_flow._state.phase == Phase.FEASIBILITY
        assert mock_flow._state.retry_count == 0  # Reset for next phase


# ===========================================================================
# FEASIBILITY GATE TESTS
# ===========================================================================

class TestFeasibilityGate:
    """Test feasibility_gate router decisions."""

    def test_impossible_triggers_downgrade(self, mock_flow, feasibility_test_state):
        """IMPOSSIBLE feasibility should trigger downgrade protocol."""
        feasibility_test_state.feasibility_status = FeasibilitySignal.RED_IMPOSSIBLE
        feasibility_test_state.feasibility_evidence.core_features_feasible = {
            "ai_engine": "IMPOSSIBLE",
            "dashboard": "POSSIBLE",
        }
        mock_flow._state = feasibility_test_state

        result = mock_flow.feasibility_gate()

        assert result == "downgrade_and_retest"
        assert mock_flow._state.human_input_required is True

    def test_constrained_tests_degraded(self, mock_flow, feasibility_test_state):
        """CONSTRAINED feasibility should test degraded version."""
        feasibility_test_state.feasibility_status = FeasibilitySignal.ORANGE_CONSTRAINED
        mock_flow._state = feasibility_test_state

        result = mock_flow.feasibility_gate()

        assert result == "test_degraded_desirability"

    def test_possible_proceeds_to_viability(self, mock_flow, feasibility_test_state):
        """POSSIBLE (GREEN) feasibility should proceed to viability."""
        feasibility_test_state.feasibility_status = FeasibilitySignal.GREEN
        mock_flow._state = feasibility_test_state

        result = mock_flow.feasibility_gate()

        assert result == "proceed_to_viability"
        assert mock_flow._state.phase == Phase.VIABILITY
        assert mock_flow._state.retry_count == 0

    def test_unknown_status_escalates(self, mock_flow, feasibility_test_state):
        """Unknown feasibility status should escalate to Compass."""
        feasibility_test_state.feasibility_status = None
        mock_flow._state = feasibility_test_state

        result = mock_flow.feasibility_gate()

        assert result == "compass_synthesis_required"


# ===========================================================================
# VIABILITY GATE TESTS
# ===========================================================================

class TestViabilityGate:
    """Test viability_gate router decisions."""

    def test_underwater_awaits_human_decision(self, mock_flow, viability_test_state):
        """UNDERWATER unit economics should await human decision."""
        viability_test_state.unit_economics_status = ViabilitySignal.UNDERWATER
        viability_test_state.viability_evidence.ltv_cac_ratio = 0.5
        mock_flow._state = viability_test_state

        result = mock_flow.viability_gate()

        assert result == "await_viability_decision"
        assert mock_flow._state.human_input_required is True

    def test_marginal_with_retries_optimizes(self, mock_flow, viability_test_state):
        """MARGINAL economics with retries should optimize."""
        viability_test_state.unit_economics_status = ViabilitySignal.MARGINAL
        viability_test_state.viability_evidence.ltv_cac_ratio = 2.0
        viability_test_state.retry_count = 0
        mock_flow._state = viability_test_state

        result = mock_flow.viability_gate()

        assert result == "optimize_economics"
        assert mock_flow._state.retry_count == 1

    def test_marginal_exhausted_retries_awaits_human(self, mock_flow, viability_test_state):
        """MARGINAL economics with exhausted retries should await human."""
        viability_test_state.unit_economics_status = ViabilitySignal.MARGINAL
        viability_test_state.viability_evidence.ltv_cac_ratio = 2.0
        viability_test_state.retry_count = 2  # Max is 2 for viability
        mock_flow._state = viability_test_state

        result = mock_flow.viability_gate()

        assert result == "await_viability_decision"
        assert mock_flow._state.human_input_required is True

    def test_profitable_completes_validation(self, mock_flow, viability_test_state):
        """PROFITABLE economics should complete validation."""
        viability_test_state.unit_economics_status = ViabilitySignal.PROFITABLE
        viability_test_state.viability_evidence.ltv_cac_ratio = 4.0
        mock_flow._state = viability_test_state

        result = mock_flow.viability_gate()

        assert result == "validation_complete"
        assert mock_flow._state.phase == Phase.VALIDATED

    def test_unknown_status_escalates(self, mock_flow, viability_test_state):
        """Unknown viability status should escalate to Compass."""
        viability_test_state.unit_economics_status = None
        mock_flow._state = viability_test_state

        result = mock_flow.viability_gate()

        assert result == "compass_synthesis_required"


# ===========================================================================
# CREATIVE APPROVAL GATE TESTS
# ===========================================================================

class TestCreativeApprovalGate:
    """Test creative_approval_gate router decisions."""

    def test_no_creatives_proceeds(self, mock_flow, desirability_test_state):
        """No creatives to review should proceed."""
        mock_flow._state = desirability_test_state
        # No creative_review_results attribute

        result = mock_flow.creative_approval_gate()

        assert result == "creatives_approved"

    def test_empty_creatives_proceeds(self, mock_flow, desirability_test_state):
        """Empty creative review results should proceed."""
        mock_flow._state = desirability_test_state
        mock_flow._state.creative_review_results = []

        result = mock_flow.creative_approval_gate()

        assert result == "creatives_approved"

    def test_all_auto_approved_proceeds(self, mock_flow, desirability_test_state):
        """All auto-approved creatives should proceed."""
        mock_flow._state = desirability_test_state
        mock_flow._state.creative_review_results = [
            {"artifact_id": "lp_1"},
            {"artifact_id": "lp_2"},
        ]
        mock_flow._state.auto_approved_creatives = ["lp_1", "lp_2"]
        mock_flow._state.creatives_needing_human_review = []

        result = mock_flow.creative_approval_gate()

        assert result == "creatives_approved"

    def test_some_need_review_awaits(self, mock_flow, desirability_test_state):
        """Some creatives needing review should await human approval."""
        mock_flow._state = desirability_test_state
        mock_flow._state.creative_review_results = [
            {"artifact_id": "lp_1"},
            {"artifact_id": "lp_2"},
        ]
        mock_flow._state.auto_approved_creatives = ["lp_1"]
        mock_flow._state.creatives_needing_human_review = [
            {"artifact_id": "lp_2", "issues": []}
        ]

        result = mock_flow.creative_approval_gate()

        assert result == "await_creative_approval"
        assert mock_flow._state.human_input_required is True

    def test_all_rejected_regenerates(self, mock_flow, desirability_test_state):
        """All rejected creatives should trigger regeneration."""
        mock_flow._state = desirability_test_state
        mock_flow._state.creative_review_results = [
            {"artifact_id": "lp_1"},
        ]
        mock_flow._state.auto_approved_creatives = []
        mock_flow._state.creatives_needing_human_review = []

        result = mock_flow.creative_approval_gate()

        assert result == "creatives_rejected"


# ===========================================================================
# EDGE CASE TESTS
# ===========================================================================

class TestGateEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_desirability_boundary_problem_resonance(self, mock_flow, desirability_test_state):
        """Test boundary condition at problem_resonance = 0.3."""
        desirability_test_state.desirability_evidence.problem_resonance = 0.3
        desirability_test_state.evidence_strength = EvidenceStrength.WEAK
        desirability_test_state.retry_count = 0
        mock_flow._state = desirability_test_state

        with patch.object(StartupValidationState, 'calculate_zombie_ratio', return_value=0.5):
            result = mock_flow.desirability_gate()

        # At exactly 0.3, should NOT trigger segment pivot (< 0.3 required)
        assert result != "segment_pivot_required"

    def test_viability_boundary_retry_count(self, mock_flow, viability_test_state):
        """Test boundary at retry_count = 2 for viability gate."""
        viability_test_state.unit_economics_status = ViabilitySignal.MARGINAL
        viability_test_state.retry_count = 1  # One retry left
        mock_flow._state = viability_test_state

        result = mock_flow.viability_gate()

        # Should still optimize with 1 retry
        assert result == "optimize_economics"
        assert mock_flow._state.retry_count == 2

    def test_feasibility_with_multiple_impossible_features(self, mock_flow, feasibility_test_state):
        """Test feasibility gate with multiple impossible features."""
        feasibility_test_state.feasibility_status = FeasibilitySignal.RED_IMPOSSIBLE
        feasibility_test_state.feasibility_evidence.core_features_feasible = {
            "ai_engine": "IMPOSSIBLE",
            "ml_pipeline": "IMPOSSIBLE",
            "dashboard": "POSSIBLE",
        }
        mock_flow._state = feasibility_test_state

        result = mock_flow.feasibility_gate()

        assert result == "downgrade_and_retest"
        # Human input reason should mention impossible features
        assert "impossible" in mock_flow._state.human_input_reason.lower()
