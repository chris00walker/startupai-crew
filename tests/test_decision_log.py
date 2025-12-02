"""
Decision Log Tests - Decision Logger Unit Tests

Tests for DecisionLogger with mocked Supabase client.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from startupai.persistence.decision_log import (
    DecisionType,
    ActorType,
    DecisionRecord,
    DecisionLogEntry,
    DecisionLogger,
    log_human_approval,
    log_policy_selection,
    log_router_decision,
    log_pivot_decision,
    get_project_decision_history,
)
from startupai.flows.state_schemas import EnforcementMode


# ===========================================================================
# ENUM TESTS
# ===========================================================================

class TestDecisionType:
    """Test DecisionType enum."""

    def test_all_decision_types_exist(self):
        """Verify all expected decision types exist."""
        expected = [
            "budget_check", "budget_escalation", "budget_override",
            "human_approval", "router_decision", "policy_selection",
            "pivot_decision", "creative_approval", "viability_approval",
        ]
        actual = [dt.value for dt in DecisionType]
        for exp in expected:
            assert exp in actual, f"Missing decision type: {exp}"

    def test_decision_type_values_are_snake_case(self):
        """Decision type values should be lowercase snake_case."""
        for dt in DecisionType:
            assert dt.value == dt.value.lower()
            assert "_" in dt.value or dt.value.isalpha()


class TestActorType:
    """Test ActorType enum."""

    def test_all_actor_types_exist(self):
        """Verify all expected actor types exist."""
        expected = [
            "system", "human", "human_founder", "admin",
            "guardian_agent", "synthesis_agent",
        ]
        actual = [at.value for at in ActorType]
        for exp in expected:
            assert exp in actual, f"Missing actor type: {exp}"


# ===========================================================================
# MODEL TESTS
# ===========================================================================

class TestDecisionRecord:
    """Test DecisionRecord model."""

    def test_minimal_record(self):
        """Create record with minimal required fields."""
        record = DecisionRecord(
            project_id="proj_001",
            decision_type=DecisionType.ROUTER_DECISION,
            decision_point="desirability_gate",
            decision="passed",
            actor_type=ActorType.SYSTEM,
        )
        assert record.project_id == "proj_001"
        assert record.decision_type == DecisionType.ROUTER_DECISION
        assert record.decision == "passed"
        assert record.actor_type == ActorType.SYSTEM
        assert record.rationale is None
        assert record.is_override is False

    def test_full_record(self):
        """Create record with all fields."""
        record = DecisionRecord(
            project_id="proj_002",
            decision_type=DecisionType.BUDGET_OVERRIDE,
            decision_point="viability_budget",
            decision="approved",
            rationale="Critical pivot experiment",
            actor_type=ActorType.ADMIN,
            actor_id="admin_123",
            enforcement_mode=EnforcementMode.HARD,
            budget_limit_usd=1000.0,
            current_spend_usd=850.0,
            threshold_pct=0.85,
            context_snapshot={"experiment_type": "value_test"},
            is_override=True,
            override_reason="Approved by CTO",
            overridden_by="admin_123",
            metadata={"priority": "high"},
        )
        assert record.is_override is True
        assert record.budget_limit_usd == 1000.0
        assert record.threshold_pct == 0.85
        assert record.metadata["priority"] == "high"


class TestDecisionLogEntry:
    """Test DecisionLogEntry model."""

    def test_entry_creation(self):
        """Create entry from database row data."""
        entry = DecisionLogEntry(
            id="entry_001",
            project_id="proj_001",
            decision_type="router_decision",
            decision_point="feasibility_gate",
            decision="passed",
            rationale="All features feasible",
            actor_type="system",
            actor_id=None,
            enforcement_mode=None,
            budget_limit_usd=None,
            current_spend_usd=None,
            threshold_pct=None,
            context_snapshot={"feasibility_score": 0.92},
            is_override=False,
            override_reason=None,
            overridden_by=None,
            created_at=datetime(2024, 6, 15, 10, 30, 0),
            metadata={},
        )
        assert entry.id == "entry_001"
        assert entry.decision_type == "router_decision"
        assert entry.context_snapshot["feasibility_score"] == 0.92


# ===========================================================================
# DECISION LOGGER TESTS
# ===========================================================================

class TestDecisionLogger:
    """Test DecisionLogger with mocked Supabase."""

    @pytest.fixture
    def mock_supabase(self):
        """Create mock Supabase client."""
        client = MagicMock()

        # Mock RPC
        client.rpc.return_value.execute.return_value = Mock(data="entry_123")

        # Mock table operations
        table = MagicMock()
        client.table.return_value = table
        client.from_.return_value = table

        # Mock select chain
        select = MagicMock()
        table.select.return_value = select
        select.eq.return_value = select
        select.order.return_value = select
        select.limit.return_value = select
        select.execute.return_value = Mock(data=[])

        return client

    @pytest.fixture
    def logger(self, mock_supabase):
        """Create DecisionLogger with mocked client."""
        with patch(
            'startupai.persistence.decision_log.get_supabase_client',
            return_value=mock_supabase
        ):
            logger = DecisionLogger()
            # Force lazy load
            _ = logger.supabase
            yield logger

    def test_log_decision_success(self, logger, mock_supabase):
        """log_decision returns success with entry ID."""
        record = DecisionRecord(
            project_id="proj_001",
            decision_type=DecisionType.ROUTER_DECISION,
            decision_point="desirability_gate",
            decision="passed",
            actor_type=ActorType.SYSTEM,
        )

        result = logger.log_decision(record)

        assert result.is_usable
        assert result.data == "entry_123"
        mock_supabase.rpc.assert_called_once()

    def test_log_decision_rpc_params(self, logger, mock_supabase):
        """log_decision sends correct RPC parameters."""
        record = DecisionRecord(
            project_id="proj_001",
            decision_type=DecisionType.BUDGET_CHECK,
            decision_point="viability_budget",
            decision="approved",
            rationale="Within budget",
            actor_type=ActorType.GUARDIAN_AGENT,
            enforcement_mode=EnforcementMode.SOFT,
            budget_limit_usd=500.0,
            current_spend_usd=300.0,
            threshold_pct=0.6,
        )

        logger.log_decision(record)

        call_args = mock_supabase.rpc.call_args
        params = call_args[0][1]

        assert params['p_project_id'] == "proj_001"
        assert params['p_decision_type'] == "budget_check"
        assert params['p_decision'] == "approved"
        assert params['p_rationale'] == "Within budget"
        assert params['p_enforcement_mode'] == "soft"
        assert params['p_budget_limit_usd'] == 500.0

    def test_log_decision_handles_error(self, logger, mock_supabase):
        """log_decision handles database errors gracefully."""
        mock_supabase.rpc.side_effect = Exception("Database connection failed")

        record = DecisionRecord(
            project_id="proj",
            decision_type=DecisionType.ROUTER_DECISION,
            decision_point="gate",
            decision="passed",
            actor_type=ActorType.SYSTEM,
        )

        result = logger.log_decision(record)

        assert not result.is_usable
        assert "Failed to log decision" in result.error_message
        assert result.error_code == "DECISION_LOG_ERROR"

    def test_get_decisions_success(self, logger, mock_supabase):
        """get_decisions returns list of entries."""
        mock_supabase.table().select().eq().order().limit().execute.return_value = Mock(
            data=[
                {
                    'id': 'entry_1',
                    'project_id': 'proj_001',
                    'decision_type': 'router_decision',
                    'decision_point': 'desirability_gate',
                    'decision': 'passed',
                    'rationale': 'Strong signals',
                    'actor_type': 'system',
                    'created_at': '2024-06-15T10:30:00Z',
                },
                {
                    'id': 'entry_2',
                    'project_id': 'proj_001',
                    'decision_type': 'router_decision',
                    'decision_point': 'feasibility_gate',
                    'decision': 'passed',
                    'rationale': 'All feasible',
                    'actor_type': 'system',
                    'created_at': '2024-06-16T14:00:00Z',
                },
            ]
        )

        result = logger.get_decisions("proj_001")

        assert result.is_usable
        assert len(result.data) == 2
        assert result.data[0].id == "entry_1"
        assert result.data[1].decision_point == "feasibility_gate"

    def test_get_decisions_with_type_filter(self, logger, mock_supabase):
        """get_decisions applies decision type filter."""
        mock_chain = mock_supabase.table().select().eq().order().limit()
        mock_chain.eq.return_value.execute.return_value = Mock(data=[])

        logger.get_decisions("proj_001", decision_type=DecisionType.BUDGET_CHECK)

        # Verify second eq call for decision_type filter
        mock_chain.eq.assert_called_with('decision_type', 'budget_check')

    def test_get_decisions_handles_error(self, logger, mock_supabase):
        """get_decisions handles database errors gracefully."""
        mock_supabase.table.side_effect = Exception("Query failed")

        result = logger.get_decisions("proj_001")

        assert not result.is_usable
        assert result.error_code == "DECISION_QUERY_ERROR"

    def test_get_overrides_success(self, logger, mock_supabase):
        """get_overrides returns override entries."""
        mock_supabase.from_().select().order().limit().execute.return_value = Mock(
            data=[
                {
                    'id': 'override_1',
                    'project_id': 'proj_001',
                    'decision_type': 'budget_override',
                    'decision_point': 'viability_budget',
                    'decision': 'approved',
                    'rationale': 'Critical experiment',
                    'actor_type': 'admin',
                    'override_reason': 'CTO approval',
                    'overridden_by': 'admin_001',
                    'created_at': '2024-06-15T10:30:00Z',
                },
            ]
        )

        result = logger.get_overrides()

        assert result.is_usable
        assert len(result.data) == 1
        assert result.data[0].is_override is True

    def test_get_budget_summary_success(self, logger, mock_supabase):
        """get_budget_summary returns summary data."""
        mock_supabase.from_().select().eq().execute.return_value = Mock(
            data=[{
                'project_id': 'proj_001',
                'approved_count': 5,
                'rejected_count': 1,
                'escalated_count': 2,
                'override_count': 1,
            }]
        )

        result = logger.get_budget_summary("proj_001")

        assert result.is_usable
        assert result.data['approved_count'] == 5
        assert result.data['override_count'] == 1

    def test_get_budget_summary_empty(self, logger, mock_supabase):
        """get_budget_summary returns defaults for new project."""
        mock_supabase.from_().select().eq().execute.return_value = Mock(data=[])

        result = logger.get_budget_summary("new_proj")

        assert result.is_usable
        assert result.data['approved_count'] == 0
        assert result.data['override_count'] == 0


# ===========================================================================
# CONVENIENCE FUNCTION TESTS
# ===========================================================================

class TestConvenienceFunctions:
    """Test convenience logging functions."""

    @pytest.fixture
    def mock_logger(self):
        """Mock DecisionLogger for convenience functions."""
        with patch('startupai.persistence.decision_log.DecisionLogger') as MockLogger:
            mock_instance = MagicMock()
            mock_instance.log_decision.return_value = Mock(
                is_usable=True, data="entry_123"
            )
            MockLogger.return_value = mock_instance
            yield mock_instance

    def test_log_human_approval(self, mock_logger):
        """log_human_approval creates correct record."""
        result = log_human_approval(
            project_id="proj_001",
            decision_point="creative_review",
            approved=True,
            rationale="Landing page looks good",
            actor_id="user_123",
            context={"artifact_id": "lp_001"},
        )

        mock_logger.log_decision.assert_called_once()
        record = mock_logger.log_decision.call_args[0][0]

        assert record.decision_type == DecisionType.HUMAN_APPROVAL
        assert record.decision == "approved"
        assert record.actor_type == ActorType.HUMAN_FOUNDER
        assert record.actor_id == "user_123"
        assert record.context_snapshot["artifact_id"] == "lp_001"

    def test_log_human_approval_rejection(self, mock_logger):
        """log_human_approval handles rejection."""
        log_human_approval(
            project_id="proj",
            decision_point="viability_review",
            approved=False,
            rationale="Unit economics too weak",
            actor_id="user_456",
        )

        record = mock_logger.log_decision.call_args[0][0]
        assert record.decision == "rejected"

    def test_log_policy_selection(self, mock_logger):
        """log_policy_selection creates correct record."""
        log_policy_selection(
            project_id="proj_001",
            policy_version="retrieval_v1",
            selection_reason="A/B test assignment",
            experiment_type="landing_page",
        )

        record = mock_logger.log_decision.call_args[0][0]

        assert record.decision_type == DecisionType.POLICY_SELECTION
        assert record.decision == "retrieval_v1"
        assert record.decision_point == "experiment_landing_page"
        assert record.actor_type == ActorType.SYSTEM
        assert record.metadata["experiment_type"] == "landing_page"

    def test_log_router_decision(self, mock_logger):
        """log_router_decision creates correct record."""
        evidence = {"problem_resonance": 0.75, "conversion_rate": 0.12}
        log_router_decision(
            project_id="proj_001",
            gate_name="desirability",
            passed=True,
            rationale="Strong commitment signals",
            evidence_summary=evidence,
        )

        record = mock_logger.log_decision.call_args[0][0]

        assert record.decision_type == DecisionType.ROUTER_DECISION
        assert record.decision_point == "desirability_gate"
        assert record.decision == "passed"
        assert record.context_snapshot["problem_resonance"] == 0.75

    def test_log_router_decision_failure(self, mock_logger):
        """log_router_decision handles gate failure."""
        log_router_decision(
            project_id="proj",
            gate_name="viability",
            passed=False,
            rationale="LTV/CAC ratio below threshold",
        )

        record = mock_logger.log_decision.call_args[0][0]
        assert record.decision == "failed"

    def test_log_pivot_decision(self, mock_logger):
        """log_pivot_decision creates correct record."""
        log_pivot_decision(
            project_id="proj_001",
            pivot_type="segment_pivot",
            rationale="Low resonance with SMBs, try Enterprise",
            confidence_level="high",
            actor_type=ActorType.SYNTHESIS_AGENT,
            human_approved=True,
            human_approver_id="user_789",
        )

        record = mock_logger.log_decision.call_args[0][0]

        assert record.decision_type == DecisionType.PIVOT_DECISION
        assert record.decision == "segment_pivot"
        assert record.actor_type == ActorType.SYNTHESIS_AGENT
        assert record.actor_id == "user_789"
        assert record.metadata["confidence_level"] == "high"
        assert record.metadata["human_approved"] is True


class TestGetProjectDecisionHistory:
    """Test get_project_decision_history function."""

    def test_returns_entries_on_success(self):
        """Returns decision entries when query succeeds."""
        mock_entries = [
            MagicMock(spec=DecisionLogEntry),
            MagicMock(spec=DecisionLogEntry),
        ]

        with patch('startupai.persistence.decision_log.DecisionLogger') as MockLogger:
            mock_instance = MagicMock()
            mock_instance.get_decisions.return_value = Mock(
                is_usable=True, data=mock_entries
            )
            MockLogger.return_value = mock_instance

            result = get_project_decision_history("proj_001")

            assert len(result) == 2

    def test_returns_empty_on_failure(self):
        """Returns empty list when query fails."""
        with patch('startupai.persistence.decision_log.DecisionLogger') as MockLogger:
            mock_instance = MagicMock()
            mock_instance.get_decisions.return_value = Mock(
                is_usable=False, data=None
            )
            MockLogger.return_value = mock_instance

            result = get_project_decision_history("proj_001")

            assert result == []

    def test_filters_by_decision_type(self):
        """Passes decision type filter to logger."""
        with patch('startupai.persistence.decision_log.DecisionLogger') as MockLogger:
            mock_instance = MagicMock()
            mock_instance.get_decisions.return_value = Mock(is_usable=True, data=[])
            MockLogger.return_value = mock_instance

            get_project_decision_history("proj_001", decision_type="budget_check")

            mock_instance.get_decisions.assert_called_with(
                "proj_001", decision_type=DecisionType.BUDGET_CHECK
            )
