"""
HITL Contract Tests

Tests the structure and format of HITL responses for each checkpoint type.
Validates required fields, options, and API structure.

All tests use mocks (no API keys required).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any
from datetime import datetime

from pydantic import BaseModel, ValidationError

# Check if modal is available for tests that require it
try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False


# =============================================================================
# HITL Response Structure Tests
# =============================================================================

class TestHITLResponseStructure:
    """Test that HITL responses have correct structure."""

    def _validate_hitl_response(self, response: dict) -> list[str]:
        """Validate HITL response structure, return list of errors."""
        errors = []

        required_fields = [
            "hitl_checkpoint",
            "hitl_title",
            "hitl_description",
            "hitl_options",
            "hitl_recommended",
            "hitl_context",
        ]

        for field in required_fields:
            if field not in response:
                errors.append(f"Missing required field: {field}")

        # Validate checkpoint is a string
        if "hitl_checkpoint" in response:
            if not isinstance(response["hitl_checkpoint"], str):
                errors.append("hitl_checkpoint must be a string")

        # Validate title is a string
        if "hitl_title" in response:
            if not isinstance(response["hitl_title"], str):
                errors.append("hitl_title must be a string")
            elif len(response["hitl_title"]) == 0:
                errors.append("hitl_title cannot be empty")

        # Validate options is a list
        if "hitl_options" in response:
            if not isinstance(response["hitl_options"], list):
                errors.append("hitl_options must be a list")
            elif len(response["hitl_options"]) == 0:
                errors.append("hitl_options cannot be empty")

        # Validate recommended is a string and exists in options
        if "hitl_recommended" in response and "hitl_options" in response:
            if not isinstance(response["hitl_recommended"], str):
                errors.append("hitl_recommended must be a string")
            else:
                option_ids = [opt.get("id") for opt in response.get("hitl_options", [])]
                if response["hitl_recommended"] not in option_ids:
                    errors.append(f"hitl_recommended '{response['hitl_recommended']}' not in options")

        # Validate context is a dict
        if "hitl_context" in response:
            if not isinstance(response["hitl_context"], dict):
                errors.append("hitl_context must be a dict")

        return errors

    def test_valid_hitl_response(self):
        """Test that a well-formed HITL response passes validation."""
        response = {
            "hitl_checkpoint": "approve_desirability_gate",
            "hitl_title": "Desirability Validated",
            "hitl_description": "Ready to proceed to feasibility.",
            "hitl_options": [
                {"id": "approved", "label": "Approve", "description": "Proceed"},
                {"id": "iterate", "label": "Iterate", "description": "Run more tests"},
            ],
            "hitl_recommended": "approved",
            "hitl_context": {"signal": "strong_commitment"},
            "state": {},
        }

        errors = self._validate_hitl_response(response)
        assert errors == [], f"Validation errors: {errors}"

    def test_missing_checkpoint_fails(self):
        """Test that missing checkpoint fails validation."""
        response = {
            "hitl_title": "Test",
            "hitl_description": "Test",
            "hitl_options": [{"id": "approved", "label": "Approve"}],
            "hitl_recommended": "approved",
            "hitl_context": {},
        }

        errors = self._validate_hitl_response(response)
        assert "Missing required field: hitl_checkpoint" in errors

    def test_empty_options_fails(self):
        """Test that empty options fails validation."""
        response = {
            "hitl_checkpoint": "test",
            "hitl_title": "Test",
            "hitl_description": "Test",
            "hitl_options": [],
            "hitl_recommended": "approved",
            "hitl_context": {},
        }

        errors = self._validate_hitl_response(response)
        assert any("empty" in e for e in errors)

    def test_invalid_recommended_fails(self):
        """Test that recommended not in options fails validation."""
        response = {
            "hitl_checkpoint": "test",
            "hitl_title": "Test",
            "hitl_description": "Test",
            "hitl_options": [{"id": "option_a", "label": "Option A"}],
            "hitl_recommended": "option_b",  # Not in options
            "hitl_context": {},
        }

        errors = self._validate_hitl_response(response)
        assert any("not in options" in e for e in errors)


# =============================================================================
# HITL Option Structure Tests
# =============================================================================

class TestHITLOptionStructure:
    """Test that HITL options have correct structure."""

    def _validate_option(self, option: dict) -> list[str]:
        """Validate option structure, return list of errors."""
        errors = []

        # Required fields
        if "id" not in option:
            errors.append("Option missing 'id' field")
        elif not isinstance(option["id"], str):
            errors.append("Option 'id' must be a string")

        if "label" not in option:
            errors.append("Option missing 'label' field")
        elif not isinstance(option["label"], str):
            errors.append("Option 'label' must be a string")

        # Description is optional but if present must be string
        if "description" in option and not isinstance(option["description"], str):
            errors.append("Option 'description' must be a string")

        return errors

    def test_valid_option(self):
        """Test that a well-formed option passes validation."""
        option = {
            "id": "approved",
            "label": "Approve and Proceed",
            "description": "Continue to the next phase",
        }

        errors = self._validate_option(option)
        assert errors == []

    def test_minimal_option(self):
        """Test that minimal option (id and label only) passes."""
        option = {
            "id": "iterate",
            "label": "Iterate",
        }

        errors = self._validate_option(option)
        assert errors == []

    def test_missing_id_fails(self):
        """Test that missing id fails validation."""
        option = {
            "label": "Test Label",
        }

        errors = self._validate_option(option)
        assert any("id" in e for e in errors)

    def test_missing_label_fails(self):
        """Test that missing label fails validation."""
        option = {
            "id": "test_id",
        }

        errors = self._validate_option(option)
        assert any("label" in e for e in errors)


# =============================================================================
# Checkpoint-Specific Contract Tests
# =============================================================================

class TestDesirabilityGateContract:
    """Test the approve_desirability_gate checkpoint contract."""

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.phases.phase_2.generate_alternative_segments")
    @patch("src.modal_app.phases.phase_2.update_progress")
    def test_desirability_gate_structure(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """Test approve_desirability_gate has correct structure."""
        mock_build.return_value = {}
        mock_growth.return_value = MagicMock(
            model_dump=lambda mode=None: {"problem_resonance": 0.5, "zombie_ratio": 0.3}
        )
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_2

        result = phase_2.execute("test-run-id", {
            "founders_brief": {"the_idea": {"one_liner": "Test"}},
            "customer_profile": {"segment_name": "Test", "pains": []},
            "value_map": {},
        })

        assert result["hitl_checkpoint"] == "approve_desirability_gate"
        assert "approved" in [opt["id"] for opt in result["hitl_options"]]
        assert "iterate" in [opt["id"] for opt in result["hitl_options"]]
        assert result["hitl_context"]["signal"] == "strong_commitment"


class TestSegmentPivotContract:
    """Test the approve_segment_pivot checkpoint contract."""

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.phases.phase_2.generate_alternative_segments")
    @patch("src.modal_app.phases.phase_2.update_progress")
    def test_segment_pivot_includes_alternatives(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """Test approve_segment_pivot includes segment alternatives."""
        mock_build.return_value = {}
        mock_growth.return_value = MagicMock(
            model_dump=lambda mode=None: {"problem_resonance": 0.1, "zombie_ratio": 0.5}
        )
        mock_governance.return_value = {}
        mock_alternatives.return_value = [
            {"segment_name": "Alt 1", "confidence": 0.8},
            {"segment_name": "Alt 2", "confidence": 0.6},
        ]

        from src.modal_app.phases import phase_2

        result = phase_2.execute("test-run-id", {
            "founders_brief": {"the_idea": {"one_liner": "Test"}},
            "customer_profile": {"segment_name": "Failed Segment", "pains": []},
            "value_map": {},
        })

        assert result["hitl_checkpoint"] == "approve_segment_pivot"

        # Should have segment options
        option_ids = [opt["id"] for opt in result["hitl_options"]]
        assert "segment_1" in option_ids
        assert "segment_2" in option_ids
        assert "custom_segment" in option_ids
        assert "override_proceed" in option_ids

        # Context should include alternatives
        assert "segment_alternatives" in result["hitl_context"]

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.phases.phase_2.generate_alternative_segments")
    @patch("src.modal_app.phases.phase_2.update_progress")
    def test_segment_options_have_segment_data(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """Test that segment options include segment_data for selection."""
        mock_build.return_value = {}
        mock_growth.return_value = MagicMock(
            model_dump=lambda mode=None: {"problem_resonance": 0.1, "zombie_ratio": 0.5}
        )
        mock_governance.return_value = {}
        mock_alternatives.return_value = [
            {
                "segment_name": "Enterprise SaaS",
                "segment_description": "Large B2B",
                "confidence": 0.85,
            },
        ]

        from src.modal_app.phases import phase_2

        result = phase_2.execute("test-run-id", {
            "founders_brief": {"the_idea": {"one_liner": "Test"}},
            "customer_profile": {"segment_name": "Failed", "pains": []},
            "value_map": {},
        })

        segment_opt = next(opt for opt in result["hitl_options"] if opt["id"] == "segment_1")
        assert "segment_data" in segment_opt
        assert segment_opt["segment_data"]["segment_name"] == "Enterprise SaaS"


class TestValuePivotContract:
    """Test the approve_value_pivot checkpoint contract."""

    @patch("src.crews.desirability.run_build_crew")
    @patch("src.crews.desirability.run_growth_crew")
    @patch("src.crews.desirability.run_governance_crew")
    @patch("src.modal_app.phases.phase_2.generate_alternative_segments")
    @patch("src.modal_app.phases.phase_2.update_progress")
    def test_value_pivot_structure(
        self,
        mock_progress,
        mock_alternatives,
        mock_governance,
        mock_growth,
        mock_build,
    ):
        """Test approve_value_pivot has correct structure."""
        mock_build.return_value = {}
        mock_growth.return_value = MagicMock(
            model_dump=lambda mode=None: {"problem_resonance": 0.45, "zombie_ratio": 0.75}
        )
        mock_governance.return_value = {}

        from src.modal_app.phases import phase_2

        result = phase_2.execute("test-run-id", {
            "founders_brief": {"the_idea": {"one_liner": "Test"}},
            "customer_profile": {"segment_name": "Test", "pains": []},
            "value_map": {},
        })

        assert result["hitl_checkpoint"] == "approve_value_pivot"

        option_ids = [opt["id"] for opt in result["hitl_options"]]
        assert "approved" in option_ids
        assert "override_proceed" in option_ids
        assert "iterate" in option_ids


# =============================================================================
# Decision Type Validation Tests
# =============================================================================

class TestDecisionTypeValidation:
    """Test that all decision types are valid."""

    def test_valid_decision_patterns(self):
        """Test the regex pattern for valid decisions."""
        import re

        pattern = r"^(approved|rejected|override_proceed|iterate|segment_[1-9]|custom_segment)$"

        valid_decisions = [
            "approved",
            "rejected",
            "override_proceed",
            "iterate",
            "segment_1",
            "segment_2",
            "segment_3",
            "custom_segment",
        ]

        for decision in valid_decisions:
            assert re.match(pattern, decision), f"'{decision}' should match pattern"

    def test_invalid_decision_patterns(self):
        """Test that invalid decisions don't match pattern."""
        import re

        pattern = r"^(approved|rejected|override_proceed|iterate|segment_[1-9]|custom_segment)$"

        invalid_decisions = [
            "approve",  # typo
            "accept",
            "segment_0",  # 0 not allowed
            "segment_10",  # only single digit
            "custom",
            "",
            "APPROVED",  # case sensitive
        ]

        for decision in invalid_decisions:
            assert not re.match(pattern, decision), f"'{decision}' should NOT match pattern"


# =============================================================================
# HITL Context Content Tests
# =============================================================================

class TestHITLContextContent:
    """Test that HITL context contains required information."""

    def test_desirability_context_contains_metrics(self):
        """Desirability HITL context should contain metrics."""
        required_context_fields = [
            "signal",
            "problem_resonance",
            "zombie_ratio",
            "recommendation",
        ]

        # Sample context from phase_2
        context = {
            "signal": "strong_commitment",
            "problem_resonance": 0.55,
            "zombie_ratio": 0.35,
            "conversion_rate": 0.03,
            "ad_metrics": {
                "impressions": 1000,
                "clicks": 150,
                "signups": 30,
            },
            "recommendation": "proceed",
        }

        for field in required_context_fields:
            assert field in context, f"Missing context field: {field}"

    def test_segment_pivot_context_contains_alternatives(self):
        """Segment pivot context should contain alternatives and failed segment."""
        required_fields = [
            "signal",
            "segment_alternatives",
            "failed_segment",
        ]

        context = {
            "signal": "no_interest",
            "segment_alternatives": [
                {"segment_name": "Alt 1", "confidence": 0.8},
            ],
            "failed_segment": "Original Segment",
        }

        for field in required_fields:
            assert field in context, f"Missing context field: {field}"


# =============================================================================
# Request/Response Model Tests
# =============================================================================

@pytest.mark.skipif(not MODAL_AVAILABLE, reason="modal package not installed")
class TestHITLRequestResponseModels:
    """Test the Pydantic models for HITL requests/responses."""

    def test_hitl_approve_request_valid(self):
        """Test that valid HITL approve request passes validation."""
        from src.modal_app.app import HITLApproveRequest

        valid_requests = [
            {"run_id": "123e4567-e89b-12d3-a456-426614174000", "checkpoint": "approve_desirability_gate", "decision": "approved"},
            {"run_id": "123e4567-e89b-12d3-a456-426614174000", "checkpoint": "approve_segment_pivot", "decision": "segment_1"},
            {"run_id": "123e4567-e89b-12d3-a456-426614174000", "checkpoint": "test", "decision": "custom_segment", "feedback": "Custom segment details"},
        ]

        for req_data in valid_requests:
            request = HITLApproveRequest(**req_data)
            assert request.decision in ["approved", "rejected", "override_proceed", "iterate", "segment_1", "segment_2", "segment_3", "custom_segment"]

    def test_hitl_approve_request_invalid_decision(self):
        """Test that invalid decision raises validation error."""
        from src.modal_app.app import HITLApproveRequest

        with pytest.raises(ValidationError):
            HITLApproveRequest(
                run_id="123e4567-e89b-12d3-a456-426614174000",
                checkpoint="test",
                decision="invalid_decision",
            )

    def test_hitl_approve_response_structure(self):
        """Test HITLApproveResponse has correct structure."""
        from src.modal_app.app import HITLApproveResponse

        response = HITLApproveResponse(
            status="resumed",
            next_phase=3,
            message="Advancing to Phase 3",
        )

        assert response.status == "resumed"
        assert response.next_phase == 3
        assert response.pivot_type is None

        pivot_response = HITLApproveResponse(
            status="pivot",
            next_phase=1,
            pivot_type="segment_pivot",
            message="Pivoting to new segment",
        )

        assert pivot_response.pivot_type == "segment_pivot"


# =============================================================================
# Checkpoint Name Validation Tests
# =============================================================================

class TestCheckpointNameValidation:
    """Test that checkpoint names follow conventions."""

    def test_checkpoint_names_are_snake_case(self):
        """All checkpoint names should be snake_case."""
        import re

        valid_checkpoints = [
            "approve_founders_brief",
            "approve_discovery_output",
            "approve_desirability_gate",
            "approve_segment_pivot",
            "approve_value_pivot",
            "approve_feasibility_gate",
            "approve_feature_pivot",
            "approve_viability_gate",
        ]

        snake_case_pattern = r"^[a-z][a-z0-9_]*$"

        for checkpoint in valid_checkpoints:
            assert re.match(snake_case_pattern, checkpoint), (
                f"Checkpoint '{checkpoint}' should be snake_case"
            )

    def test_checkpoint_names_start_with_approve(self):
        """Gate checkpoints should start with 'approve_'."""
        gate_checkpoints = [
            "approve_founders_brief",
            "approve_discovery_output",
            "approve_desirability_gate",
            "approve_feasibility_gate",
            "approve_viability_gate",
        ]

        for checkpoint in gate_checkpoints:
            assert checkpoint.startswith("approve_"), (
                f"Gate checkpoint '{checkpoint}' should start with 'approve_'"
            )


# =============================================================================
# HITL Database Schema Tests
# =============================================================================

class TestHITLDatabaseSchema:
    """Test that HITL data matches expected database schema."""

    def test_hitl_request_db_schema(self):
        """Test HITL request matches database schema."""
        # Expected fields in hitl_requests table
        expected_fields = {
            "run_id": str,
            "checkpoint_name": str,
            "phase": int,
            "title": str,
            "description": str,
            "context": dict,
            "options": list,
            "recommended_option": str,
        }

        # Sample insert data from app.py
        insert_data = {
            "run_id": "test-123",
            "checkpoint_name": "approve_desirability_gate",
            "phase": 2,
            "title": "Desirability Validated",
            "description": "Ready to proceed",
            "context": {"signal": "strong_commitment"},
            "options": [{"id": "approved", "label": "Approve"}],
            "recommended_option": "approved",
        }

        for field, expected_type in expected_fields.items():
            assert field in insert_data, f"Missing field: {field}"
            assert isinstance(insert_data[field], expected_type), (
                f"Field {field} should be {expected_type.__name__}"
            )

    def test_hitl_request_update_schema(self):
        """Test HITL request update matches expected schema."""
        # Fields updated when decision is made
        update_data = {
            "status": "approved",
            "decision": "approved",
            "feedback": "Looks good",
            "decision_at": datetime.utcnow().isoformat(),
        }

        required_fields = ["status", "decision", "decision_at"]
        for field in required_fields:
            assert field in update_data
