"""
End-to-End Pipeline Tests.

Tests the complete flow from flow execution through webhook delivery.
Uses mocked crews to avoid LLM costs while testing the full pipeline.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from startupai.flows.state_schemas import (
    StartupValidationState,
    Phase,
    DesirabilitySignal,
    FeasibilitySignal,
    ViabilitySignal,
    DesirabilityEvidence,
    FeasibilityEvidence,
    ViabilityEvidence,
    PivotType,
    QAReport,
)
from startupai.flows.internal_validation_flow import InternalValidationFlow
from startupai.webhooks.contracts import (
    FounderValidationPayload,
    validate_founder_validation_payload,
)


# ===========================================================================
# FIXTURES
# ===========================================================================

@pytest.fixture
def webhook_capture():
    """Captures webhook calls for verification."""
    captured = {"calls": [], "payloads": []}

    def capture_post(url, **kwargs):
        captured["calls"].append({"url": url, "kwargs": kwargs})
        if "json" in kwargs:
            captured["payloads"].append(kwargs["json"])
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "report_id": "rpt-test-123",
            "evidence_created": 3,
            "gate_scores_created": 3,
        }
        return response

    return captured, capture_post


@pytest.fixture
def mock_httpx_with_capture(webhook_capture):
    """Mock httpx.Client that captures webhook calls."""
    captured, capture_post = webhook_capture

    with patch("startupai.flows.internal_validation_flow.httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.post = capture_post
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client
        yield captured


@pytest.fixture
def e2e_validated_state() -> StartupValidationState:
    """Create a state that simulates a completed validation flow."""
    state = StartupValidationState(
        project_id="e2e-test-project",
        user_id="e2e-test-user",
        session_id="e2e-test-session",
        kickoff_id="e2e-test-kickoff",
        entrepreneur_input="E2E test: AI-powered logistics platform",
        phase=Phase.VALIDATED,
        business_idea="AI-powered logistics optimization",
        target_segments=["Supply Chain Managers"],
        current_segment="Supply Chain Managers",
        desirability_signal=DesirabilitySignal.STRONG_COMMITMENT,
        feasibility_signal=FeasibilitySignal.GREEN,
        viability_signal=ViabilitySignal.PROFITABLE,
        final_recommendation="PROCEED",
        evidence_summary="Strong validation across all dimensions",
        pivot_recommendation=PivotType.NONE,
        next_steps=["Build MVP", "Secure first customer"],
    )

    # Populate evidence
    state.desirability_evidence = DesirabilityEvidence(
        problem_resonance=0.82,
        conversion_rate=0.15,
        commitment_depth="skin_in_game",
        zombie_ratio=0.12,
        traffic_quality="High",
        key_learnings=["Strong pain point resonance"],
        tested_segments=["Supply Chain Managers"],
        impressions=5000,
        clicks=750,
        signups=30,
        spend_usd=250.0,
    )

    state.feasibility_evidence = FeasibilityEvidence(
        core_features_feasible={"route_optimization": "fully_feasible"},
        technical_risks=["Integration complexity"],
        skill_requirements=["ML Engineer"],
        estimated_effort="4 months",
        downgrade_required=False,
        monthly_cost_estimate_usd=1500.0,
    )

    state.viability_evidence = ViabilityEvidence(
        cac=200.0,
        ltv=2400.0,
        ltv_cac_ratio=12.0,
        gross_margin=0.68,
        payback_months=3.0,
        break_even_customers=40,
        tam_usd=8000000000.0,
        market_share_target=0.005,
        viability_assessment="Excellent unit economics",
    )

    state.qa_reports = [
        QAReport(
            status="passed",
            framework_compliance=True,
            logical_consistency=True,
            completeness=True,
            confidence_score=0.95,
        )
    ]

    return state


# ===========================================================================
# E2E PIPELINE TESTS
# ===========================================================================

class TestE2EPipeline:
    """End-to-end pipeline tests."""

    def test_flow_delivers_webhook_on_completion(
        self, e2e_validated_state, mock_httpx_with_capture
    ):
        """Verify completed flow delivers webhook to product app."""
        # Create flow with validated state
        flow = object.__new__(InternalValidationFlow)
        flow._state = e2e_validated_state

        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://app.startupai.site/api/crewai/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-bearer-token",
        }):
            # Generate deliverables and persist
            deliverables = flow._generate_final_deliverables()
            result = flow._persist_to_supabase(deliverables)

            # Verify webhook was called
            assert result is True
            assert len(mock_httpx_with_capture["calls"]) == 1
            assert len(mock_httpx_with_capture["payloads"]) == 1

    def test_webhook_payload_validates_against_contract(
        self, e2e_validated_state, mock_httpx_with_capture
    ):
        """Verify webhook payload matches contract schema."""
        flow = object.__new__(InternalValidationFlow)
        flow._state = e2e_validated_state

        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://app.startupai.site/api/crewai/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = flow._generate_final_deliverables()
            flow._persist_to_supabase(deliverables)

            # Get the payload that was sent
            payload = mock_httpx_with_capture["payloads"][0]

            # Validate against contract schema
            # This should not raise ValidationError
            validated = validate_founder_validation_payload(payload)

            assert validated.flow_type == "founder_validation"
            assert validated.project_id == "e2e-test-project"
            assert validated.user_id == "e2e-test-user"

    def test_all_evidence_phases_included(
        self, e2e_validated_state, mock_httpx_with_capture
    ):
        """Verify all three evidence phases are in payload."""
        flow = object.__new__(InternalValidationFlow)
        flow._state = e2e_validated_state

        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = flow._generate_final_deliverables()
            flow._persist_to_supabase(deliverables)

            payload = mock_httpx_with_capture["payloads"][0]

            # All three phases present
            assert payload["evidence"]["desirability"] is not None
            assert payload["evidence"]["feasibility"] is not None
            assert payload["evidence"]["viability"] is not None

    def test_gate_scores_fields_present(
        self, e2e_validated_state, mock_httpx_with_capture
    ):
        """Verify fields needed for gate_scores table are present."""
        flow = object.__new__(InternalValidationFlow)
        flow._state = e2e_validated_state

        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = flow._generate_final_deliverables()
            flow._persist_to_supabase(deliverables)

            payload = mock_httpx_with_capture["payloads"][0]

            # Desirability gate_scores fields
            desirability = payload["evidence"]["desirability"]
            assert "problem_resonance" in desirability
            assert "zombie_ratio" in desirability
            assert "commitment_depth" in desirability
            assert desirability["problem_resonance"] == 0.82
            assert desirability["zombie_ratio"] == 0.12

            # Viability gate_scores fields
            viability = payload["evidence"]["viability"]
            assert "cac" in viability
            assert "ltv" in viability
            assert "ltv_cac_ratio" in viability
            assert viability["cac"] == 200.0
            assert viability["ltv"] == 2400.0
            assert viability["ltv_cac_ratio"] == 12.0

    def test_validation_report_structure(
        self, e2e_validated_state, mock_httpx_with_capture
    ):
        """Verify validation report has expected structure."""
        flow = object.__new__(InternalValidationFlow)
        flow._state = e2e_validated_state

        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = flow._generate_final_deliverables()
            flow._persist_to_supabase(deliverables)

            payload = mock_httpx_with_capture["payloads"][0]
            report = payload["validation_report"]

            assert "id" in report
            assert "business_idea" in report
            assert "validation_outcome" in report
            assert "evidence_summary" in report
            assert "next_steps" in report
            assert report["validation_outcome"] == "PROCEED"

    def test_qa_report_included_when_present(
        self, e2e_validated_state, mock_httpx_with_capture
    ):
        """Verify QA report is included in payload."""
        flow = object.__new__(InternalValidationFlow)
        flow._state = e2e_validated_state

        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = flow._generate_final_deliverables()
            flow._persist_to_supabase(deliverables)

            payload = mock_httpx_with_capture["payloads"][0]

            assert payload["qa_report"] is not None
            assert payload["qa_report"]["status"] == "passed"
            assert payload["qa_report"]["confidence_score"] == 0.95


class TestE2EPayloadSerialization:
    """Tests for payload serialization."""

    def test_payload_is_json_serializable(self, e2e_validated_state):
        """Verify payload can be JSON serialized."""
        flow = object.__new__(InternalValidationFlow)
        flow._state = e2e_validated_state

        deliverables = flow._generate_final_deliverables()

        # Build payload as the flow does
        payload = {
            "flow_type": "founder_validation",
            "project_id": e2e_validated_state.project_id,
            "user_id": e2e_validated_state.user_id,
            "validation_report": deliverables.get("validation_report", {}),
            "evidence": deliverables.get("evidence", {}),
            "completed_at": datetime.now().isoformat(),
        }

        # Should not raise
        json_str = json.dumps(payload)
        assert len(json_str) > 0

        # Should round-trip
        parsed = json.loads(json_str)
        assert parsed["flow_type"] == "founder_validation"

    def test_enum_values_serialized_correctly(self, e2e_validated_state):
        """Verify enum values are serialized as strings."""
        flow = object.__new__(InternalValidationFlow)
        flow._state = e2e_validated_state

        deliverables = flow._generate_final_deliverables()

        # pivot_recommendation should be serialized as string, not enum
        pivot_rec = deliverables["validation_report"]["pivot_recommendation"]
        assert pivot_rec is None or isinstance(pivot_rec, str)


class TestE2EEdgeCases:
    """Edge case tests for E2E pipeline."""

    def test_handles_missing_evidence_gracefully(self, mock_httpx_with_capture):
        """Verify flow handles missing evidence phases."""
        state = StartupValidationState(
            project_id="edge-case-project",
            user_id="edge-case-user",
            entrepreneur_input="Test idea",
            phase=Phase.DESIRABILITY,  # Early phase, no viability yet
        )
        state.final_recommendation = "IN_PROGRESS"
        state.next_steps = []

        flow = object.__new__(InternalValidationFlow)
        flow._state = state

        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = flow._generate_final_deliverables()
            result = flow._persist_to_supabase(deliverables)

            assert result is True
            payload = mock_httpx_with_capture["payloads"][0]

            # Evidence should have None for missing phases
            assert payload["evidence"]["desirability"] is None
            assert payload["evidence"]["feasibility"] is None
            assert payload["evidence"]["viability"] is None

    def test_handles_empty_customer_profiles(self, mock_httpx_with_capture):
        """Verify flow handles empty customer profiles."""
        state = StartupValidationState(
            project_id="empty-profiles-project",
            user_id="empty-profiles-user",
            entrepreneur_input="Test idea",
            phase=Phase.VALIDATED,
        )
        state.customer_profiles = {}
        state.value_maps = {}
        state.final_recommendation = "PROCEED"
        state.next_steps = ["Build MVP"]

        flow = object.__new__(InternalValidationFlow)
        flow._state = state

        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = flow._generate_final_deliverables()
            result = flow._persist_to_supabase(deliverables)

            assert result is True
            payload = mock_httpx_with_capture["payloads"][0]
            assert payload["value_proposition_canvas"] == {}
