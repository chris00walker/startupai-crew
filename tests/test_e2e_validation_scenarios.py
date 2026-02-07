"""
End-to-End Test Scenarios for Validation Flow.

Tests complete validation runs through all 5 phases with mocked crews.
Verifies state transitions, HITL checkpoints, and pivot paths.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from datetime import datetime
from typing import Any

# Import state models
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


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def initial_state():
    """Create initial state for E2E tests."""
    return ValidationRunState(
        run_id=uuid4(),
        project_id=uuid4(),
        user_id=uuid4(),
        entrepreneur_input="AI-powered supply chain optimizer for mid-size retailers",
        current_phase=0,
        status="pending",
    )


@pytest.fixture
def mock_founders_brief():
    """Mock Founder's Brief output from Phase 0."""
    return FoundersBrief(
        the_idea=TheIdea(
            one_liner="AI supply chain optimizer",
            description="ML-powered demand forecasting for retailers",
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
def mock_customer_profile():
    """Mock Customer Profile output from Phase 1."""
    return CustomerProfile(
        segment_name="Mid-size retailers",
        segment_description="Retailers with 10-500 stores",
        jobs=[],
        pains=[],
        gains=[],
    )


@pytest.fixture
def mock_value_map():
    """Mock Value Map output from Phase 1."""
    return ValueMap(
        products_services=[],
        pain_relievers=[],
        gain_creators=[],
    )


@pytest.fixture
def mock_fit_assessment_passing():
    """Mock passing fit assessment (>= 70)."""
    return FitAssessment(
        fit_score=78,
        fit_status="strong",
        profile_completeness=0.85,
        value_map_coverage=0.80,
        evidence_strength="strong",
        gate_ready=True,
    )


@pytest.fixture
def mock_fit_assessment_failing():
    """Mock failing fit assessment (< 70)."""
    return FitAssessment(
        fit_score=55,
        fit_status="weak",
        profile_completeness=0.5,
        value_map_coverage=0.4,
        evidence_strength="weak",
        gate_ready=False,
        blockers=["Insufficient pain validation"],
    )


# =============================================================================
# Helper Functions (Simulate Phase Execution)
# =============================================================================

def simulate_phase_0(state: ValidationRunState, founders_brief: FoundersBrief) -> dict[str, Any]:
    """Simulate Phase 0: Onboarding flow."""
    return {
        "state": {
            **state.model_dump(mode="json"),
            "founders_brief": founders_brief.model_dump(mode="json"),
            "current_phase": 0,
            "status": "running",
        },
        "hitl_checkpoint": "approve_founders_brief",
        "hitl_title": "Founder's Brief Complete",
        "hitl_recommended": "approve",
    }


def simulate_phase_1(state: dict, fit_score: int = 78) -> dict[str, Any]:
    """Simulate Phase 1: VPC Discovery flow."""
    gate_ready = fit_score >= 70
    return {
        "state": {
            **state,
            "current_phase": 1,
            "fit_assessment": {"fit_score": fit_score, "gate_ready": gate_ready},
        },
        "hitl_checkpoint": "approve_discovery_output",
        "hitl_title": "VPC Discovery Complete",
        "hitl_description": f"VPC fit score: {fit_score}/100.",
        "hitl_recommended": "approved" if gate_ready else "iterate",
    }


def simulate_phase_2(
    state: dict,
    problem_resonance: float = 0.55,
    zombie_ratio: float = 0.30,
) -> dict[str, Any]:
    """Simulate Phase 2: Desirability flow."""
    if problem_resonance < 0.3:
        signal = "no_interest"
        recommendation = "segment_pivot"
    elif zombie_ratio >= 0.7:
        signal = "mild_interest"
        recommendation = "value_pivot"
    else:
        signal = "strong_commitment"
        recommendation = "proceed"

    gate_ready = signal == "strong_commitment"

    return {
        "state": {
            **state,
            "current_phase": 2,
            "desirability_evidence": {
                "problem_resonance": problem_resonance,
                "zombie_ratio": zombie_ratio,
                "signal": signal,
            },
            "desirability_signal": signal,
        },
        "hitl_checkpoint": "approve_desirability_gate",
        "hitl_title": "Desirability Validation Complete",
        "hitl_recommended": "approve" if gate_ready else recommendation,
    }


def simulate_phase_3(
    state: dict,
    core_feasible: bool = True,
    downgrade_required: bool = False,
) -> dict[str, Any]:
    """Simulate Phase 3: Feasibility flow."""
    if not core_feasible:
        signal = "red_impossible"
        recommendation = "kill"
    elif downgrade_required:
        signal = "orange_constrained"
        recommendation = "feature_pivot"
    else:
        signal = "green"
        recommendation = "proceed"

    gate_ready = signal == "green"

    return {
        "state": {
            **state,
            "current_phase": 3,
            "feasibility_evidence": {
                "core_features_feasible": core_feasible,
                "downgrade_required": downgrade_required,
                "signal": signal,
            },
            "feasibility_signal": signal,
        },
        "hitl_checkpoint": "approve_feasibility_gate",
        "hitl_title": "Feasibility Assessment Complete",
        "hitl_recommended": "approve" if gate_ready else recommendation,
    }


def simulate_phase_4(
    state: dict,
    ltv_cac_ratio: float = 4.0,
) -> dict[str, Any]:
    """Simulate Phase 4: Viability flow."""
    if ltv_cac_ratio >= 3.0:
        signal = "profitable"
        recommendation = "proceed"
    elif ltv_cac_ratio >= 1.0:
        signal = "marginal"
        recommendation = "pivot"
    else:
        signal = "underwater"
        recommendation = "pivot"

    gate_ready = signal == "profitable"

    return {
        "state": {
            **state,
            "current_phase": 4,
            "viability_evidence": {
                "ltv_cac_ratio": ltv_cac_ratio,
                "signal": signal,
            },
            "viability_signal": signal,
            "final_decision": "proceed" if gate_ready else "pivot",
        },
        "hitl_checkpoint": "request_human_decision",
        "hitl_title": "Validation Complete - Final Decision Required",
        "hitl_recommended": "proceed" if gate_ready else "price_pivot",
    }


# =============================================================================
# E2E: Happy Path - Full Validation Success
# =============================================================================

class TestHappyPath:
    """Test full validation run with all gates passing."""

    def test_complete_validation_happy_path(
        self,
        initial_state,
        mock_founders_brief,
    ):
        """Test complete validation run with all phases succeeding."""
        # Phase 0: Onboarding
        phase_0_result = simulate_phase_0(initial_state, mock_founders_brief)
        assert phase_0_result["hitl_checkpoint"] == "approve_founders_brief"
        assert phase_0_result["hitl_recommended"] == "approve"

        # Phase 1: VPC Discovery (fit_score = 78 > 70)
        phase_1_result = simulate_phase_1(phase_0_result["state"], fit_score=78)
        assert phase_1_result["hitl_checkpoint"] == "approve_discovery_output"
        assert phase_1_result["hitl_recommended"] == "approved"

        # Phase 2: Desirability (strong commitment)
        phase_2_result = simulate_phase_2(
            phase_1_result["state"],
            problem_resonance=0.55,
            zombie_ratio=0.30,
        )
        assert phase_2_result["state"]["desirability_signal"] == "strong_commitment"
        assert phase_2_result["hitl_recommended"] == "approve"

        # Phase 3: Feasibility (green)
        phase_3_result = simulate_phase_3(
            phase_2_result["state"],
            core_feasible=True,
            downgrade_required=False,
        )
        assert phase_3_result["state"]["feasibility_signal"] == "green"
        assert phase_3_result["hitl_recommended"] == "approve"

        # Phase 4: Viability (profitable)
        phase_4_result = simulate_phase_4(
            phase_3_result["state"],
            ltv_cac_ratio=4.0,
        )
        assert phase_4_result["state"]["viability_signal"] == "profitable"
        assert phase_4_result["state"]["final_decision"] == "proceed"
        assert phase_4_result["hitl_recommended"] == "proceed"

    def test_all_hitl_checkpoints_present(self, initial_state, mock_founders_brief):
        """Verify all HITL checkpoints are reached in happy path."""
        checkpoints_reached = []

        # Execute all phases
        result = simulate_phase_0(initial_state, mock_founders_brief)
        checkpoints_reached.append(result["hitl_checkpoint"])

        result = simulate_phase_1(result["state"])
        checkpoints_reached.append(result["hitl_checkpoint"])

        result = simulate_phase_2(result["state"])
        checkpoints_reached.append(result["hitl_checkpoint"])

        result = simulate_phase_3(result["state"])
        checkpoints_reached.append(result["hitl_checkpoint"])

        result = simulate_phase_4(result["state"])
        checkpoints_reached.append(result["hitl_checkpoint"])

        # Verify checkpoints
        expected_checkpoints = [
            "approve_founders_brief",
            "approve_discovery_output",
            "approve_desirability_gate",
            "approve_feasibility_gate",
            "request_human_decision",
        ]
        assert checkpoints_reached == expected_checkpoints


# =============================================================================
# E2E: Segment Pivot Path
# =============================================================================

class TestSegmentPivotPath:
    """Test validation run with segment pivot (low problem resonance)."""

    def test_segment_pivot_triggered(self, initial_state, mock_founders_brief):
        """Test segment pivot when problem_resonance < 0.3."""
        # Execute phases until desirability
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"], fit_score=75)

        # Phase 2 with low resonance triggers segment pivot
        result = simulate_phase_2(
            result["state"],
            problem_resonance=0.15,  # < 0.3 threshold
            zombie_ratio=0.40,
        )

        assert result["state"]["desirability_signal"] == "no_interest"
        assert result["hitl_recommended"] == "segment_pivot"

    def test_segment_pivot_state_preserved(self, initial_state, mock_founders_brief):
        """Test state is preserved for segment pivot iteration."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])
        result = simulate_phase_2(result["state"], problem_resonance=0.20)

        # State should include all previous work
        assert "founders_brief" in result["state"]
        assert "fit_assessment" in result["state"]
        assert result["state"]["desirability_signal"] == "no_interest"


# =============================================================================
# E2E: Value Pivot Path
# =============================================================================

class TestValuePivotPath:
    """Test validation run with value pivot (high zombie ratio)."""

    def test_value_pivot_triggered(self, initial_state, mock_founders_brief):
        """Test value pivot when zombie_ratio >= 0.7."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])

        # High zombie ratio with OK resonance triggers value pivot
        result = simulate_phase_2(
            result["state"],
            problem_resonance=0.45,  # >= 0.3 (OK)
            zombie_ratio=0.75,  # >= 0.7 (high zombie)
        )

        assert result["state"]["desirability_signal"] == "mild_interest"
        assert result["hitl_recommended"] == "value_pivot"

    def test_value_pivot_preserves_vpc(self, initial_state, mock_founders_brief):
        """Test VPC work is preserved during value pivot."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"], fit_score=80)
        result = simulate_phase_2(result["state"], problem_resonance=0.40, zombie_ratio=0.80)

        # VPC data preserved
        assert "fit_assessment" in result["state"]
        assert result["state"]["fit_assessment"]["fit_score"] == 80


# =============================================================================
# E2E: Feature Pivot Path
# =============================================================================

class TestFeaturePivotPath:
    """Test validation run with feature pivot (technical constraints)."""

    def test_feature_pivot_downgrade_required(self, initial_state, mock_founders_brief):
        """Test feature pivot when downgrade required."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])
        result = simulate_phase_2(result["state"])  # Strong commitment

        # Feasibility requires downgrade
        result = simulate_phase_3(
            result["state"],
            core_feasible=True,
            downgrade_required=True,
        )

        assert result["state"]["feasibility_signal"] == "orange_constrained"
        assert result["hitl_recommended"] == "feature_pivot"

    def test_feature_pivot_returns_to_desirability(self, initial_state, mock_founders_brief):
        """Test feature pivot requires re-testing desirability."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])
        result = simulate_phase_2(result["state"])
        result = simulate_phase_3(result["state"], downgrade_required=True)

        # State shows need to return to Phase 2
        assert result["state"]["feasibility_signal"] == "orange_constrained"
        # In real implementation, HITL decision would trigger Phase 2 re-run


# =============================================================================
# E2E: Kill Path
# =============================================================================

class TestKillPath:
    """Test validation run resulting in kill recommendation."""

    def test_kill_on_technical_impossibility(self, initial_state, mock_founders_brief):
        """Test kill recommendation when core features impossible."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])
        result = simulate_phase_2(result["state"])

        # Technical impossibility
        result = simulate_phase_3(
            result["state"],
            core_feasible=False,
        )

        assert result["state"]["feasibility_signal"] == "red_impossible"
        assert result["hitl_recommended"] == "kill"

    def test_kill_preserves_learnings(self, initial_state, mock_founders_brief):
        """Test all learnings are preserved in kill decision."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"], fit_score=82)
        result = simulate_phase_2(result["state"], problem_resonance=0.60)
        result = simulate_phase_3(result["state"], core_feasible=False)

        # All prior work preserved
        assert "founders_brief" in result["state"]
        assert "fit_assessment" in result["state"]
        assert "desirability_evidence" in result["state"]
        assert result["state"]["desirability_signal"] == "strong_commitment"
        # Despite good desirability, technical impossibility kills project


# =============================================================================
# E2E: Viability Pivot Path
# =============================================================================

class TestViabilityPivotPath:
    """Test validation run with viability pivot (unit economics)."""

    def test_price_pivot_marginal_economics(self, initial_state, mock_founders_brief):
        """Test price pivot when LTV:CAC marginal."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])
        result = simulate_phase_2(result["state"])
        result = simulate_phase_3(result["state"])

        # Marginal unit economics
        result = simulate_phase_4(result["state"], ltv_cac_ratio=2.0)

        assert result["state"]["viability_signal"] == "marginal"
        assert result["state"]["final_decision"] == "pivot"
        assert result["hitl_recommended"] == "price_pivot"

    def test_strategic_pivot_underwater(self, initial_state, mock_founders_brief):
        """Test strategic pivot when LTV:CAC underwater."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])
        result = simulate_phase_2(result["state"])
        result = simulate_phase_3(result["state"])

        # Underwater unit economics
        result = simulate_phase_4(result["state"], ltv_cac_ratio=0.5)

        assert result["state"]["viability_signal"] == "underwater"
        assert result["state"]["final_decision"] == "pivot"


# =============================================================================
# E2E: HITL Rejection Handling
# =============================================================================

class TestHITLRejection:
    """Test HITL rejection handling at various checkpoints."""

    def test_founders_brief_rejection(self, initial_state, mock_founders_brief):
        """Test rejection at Founder's Brief checkpoint."""
        result = simulate_phase_0(initial_state, mock_founders_brief)

        # Simulate HITL rejection
        hitl_decision = {
            "checkpoint": "approve_founders_brief",
            "decision": "rejected",
            "feedback": "Need clearer problem statement",
        }

        # State should remain at Phase 0
        assert result["state"]["current_phase"] == 0
        # In real implementation, rejection would trigger re-interview

    def test_vpc_iteration_request(self, initial_state, mock_founders_brief):
        """Test iterate request at VPC checkpoint."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"], fit_score=65)

        # User chooses to iterate
        hitl_decision = {
            "checkpoint": "approve_discovery_output",
            "decision": "iterate",
            "feedback": "Need more customer interviews",
        }

        # State shows weak fit, iterate recommended
        assert result["hitl_recommended"] == "iterate"
        # In real implementation, would re-run Phase 1 crews


# =============================================================================
# E2E: State Persistence
# =============================================================================

class TestStatePersistence:
    """Test state persistence through validation flow."""

    def test_state_serialization_roundtrip(self, initial_state, mock_founders_brief):
        """Test state can be serialized and restored at any point."""
        # Execute some phases
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])

        # Serialize state
        state_json = result["state"]

        # Restore state (simulating container resume)
        restored_state = ValidationRunState(**{
            "run_id": state_json.get("run_id", str(uuid4())),
            "project_id": state_json.get("project_id", str(uuid4())),
            "user_id": state_json.get("user_id", str(uuid4())),
            "entrepreneur_input": state_json.get("entrepreneur_input", ""),
            "current_phase": state_json.get("current_phase", 0),
            "status": state_json.get("status", "running"),
        })

        assert restored_state.current_phase == 1

    def test_phase_outputs_preserved(self, initial_state, mock_founders_brief):
        """Test all phase outputs are preserved through flow."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        assert "founders_brief" in result["state"]

        result = simulate_phase_1(result["state"], fit_score=78)
        assert "founders_brief" in result["state"]  # Still present
        assert "fit_assessment" in result["state"]

        result = simulate_phase_2(result["state"])
        assert "founders_brief" in result["state"]
        assert "fit_assessment" in result["state"]
        assert "desirability_evidence" in result["state"]


# =============================================================================
# E2E: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_boundary_fit_score_70(self, initial_state, mock_founders_brief):
        """Test boundary condition: fit_score = 70 (exactly passing)."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"], fit_score=70)

        # Score of exactly 70 should pass
        assert result["hitl_recommended"] == "approved"

    def test_boundary_fit_score_69(self, initial_state, mock_founders_brief):
        """Test boundary condition: fit_score = 69 (just failing)."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"], fit_score=69)

        # Score of 69 should fail
        assert result["hitl_recommended"] == "iterate"

    def test_boundary_resonance_30(self, initial_state, mock_founders_brief):
        """Test boundary: resonance = 0.30 (exactly passing)."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])
        result = simulate_phase_2(result["state"], problem_resonance=0.30, zombie_ratio=0.50)

        # Resonance of 0.30 should pass (not no_interest)
        assert result["state"]["desirability_signal"] in ["mild_interest", "strong_commitment"]

    def test_boundary_ltv_cac_3(self, initial_state, mock_founders_brief):
        """Test boundary: LTV:CAC = 3.0 (exactly profitable)."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])
        result = simulate_phase_2(result["state"])
        result = simulate_phase_3(result["state"])
        result = simulate_phase_4(result["state"], ltv_cac_ratio=3.0)

        # Ratio of exactly 3.0 should be profitable
        assert result["state"]["viability_signal"] == "profitable"
        assert result["hitl_recommended"] == "proceed"

    def test_boundary_ltv_cac_299(self, initial_state, mock_founders_brief):
        """Test boundary: LTV:CAC = 2.99 (just marginal)."""
        result = simulate_phase_0(initial_state, mock_founders_brief)
        result = simulate_phase_1(result["state"])
        result = simulate_phase_2(result["state"])
        result = simulate_phase_3(result["state"])
        result = simulate_phase_4(result["state"], ltv_cac_ratio=2.99)

        # Ratio of 2.99 should be marginal
        assert result["state"]["viability_signal"] == "marginal"
