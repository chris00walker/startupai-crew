"""
Tests for State Schema Models.

Tests enum values, model validation, and helper methods.
"""

import pytest
from datetime import datetime

from startupai.flows.state_schemas import (
    # Main state
    StartupValidationState,
    # Phase enums
    Phase,
    RiskAxis,
    # Signal enums
    DesirabilitySignal,
    FeasibilitySignal,
    ViabilitySignal,
    ProblemFit,
    # Pivot types
    PivotType,
    # HITL
    HumanApprovalStatus,
    ArtifactApprovalStatus,
    # Legacy aliases
    ValidationState,
    ValidationPhase,
    PivotRecommendation,
    FeasibilityStatus,
    UnitEconomicsStatus,
    # Supporting models
    Assumption,
    AssumptionCategory,
    CustomerProfile,
    ValueMap,
)


class TestPhaseEnum:
    """Tests for Phase enum values."""

    def test_phase_values(self):
        """Test all phase values exist and are correct."""
        assert Phase.IDEATION.value == "ideation"
        assert Phase.DESIRABILITY.value == "desirability"
        assert Phase.FEASIBILITY.value == "feasibility"
        assert Phase.VIABILITY.value == "viability"
        assert Phase.VALIDATED.value == "validated"
        assert Phase.KILLED.value == "killed"

    def test_phase_count(self):
        """Test expected number of phases."""
        assert len(Phase) == 6


class TestSignalEnums:
    """Tests for signal enum values."""

    def test_desirability_signal_values(self):
        """Test all desirability signal values."""
        assert DesirabilitySignal.NO_SIGNAL.value == "no_signal"
        assert DesirabilitySignal.NO_INTEREST.value == "no_interest"
        assert DesirabilitySignal.WEAK_INTEREST.value == "weak_interest"
        assert DesirabilitySignal.STRONG_COMMITMENT.value == "strong_commitment"

    def test_feasibility_signal_values(self):
        """Test all feasibility signal values."""
        assert FeasibilitySignal.UNKNOWN.value == "unknown"
        assert FeasibilitySignal.GREEN.value == "green"
        assert FeasibilitySignal.ORANGE_CONSTRAINED.value == "orange_constrained"
        assert FeasibilitySignal.RED_IMPOSSIBLE.value == "red_impossible"

    def test_viability_signal_values(self):
        """Test all viability signal values."""
        assert ViabilitySignal.UNKNOWN.value == "unknown"
        assert ViabilitySignal.PROFITABLE.value == "profitable"
        assert ViabilitySignal.UNDERWATER.value == "underwater"
        assert ViabilitySignal.ZOMBIE_MARKET.value == "zombie_market"


class TestPivotTypes:
    """Tests for pivot type enum values."""

    def test_pivot_type_values(self):
        """Test all pivot type values."""
        assert PivotType.NONE.value == "none"
        assert PivotType.SEGMENT_PIVOT.value == "segment_pivot"
        assert PivotType.VALUE_PIVOT.value == "value_pivot"
        assert PivotType.CHANNEL_PIVOT.value == "channel_pivot"
        assert PivotType.PRICE_PIVOT.value == "price_pivot"
        assert PivotType.COST_PIVOT.value == "cost_pivot"
        assert PivotType.KILL.value == "kill"

    def test_pivot_type_count(self):
        """Test expected number of pivot types."""
        assert len(PivotType) == 7


class TestBackwardCompatibilityAliases:
    """Tests for backward compatibility aliases."""

    def test_validation_state_alias(self):
        """Test that ValidationState is alias for StartupValidationState."""
        assert ValidationState is StartupValidationState

    def test_validation_phase_alias(self):
        """Test that ValidationPhase is alias for Phase."""
        assert ValidationPhase is Phase

    def test_pivot_recommendation_alias(self):
        """Test that PivotRecommendation is alias for PivotType."""
        assert PivotRecommendation is PivotType

    def test_feasibility_status_alias(self):
        """Test that FeasibilityStatus is alias for FeasibilitySignal."""
        assert FeasibilityStatus is FeasibilitySignal

    def test_unit_economics_status_alias(self):
        """Test that UnitEconomicsStatus is alias for ViabilitySignal."""
        assert UnitEconomicsStatus is ViabilitySignal


class TestStartupValidationState:
    """Tests for the main state model."""

    def test_minimal_state_creation(self):
        """Test creating a state with minimal fields."""
        state = StartupValidationState(
            project_id="test_001",
            entrepreneur_input="A test business idea",
        )
        assert state.project_id == "test_001"
        assert state.phase == Phase.IDEATION  # Default

    def test_default_values(self):
        """Test that defaults are set correctly."""
        state = StartupValidationState(
            project_id="test_002",
            entrepreneur_input="Test",
        )
        assert state.phase == Phase.IDEATION
        assert state.current_risk_axis == RiskAxis.DESIRABILITY
        assert state.iteration == 0
        assert state.desirability_signal == DesirabilitySignal.NO_SIGNAL
        assert state.feasibility_signal == FeasibilitySignal.UNKNOWN
        assert state.viability_signal == ViabilitySignal.UNKNOWN
        assert state.target_segments == []
        assert state.last_pivot_type == PivotType.NONE
        assert state.pending_pivot_type == PivotType.NONE

    def test_state_serialization(self):
        """Test that state can be serialized to dict."""
        state = StartupValidationState(
            project_id="test_003",
            entrepreneur_input="Test idea",
            phase=Phase.DESIRABILITY,
        )
        state_dict = state.dict()
        assert state_dict["project_id"] == "test_003"
        assert state_dict["phase"] == "desirability"

    def test_state_from_dict(self):
        """Test creating state from dict."""
        data = {
            "project_id": "test_004",
            "entrepreneur_input": "Test",
            "phase": "feasibility",
            "desirability_signal": "strong_commitment",
        }
        state = StartupValidationState(**data)
        assert state.phase == Phase.FEASIBILITY
        assert state.desirability_signal == DesirabilitySignal.STRONG_COMMITMENT


class TestAssumption:
    """Tests for Assumption model."""

    def test_assumption_creation(self):
        """Test creating an assumption."""
        from startupai.flows.state_schemas import AssumptionStatus

        assumption = Assumption(
            id="asm_001",
            statement="Customers will pay $100/month",
            category=AssumptionCategory.VIABILITY,
            priority=1,
            evidence_needed="Price sensitivity testing",
        )
        assert assumption.id == "asm_001"
        assert assumption.category == AssumptionCategory.VIABILITY
        assert assumption.priority == 1
        assert assumption.status == AssumptionStatus.UNTESTED

    def test_assumption_defaults(self):
        """Test assumption default values."""
        from startupai.flows.state_schemas import AssumptionStatus

        assumption = Assumption(
            id="asm_002",
            statement="Test assumption",
            category=AssumptionCategory.DESIRABILITY,
            priority=5,
            evidence_needed="Customer interviews",
        )
        assert assumption.status == AssumptionStatus.UNTESTED
        assert assumption.evidence_strength is None


class TestCustomerProfile:
    """Tests for CustomerProfile model."""

    def test_customer_profile_creation(self):
        """Test creating a customer profile."""
        from startupai.flows.state_schemas import CustomerJob

        job1 = CustomerJob(
            functional="Manage budgets",
            emotional="Feel in control",
            social="Be seen as strategic",
            importance=8,
        )
        job2 = CustomerJob(
            functional="Reduce costs",
            emotional="Feel secure",
            social="Be seen as efficient",
            importance=9,
        )
        profile = CustomerProfile(
            segment_name="Enterprise CFOs",
            jobs=[job1, job2],
            pains=["Slow reporting", "Data silos"],
            gains=["Real-time insights", "Cost savings"],
        )
        assert profile.segment_name == "Enterprise CFOs"
        assert len(profile.jobs) == 2
        assert len(profile.pains) == 2
        assert len(profile.gains) == 2


class TestValueMap:
    """Tests for ValueMap model."""

    def test_value_map_creation(self):
        """Test creating a value map."""
        value_map = ValueMap(
            products_services=["Dashboard", "Alerts"],
            pain_relievers={"Slow reporting": "Automated reporting", "Data silos": "Integration"},
            gain_creators={"Real-time insights": "Live dashboard", "Cost savings": "Benchmarking"},
            differentiators=["AI-powered", "Real-time"],
        )
        assert len(value_map.products_services) == 2
        assert len(value_map.differentiators) == 2


class TestHumanApprovalStatus:
    """Tests for HITL status enums."""

    def test_approval_status_values(self):
        """Test all approval status values."""
        assert HumanApprovalStatus.NOT_REQUIRED.value == "not_required"
        assert HumanApprovalStatus.PENDING.value == "pending"
        assert HumanApprovalStatus.APPROVED.value == "approved"
        assert HumanApprovalStatus.REJECTED.value == "rejected"
        assert HumanApprovalStatus.OVERRIDDEN.value == "overridden"

    def test_artifact_approval_status_values(self):
        """Test artifact approval status values."""
        assert ArtifactApprovalStatus.DRAFT.value == "draft"
        assert ArtifactApprovalStatus.PENDING_REVIEW.value == "pending_review"
        assert ArtifactApprovalStatus.APPROVED.value == "approved"
        assert ArtifactApprovalStatus.REJECTED.value == "rejected"


class TestStateHelperMethods:
    """Tests for state helper methods."""

    def test_get_critical_assumptions(self):
        """Test getting critical assumptions (priority 1-3)."""
        state = StartupValidationState(
            project_id="test_005",
            entrepreneur_input="Test",
            assumptions=[
                Assumption(
                    id="asm_001",
                    statement="Critical assumption",
                    category=AssumptionCategory.DESIRABILITY,
                    priority=2,
                    evidence_needed="Customer interviews",
                ),
                Assumption(
                    id="asm_002",
                    statement="Non-critical assumption",
                    category=AssumptionCategory.DESIRABILITY,
                    priority=7,
                    evidence_needed="Market research",
                ),
            ],
        )
        critical = state.get_critical_assumptions()
        assert len(critical) == 1
        assert critical[0].priority <= 3

    def test_calculate_zombie_ratio(self):
        """Test zombie ratio calculation."""
        state = StartupValidationState(
            project_id="test_006",
            entrepreneur_input="Test",
        )
        # Default should be 0 or have default behavior
        ratio = state.calculate_zombie_ratio()
        assert isinstance(ratio, (int, float))
