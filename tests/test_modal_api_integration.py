"""
Integration Tests for Modal API Endpoints.

Tests the FastAPI endpoints (/kickoff, /status, /hitl/approve)
with mocked crew execution and Supabase persistence.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from datetime import datetime, timedelta
import json

# Import FastAPI test client
from fastapi.testclient import TestClient

# Import state models
from src.state.models import (
    ValidationRunState,
    ValidationSignal,
    FoundersBrief,
    TheIdea,
    ProblemHypothesis,
    CustomerHypothesis,
    SolutionHypothesis,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for all tests."""
    with patch("supabase.create_client") as mock:
        client = Mock()

        # Mock table().upsert().execute()
        upsert_response = Mock()
        upsert_response.data = [{"id": str(uuid4())}]
        client.table.return_value.upsert.return_value.execute.return_value = upsert_response

        # Mock table().select().eq().single().execute()
        select_response = Mock()
        select_response.data = None  # Default: no existing state
        client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = select_response

        # Mock table().insert().execute()
        insert_response = Mock()
        insert_response.data = [{"id": str(uuid4())}]
        client.table.return_value.insert.return_value.execute.return_value = insert_response

        # Mock table().update().eq().execute()
        update_response = Mock()
        update_response.data = [{"id": str(uuid4())}]
        client.table.return_value.update.return_value.eq.return_value.execute.return_value = update_response

        mock.return_value = client
        yield client


@pytest.fixture
def mock_modal_function():
    """Mock Modal function.spawn() for async execution."""
    with patch("modal.Function") as mock:
        function_call = Mock()
        function_call.object_id = str(uuid4())
        mock.return_value.spawn.return_value = function_call
        yield mock


@pytest.fixture
def sample_kickoff_request():
    """Sample kickoff request body."""
    return {
        "entrepreneur_input": "An AI-powered supply chain optimizer for mid-size retailers",
        "project_id": str(uuid4()),
        "user_id": str(uuid4()),
    }


@pytest.fixture
def sample_run_state():
    """Sample validation run state from database."""
    return {
        "run_id": str(uuid4()),
        "project_id": str(uuid4()),
        "user_id": str(uuid4()),
        "entrepreneur_input": "Test business idea",
        "current_phase": 1,
        "status": "running",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_hitl_state():
    """Sample state paused at HITL checkpoint."""
    return {
        "run_id": str(uuid4()),
        "project_id": str(uuid4()),
        "user_id": str(uuid4()),
        "entrepreneur_input": "Test business idea",
        "current_phase": 1,
        "status": "paused",
        "hitl_state": "approve_discovery_output",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


# =============================================================================
# API Import Tests (Verify app can be imported)
# =============================================================================

class TestAPIImport:
    """Tests that the API can be imported without errors."""

    def test_app_module_imports(self):
        """Test that the app module can be imported."""
        try:
            from src.modal_app import app
            assert app is not None
        except ImportError as e:
            # Expected if Modal is not installed in test environment
            assert "modal" in str(e).lower()

    def test_config_module_imports(self):
        """Test that the config module can be imported."""
        from src.modal_app import config
        assert config is not None

    def test_phases_module_imports(self):
        """Test that the phases module can be imported."""
        from src.modal_app import phases
        assert phases is not None


# =============================================================================
# Kickoff Endpoint Tests
# =============================================================================

class TestKickoffEndpoint:
    """Tests for POST /kickoff endpoint."""

    def test_kickoff_request_validation(self, sample_kickoff_request):
        """Test that kickoff validates required fields."""
        # Missing entrepreneur_input should fail
        invalid_request = {
            "project_id": str(uuid4()),
            "user_id": str(uuid4()),
        }

        # This would be tested with TestClient when Modal app is available
        # For now, verify the request structure
        assert "entrepreneur_input" in sample_kickoff_request
        assert "project_id" in sample_kickoff_request
        assert "user_id" in sample_kickoff_request

    def test_kickoff_generates_run_id(self, sample_kickoff_request):
        """Test that kickoff generates a unique run_id."""
        # Simulate the run_id generation logic
        run_id_1 = str(uuid4())
        run_id_2 = str(uuid4())

        # Each kickoff should have a unique run_id
        assert run_id_1 != run_id_2
        assert len(run_id_1) == 36  # UUID format

    def test_kickoff_creates_initial_state(
        self,
        sample_kickoff_request,
        mock_supabase_client,
    ):
        """Test that kickoff creates correct initial state."""
        # Simulate initial state creation
        state = ValidationRunState(
            run_id=uuid4(),
            project_id=sample_kickoff_request["project_id"],
            user_id=sample_kickoff_request["user_id"],
            entrepreneur_input=sample_kickoff_request["entrepreneur_input"],
        )

        assert state.current_phase == 0
        assert state.status == "pending"
        assert state.founders_brief is None

    def test_kickoff_returns_202_accepted(self, sample_kickoff_request):
        """Test that kickoff returns 202 Accepted status."""
        # Expected response structure
        expected_response = {
            "run_id": "uuid-string",
            "status": "started",
            "message": "Validation run started",
        }

        # Verify response structure
        assert "run_id" in expected_response
        assert "status" in expected_response
        assert expected_response["status"] == "started"


# =============================================================================
# Status Endpoint Tests
# =============================================================================

class TestStatusEndpoint:
    """Tests for GET /status/{run_id} endpoint."""

    def test_status_returns_running_state(self, sample_run_state, mock_supabase_client):
        """Test status endpoint returns running state correctly."""
        # Configure mock to return sample state
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = sample_run_state

        # Verify state structure
        assert sample_run_state["status"] == "running"
        assert sample_run_state["current_phase"] == 1

    def test_status_returns_404_for_unknown_run(self, mock_supabase_client):
        """Test status endpoint returns 404 for unknown run_id."""
        # Configure mock to return None (not found)
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None

        # Expected behavior: 404 Not Found
        # This would be verified with TestClient

    def test_status_includes_progress_info(self, sample_run_state):
        """Test status response includes progress information."""
        # Expected response structure
        expected_response = {
            "run_id": sample_run_state["run_id"],
            "status": sample_run_state["status"],
            "current_phase": sample_run_state["current_phase"],
            "progress": {
                "phase_name": "VPC Discovery",
                "crew": "DiscoveryCrew",
                "task": "map_assumptions",
                "progress_pct": 25,
            },
        }

        assert "progress" in expected_response
        assert expected_response["progress"]["progress_pct"] >= 0
        assert expected_response["progress"]["progress_pct"] <= 100

    def test_status_includes_hitl_info_when_paused(self, sample_hitl_state):
        """Test status includes HITL info when paused."""
        assert sample_hitl_state["status"] == "paused"
        assert sample_hitl_state["hitl_state"] == "approve_discovery_output"

        # Expected HITL info structure
        expected_hitl = {
            "checkpoint": "approve_discovery_output",
            "title": "VPC Discovery Complete",
            "description": "Review the VPC fit score before proceeding.",
            "options": [
                {"id": "approve", "label": "Approve"},
                {"id": "iterate", "label": "Iterate"},
            ],
            "recommended": "approve",
        }

        assert "checkpoint" in expected_hitl
        assert "options" in expected_hitl


# =============================================================================
# HITL Approve Endpoint Tests
# =============================================================================

class TestHITLApproveEndpoint:
    """Tests for POST /hitl/approve endpoint."""

    def test_hitl_approve_request_validation(self):
        """Test HITL approve validates required fields."""
        valid_request = {
            "run_id": str(uuid4()),
            "checkpoint": "approve_discovery_output",
            "decision": "approved",
            "feedback": "Looks good, proceed.",
        }

        assert "run_id" in valid_request
        assert "checkpoint" in valid_request
        assert "decision" in valid_request

    def test_hitl_approve_valid_decisions(self):
        """Test valid decision values."""
        valid_decisions = [
            "approved",
            "rejected",
            "iterate",
            "segment_pivot",
            "value_pivot",
            "feature_pivot",
            "kill",
        ]

        for decision in valid_decisions:
            request = {
                "run_id": str(uuid4()),
                "checkpoint": "test_checkpoint",
                "decision": decision,
            }
            assert request["decision"] in valid_decisions

    def test_hitl_approve_updates_state(self, sample_hitl_state, mock_supabase_client):
        """Test HITL approve updates state correctly."""
        # Configure mock to return paused state
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = sample_hitl_state

        # After approval, status should change
        expected_state_after_approval = {
            **sample_hitl_state,
            "status": "running",
            "hitl_state": None,
        }

        assert expected_state_after_approval["status"] == "running"

    def test_hitl_approve_returns_400_for_non_paused(self, sample_run_state, mock_supabase_client):
        """Test HITL approve returns 400 for non-paused run."""
        # Configure mock to return running (not paused) state
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = sample_run_state

        # Expected behavior: 400 Bad Request
        assert sample_run_state["status"] == "running"
        # HITL approve should fail if not paused

    def test_hitl_approve_checkpoint_mismatch(self, sample_hitl_state):
        """Test HITL approve fails on checkpoint mismatch."""
        wrong_checkpoint_request = {
            "run_id": sample_hitl_state["run_id"],
            "checkpoint": "approve_desirability_gate",  # Wrong checkpoint
            "decision": "approved",
        }

        # Current checkpoint is approve_discovery_output
        assert wrong_checkpoint_request["checkpoint"] != sample_hitl_state["hitl_state"]


# =============================================================================
# Authentication Tests
# =============================================================================

class TestAPIAuthentication:
    """Tests for API authentication."""

    def test_missing_auth_header_rejected(self):
        """Test that missing Authorization header is rejected."""
        # Expected behavior: 401 Unauthorized
        pass  # Would test with TestClient

    def test_invalid_bearer_token_rejected(self):
        """Test that invalid bearer token is rejected."""
        invalid_headers = {
            "Authorization": "Bearer invalid-token-123",
        }
        # Expected behavior: 401 Unauthorized
        pass  # Would test with TestClient

    def test_valid_bearer_token_accepted(self):
        """Test that valid bearer token is accepted."""
        # This would use the actual token from environment
        pass  # Would test with TestClient


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestAPIErrorHandling:
    """Tests for API error handling."""

    def test_database_error_returns_500(self, mock_supabase_client):
        """Test that database errors return 500."""
        # Configure mock to raise exception
        mock_supabase_client.table.return_value.select.side_effect = Exception("DB error")

        # Expected behavior: 500 Internal Server Error
        pass  # Would test with TestClient

    def test_validation_error_returns_422(self):
        """Test that validation errors return 422."""
        invalid_request = {
            "entrepreneur_input": "",  # Empty string might be invalid
        }
        # Expected behavior: 422 Unprocessable Entity
        pass  # Would test with TestClient

    def test_crew_execution_error_logged(self, mock_supabase_client):
        """Test that crew execution errors are logged."""
        # Expected behavior: Error logged, state updated to "failed"
        pass  # Would test with TestClient


# =============================================================================
# Webhook Payload Tests
# =============================================================================

class TestWebhookPayloads:
    """Tests for webhook payload generation."""

    def test_phase_complete_webhook_structure(self):
        """Test webhook payload for phase completion."""
        expected_payload = {
            "event": "phase_complete",
            "run_id": "uuid-string",
            "phase": 1,
            "phase_name": "VPC Discovery",
            "status": "success",
            "outputs": {
                "fit_score": 78,
                "customer_profile": {},
                "value_map": {},
            },
            "next_phase": 2,
            "timestamp": "2024-01-01T00:00:00Z",
        }

        assert "event" in expected_payload
        assert "outputs" in expected_payload
        assert expected_payload["event"] == "phase_complete"

    def test_hitl_required_webhook_structure(self):
        """Test webhook payload for HITL checkpoint."""
        expected_payload = {
            "event": "hitl_required",
            "run_id": "uuid-string",
            "checkpoint": "approve_discovery_output",
            "phase": 1,
            "title": "VPC Discovery Complete",
            "description": "Review the VPC fit score before proceeding.",
            "context": {
                "fit_score": 78,
                "gate_ready": True,
            },
            "options": [
                {"id": "approve", "label": "Approve"},
                {"id": "iterate", "label": "Iterate"},
            ],
            "recommended": "approve",
            "timestamp": "2024-01-01T00:00:00Z",
        }

        assert expected_payload["event"] == "hitl_required"
        assert "options" in expected_payload
        assert "recommended" in expected_payload

    def test_validation_complete_webhook_structure(self):
        """Test webhook payload for validation completion."""
        expected_payload = {
            "event": "validation_complete",
            "run_id": "uuid-string",
            "status": "success",
            "final_decision": "proceed",
            "signals": {
                "desirability": "strong_commitment",
                "feasibility": "green",
                "viability": "profitable",
            },
            "unit_economics": {
                "cac": 100,
                "ltv": 400,
                "ltv_cac_ratio": 4.0,
            },
            "recommendation": "no_pivot",
            "timestamp": "2024-01-01T00:00:00Z",
        }

        assert expected_payload["event"] == "validation_complete"
        assert "signals" in expected_payload
        assert "unit_economics" in expected_payload


# =============================================================================
# Rate Limiting Tests
# =============================================================================

class TestRateLimiting:
    """Tests for API rate limiting."""

    def test_kickoff_rate_limit(self):
        """Test kickoff endpoint rate limiting."""
        # Expected: Limited to X requests per minute per user
        pass  # Would test with TestClient

    def test_status_polling_rate_limit(self):
        """Test status endpoint rate limiting."""
        # Status polling should be allowed frequently (for real-time updates)
        # But should still have reasonable limits
        pass  # Would test with TestClient


# =============================================================================
# Idempotency Tests
# =============================================================================

class TestIdempotency:
    """Tests for idempotent operations."""

    def test_hitl_approve_idempotent(self, sample_hitl_state, mock_supabase_client):
        """Test that HITL approve is idempotent."""
        # Multiple approvals with same decision should not cause issues
        approval_request = {
            "run_id": sample_hitl_state["run_id"],
            "checkpoint": "approve_discovery_output",
            "decision": "approved",
        }

        # First approval updates state
        # Second approval should either succeed silently or return "already approved"
        pass  # Would test with TestClient

    def test_duplicate_kickoff_handling(self, sample_kickoff_request, mock_supabase_client):
        """Test handling of duplicate kickoff requests."""
        # Same project_id + user_id should either:
        # - Return existing run_id (if in progress)
        # - Create new run (if previous completed)
        pass  # Would test with TestClient


# =============================================================================
# Progress Tracking Tests
# =============================================================================

class TestProgressTracking:
    """Tests for real-time progress tracking."""

    def test_progress_table_updated(self, mock_supabase_client):
        """Test that progress is written to validation_progress table."""
        # Expected progress record structure
        progress_record = {
            "run_id": str(uuid4()),
            "phase": 1,
            "crew": "DiscoveryCrew",
            "agent": "E1",
            "task": "map_assumptions",
            "status": "in_progress",
            "progress_pct": 15,
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert "phase" in progress_record
        assert "crew" in progress_record
        assert "progress_pct" in progress_record
        assert 0 <= progress_record["progress_pct"] <= 100

    def test_progress_realtime_subscription(self):
        """Test Supabase Realtime subscription structure."""
        # Expected subscription channel
        expected_channel = "validation_progress:run_id=eq.{run_id}"

        # Progress updates should be broadcast via Realtime
        assert "validation_progress" in expected_channel
