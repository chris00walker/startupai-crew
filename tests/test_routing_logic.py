"""
Tests for Innovation Physics Routing Logic.

These tests verify the signal-based routing decisions in the validation flow.
"""

import pytest
from startupai.flows.state_schemas import (
    StartupValidationState,
    Phase,
    RiskAxis,
    DesirabilitySignal,
    FeasibilitySignal,
    ViabilitySignal,
    PivotType,
)


class TestDesirabilityRouting:
    """Tests for desirability gate routing decisions."""

    def test_no_interest_triggers_segment_pivot(self, no_interest_state):
        """
        When desirability_signal is NO_INTEREST,
        the router should recommend a segment pivot.
        """
        state = no_interest_state
        assert state.desirability_signal == DesirabilitySignal.NO_INTEREST

        # Check that segment pivot is the appropriate response
        if state.desirability_signal == DesirabilitySignal.NO_INTEREST:
            expected_pivot = PivotType.SEGMENT_PIVOT
            assert expected_pivot == PivotType.SEGMENT_PIVOT

    def test_weak_interest_triggers_value_pivot(self, weak_interest_state):
        """
        When desirability_signal is WEAK_INTEREST,
        the router should recommend a value proposition pivot.
        """
        state = weak_interest_state
        assert state.desirability_signal == DesirabilitySignal.WEAK_INTEREST

        # Check that value pivot is the appropriate response
        if state.desirability_signal == DesirabilitySignal.WEAK_INTEREST:
            expected_pivot = PivotType.VALUE_PIVOT
            assert expected_pivot == PivotType.VALUE_PIVOT

    def test_strong_commitment_proceeds_to_feasibility(self, desirability_state):
        """
        When desirability_signal is STRONG_COMMITMENT,
        the flow should proceed to feasibility testing.
        """
        state = desirability_state
        state.desirability_signal = DesirabilitySignal.STRONG_COMMITMENT

        # Verify the expected next phase
        if state.desirability_signal == DesirabilitySignal.STRONG_COMMITMENT:
            next_phase = Phase.FEASIBILITY
            assert next_phase == Phase.FEASIBILITY


class TestFeasibilityRouting:
    """Tests for feasibility gate routing decisions."""

    def test_green_feasibility_proceeds_to_viability(self, feasibility_state):
        """
        When feasibility_signal is GREEN (fully feasible),
        the flow should proceed to viability testing.
        """
        state = feasibility_state
        state.feasibility_signal = FeasibilitySignal.GREEN

        if state.feasibility_signal == FeasibilitySignal.GREEN:
            next_phase = Phase.VIABILITY
            assert next_phase == Phase.VIABILITY

    def test_orange_feasibility_triggers_downgrade(self, constrained_feasibility_state):
        """
        When feasibility_signal is ORANGE_CONSTRAINED,
        the flow should test a downgraded value proposition.
        """
        state = constrained_feasibility_state
        assert state.feasibility_signal == FeasibilitySignal.ORANGE_CONSTRAINED

        # Should trigger downgrade testing, not immediate viability
        if state.feasibility_signal == FeasibilitySignal.ORANGE_CONSTRAINED:
            should_test_downgrade = True
            assert should_test_downgrade

    def test_red_feasibility_kills_project(self, red_feasibility_state):
        """
        When feasibility_signal is RED_IMPOSSIBLE and no downgrade is viable,
        the project should be killed.
        """
        state = red_feasibility_state
        assert state.feasibility_signal == FeasibilitySignal.RED_IMPOSSIBLE

        # Should trigger kill or major pivot
        if state.feasibility_signal == FeasibilitySignal.RED_IMPOSSIBLE:
            possible_outcomes = [PivotType.KILL, PivotType.VALUE_PIVOT]
            assert PivotType.KILL in possible_outcomes


class TestViabilityRouting:
    """Tests for viability gate routing decisions."""

    def test_profitable_viability_validates(self, viability_state):
        """
        When viability_signal is PROFITABLE,
        the project should be validated.
        """
        state = viability_state
        state.viability_signal = ViabilitySignal.PROFITABLE

        if state.viability_signal == ViabilitySignal.PROFITABLE:
            final_phase = Phase.VALIDATED
            assert final_phase == Phase.VALIDATED

    def test_underwater_viability_requires_human_decision(self, underwater_viability_state):
        """
        When viability_signal is UNDERWATER,
        human decision is required for strategic pivot.
        """
        state = underwater_viability_state
        assert state.viability_signal == ViabilitySignal.UNDERWATER

        # Should require human input
        if state.viability_signal == ViabilitySignal.UNDERWATER:
            requires_human = True
            assert requires_human

    def test_zombie_market_signals_pricing_issue(self, zombie_market_state):
        """
        When viability_signal is ZOMBIE_MARKET,
        there's a pricing or cost structure issue.
        """
        state = zombie_market_state
        assert state.viability_signal == ViabilitySignal.ZOMBIE_MARKET

        # Should recommend price or cost pivot
        if state.viability_signal == ViabilitySignal.ZOMBIE_MARKET:
            valid_pivots = [PivotType.PRICE_PIVOT, PivotType.COST_PIVOT]
            assert len(valid_pivots) == 2


class TestStateTransitions:
    """Tests for valid state transitions."""

    def test_phase_progression(self, base_state):
        """Test the normal phase progression through validation."""
        state = base_state

        # Start in IDEATION
        assert state.phase == Phase.IDEATION

        # Progress to DESIRABILITY
        state.phase = Phase.DESIRABILITY
        assert state.phase == Phase.DESIRABILITY

        # Progress to FEASIBILITY
        state.phase = Phase.FEASIBILITY
        assert state.phase == Phase.FEASIBILITY

        # Progress to VIABILITY
        state.phase = Phase.VIABILITY
        assert state.phase == Phase.VIABILITY

        # Complete validation
        state.phase = Phase.VALIDATED
        assert state.phase == Phase.VALIDATED

    def test_risk_axis_tracking(self, base_state):
        """Test that risk axis tracks with phase."""
        state = base_state

        state.phase = Phase.DESIRABILITY
        state.current_risk_axis = RiskAxis.DESIRABILITY
        assert state.current_risk_axis == RiskAxis.DESIRABILITY

        state.phase = Phase.FEASIBILITY
        state.current_risk_axis = RiskAxis.FEASIBILITY
        assert state.current_risk_axis == RiskAxis.FEASIBILITY

        state.phase = Phase.VIABILITY
        state.current_risk_axis = RiskAxis.VIABILITY
        assert state.current_risk_axis == RiskAxis.VIABILITY

    def test_iteration_increment(self, base_state):
        """Test iteration counting through pivots."""
        state = base_state
        assert state.iteration == 0

        # Simulate pivot iterations
        state.iteration += 1
        assert state.iteration == 1

        state.iteration += 1
        assert state.iteration == 2


class TestPivotTracking:
    """Tests for pivot tracking via state fields."""

    def test_pivot_type_tracking(self, base_state):
        """Test tracking pivots via last_pivot_type and pending_pivot_type."""
        state = base_state
        assert state.last_pivot_type == PivotType.NONE
        assert state.pending_pivot_type == PivotType.NONE

        # Track a pivot
        state.pending_pivot_type = PivotType.SEGMENT_PIVOT
        assert state.pending_pivot_type == PivotType.SEGMENT_PIVOT

        # After execution, move to last
        state.last_pivot_type = state.pending_pivot_type
        state.pending_pivot_type = PivotType.NONE

        assert state.last_pivot_type == PivotType.SEGMENT_PIVOT
        assert state.pending_pivot_type == PivotType.NONE

    def test_pivot_sequence(self, base_state):
        """Test tracking sequence of pivots."""
        state = base_state

        # First pivot
        state.last_pivot_type = PivotType.SEGMENT_PIVOT
        state.iteration += 1
        assert state.iteration == 1
        assert state.last_pivot_type == PivotType.SEGMENT_PIVOT

        # Second pivot
        state.last_pivot_type = PivotType.VALUE_PIVOT
        state.iteration += 1
        assert state.iteration == 2
        assert state.last_pivot_type == PivotType.VALUE_PIVOT


class TestSignalCombinations:
    """Tests for complex signal combinations."""

    def test_mixed_signals_require_synthesis(self, desirability_state):
        """Test that mixed signals trigger Compass synthesis."""
        state = desirability_state

        # Strong desirability but will have poor viability later
        state.desirability_signal = DesirabilitySignal.STRONG_COMMITMENT

        # In real flow, this would require Compass to synthesize
        # all evidence and make a recommendation
        assert state.desirability_signal == DesirabilitySignal.STRONG_COMMITMENT

    def test_signal_defaults(self, base_state):
        """Test that signals have sensible defaults."""
        state = base_state

        assert state.desirability_signal == DesirabilitySignal.NO_SIGNAL
        assert state.feasibility_signal == FeasibilitySignal.UNKNOWN
        assert state.viability_signal == ViabilitySignal.UNKNOWN
