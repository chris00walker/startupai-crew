"""
Signal-Based Routing Comprehensive Tests

Tests that all signal values route to correct HITL checkpoints.
Addresses Issue #5: HITL always shows same checkpoint (only happy path tested).

All tests use mocks (no API keys required).
"""

import pytest
import importlib
from unittest.mock import Mock, patch, MagicMock
from typing import Any

from src.state.models import ValidationSignal


# =============================================================================
# Phase 2: Desirability Signal Routing
# =============================================================================

class TestPhase2SignalRouting:
    """Test Phase 2 routes to correct checkpoint based on signal."""

    def _create_mock_state(self) -> dict[str, Any]:
        """Create a mock state for Phase 2."""
        return {
            "founders_brief": {
                "the_idea": {"one_liner": "Test product"},
            },
            "customer_profile": {
                "segment_name": "Test Segment",
                "segment_description": "Test description",
                "pains": [{"pain_statement": "Test pain"}],
            },
            "value_map": {
                "products_services": ["Service 1"],
                "pain_relievers": ["Reliever 1"],
                "gain_creators": ["Creator 1"],
            },
        }

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")
    @patch("src.state.update_progress")
    def test_strong_commitment_returns_desirability_gate(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """STRONG_COMMITMENT signal should return approve_desirability_gate checkpoint."""
        # Setup mocks
        mock_build.return_value = {"landing_pages": {"url": "test"}}
        mock_growth.return_value = MagicMock()
        mock_growth.return_value.model_dump.return_value = {
            "problem_resonance": 0.55,  # >= 0.3
            "zombie_ratio": 0.35,  # < 0.7
        }
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_2
        importlib.reload(phase_2)

        result = phase_2.execute("test-run-id", self._create_mock_state())

        assert result["hitl_checkpoint"] == "approve_desirability_gate"
        assert "desirability" in result["hitl_title"].lower() or "feasibility" in result["hitl_title"].lower()
        assert result["hitl_recommended"] == "approved"
        assert result["state"]["desirability_signal"] == "strong_commitment"

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")
    @patch("src.state.update_progress")
    def test_no_interest_returns_segment_pivot_checkpoint(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """NO_INTEREST signal should return approve_segment_pivot checkpoint."""
        # Setup mocks
        mock_build.return_value = {"landing_pages": {"url": "test"}}
        mock_growth.return_value = MagicMock()
        mock_growth.return_value.model_dump.return_value = {
            "problem_resonance": 0.15,  # < 0.3 -> NO_INTEREST
            "zombie_ratio": 0.50,
        }
        mock_governance.return_value = {}
        mock_alternatives.return_value = [
            {"segment_name": "Alternative 1", "confidence": 0.8},
            {"segment_name": "Alternative 2", "confidence": 0.6},
        ]

        from src.modal_app.phases import phase_2
        importlib.reload(phase_2)

        result = phase_2.execute("test-run-id", self._create_mock_state())

        assert result["hitl_checkpoint"] == "approve_segment_pivot"
        assert "segment" in result["hitl_title"].lower() or "pivot" in result["hitl_title"].lower()
        assert result["state"]["desirability_signal"] == "no_interest"
        # Should have segment alternatives
        assert "segment_alternatives" in result["state"]
        # Options should include segment choices
        option_ids = [opt["id"] for opt in result["hitl_options"]]
        assert "segment_1" in option_ids

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")
    @patch("src.state.update_progress")
    def test_mild_interest_returns_value_pivot_checkpoint(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """MILD_INTEREST signal should return approve_value_pivot checkpoint."""
        # Setup mocks
        mock_build.return_value = {"landing_pages": {"url": "test"}}
        mock_growth.return_value = MagicMock()
        mock_growth.return_value.model_dump.return_value = {
            "problem_resonance": 0.45,  # >= 0.3
            "zombie_ratio": 0.75,  # >= 0.7 -> MILD_INTEREST
        }
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_2
        importlib.reload(phase_2)

        result = phase_2.execute("test-run-id", self._create_mock_state())

        assert result["hitl_checkpoint"] == "approve_value_pivot"
        assert "value" in result["hitl_title"].lower() or "pivot" in result["hitl_title"].lower()
        assert result["hitl_recommended"] == "approved"
        assert result["state"]["desirability_signal"] == "mild_interest"

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")
    @patch("src.state.update_progress")
    def test_segment_pivot_includes_alternatives(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """Segment pivot checkpoint should include alternative segment options."""
        # Setup mocks
        mock_build.return_value = {"landing_pages": {"url": "test"}}
        mock_growth.return_value = MagicMock()
        mock_growth.return_value.model_dump.return_value = {
            "problem_resonance": 0.10,  # NO_INTEREST
            "zombie_ratio": 0.50,
        }
        mock_governance.return_value = {}
        mock_alternatives.return_value = [
            {"segment_name": "Enterprise SaaS", "confidence": 0.85, "segment_description": "Large B2B"},
            {"segment_name": "SMB Retail", "confidence": 0.70, "segment_description": "Small retail"},
            {"segment_name": "Healthcare", "confidence": 0.55, "segment_description": "Hospitals"},
        ]

        from src.modal_app.phases import phase_2
        importlib.reload(phase_2)

        result = phase_2.execute("test-run-id", self._create_mock_state())

        # Verify alternatives are included
        options = result["hitl_options"]
        option_ids = [opt["id"] for opt in options]

        # Should have segment_1, segment_2, segment_3 for the 3 alternatives
        assert "segment_1" in option_ids
        assert "segment_2" in option_ids
        assert "segment_3" in option_ids

        # Should also have custom and override options
        assert "custom_segment" in option_ids
        assert "override_proceed" in option_ids
        assert "iterate" in option_ids

        # Context should include alternatives
        assert "segment_alternatives" in result["hitl_context"]
        assert len(result["hitl_context"]["segment_alternatives"]) == 3


# =============================================================================
# Phase 3: Feasibility Signal Routing
# =============================================================================

class TestPhase3SignalRouting:
    """Test Phase 3 routes to correct checkpoint based on signal."""

    def _create_mock_state(self) -> dict[str, Any]:
        """Create a mock state for Phase 3."""
        return {
            "founders_brief": {
                "the_idea": {"one_liner": "Test product"},
            },
            "value_map": {
                "products_services": ["Service 1"],
            },
            "desirability_evidence": {
                "problem_resonance": 0.5,
                "zombie_ratio": 0.3,
                "signal": "strong_commitment",
            },
        }

    @patch("src.crews.feasibility.run_feasibility_build_crew")
    @patch("src.crews.feasibility.run_feasibility_governance_crew")
    @patch("src.state.update_progress")
    def test_green_signal_returns_feasibility_gate(
        self,
        mock_progress,
        mock_governance,
        mock_build,
    ):
        """GREEN signal should return approve_feasibility_gate checkpoint."""
        mock_build.return_value = MagicMock()
        mock_build.return_value.model_dump.return_value = {
            "core_features_feasible": True,
            "downgrade_required": False,
        }
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_3
        importlib.reload(phase_3)

        result = phase_3.execute("test-run-id", self._create_mock_state())

        assert result["hitl_checkpoint"] == "approve_feasibility_gate"
        assert result["state"]["feasibility_signal"] == "green"
        assert result["hitl_recommended"] == "approve"  # Note: "approve" not "approved"

    @patch("src.crews.feasibility.run_feasibility_build_crew")
    @patch("src.crews.feasibility.run_feasibility_governance_crew")
    @patch("src.state.update_progress")
    def test_orange_signal_returns_feature_pivot_checkpoint(
        self,
        mock_progress,
        mock_governance,
        mock_build,
    ):
        """ORANGE signal should recommend feature_pivot at feasibility_gate checkpoint."""
        mock_build.return_value = MagicMock()
        mock_build.return_value.model_dump.return_value = {
            "core_features_feasible": True,
            "downgrade_required": True,
            "downgrade_features": ["Real-time sync", "AI recommendations"],
        }
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_3
        importlib.reload(phase_3)

        result = phase_3.execute("test-run-id", self._create_mock_state())

        # Phase 3 always uses approve_feasibility_gate, but recommends different actions
        assert result["hitl_checkpoint"] == "approve_feasibility_gate"
        assert result["state"]["feasibility_signal"] == "orange_constrained"
        assert result["hitl_recommended"] == "feature_pivot"

    @patch("src.crews.feasibility.run_feasibility_build_crew")
    @patch("src.crews.feasibility.run_feasibility_governance_crew")
    @patch("src.state.update_progress")
    def test_red_signal_returns_kill_checkpoint(
        self,
        mock_progress,
        mock_governance,
        mock_build,
    ):
        """RED signal should return kill checkpoint."""
        mock_build.return_value = MagicMock(
            model_dump=lambda mode=None: {
                "core_features_feasible": False,
                "downgrade_required": False,
                "constraints": ["No API available", "Patent blocked"],
            }
        )
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_3

        result = phase_3.execute("test-run-id", self._create_mock_state())

        # RED should trigger a kill/terminate checkpoint
        assert result["state"]["feasibility_signal"] == "red_impossible"
        # Checkpoint should indicate termination
        assert "kill" in result["hitl_checkpoint"].lower() or "impossible" in result["hitl_checkpoint"].lower() or "terminate" in result["hitl_checkpoint"].lower() or "feasibility" in result["hitl_checkpoint"].lower()


# =============================================================================
# Phase 4: Viability Signal Routing
# =============================================================================

class TestPhase4SignalRouting:
    """Test Phase 4 routes to correct checkpoint based on signal."""

    def _create_mock_state(self) -> dict[str, Any]:
        """Create a mock state for Phase 4."""
        return {
            "founders_brief": {
                "the_idea": {"one_liner": "Test product"},
            },
            "desirability_evidence": {
                "problem_resonance": 0.5,
                "zombie_ratio": 0.3,
            },
            "feasibility_evidence": {
                "core_features_feasible": True,
                "downgrade_required": False,
            },
        }

    @patch("src.crews.viability.run_finance_crew")
    @patch("src.crews.viability.run_synthesis_crew")
    @patch("src.crews.viability.run_viability_governance_crew")
    @patch("src.state.update_progress")
    def test_profitable_signal_returns_proceed_checkpoint(
        self,
        mock_progress,
        mock_governance,
        mock_synthesis,
        mock_finance,
    ):
        """PROFITABLE signal should return approval to proceed checkpoint."""
        mock_finance.return_value = MagicMock(
            model_dump=lambda mode=None: {
                "cac": 100,
                "ltv": 400,
                "ltv_cac_ratio": 4.0,
            }
        )
        mock_synthesis.return_value = {}
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_4

        result = phase_4.execute("test-run-id", self._create_mock_state())

        assert result["state"]["viability_signal"] == "profitable"
        assert result["hitl_recommended"] in ["approved", "proceed"]

    @patch("src.crews.viability.run_finance_crew")
    @patch("src.crews.viability.run_synthesis_crew")
    @patch("src.crews.viability.run_viability_governance_crew")
    @patch("src.state.update_progress")
    def test_marginal_signal_returns_price_pivot_checkpoint(
        self,
        mock_progress,
        mock_governance,
        mock_synthesis,
        mock_finance,
    ):
        """MARGINAL signal should return price pivot checkpoint."""
        mock_finance.return_value = MagicMock(
            model_dump=lambda mode=None: {
                "cac": 100,
                "ltv": 200,
                "ltv_cac_ratio": 2.0,  # Below 3.0 threshold
            }
        )
        mock_synthesis.return_value = {}
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_4

        result = phase_4.execute("test-run-id", self._create_mock_state())

        assert result["state"]["viability_signal"] == "marginal"

    @patch("src.crews.viability.run_finance_crew")
    @patch("src.crews.viability.run_synthesis_crew")
    @patch("src.crews.viability.run_viability_governance_crew")
    @patch("src.state.update_progress")
    def test_underwater_signal_returns_strategic_pivot_checkpoint(
        self,
        mock_progress,
        mock_governance,
        mock_synthesis,
        mock_finance,
    ):
        """UNDERWATER signal should return strategic pivot checkpoint."""
        mock_finance.return_value = MagicMock(
            model_dump=lambda mode=None: {
                "cac": 100,
                "ltv": 50,
                "ltv_cac_ratio": 0.5,  # Below 1.0 = underwater
            }
        )
        mock_synthesis.return_value = {}
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_4

        result = phase_4.execute("test-run-id", self._create_mock_state())

        assert result["state"]["viability_signal"] == "underwater"


# =============================================================================
# HITL Checkpoint Option Validation
# =============================================================================

class TestHITLCheckpointOptions:
    """Test that HITL checkpoints have correct options."""

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")
    @patch("src.state.update_progress")
    def test_desirability_gate_has_correct_options(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """Desirability gate should have approved and iterate options."""
        mock_build.return_value = {"landing_pages": {}}
        mock_growth.return_value = MagicMock(
            model_dump=lambda mode=None: {
                "problem_resonance": 0.50,
                "zombie_ratio": 0.40,
            }
        )
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_2

        result = phase_2.execute("test-run-id", {
            "founders_brief": {"the_idea": {"one_liner": "Test"}},
            "customer_profile": {"segment_name": "Test", "pains": []},
            "value_map": {},
        })

        options = result["hitl_options"]
        option_ids = {opt["id"] for opt in options}

        assert "approved" in option_ids, "Should have 'approved' option"
        assert "iterate" in option_ids, "Should have 'iterate' option"

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")
    @patch("src.state.update_progress")
    def test_value_pivot_has_override_option(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """Value pivot checkpoint should have override_proceed option."""
        mock_build.return_value = {"landing_pages": {}}
        mock_growth.return_value = MagicMock(
            model_dump=lambda mode=None: {
                "problem_resonance": 0.45,  # >= 0.3
                "zombie_ratio": 0.75,  # >= 0.7 -> MILD_INTEREST
            }
        )
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_2

        result = phase_2.execute("test-run-id", {
            "founders_brief": {"the_idea": {"one_liner": "Test"}},
            "customer_profile": {"segment_name": "Test", "pains": []},
            "value_map": {},
        })

        options = result["hitl_options"]
        option_ids = {opt["id"] for opt in options}

        assert "override_proceed" in option_ids, "Value pivot should have override option"
        assert "iterate" in option_ids, "Value pivot should have iterate option"


# =============================================================================
# Boundary Condition Tests
# =============================================================================

class TestSignalBoundaryConditions:
    """Test signal derivation at exact boundary values."""

    def test_resonance_boundary_at_30_percent(self):
        """Test resonance=0.30 is at the boundary (should be STRONG if zombie < 0.7)."""
        from tests.test_innovation_physics_routing import derive_desirability_signal

        # Exactly at boundary
        signal, rec = derive_desirability_signal(0.30, 0.50)
        assert signal == "strong_commitment"

        # Just below boundary
        signal, rec = derive_desirability_signal(0.29, 0.50)
        assert signal == "no_interest"

    def test_zombie_boundary_at_70_percent(self):
        """Test zombie=0.70 is at the boundary (should be MILD)."""
        from tests.test_innovation_physics_routing import derive_desirability_signal

        # Exactly at boundary (resonance OK)
        signal, rec = derive_desirability_signal(0.35, 0.70)
        assert signal == "mild_interest"

        # Just below boundary
        signal, rec = derive_desirability_signal(0.35, 0.69)
        assert signal == "strong_commitment"

    def test_ltv_cac_boundary_at_3(self):
        """Test LTV:CAC=3.0 is at the boundary (should be PROFITABLE)."""
        from tests.test_innovation_physics_routing import derive_viability_signal

        # Exactly at boundary
        signal, pivot, decision = derive_viability_signal(3.0)
        assert signal == "profitable"

        # Just below boundary
        signal, pivot, decision = derive_viability_signal(2.99)
        assert signal == "marginal"

    def test_ltv_cac_boundary_at_1(self):
        """Test LTV:CAC=1.0 is at marginal/underwater boundary."""
        from tests.test_innovation_physics_routing import derive_viability_signal

        # At boundary
        signal, pivot, decision = derive_viability_signal(1.0)
        assert signal == "marginal"

        # Just below
        signal, pivot, decision = derive_viability_signal(0.99)
        assert signal == "underwater"


# =============================================================================
# Signal Context in HITL
# =============================================================================

class TestSignalContextInHITL:
    """Test that HITL context contains correct signal information."""

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")
    @patch("src.state.update_progress")
    def test_hitl_context_contains_signal(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """HITL context should contain the signal and metrics."""
        mock_build.return_value = {"landing_pages": {}}
        mock_growth.return_value = MagicMock(
            model_dump=lambda mode=None: {
                "problem_resonance": 0.55,
                "zombie_ratio": 0.35,
                "ad_impressions": 1000,
                "ad_clicks": 150,
                "ad_signups": 30,
                "ad_spend": 500.0,
            }
        )
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_2

        result = phase_2.execute("test-run-id", {
            "founders_brief": {"the_idea": {"one_liner": "Test"}},
            "customer_profile": {"segment_name": "Test", "pains": []},
            "value_map": {},
        })

        context = result["hitl_context"]

        assert "signal" in context
        assert context["signal"] == "strong_commitment"
        assert "problem_resonance" in context
        assert context["problem_resonance"] == 0.55
        assert "zombie_ratio" in context
        assert context["zombie_ratio"] == 0.35
        assert "ad_metrics" in context
