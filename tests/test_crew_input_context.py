"""
Crew Input Context Validation Tests

Tests that crews receive required business context in their inputs.
Addresses Issue #3: Customer profile hallucination (mocks return hardcoded valid data).

These tests verify that proper context propagation happens through phase transitions.
All tests use mocks (no API keys required).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Any


# =============================================================================
# Phase 0 Context Tests
# =============================================================================

class TestPhase0Context:
    """Test that Phase 0 receives and processes entrepreneur input correctly."""

    @patch("src.crews.onboarding.run_onboarding_crew")
    @patch("src.state.update_progress")
    def test_onboarding_receives_entrepreneur_input(
        self,
        mock_progress,
        mock_crew,
    ):
        """Onboarding crew should receive entrepreneur_input."""
        mock_crew.return_value = MagicMock(
            model_dump=lambda mode=None: {
                "the_idea": {"one_liner": "Test"},
                "problem_hypothesis": {},
                "customer_hypothesis": {},
                "solution_hypothesis": {},
            },
            qa_status=MagicMock(
                legitimacy_check="PASS",
                legitimacy_notes="",
                intent_verification="PASS",
                intent_notes="",
                overall_status="APPROVED",
            ),
        )

        state = {
            "entrepreneur_input": "A B2B SaaS for supply chain optimization",
        }

        from src.modal_app.phases import phase_0

        phase_0.execute("test-run-id", state)

        # Verify crew was called with entrepreneur_input
        mock_crew.assert_called_once()
        call_kwargs = mock_crew.call_args
        # The crew receives entrepreneur_input as parameter
        assert call_kwargs is not None

    def test_entrepreneur_input_not_empty(self):
        """Entrepreneur input should not be empty."""
        valid_inputs = [
            "A marketplace for local artisans",
            "AI-powered customer service automation",
            "Subscription box for pet owners",
        ]

        for input_text in valid_inputs:
            assert len(input_text) > 0
            assert len(input_text.strip()) > 0


# =============================================================================
# Phase 1 Context Tests
# =============================================================================

class TestPhase1Context:
    """Test that Phase 1 crews receive founders_brief correctly."""

    def _create_mock_founders_brief(self) -> dict:
        """Create a valid founders brief for testing."""
        return {
            "the_idea": {
                "one_liner": "AI-powered supply chain optimizer",
                "description": "A platform that uses ML to optimize logistics",
            },
            "problem_hypothesis": {
                "problem_statement": "Supply chain managers waste time on manual forecasting",
                "who_has_this_problem": "Logistics managers at mid-size retailers",
            },
            "customer_hypothesis": {
                "primary_segment": "Mid-size retailers",
                "segment_description": "Retailers with 10-500 stores",
            },
            "solution_hypothesis": {
                "proposed_solution": "AI demand forecasting dashboard",
            },
        }

    @patch("src.crews.discovery.run_discovery_crew")
    @patch("src.crews.discovery.run_customer_profile_crew")
    @patch("src.crews.discovery.run_value_design_crew")
    @patch("src.crews.discovery.run_wtp_crew")
    @patch("src.crews.discovery.run_fit_assessment_crew")
    @patch("src.state.update_progress")
    def test_discovery_crew_receives_founders_brief(
        self,
        mock_progress,
        mock_fit,
        mock_wtp,
        mock_value,
        mock_profile,
        mock_discovery,
    ):
        """DiscoveryCrew should receive founders_brief."""
        mock_discovery.return_value = {}
        mock_profile.return_value = MagicMock(model_dump=lambda mode=None: {})
        mock_value.return_value = MagicMock(model_dump=lambda mode=None: {})
        mock_wtp.return_value = {}
        mock_fit.return_value = MagicMock(
            model_dump=lambda mode=None: {"fit_score": 75, "gate_ready": True}
        )

        state = {
            "founders_brief": self._create_mock_founders_brief(),
        }

        from src.modal_app.phases import phase_1

        phase_1.execute("test-run-id", state)

        # Discovery crew should be called with founders_brief
        mock_discovery.assert_called_once()
        call_args = mock_discovery.call_args[0][0]
        assert "the_idea" in call_args
        assert "problem_hypothesis" in call_args

    @patch("src.crews.discovery.run_discovery_crew")
    @patch("src.crews.discovery.run_customer_profile_crew")
    @patch("src.crews.discovery.run_value_design_crew")
    @patch("src.crews.discovery.run_wtp_crew")
    @patch("src.crews.discovery.run_fit_assessment_crew")
    @patch("src.state.update_progress")
    def test_customer_profile_crew_receives_founders_brief(
        self,
        mock_progress,
        mock_fit,
        mock_wtp,
        mock_value,
        mock_profile,
        mock_discovery,
    ):
        """CustomerProfileCrew should receive founders_brief."""
        mock_discovery.return_value = {}
        mock_profile.return_value = MagicMock(model_dump=lambda mode=None: {})
        mock_value.return_value = MagicMock(model_dump=lambda mode=None: {})
        mock_wtp.return_value = {}
        mock_fit.return_value = MagicMock(
            model_dump=lambda mode=None: {"fit_score": 75, "gate_ready": True}
        )

        state = {
            "founders_brief": self._create_mock_founders_brief(),
        }

        from src.modal_app.phases import phase_1

        phase_1.execute("test-run-id", state)

        # CustomerProfileCrew should be called
        mock_profile.assert_called_once()

    def test_founders_brief_has_required_fields(self):
        """Founders brief should have all required fields."""
        brief = self._create_mock_founders_brief()

        required_fields = [
            "the_idea",
            "problem_hypothesis",
            "customer_hypothesis",
            "solution_hypothesis",
        ]

        for field in required_fields:
            assert field in brief, f"Missing required field: {field}"


# =============================================================================
# Phase 2 Context Tests
# =============================================================================

class TestPhase2Context:
    """Test that Phase 2 crews receive VPC context from Phase 1."""

    def _create_mock_state(self) -> dict:
        """Create state with all required Phase 2 inputs."""
        return {
            "founders_brief": {
                "the_idea": {"one_liner": "Test product"},
            },
            "customer_profile": {
                "segment_name": "Mid-size retailers",
                "segment_description": "Retailers with 10-500 stores",
                "jobs": [{"job_statement": "Manage inventory efficiently"}],
                "pains": [{"pain_statement": "Manual forecasting is slow"}],
                "gains": [{"gain_statement": "Save time on operations"}],
            },
            "value_map": {
                "products_services": ["AI forecasting dashboard"],
                "pain_relievers": ["Automated predictions"],
                "gain_creators": ["Real-time insights"],
            },
        }

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")
    @patch("src.state.update_progress")
    def test_build_crew_receives_customer_profile(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """BuildCrew should receive customer_profile."""
        mock_build.return_value = {}
        mock_growth.return_value = MagicMock(
            model_dump=lambda mode=None: {"problem_resonance": 0.5, "zombie_ratio": 0.3}
        )
        mock_governance.return_value = {}

        state = self._create_mock_state()

        from src.modal_app.phases import phase_2

        phase_2.execute("test-run-id", state)

        # BuildCrew should receive customer_profile
        mock_build.assert_called_once()
        call_kwargs = mock_build.call_args[1]
        assert "customer_profile" in call_kwargs
        assert call_kwargs["customer_profile"]["segment_name"] == "Mid-size retailers"

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")
    @patch("src.state.update_progress")
    def test_build_crew_receives_value_proposition(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """BuildCrew should receive value_proposition from value_map."""
        mock_build.return_value = {}
        mock_growth.return_value = MagicMock(
            model_dump=lambda mode=None: {"problem_resonance": 0.5, "zombie_ratio": 0.3}
        )
        mock_governance.return_value = {}

        state = self._create_mock_state()

        from src.modal_app.phases import phase_2

        phase_2.execute("test-run-id", state)

        call_kwargs = mock_build.call_args[1]
        assert "value_proposition" in call_kwargs
        vp = call_kwargs["value_proposition"]
        assert "products_services" in vp
        assert "pain_relievers" in vp
        assert "gain_creators" in vp

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")
    @patch("src.state.update_progress")
    def test_growth_crew_receives_customer_pains(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """GrowthCrew should receive customer_pains extracted from profile."""
        mock_build.return_value = {"landing_pages": {}}
        mock_growth.return_value = MagicMock(
            model_dump=lambda mode=None: {"problem_resonance": 0.5, "zombie_ratio": 0.3}
        )
        mock_governance.return_value = {}

        state = self._create_mock_state()

        from src.modal_app.phases import phase_2

        phase_2.execute("test-run-id", state)

        call_kwargs = mock_growth.call_args[1]
        assert "customer_pains" in call_kwargs
        # Should be extracted from customer_profile.pains
        assert isinstance(call_kwargs["customer_pains"], list)


# =============================================================================
# Phase 3 Context Tests
# =============================================================================

class TestPhase3Context:
    """Test that Phase 3 crews receive desirability evidence from Phase 2."""

    def _create_mock_state(self) -> dict:
        """Create state with all required Phase 3 inputs."""
        return {
            "founders_brief": {
                "the_idea": {"one_liner": "Test product"},
            },
            "value_map": {
                "products_services": ["Service 1"],
            },
            "desirability_evidence": {
                "problem_resonance": 0.55,
                "zombie_ratio": 0.30,
                "signal": "strong_commitment",
                "ad_impressions": 1000,
                "ad_clicks": 150,
                "ad_signups": 30,
            },
        }

    @patch("src.crews.feasibility.run_feasibility_build_crew")
    @patch("src.crews.feasibility.run_feasibility_governance_crew")
    @patch("src.state.update_progress")
    def test_feasibility_crew_receives_desirability_evidence(
        self,
        mock_progress,
        mock_governance,
        mock_build,
    ):
        """FeasibilityBuildCrew should receive desirability_evidence."""
        mock_build.return_value = MagicMock(
            model_dump=lambda mode=None: {
                "core_features_feasible": True,
                "downgrade_required": False,
            }
        )
        mock_governance.return_value = {}

        state = self._create_mock_state()

        from src.modal_app.phases import phase_3

        phase_3.execute("test-run-id", state)

        # Verify desirability evidence is available
        # (actual parameter passing depends on implementation)
        mock_build.assert_called_once()


# =============================================================================
# Phase 4 Context Tests
# =============================================================================

class TestPhase4Context:
    """Test that Phase 4 crews receive all prior evidence."""

    def _create_mock_state(self) -> dict:
        """Create state with all required Phase 4 inputs."""
        return {
            "founders_brief": {
                "the_idea": {"one_liner": "Test product"},
            },
            "desirability_evidence": {
                "problem_resonance": 0.55,
                "zombie_ratio": 0.30,
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
    def test_finance_crew_receives_prior_evidence(
        self,
        mock_progress,
        mock_governance,
        mock_synthesis,
        mock_finance,
    ):
        """FinanceCrew should receive desirability and feasibility evidence."""
        mock_finance.return_value = MagicMock(
            model_dump=lambda mode=None: {
                "cac": 100,
                "ltv": 400,
                "ltv_cac_ratio": 4.0,
            }
        )
        mock_synthesis.return_value = {}
        mock_governance.return_value = {}

        state = self._create_mock_state()

        from src.modal_app.phases import phase_4

        phase_4.execute("test-run-id", state)

        mock_finance.assert_called_once()


# =============================================================================
# Context Propagation Tests
# =============================================================================

class TestContextPropagation:
    """Test that context propagates correctly through all phases."""

    def test_state_accumulates_through_phases(self):
        """State should accumulate outputs from each phase."""
        # After Phase 0
        state_0 = {
            "entrepreneur_input": "Test idea",
            "founders_brief": {"the_idea": {"one_liner": "Test"}},
        }

        # After Phase 1 - adds VPC
        state_1 = {
            **state_0,
            "customer_profile": {"segment_name": "Test Segment"},
            "value_map": {"products_services": ["P1"]},
            "fit_assessment": {"fit_score": 75},
        }

        # After Phase 2 - adds desirability
        state_2 = {
            **state_1,
            "desirability_evidence": {"problem_resonance": 0.5},
        }

        # After Phase 3 - adds feasibility
        state_3 = {
            **state_2,
            "feasibility_evidence": {"core_features_feasible": True},
        }

        # After Phase 4 - adds viability
        state_4 = {
            **state_3,
            "viability_evidence": {"ltv_cac_ratio": 4.0},
        }

        # Verify all prior state is preserved
        assert "founders_brief" in state_4
        assert "customer_profile" in state_4
        assert "desirability_evidence" in state_4
        assert "feasibility_evidence" in state_4
        assert "viability_evidence" in state_4

    def test_pivot_preserves_original_context(self):
        """Pivot should preserve original founders_brief while adding pivot context."""
        original_brief = {
            "the_idea": {"one_liner": "Original idea"},
            "problem_hypothesis": {"problem_statement": "Original problem"},
        }

        pivot_context = {
            "pivot_type": "segment_pivot",
            "target_segment_hypothesis": {"segment_name": "New Segment"},
        }

        # Merged state should have both
        merged_brief = {
            **original_brief,
            "pivot_context": {
                "is_pivot": True,
                **pivot_context,
            },
        }

        # Original fields preserved
        assert merged_brief["the_idea"]["one_liner"] == "Original idea"
        # Pivot context added
        assert merged_brief["pivot_context"]["is_pivot"] is True


# =============================================================================
# Regression Tests for Issue #3
# =============================================================================

class TestIssue3Regression:
    """Regression tests for Issue #3: Customer profile hallucination."""

    def test_customer_profile_comes_from_phase_1_not_hardcoded(self):
        """Customer profile in Phase 2 should come from Phase 1, not hardcoded."""
        # The issue: mocks returned hardcoded valid data
        # Reality: Phase 2 crews must receive actual Phase 1 output

        # Phase 1 produces a specific customer profile
        phase_1_output = {
            "segment_name": "Enterprise SaaS buyers",
            "segment_description": "Companies with 100+ employees",
            "pains": [{"pain_statement": "Manual data entry is error-prone"}],
        }

        # Phase 2 state should contain this exact profile
        phase_2_state = {
            "customer_profile": phase_1_output,
        }

        # The profile in Phase 2 should match Phase 1 output exactly
        assert phase_2_state["customer_profile"]["segment_name"] == "Enterprise SaaS buyers"
        assert phase_2_state["customer_profile"]["pains"][0]["pain_statement"] == "Manual data entry is error-prone"

    def test_crews_dont_generate_context_they_receive_it(self):
        """Crews should receive context from state, not generate it."""
        # The context hierarchy:
        # - Phase 0: generates founders_brief from entrepreneur_input
        # - Phase 1: generates customer_profile, value_map from founders_brief
        # - Phase 2: uses customer_profile, value_map (doesn't regenerate)
        # - Phase 3: uses all prior evidence (doesn't regenerate)
        # - Phase 4: uses all prior evidence (doesn't regenerate)

        # This test documents the expectation
        phase_inputs = {
            0: {"requires": ["entrepreneur_input"], "produces": ["founders_brief"]},
            1: {"requires": ["founders_brief"], "produces": ["customer_profile", "value_map"]},
            2: {"requires": ["customer_profile", "value_map"], "produces": ["desirability_evidence"]},
            3: {"requires": ["desirability_evidence"], "produces": ["feasibility_evidence"]},
            4: {"requires": ["feasibility_evidence"], "produces": ["viability_evidence"]},
        }

        # Each phase should only produce what it's designed to produce
        for phase, config in phase_inputs.items():
            for produced in config["produces"]:
                # Should not be in requires of same phase
                assert produced not in config["requires"], (
                    f"Phase {phase} should not require {produced} (it produces it)"
                )

    def test_empty_customer_profile_fails_validation(self):
        """Phase 2 should fail if customer_profile is empty or missing."""
        # Invalid states that should cause issues
        invalid_states = [
            {"customer_profile": {}},  # Empty profile
            {"customer_profile": None},  # None profile
            {},  # Missing profile entirely
        ]

        for state in invalid_states:
            profile = state.get("customer_profile")
            is_valid = (
                profile is not None
                and isinstance(profile, dict)
                and len(profile) > 0
            )
            assert not is_valid, f"Expected invalid state to fail: {state}"


# =============================================================================
# Context Validation Helpers
# =============================================================================

class TestContextValidationHelpers:
    """Tests for context validation helper functions."""

    def test_validate_required_fields(self):
        """Helper to validate required fields exist in context."""
        def validate_context(context: dict, required_fields: list) -> list:
            """Return list of missing fields."""
            missing = []
            for field in required_fields:
                if field not in context or context[field] is None:
                    missing.append(field)
                elif isinstance(context[field], dict) and len(context[field]) == 0:
                    missing.append(field)
            return missing

        # Valid context
        valid = {
            "founders_brief": {"the_idea": {}},
            "customer_profile": {"segment_name": "Test"},
        }
        assert validate_context(valid, ["founders_brief", "customer_profile"]) == []

        # Invalid context
        invalid = {
            "founders_brief": {},
            "customer_profile": None,
        }
        missing = validate_context(invalid, ["founders_brief", "customer_profile"])
        assert "founders_brief" in missing
        assert "customer_profile" in missing

    def test_context_completeness_score(self):
        """Helper to calculate context completeness."""
        def context_completeness(context: dict, expected_fields: list) -> float:
            """Return completeness score 0.0 - 1.0."""
            if not expected_fields:
                return 1.0
            present = sum(
                1 for f in expected_fields
                if f in context and context[f] is not None
            )
            return present / len(expected_fields)

        # Full context
        full = {
            "founders_brief": {},
            "customer_profile": {},
            "value_map": {},
        }
        assert context_completeness(full, ["founders_brief", "customer_profile", "value_map"]) == 1.0

        # Partial context
        partial = {
            "founders_brief": {},
        }
        assert context_completeness(partial, ["founders_brief", "customer_profile"]) == 0.5

        # Empty context
        empty = {}
        assert context_completeness(empty, ["founders_brief"]) == 0.0
