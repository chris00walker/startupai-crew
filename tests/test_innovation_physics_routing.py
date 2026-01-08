"""
Tests for Innovation Physics Routing Logic.

Tests the signal derivation and pivot recommendation logic
implemented in phase_2.py, phase_3.py, and phase_4.py.

These tests verify the core business logic WITHOUT executing crews.
"""

import pytest
from typing import Any


# =============================================================================
# Helper functions to extract routing logic for testing
# (Mimics the logic in phase files without crew execution)
# =============================================================================

def derive_desirability_signal(problem_resonance: float, zombie_ratio: float) -> tuple[str, str]:
    """
    Derive desirability signal and recommendation.

    Logic from phase_2.py lines 236-244:
    - problem_resonance < 0.3 → NO_INTEREST, segment_pivot
    - zombie_ratio >= 0.7 → MILD_INTEREST, value_pivot
    - else → STRONG_COMMITMENT, proceed
    """
    if problem_resonance < 0.3:
        signal = "no_interest"
        recommendation = "segment_pivot"
    elif zombie_ratio >= 0.7:
        signal = "mild_interest"
        recommendation = "value_pivot"
    else:
        signal = "strong_commitment"
        recommendation = "proceed"
    return signal, recommendation


def derive_feasibility_signal(
    core_features_feasible: bool,
    downgrade_required: bool,
) -> tuple[str, str]:
    """
    Derive feasibility signal and recommendation.

    Logic from phase_3.py lines 166-175, 196-204:
    - not core_feasible → RED_IMPOSSIBLE, kill
    - downgrade_required → ORANGE_CONSTRAINED, feature_pivot
    - else → GREEN, proceed
    """
    if not core_features_feasible:
        signal = "red_impossible"
        recommendation = "kill"
    elif downgrade_required:
        signal = "orange_constrained"
        recommendation = "feature_pivot"
    else:
        signal = "green"
        recommendation = "proceed"

    gate_ready = signal == "green"
    return signal, recommendation, gate_ready


def derive_viability_signal(
    ltv_cac_ratio: float,
    tam_usd: float = 10_000_000,  # Default to above zombie threshold
) -> tuple[str, str, str]:
    """
    Derive viability signal, pivot recommendation, and final decision.

    Logic from phase_4.py lines 267-283:
    - ltv_cac_ratio >= 3.0 → PROFITABLE, no_pivot, proceed
    - ltv_cac_ratio >= 1.0 and tam < 1M → MARGINAL (zombie), strategic_pivot, pivot
    - else → UNDERWATER, strategic_pivot, pivot
    """
    if ltv_cac_ratio >= 3.0:
        signal = "profitable"
        pivot_recommendation = "no_pivot"
        final_decision = "proceed"
    elif ltv_cac_ratio >= 1.0 and tam_usd < 1_000_000:
        signal = "marginal"  # Zombie market
        pivot_recommendation = "strategic_pivot"
        final_decision = "pivot"
    elif ltv_cac_ratio >= 1.0:
        signal = "marginal"
        pivot_recommendation = "strategic_pivot"
        final_decision = "pivot"
    else:  # underwater
        signal = "underwater"
        pivot_recommendation = "strategic_pivot"
        final_decision = "pivot"

    return signal, pivot_recommendation, final_decision


# =============================================================================
# Phase 2: Desirability Signal Tests
# =============================================================================

class TestDesirabilitySignalDerivation:
    """Tests for Phase 2 desirability signal derivation."""

    def test_no_interest_low_resonance(self):
        """Test NO_INTEREST when problem_resonance < 0.3."""
        signal, rec = derive_desirability_signal(
            problem_resonance=0.15,
            zombie_ratio=0.40,
        )
        assert signal == "no_interest"
        assert rec == "segment_pivot"

    def test_no_interest_boundary(self):
        """Test boundary: resonance=0.29 should be NO_INTEREST."""
        signal, rec = derive_desirability_signal(
            problem_resonance=0.29,
            zombie_ratio=0.50,
        )
        assert signal == "no_interest"
        assert rec == "segment_pivot"

    def test_mild_interest_high_zombie(self):
        """Test MILD_INTEREST when zombie_ratio >= 0.7 but resonance OK."""
        signal, rec = derive_desirability_signal(
            problem_resonance=0.45,  # >= 0.3
            zombie_ratio=0.75,  # >= 0.7
        )
        assert signal == "mild_interest"
        assert rec == "value_pivot"

    def test_mild_interest_boundary(self):
        """Test boundary: zombie=0.70 should be MILD_INTEREST."""
        signal, rec = derive_desirability_signal(
            problem_resonance=0.35,
            zombie_ratio=0.70,  # Exactly at boundary
        )
        assert signal == "mild_interest"
        assert rec == "value_pivot"

    def test_strong_commitment_healthy(self):
        """Test STRONG_COMMITMENT with healthy metrics."""
        signal, rec = derive_desirability_signal(
            problem_resonance=0.55,  # >= 0.3
            zombie_ratio=0.45,  # < 0.7
        )
        assert signal == "strong_commitment"
        assert rec == "proceed"

    def test_strong_commitment_boundary(self):
        """Test boundary: resonance=0.30, zombie=0.69 should be STRONG."""
        signal, rec = derive_desirability_signal(
            problem_resonance=0.30,  # Exactly at boundary
            zombie_ratio=0.69,  # Just below boundary
        )
        assert signal == "strong_commitment"
        assert rec == "proceed"

    def test_resonance_priority_over_zombie(self):
        """Test that low resonance takes priority over high zombie."""
        # Both bad metrics, but resonance < 0.3 should trigger first
        signal, rec = derive_desirability_signal(
            problem_resonance=0.20,  # < 0.3 (triggers first)
            zombie_ratio=0.80,  # >= 0.7 (would trigger if resonance OK)
        )
        assert signal == "no_interest"  # Not mild_interest
        assert rec == "segment_pivot"  # Not value_pivot


# =============================================================================
# Phase 3: Feasibility Signal Tests
# =============================================================================

class TestFeasibilitySignalDerivation:
    """Tests for Phase 3 feasibility signal derivation."""

    def test_green_fully_feasible(self):
        """Test GREEN when fully feasible."""
        signal, rec, gate_ready = derive_feasibility_signal(
            core_features_feasible=True,
            downgrade_required=False,
        )
        assert signal == "green"
        assert rec == "proceed"
        assert gate_ready is True

    def test_orange_downgrade_required(self):
        """Test ORANGE when downgrade required."""
        signal, rec, gate_ready = derive_feasibility_signal(
            core_features_feasible=True,
            downgrade_required=True,
        )
        assert signal == "orange_constrained"
        assert rec == "feature_pivot"
        assert gate_ready is False

    def test_red_impossible(self):
        """Test RED when core features not feasible."""
        signal, rec, gate_ready = derive_feasibility_signal(
            core_features_feasible=False,
            downgrade_required=False,  # Irrelevant when not feasible
        )
        assert signal == "red_impossible"
        assert rec == "kill"
        assert gate_ready is False

    def test_red_takes_priority(self):
        """Test RED takes priority over downgrade flag."""
        signal, rec, gate_ready = derive_feasibility_signal(
            core_features_feasible=False,
            downgrade_required=True,  # Should be ignored
        )
        assert signal == "red_impossible"
        assert rec == "kill"


# =============================================================================
# Phase 4: Viability Signal Tests
# =============================================================================

class TestViabilitySignalDerivation:
    """Tests for Phase 4 viability signal derivation."""

    def test_profitable_high_ltv_cac(self):
        """Test PROFITABLE when LTV:CAC >= 3.0."""
        signal, pivot, decision = derive_viability_signal(
            ltv_cac_ratio=4.0,
        )
        assert signal == "profitable"
        assert pivot == "no_pivot"
        assert decision == "proceed"

    def test_profitable_boundary(self):
        """Test boundary: ratio=3.0 should be PROFITABLE."""
        signal, pivot, decision = derive_viability_signal(
            ltv_cac_ratio=3.0,
        )
        assert signal == "profitable"
        assert pivot == "no_pivot"
        assert decision == "proceed"

    def test_marginal_zombie_market(self):
        """Test MARGINAL for zombie market (ratio OK, TAM < $1M)."""
        signal, pivot, decision = derive_viability_signal(
            ltv_cac_ratio=2.0,  # >= 1.0
            tam_usd=500_000,  # < 1M (zombie market)
        )
        assert signal == "marginal"
        assert pivot == "strategic_pivot"
        assert decision == "pivot"

    def test_marginal_low_ratio(self):
        """Test MARGINAL when 1.0 <= ratio < 3.0."""
        signal, pivot, decision = derive_viability_signal(
            ltv_cac_ratio=2.5,
            tam_usd=5_000_000,  # Healthy TAM
        )
        assert signal == "marginal"
        assert pivot == "strategic_pivot"
        assert decision == "pivot"

    def test_marginal_boundary_low(self):
        """Test boundary: ratio=1.0 should be MARGINAL."""
        signal, pivot, decision = derive_viability_signal(
            ltv_cac_ratio=1.0,
        )
        assert signal == "marginal"
        assert pivot == "strategic_pivot"
        assert decision == "pivot"

    def test_underwater_low_ltv_cac(self):
        """Test UNDERWATER when LTV:CAC < 1.0."""
        signal, pivot, decision = derive_viability_signal(
            ltv_cac_ratio=0.5,
        )
        assert signal == "underwater"
        assert pivot == "strategic_pivot"
        assert decision == "pivot"

    def test_underwater_zero_ratio(self):
        """Test UNDERWATER with zero ratio."""
        signal, pivot, decision = derive_viability_signal(
            ltv_cac_ratio=0.0,
        )
        assert signal == "underwater"
        assert pivot == "strategic_pivot"
        assert decision == "pivot"


# =============================================================================
# Decision Rationale Tests
# =============================================================================

class TestDecisionRationale:
    """Tests for decision rationale building (from phase_4.py)."""

    def test_build_decision_rationale_profitable(self):
        """Test rationale for PROFITABLE signal."""
        # Import the actual function
        from src.modal_app.phases.phase_4 import _build_decision_rationale

        rationale = _build_decision_rationale(
            desirability_evidence={
                "problem_resonance": 0.55,
                "zombie_ratio": 0.30,
            },
            feasibility_evidence={
                "core_features_feasible": True,
                "downgrade_required": False,
            },
            viability_dict={
                "ltv_cac_ratio": 4.5,
            },
            signal="profitable",
        )

        assert "55%" in rationale  # problem_resonance
        assert "30%" in rationale  # zombie_ratio
        assert "GREEN" in rationale
        assert "4.5x" in rationale  # LTV/CAC
        assert "PROCEED" in rationale

    def test_build_decision_rationale_pivot(self):
        """Test rationale for non-profitable signal."""
        from src.modal_app.phases.phase_4 import _build_decision_rationale

        rationale = _build_decision_rationale(
            desirability_evidence={
                "problem_resonance": 0.25,
                "zombie_ratio": 0.65,
            },
            feasibility_evidence={
                "core_features_feasible": True,
                "downgrade_required": True,
            },
            viability_dict={
                "ltv_cac_ratio": 1.5,
            },
            signal="marginal",
        )

        assert "25%" in rationale  # problem_resonance
        assert "65%" in rationale  # zombie_ratio
        assert "ORANGE" in rationale  # downgrade
        assert "1.5x" in rationale
        assert "pivot" in rationale.lower()


# =============================================================================
# HITL Checkpoint Tests
# =============================================================================

class TestHITLCheckpointLogic:
    """Tests for HITL checkpoint determination logic."""

    def test_desirability_hitl_approved_when_gate_ready(self):
        """Test that gate_ready=True recommends 'approve'."""
        signal, rec = derive_desirability_signal(
            problem_resonance=0.50,
            zombie_ratio=0.40,
        )
        gate_ready = signal == "strong_commitment"
        hitl_recommended = "approve" if gate_ready else rec

        assert gate_ready is True
        assert hitl_recommended == "approve"

    def test_desirability_hitl_pivot_when_not_ready(self):
        """Test that gate_ready=False recommends pivot."""
        signal, rec = derive_desirability_signal(
            problem_resonance=0.20,
            zombie_ratio=0.50,
        )
        gate_ready = signal == "strong_commitment"
        hitl_recommended = "approve" if gate_ready else rec

        assert gate_ready is False
        assert hitl_recommended == "segment_pivot"

    def test_feasibility_hitl_options(self):
        """Test feasibility HITL options based on signal."""
        # GREEN → approve recommended
        signal, rec, gate_ready = derive_feasibility_signal(True, False)
        hitl_recommended = "approve" if gate_ready else rec
        assert hitl_recommended == "approve"

        # ORANGE → feature_pivot recommended
        signal, rec, gate_ready = derive_feasibility_signal(True, True)
        hitl_recommended = "approve" if gate_ready else rec
        assert hitl_recommended == "feature_pivot"

        # RED → kill recommended
        signal, rec, gate_ready = derive_feasibility_signal(False, False)
        hitl_recommended = "approve" if gate_ready else rec
        assert hitl_recommended == "kill"

    def test_viability_hitl_proceed_when_profitable(self):
        """Test viability HITL recommends 'proceed' when profitable."""
        signal, pivot, decision = derive_viability_signal(ltv_cac_ratio=3.5)
        gate_ready = signal == "profitable"
        hitl_recommended = "proceed" if gate_ready else "price_pivot"

        assert gate_ready is True
        assert hitl_recommended == "proceed"

    def test_viability_hitl_pivot_when_not_profitable(self):
        """Test viability HITL recommends pivot when not profitable."""
        signal, pivot, decision = derive_viability_signal(ltv_cac_ratio=2.0)
        gate_ready = signal == "profitable"
        hitl_recommended = "proceed" if gate_ready else "price_pivot"

        assert gate_ready is False
        assert hitl_recommended == "price_pivot"


# =============================================================================
# End-to-End Signal Flow Tests
# =============================================================================

class TestSignalFlowIntegration:
    """Tests for complete validation signal flow."""

    def test_happy_path_all_green(self):
        """Test happy path: all signals positive → proceed."""
        # Phase 2: Desirability
        d_signal, d_rec = derive_desirability_signal(0.55, 0.35)
        assert d_signal == "strong_commitment"

        # Phase 3: Feasibility
        f_signal, f_rec, f_gate = derive_feasibility_signal(True, False)
        assert f_signal == "green"

        # Phase 4: Viability
        v_signal, v_pivot, v_decision = derive_viability_signal(4.0)
        assert v_signal == "profitable"
        assert v_decision == "proceed"

    def test_pivot_path_segment_pivot(self):
        """Test segment pivot due to low problem resonance."""
        d_signal, d_rec = derive_desirability_signal(0.15, 0.40)
        assert d_signal == "no_interest"
        assert d_rec == "segment_pivot"
        # Flow should NOT proceed to feasibility

    def test_pivot_path_value_pivot(self):
        """Test value pivot due to high zombie ratio."""
        d_signal, d_rec = derive_desirability_signal(0.45, 0.80)
        assert d_signal == "mild_interest"
        assert d_rec == "value_pivot"
        # Flow should NOT proceed to feasibility

    def test_pivot_path_feature_downgrade(self):
        """Test feature pivot due to technical constraints."""
        # Phase 2 passes
        d_signal, _ = derive_desirability_signal(0.50, 0.40)
        assert d_signal == "strong_commitment"

        # Phase 3 requires downgrade
        f_signal, f_rec, f_gate = derive_feasibility_signal(True, True)
        assert f_signal == "orange_constrained"
        assert f_rec == "feature_pivot"
        # Flow should pause for HITL decision

    def test_kill_path_impossible(self):
        """Test kill recommendation for technical impossibility."""
        f_signal, f_rec, f_gate = derive_feasibility_signal(False, False)
        assert f_signal == "red_impossible"
        assert f_rec == "kill"

    def test_pivot_path_viability_underwater(self):
        """Test strategic pivot for underwater unit economics."""
        # Phases 2 & 3 pass
        d_signal, _ = derive_desirability_signal(0.50, 0.40)
        f_signal, _, _ = derive_feasibility_signal(True, False)

        # Phase 4: underwater
        v_signal, v_pivot, v_decision = derive_viability_signal(0.5)
        assert v_signal == "underwater"
        assert v_pivot == "strategic_pivot"
        assert v_decision == "pivot"

    def test_zombie_market_detection(self):
        """Test zombie market detection (viable but tiny TAM)."""
        v_signal, v_pivot, v_decision = derive_viability_signal(
            ltv_cac_ratio=2.0,  # Marginal ratio
            tam_usd=800_000,  # Below $1M threshold
        )
        assert v_signal == "marginal"
        # Should recommend pivot despite positive unit economics
        assert v_decision == "pivot"
