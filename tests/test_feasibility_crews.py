"""
Tests for Phase 3: Feasibility Crews

Tests crew structure, agents, tasks, and flow orchestration for:
- FeasibilityBuildCrew (3 agents: F1, F2, F3)
- FeasibilityGovernanceCrew (2 agents: G1, G2)
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import yaml

from src.state.models import (
    FeasibilityEvidence,
    ValidationSignal,
)


# =============================================================================
# Crew Structure Tests
# =============================================================================

class TestPhase3CrewImports:
    """Test that all Phase 3 crews can be imported."""

    def test_feasibility_build_crew_imports(self):
        """Test FeasibilityBuildCrew can be imported."""
        from src.crews.feasibility import FeasibilityBuildCrew
        assert FeasibilityBuildCrew is not None

    def test_feasibility_governance_crew_imports(self):
        """Test FeasibilityGovernanceCrew can be imported."""
        from src.crews.feasibility import FeasibilityGovernanceCrew
        assert FeasibilityGovernanceCrew is not None

    def test_run_functions_import(self):
        """Test all run functions can be imported."""
        from src.crews.feasibility import (
            run_feasibility_build_crew,
            run_feasibility_governance_crew,
        )
        assert callable(run_feasibility_build_crew)
        assert callable(run_feasibility_governance_crew)


class TestFeasibilityBuildCrewStructure:
    """Tests for FeasibilityBuildCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        agents_yaml = crew_dir / "config" / "build_agents.yaml"
        tasks_yaml = crew_dir / "config" / "build_tasks.yaml"

        assert agents_yaml.exists(), f"build_agents.yaml not found at {agents_yaml}"
        assert tasks_yaml.exists(), f"build_tasks.yaml not found at {tasks_yaml}"

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 3 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        with open(crew_dir / "config" / "build_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "f1_requirements_analyst",
            "f2_frontend_assessor",
            "f3_backend_assessor",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"

    def test_f1_agent_definition(self):
        """Test F1 Requirements Analyst definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        with open(crew_dir / "config" / "build_agents.yaml") as f:
            agents = yaml.safe_load(f)

        f1 = agents["f1_requirements_analyst"]
        assert "role" in f1
        assert "goal" in f1
        assert "backstory" in f1
        assert "Requirements" in f1["role"] or "Analyst" in f1["role"]
        # Should know about complexity scoring
        assert "1-10" in f1["backstory"]

    def test_f2_agent_definition(self):
        """Test F2 Frontend Assessor definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        with open(crew_dir / "config" / "build_agents.yaml") as f:
            agents = yaml.safe_load(f)

        f2 = agents["f2_frontend_assessor"]
        assert "role" in f2
        assert "Frontend" in f2["role"] or "Assessor" in f2["role"]

    def test_f3_agent_definition(self):
        """Test F3 Backend Assessor definition - sets feasibility signal."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        with open(crew_dir / "config" / "build_agents.yaml") as f:
            agents = yaml.safe_load(f)

        f3 = agents["f3_backend_assessor"]
        assert "role" in f3
        assert "Backend" in f3["role"] or "Assessor" in f3["role"]
        # F3 sets the feasibility signal
        assert "GREEN" in f3["backstory"]
        assert "ORANGE" in f3["backstory"]
        assert "RED" in f3["backstory"]

    def test_tasks_yaml_has_all_tasks(self):
        """Test that tasks.yaml contains all required tasks."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        with open(crew_dir / "config" / "build_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        required_tasks = [
            "extract_feature_requirements",
            "assess_ui_complexity",
            "design_lite_variant",
            "assess_frontend_complexity",
            "identify_framework_requirements",
            "assess_backend_architecture",
            "evaluate_api_integrations",
            "estimate_costs",
            "set_feasibility_signal",
        ]

        for task_id in required_tasks:
            assert task_id in tasks, f"Task {task_id} not found"


class TestFeasibilityGovernanceCrewStructure:
    """Tests for FeasibilityGovernanceCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        agents_yaml = crew_dir / "config" / "governance_agents.yaml"
        tasks_yaml = crew_dir / "config" / "governance_tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 2 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        with open(crew_dir / "config" / "governance_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "g1_qa_agent",
            "g2_security_agent",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"

    def test_g1_qa_agent_definition(self):
        """Test G1 QA Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        with open(crew_dir / "config" / "governance_agents.yaml") as f:
            agents = yaml.safe_load(f)

        g1 = agents["g1_qa_agent"]
        assert "role" in g1
        assert "QA" in g1["role"] or "Feasibility" in g1["role"]
        # Should validate gate readiness
        assert "gate" in g1["backstory"].lower() or "readiness" in g1["backstory"].lower()

    def test_g2_security_agent_definition(self):
        """Test G2 Security Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        with open(crew_dir / "config" / "governance_agents.yaml") as f:
            agents = yaml.safe_load(f)

        g2 = agents["g2_security_agent"]
        assert "role" in g2
        assert "Security" in g2["role"] or "Architecture" in g2["role"]

    def test_tasks_yaml_has_all_tasks(self):
        """Test that tasks.yaml contains all required tasks."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"
        with open(crew_dir / "config" / "governance_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        required_tasks = [
            "validate_assessment_methodology",
            "verify_constraint_documentation",
            "review_architecture_security",
            "confirm_gate_readiness",
        ]

        for task_id in required_tasks:
            assert task_id in tasks, f"Task {task_id} not found"


# =============================================================================
# Output Schema Tests
# =============================================================================

class TestFeasibilitySchemas:
    """Tests for Feasibility output schemas."""

    def test_feasibility_evidence_creation(self):
        """Test FeasibilityEvidence schema."""
        evidence = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            signal=ValidationSignal.GREEN,
        )
        assert evidence.core_features_feasible is True
        assert evidence.downgrade_required is False
        assert evidence.signal == ValidationSignal.GREEN

    def test_green_signal(self):
        """Test GREEN signal (fully feasible)."""
        evidence = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            signal=ValidationSignal.GREEN,
        )
        assert evidence.signal == ValidationSignal.GREEN

    def test_orange_signal(self):
        """Test ORANGE_CONSTRAINED signal (feasible with downgrade)."""
        evidence = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=True,
            downgrade_features=["Real-time sync", "AI recommendations"],
            signal=ValidationSignal.ORANGE_CONSTRAINED,
        )
        assert evidence.signal == ValidationSignal.ORANGE_CONSTRAINED
        assert len(evidence.downgrade_features) == 2

    def test_red_signal(self):
        """Test RED_IMPOSSIBLE signal (not feasible)."""
        evidence = FeasibilityEvidence(
            core_features_feasible=False,
            constraints=["No API available", "Patent blocked"],
            signal=ValidationSignal.RED_IMPOSSIBLE,
        )
        assert evidence.signal == ValidationSignal.RED_IMPOSSIBLE
        assert len(evidence.constraints) == 2


# =============================================================================
# Phase 3 Flow Tests
# =============================================================================

class TestPhase3Flow:
    """Tests for Phase 3 flow orchestration."""

    def test_phase_3_module_imports(self):
        """Test that phase_3 module can be imported."""
        from src.modal_app.phases import phase_3_feasibility
        assert hasattr(phase_3_feasibility, "execute")

    def test_phase_3_returns_hitl_checkpoint(self, minimal_founders_brief):
        """Test that Phase 3 returns HITL checkpoint."""
        mock_feasibility = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            signal=ValidationSignal.GREEN,
        )

        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build, \
             patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = mock_feasibility
            mock_governance.return_value = {"gate_ready": True}

            from src.modal_app.phases.phase_3 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                },
            )

            assert "hitl_checkpoint" in result
            assert result["hitl_checkpoint"] == "approve_feasibility_gate"
            assert "hitl_options" in result

    def test_phase_3_green_signal_recommends_approve(self, minimal_founders_brief):
        """Test that GREEN signal recommends approve."""
        mock_feasibility = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            signal=ValidationSignal.GREEN,
        )

        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build, \
             patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = mock_feasibility
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_3 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                },
            )

            assert result["hitl_recommended"] == "approve"
            assert result["state"]["feasibility_signal"] == "green"

    def test_phase_3_orange_signal_recommends_feature_pivot(self, minimal_founders_brief):
        """Test that ORANGE_CONSTRAINED signal recommends feature pivot."""
        mock_feasibility = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=True,
            downgrade_features=["Real-time sync"],
            signal=ValidationSignal.ORANGE_CONSTRAINED,
        )

        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build, \
             patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = mock_feasibility
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_3 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                },
            )

            assert result["hitl_recommended"] == "feature_pivot"
            assert result["state"]["feasibility_signal"] == "orange_constrained"

    def test_phase_3_red_signal_recommends_kill(self, minimal_founders_brief):
        """Test that RED_IMPOSSIBLE signal recommends kill."""
        mock_feasibility = FeasibilityEvidence(
            core_features_feasible=False,
            constraints=["Patent blocked"],
            signal=ValidationSignal.RED_IMPOSSIBLE,
        )

        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build, \
             patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = mock_feasibility
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_3 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                },
            )

            assert result["hitl_recommended"] == "kill"
            assert result["state"]["feasibility_signal"] == "red_impossible"

    def test_phase_3_hitl_options_include_all_choices(self, minimal_founders_brief):
        """Test that HITL checkpoint includes all options."""
        mock_feasibility = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            signal=ValidationSignal.GREEN,
        )

        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build, \
             patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = mock_feasibility
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_3 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                },
            )

            option_ids = [opt["id"] for opt in result["hitl_options"]]
            assert "approve" in option_ids
            assert "feature_pivot" in option_ids
            assert "kill" in option_ids


# =============================================================================
# Downgrade Protocol Tests
# =============================================================================

class TestDowngradeProtocol:
    """Tests for downgrade protocol (Innovation Physics)."""

    def test_orange_signal_triggers_downgrade(self):
        """Test ORANGE_CONSTRAINED indicates downgrade required."""
        evidence = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=True,
            downgrade_features=["Feature A", "Feature B"],
            signal=ValidationSignal.ORANGE_CONSTRAINED,
        )
        assert evidence.downgrade_required is True
        assert len(evidence.downgrade_features) == 2

    def test_green_signal_no_downgrade(self):
        """Test GREEN signal means no downgrade needed."""
        evidence = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            signal=ValidationSignal.GREEN,
        )
        assert evidence.downgrade_required is False
        assert evidence.downgrade_features == []

    def test_red_signal_kill_not_downgrade(self):
        """Test RED_IMPOSSIBLE signal leads to kill, not downgrade."""
        evidence = FeasibilityEvidence(
            core_features_feasible=False,
            downgrade_required=False,  # No point downgrading if impossible
            constraints=["Fundamental impossibility"],
            signal=ValidationSignal.RED_IMPOSSIBLE,
        )
        assert evidence.core_features_feasible is False
        assert evidence.signal == ValidationSignal.RED_IMPOSSIBLE


# =============================================================================
# Cost Estimation Tests
# =============================================================================

class TestCostEstimation:
    """Tests for cost estimation in feasibility."""

    def test_cost_fields_in_evidence(self):
        """Test cost fields exist in FeasibilityEvidence."""
        evidence = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            api_costs_monthly=500.0,
            infra_costs_monthly=200.0,
            signal=ValidationSignal.GREEN,
        )
        assert evidence.api_costs_monthly == 500.0
        assert evidence.infra_costs_monthly == 200.0

    def test_phase_3_includes_cost_context(self, minimal_founders_brief):
        """Test that Phase 3 HITL context includes costs."""
        mock_feasibility = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            api_costs_monthly=500.0,
            infra_costs_monthly=200.0,
            signal=ValidationSignal.GREEN,
        )

        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build, \
             patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = mock_feasibility
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_3 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                },
            )

            assert "hitl_context" in result
            assert "costs" in result["hitl_context"]
            costs = result["hitl_context"]["costs"]
            assert costs["api_monthly"] == 500.0
            assert costs["infra_monthly"] == 200.0
            assert costs["total_monthly"] == 700.0


# =============================================================================
# Agent Count Verification
# =============================================================================

class TestPhase3AgentCounts:
    """Verify Phase 3 has the correct number of agents (5 total)."""

    def test_total_agent_count(self):
        """Test that Phase 3 has 5 agents total."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "feasibility"

        # Count agents in each config file
        config_files = [
            ("build_agents.yaml", 3),  # FeasibilityBuildCrew: F1, F2, F3
            ("governance_agents.yaml", 2),  # FeasibilityGovernanceCrew: G1, G2
        ]

        total_agents = 0
        for config_file, expected_count in config_files:
            with open(crew_dir / "config" / config_file) as f:
                agents = yaml.safe_load(f)
                actual_count = len(agents)
                assert actual_count == expected_count, (
                    f"{config_file}: expected {expected_count} agents, got {actual_count}"
                )
                total_agents += actual_count

        assert total_agents == 5, f"Expected 5 agents total, got {total_agents}"

    def test_crew_agent_distribution(self):
        """Test agent distribution matches specification."""
        expected = {
            "FeasibilityBuildCrew": 3,  # F1, F2, F3
            "FeasibilityGovernanceCrew": 2,  # G1, G2
        }

        total = sum(expected.values())
        assert total == 5, f"Expected 5 agents total, got {total}"


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestPhase3ErrorHandling:
    """Tests for error handling in Phase 3."""

    def test_phase_3_handles_build_crew_error(self, minimal_founders_brief):
        """Test that Phase 3 handles FeasibilityBuildCrew errors."""
        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build:

            mock_build.side_effect = Exception("FeasibilityBuildCrew failed")
            mock_progress.return_value = True

            from src.modal_app.phases.phase_3 import execute

            with pytest.raises(Exception) as exc_info:
                execute(
                    run_id="test-run-123",
                    state={
                        "founders_brief": minimal_founders_brief.model_dump(),
                        "customer_profile": {},
                        "value_map": {},
                    },
                )

            assert "FeasibilityBuildCrew failed" in str(exc_info.value)

    def test_phase_3_handles_governance_crew_error(self, minimal_founders_brief):
        """Test that Phase 3 handles FeasibilityGovernanceCrew errors."""
        mock_feasibility = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            signal=ValidationSignal.GREEN,
        )

        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build, \
             patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_governance:

            mock_build.return_value = mock_feasibility
            mock_governance.side_effect = Exception("FeasibilityGovernanceCrew failed")
            mock_progress.return_value = True

            from src.modal_app.phases.phase_3 import execute

            with pytest.raises(Exception) as exc_info:
                execute(
                    run_id="test-run-123",
                    state={
                        "founders_brief": minimal_founders_brief.model_dump(),
                        "customer_profile": {},
                        "value_map": {},
                    },
                )

            assert "FeasibilityGovernanceCrew failed" in str(exc_info.value)


# =============================================================================
# Signal Derivation Tests
# =============================================================================

class TestSignalDerivation:
    """Tests for signal derivation logic in Phase 3."""

    def test_derive_green_from_evidence(self, minimal_founders_brief):
        """Test GREEN derived from core_features_feasible=True and no downgrade."""
        mock_feasibility = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
        )

        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build, \
             patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = mock_feasibility
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_3 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                },
            )

            # Signal derived from evidence when not explicitly set
            assert result["state"]["feasibility_signal"] == "green"

    def test_derive_orange_from_downgrade_required(self, minimal_founders_brief):
        """Test ORANGE derived from downgrade_required=True."""
        mock_feasibility = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=True,
            downgrade_features=["Feature X"],
        )

        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build, \
             patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = mock_feasibility
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_3 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                },
            )

            assert result["state"]["feasibility_signal"] == "orange_constrained"

    def test_derive_red_from_core_not_feasible(self, minimal_founders_brief):
        """Test RED derived from core_features_feasible=False."""
        mock_feasibility = FeasibilityEvidence(
            core_features_feasible=False,
            constraints=["Blocking constraint"],
        )

        with patch("src.modal_app.phases.phase_3.update_progress") as mock_progress, \
             patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build, \
             patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = mock_feasibility
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_3 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                },
            )

            assert result["state"]["feasibility_signal"] == "red_impossible"
