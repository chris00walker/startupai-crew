"""
Tests for webhook delivery to product app.

These tests verify that:
1. The webhook is called with correct payload structure
2. Authentication headers are included
3. Error handling works correctly
4. Payload matches the contract expected by product app
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import httpx

from startupai.flows.state_schemas import (
    StartupValidationState,
    Phase,
    DesirabilitySignal,
    FeasibilitySignal,
    ViabilitySignal,
    DesirabilityEvidence,
    FeasibilityEvidence,
    ViabilityEvidence,
    CustomerProfile,
    QAReport,
    PivotType,
)
from startupai.flows._founder_validation_flow import FounderValidationFlow


# ===========================================================================
# FIXTURES
# ===========================================================================

@pytest.fixture
def complete_validated_state() -> StartupValidationState:
    """Create a fully validated state with all evidence populated."""
    state = StartupValidationState(
        project_id="test-project-123",
        user_id="test-user-456",
        session_id="test-session-789",
        kickoff_id="test-kickoff-abc",
        entrepreneur_input="AI-powered supply chain optimizer for logistics companies",
        phase=Phase.VALIDATED,
        business_idea="AI-powered supply chain optimizer",
        target_segments=["Logistics Managers", "Procurement Officers"],
        current_segment="Logistics Managers",
        desirability_signal=DesirabilitySignal.STRONG_COMMITMENT,
        feasibility_signal=FeasibilitySignal.GREEN,
        viability_signal=ViabilitySignal.PROFITABLE,
    )

    # Add desirability evidence
    state.desirability_evidence = DesirabilityEvidence(
        problem_resonance=0.75,
        conversion_rate=0.12,
        commitment_depth="skin_in_game",
        zombie_ratio=0.15,
        traffic_quality="High",
        key_learnings=["Users want real-time tracking", "Price sensitivity is low"],
        tested_segments=["Logistics Managers"],
        impressions=10000,
        clicks=1200,
        signups=50,
        spend_usd=500.0,
    )

    # Add feasibility evidence
    state.feasibility_evidence = FeasibilityEvidence(
        core_features_feasible={
            "real_time_tracking": "fully_feasible",
            "ai_predictions": "feasible_with_constraints",
        },
        technical_risks=["ML model accuracy depends on data quality"],
        skill_requirements=["ML Engineer", "Backend Developer"],
        estimated_effort="3-4 months",
        downgrade_required=False,
        monthly_cost_estimate_usd=2500.0,
    )

    # Add viability evidence
    state.viability_evidence = ViabilityEvidence(
        cac=150.0,
        ltv=1800.0,
        ltv_cac_ratio=12.0,
        gross_margin=0.72,
        payback_months=2.5,
        break_even_customers=50,
        tam_usd=5000000000.0,
        market_share_target=0.01,
        viability_assessment="Strong unit economics with healthy LTV/CAC ratio",
    )

    # Add customer profile (simplified for testing)
    state.customer_profiles = {
        "Logistics Managers": CustomerProfile(
            segment_name="Logistics Managers",
            jobs=[{
                "functional": "Optimize delivery routes",
                "emotional": "Feel confident about logistics",
                "social": "Be seen as efficient",
                "importance": 9
            }],
            pains=["Manual tracking is error-prone", "Lack of real-time visibility"],
            gains=["Reduced delivery times", "Lower operational costs"],
        )
    }

    # Add value map (using dict for simplicity)
    state.value_maps = {
        "Logistics Managers": {
            "products_services": ["AI Route Optimizer", "Real-time Dashboard"],
            "pain_relievers": {"Manual tracking is error-prone": "Automated tracking with ML"},
            "gain_creators": {"Reduced delivery times": "AI-optimized routes save 20% time"},
            "differentiators": ["Real-time ML predictions", "Integration with existing TMS"],
        }
    }

    # Add QA report
    state.qa_reports = [
        QAReport(
            status="passed",
            framework_compliance=True,
            logical_consistency=True,
            completeness=True,
            specific_issues=[],
            required_changes=[],
            confidence_score=0.92,
        )
    ]

    # Set fields used by _generate_final_deliverables
    state.final_recommendation = "PROCEED"
    state.evidence_summary = "Strong desirability signals with 75% problem resonance..."
    state.pivot_recommendation = PivotType.NONE
    state.next_steps = ["Build MVP", "Onboard first 10 customers", "Raise seed round"]

    return state


@pytest.fixture
def mock_flow(complete_validated_state):
    """Create a mock flow instance with the validated state."""
    # Create flow without calling __init__ to avoid CrewAI dependencies
    flow = object.__new__(FounderValidationFlow)
    flow._state = complete_validated_state
    return flow


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.Client for testing HTTP calls."""
    with patch("startupai.flows._founder_validation_flow.httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"report_id": "rpt-123", "evidence_created": 3}
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client
        yield mock_client


# ===========================================================================
# WEBHOOK DELIVERY TESTS
# ===========================================================================

class TestWebhookDelivery:
    """Tests for webhook HTTP delivery."""

    def test_webhook_called_with_correct_url(self, mock_flow, mock_httpx_client):
        """Verify webhook is called with the configured URL."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            mock_flow._persist_to_supabase(deliverables)

            mock_httpx_client.post.assert_called_once()
            call_args = mock_httpx_client.post.call_args
            assert call_args[0][0] == "https://test.example.com/webhook"

    def test_webhook_includes_bearer_auth(self, mock_flow, mock_httpx_client):
        """Verify webhook includes Bearer authorization header."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "secret-token-123",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            mock_flow._persist_to_supabase(deliverables)

            call_args = mock_httpx_client.post.call_args
            headers = call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer secret-token-123"
            assert headers["Content-Type"] == "application/json"

    def test_webhook_skipped_without_url(self, mock_flow, mock_httpx_client):
        """Verify webhook is skipped if URL not configured."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }, clear=True):
            # Remove URL from environment
            import os
            os.environ.pop("STARTUPAI_WEBHOOK_URL", None)

            deliverables = mock_flow._generate_final_deliverables()
            result = mock_flow._persist_to_supabase(deliverables)

            assert result is False
            mock_httpx_client.post.assert_not_called()

    def test_webhook_skipped_without_project_id(self, mock_flow, mock_httpx_client):
        """Verify webhook is skipped if project_id missing."""
        mock_flow._state.project_id = None

        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            result = mock_flow._persist_to_supabase(deliverables)

            assert result is False
            mock_httpx_client.post.assert_not_called()


class TestWebhookPayloadStructure:
    """Tests for webhook payload structure matching contract."""

    def test_payload_contains_flow_type(self, mock_flow, mock_httpx_client):
        """Verify payload includes flow_type for routing."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            mock_flow._persist_to_supabase(deliverables)

            call_args = mock_httpx_client.post.call_args
            payload = call_args[1]["json"]

            assert payload["flow_type"] == "founder_validation"

    def test_payload_contains_project_metadata(self, mock_flow, mock_httpx_client):
        """Verify payload includes project identifiers."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            mock_flow._persist_to_supabase(deliverables)

            call_args = mock_httpx_client.post.call_args
            payload = call_args[1]["json"]

            assert payload["project_id"] == "test-project-123"
            assert payload["user_id"] == "test-user-456"
            assert payload["kickoff_id"] == "test-kickoff-abc"
            assert payload["session_id"] == "test-session-789"

    def test_payload_contains_validation_report(self, mock_flow, mock_httpx_client):
        """Verify payload includes validation report."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            mock_flow._persist_to_supabase(deliverables)

            call_args = mock_httpx_client.post.call_args
            payload = call_args[1]["json"]

            assert "validation_report" in payload
            report = payload["validation_report"]
            assert "validation_outcome" in report
            assert "next_steps" in report

    def test_payload_contains_evidence_structure(self, mock_flow, mock_httpx_client):
        """Verify payload includes all three evidence phases."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            mock_flow._persist_to_supabase(deliverables)

            call_args = mock_httpx_client.post.call_args
            payload = call_args[1]["json"]

            assert "evidence" in payload
            evidence = payload["evidence"]
            assert "desirability" in evidence
            assert "feasibility" in evidence
            assert "viability" in evidence

    def test_desirability_evidence_fields(self, mock_flow, mock_httpx_client):
        """Verify desirability evidence contains gate_scores fields."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            mock_flow._persist_to_supabase(deliverables)

            call_args = mock_httpx_client.post.call_args
            payload = call_args[1]["json"]

            desirability = payload["evidence"]["desirability"]
            # These fields map to gate_scores table
            assert "problem_resonance" in desirability
            assert "zombie_ratio" in desirability
            assert "commitment_depth" in desirability
            assert desirability["problem_resonance"] == 0.75
            assert desirability["zombie_ratio"] == 0.15

    def test_viability_evidence_fields(self, mock_flow, mock_httpx_client):
        """Verify viability evidence contains unit economics fields."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            mock_flow._persist_to_supabase(deliverables)

            call_args = mock_httpx_client.post.call_args
            payload = call_args[1]["json"]

            viability = payload["evidence"]["viability"]
            # These fields map to gate_scores table
            assert "cac" in viability
            assert "ltv" in viability
            assert "ltv_cac_ratio" in viability
            assert viability["cac"] == 150.0
            assert viability["ltv"] == 1800.0
            assert viability["ltv_cac_ratio"] == 12.0

    def test_payload_contains_completed_at_timestamp(self, mock_flow, mock_httpx_client):
        """Verify payload includes completion timestamp."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            mock_flow._persist_to_supabase(deliverables)

            call_args = mock_httpx_client.post.call_args
            payload = call_args[1]["json"]

            assert "completed_at" in payload
            # Should be ISO format timestamp
            datetime.fromisoformat(payload["completed_at"])


class TestWebhookErrorHandling:
    """Tests for webhook error handling."""

    def test_handles_timeout_gracefully(self, mock_flow):
        """Verify timeout errors are handled gracefully."""
        with patch("startupai.flows._founder_validation_flow.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post.side_effect = httpx.TimeoutException("Connection timed out")
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            with patch.dict("os.environ", {
                "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
                "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
            }):
                deliverables = mock_flow._generate_final_deliverables()
                result = mock_flow._persist_to_supabase(deliverables)

                assert result is False

    def test_handles_connection_error(self, mock_flow):
        """Verify connection errors are handled gracefully."""
        with patch("startupai.flows._founder_validation_flow.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post.side_effect = httpx.RequestError("Connection failed")
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            with patch.dict("os.environ", {
                "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
                "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
            }):
                deliverables = mock_flow._generate_final_deliverables()
                result = mock_flow._persist_to_supabase(deliverables)

                assert result is False

    def test_handles_non_200_response(self, mock_flow):
        """Verify non-200 responses are handled correctly."""
        with patch("startupai.flows._founder_validation_flow.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_client.post.return_value = mock_response
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            with patch.dict("os.environ", {
                "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
                "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
            }):
                deliverables = mock_flow._generate_final_deliverables()
                result = mock_flow._persist_to_supabase(deliverables)

                assert result is False

    def test_returns_true_on_success(self, mock_flow, mock_httpx_client):
        """Verify True is returned on successful delivery."""
        with patch.dict("os.environ", {
            "STARTUPAI_WEBHOOK_URL": "https://test.example.com/webhook",
            "STARTUPAI_WEBHOOK_BEARER_TOKEN": "test-token",
        }):
            deliverables = mock_flow._generate_final_deliverables()
            result = mock_flow._persist_to_supabase(deliverables)

            assert result is True
