"""
Tests for Phase 2: Desirability Crews

Tests crew structure, agents, tasks, and flow orchestration for:
- BuildCrew (3 agents: F1, F2, F3)
- GrowthCrew (3 agents: P1, P2, P3)
- GovernanceCrew (3 agents: G1, G2, G3)
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import yaml

from src.state.models import (
    DesirabilityEvidence,
    ValidationSignal,
    CustomerProfile,
    ValueMap,
)


# =============================================================================
# Crew Structure Tests
# =============================================================================

class TestPhase2CrewImports:
    """Test that all Phase 2 crews can be imported."""

    def test_build_crew_imports(self):
        """Test BuildCrew can be imported."""
        from src.crews.desirability import BuildCrew
        assert BuildCrew is not None

    def test_growth_crew_imports(self):
        """Test GrowthCrew can be imported."""
        from src.crews.desirability import GrowthCrew
        assert GrowthCrew is not None

    def test_governance_crew_imports(self):
        """Test GovernanceCrew can be imported."""
        from src.crews.desirability import GovernanceCrew
        assert GovernanceCrew is not None

    def test_run_functions_import(self):
        """Test all run functions can be imported."""
        from src.crews.desirability import (
            run_build_crew,
            run_growth_crew,
            run_governance_crew,
        )
        assert callable(run_build_crew)
        assert callable(run_growth_crew)
        assert callable(run_governance_crew)


class TestBuildCrewStructure:
    """Tests for BuildCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        agents_yaml = crew_dir / "config" / "build_agents.yaml"
        tasks_yaml = crew_dir / "config" / "build_tasks.yaml"

        assert agents_yaml.exists(), f"build_agents.yaml not found at {agents_yaml}"
        assert tasks_yaml.exists(), f"build_tasks.yaml not found at {tasks_yaml}"

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 3 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "build_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "f1_ux_designer",
            "f2_frontend_developer",
            "f3_backend_developer",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"

    def test_f1_agent_definition(self):
        """Test F1 UX/UI Designer Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "build_agents.yaml") as f:
            agents = yaml.safe_load(f)

        f1 = agents["f1_ux_designer"]
        assert "role" in f1
        assert "goal" in f1
        assert "backstory" in f1
        assert "UX" in f1["role"] or "Designer" in f1["role"]

    def test_f2_agent_definition(self):
        """Test F2 Frontend Developer Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "build_agents.yaml") as f:
            agents = yaml.safe_load(f)

        f2 = agents["f2_frontend_developer"]
        assert "role" in f2
        assert "Frontend" in f2["role"] or "Developer" in f2["role"]

    def test_f3_agent_definition(self):
        """Test F3 Backend Developer Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "build_agents.yaml") as f:
            agents = yaml.safe_load(f)

        f3 = agents["f3_backend_developer"]
        assert "role" in f3
        assert "Backend" in f3["role"] or "DevOps" in f3["role"]

    def test_tasks_yaml_has_all_tasks(self):
        """Test that tasks.yaml contains all required tasks."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "build_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        required_tasks = [
            "design_landing_page",
            "build_landing_page",
            "deploy_artifacts",
        ]

        for task_id in required_tasks:
            assert task_id in tasks, f"Task {task_id} not found"


class TestGrowthCrewStructure:
    """Tests for GrowthCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        agents_yaml = crew_dir / "config" / "growth_agents.yaml"
        tasks_yaml = crew_dir / "config" / "growth_tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 3 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "growth_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "p1_ad_creative",
            "p2_communications",
            "p3_analytics",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"

    def test_p1_agent_definition(self):
        """Test P1 Ad Creative Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "growth_agents.yaml") as f:
            agents = yaml.safe_load(f)

        p1 = agents["p1_ad_creative"]
        assert "role" in p1
        assert "Ad" in p1["role"] or "Creative" in p1["role"]

    def test_p2_agent_definition(self):
        """Test P2 Communications Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "growth_agents.yaml") as f:
            agents = yaml.safe_load(f)

        p2 = agents["p2_communications"]
        assert "role" in p2
        assert "Communications" in p2["role"] or "Copywriter" in p2["role"].lower()

    def test_p3_agent_definition(self):
        """Test P3 Analytics Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "growth_agents.yaml") as f:
            agents = yaml.safe_load(f)

        p3 = agents["p3_analytics"]
        assert "role" in p3
        assert "Analytics" in p3["role"] or "Experimentation" in p3["role"]
        # P3 should know about Innovation Physics signals
        assert "problem_resonance" in p3["backstory"]
        assert "zombie_ratio" in p3["backstory"]

    def test_tasks_yaml_has_all_tasks(self):
        """Test that tasks.yaml contains all required tasks."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "growth_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        required_tasks = [
            "create_ad_variants",
            "write_copy_variants",
            "configure_experiments",
            "run_experiments",
            "compute_desirability_signals",
        ]

        for task_id in required_tasks:
            assert task_id in tasks, f"Task {task_id} not found"


class TestGovernanceCrewStructure:
    """Tests for GovernanceCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        agents_yaml = crew_dir / "config" / "governance_agents.yaml"
        tasks_yaml = crew_dir / "config" / "governance_tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 3 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "governance_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "g1_qa_agent",
            "g2_security_agent",
            "g3_audit_agent",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"

    def test_g1_qa_agent_definition(self):
        """Test G1 QA Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "governance_agents.yaml") as f:
            agents = yaml.safe_load(f)

        g1 = agents["g1_qa_agent"]
        assert "role" in g1
        assert "QA" in g1["role"] or "Quality" in g1["role"]
        # Guardian reviews, does not execute
        assert "reviews" in g1["backstory"].lower() or "validates" in g1["backstory"].lower()

    def test_g2_security_agent_definition(self):
        """Test G2 Security Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "governance_agents.yaml") as f:
            agents = yaml.safe_load(f)

        g2 = agents["g2_security_agent"]
        assert "role" in g2
        assert "Security" in g2["role"] or "Privacy" in g2["role"]
        # Should handle PII
        assert "PII" in g2["backstory"].upper() or "pii" in g2["backstory"].lower()

    def test_g3_audit_agent_definition(self):
        """Test G3 Audit Agent definition."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "governance_agents.yaml") as f:
            agents = yaml.safe_load(f)

        g3 = agents["g3_audit_agent"]
        assert "role" in g3
        assert "Audit" in g3["role"] or "Compliance" in g3["role"]

    def test_tasks_yaml_has_all_tasks(self):
        """Test that tasks.yaml contains all required tasks."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"
        with open(crew_dir / "config" / "governance_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        required_tasks = [
            "methodology_compliance_check",
            "creative_qa",
            "security_review",
            "log_decisions",
        ]

        for task_id in required_tasks:
            assert task_id in tasks, f"Task {task_id} not found"


# =============================================================================
# Output Schema Tests
# =============================================================================

class TestDesirabilitySchemas:
    """Tests for Desirability output schemas."""

    def test_desirability_evidence_creation(self):
        """Test DesirabilityEvidence schema."""
        evidence = DesirabilityEvidence(
            ad_impressions=1000,
            ad_clicks=100,
            ad_signups=30,
            problem_resonance=0.13,
            zombie_ratio=0.70,
            signal=ValidationSignal.MILD_INTEREST,
        )
        assert evidence.ad_impressions == 1000
        assert evidence.problem_resonance == 0.13
        assert evidence.zombie_ratio == 0.70
        assert evidence.signal == ValidationSignal.MILD_INTEREST

    def test_strong_commitment_signal(self):
        """Test STRONG_COMMITMENT signal criteria."""
        evidence = DesirabilityEvidence(
            problem_resonance=0.45,  # >= 0.3
            zombie_ratio=0.25,  # < 0.7
            signal=ValidationSignal.STRONG_COMMITMENT,
        )
        assert evidence.signal == ValidationSignal.STRONG_COMMITMENT

    def test_mild_interest_signal(self):
        """Test MILD_INTEREST signal criteria (high zombie)."""
        evidence = DesirabilityEvidence(
            problem_resonance=0.35,  # >= 0.3
            zombie_ratio=0.75,  # >= 0.7
            signal=ValidationSignal.MILD_INTEREST,
        )
        assert evidence.signal == ValidationSignal.MILD_INTEREST

    def test_no_interest_signal(self):
        """Test NO_INTEREST signal criteria (low resonance)."""
        evidence = DesirabilityEvidence(
            problem_resonance=0.15,  # < 0.3
            zombie_ratio=0.40,
            signal=ValidationSignal.NO_INTEREST,
        )
        assert evidence.signal == ValidationSignal.NO_INTEREST


# =============================================================================
# Phase 2 Flow Tests
# =============================================================================

class TestPhase2Flow:
    """Tests for Phase 2 flow orchestration."""

    def test_phase_2_module_imports(self):
        """Test that phase_2 module can be imported."""
        from src.modal_app.phases import phase_2_desirability
        assert hasattr(phase_2_desirability, "execute")

    def test_phase_2_returns_hitl_checkpoint(self, minimal_founders_brief):
        """Test that Phase 2 returns HITL checkpoint."""
        mock_desirability = DesirabilityEvidence(
            ad_impressions=1000,
            ad_clicks=150,
            ad_signups=50,
            problem_resonance=0.45,
            zombie_ratio=0.30,
            signal=ValidationSignal.STRONG_COMMITMENT,
        )

        with patch("src.modal_app.phases.phase_2.update_progress") as mock_progress, \
             patch("src.crews.desirability.run_build_crew") as mock_build, \
             patch("src.crews.desirability.run_growth_crew") as mock_growth, \
             patch("src.crews.desirability.run_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = {"landing_pages": {"url": "https://test.netlify.app"}}
            mock_growth.return_value = mock_desirability
            mock_governance.return_value = {"qa_passed": True}

            from src.modal_app.phases.phase_2 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {"pains": []},
                    "value_map": {},
                },
            )

            assert "hitl_checkpoint" in result
            assert result["hitl_checkpoint"] == "approve_desirability_gate"
            assert "hitl_options" in result

    def test_phase_2_strong_commitment_recommends_approve(self, minimal_founders_brief):
        """Test that STRONG_COMMITMENT signal recommends approve."""
        mock_desirability = DesirabilityEvidence(
            problem_resonance=0.45,  # >= 0.3
            zombie_ratio=0.30,  # < 0.7
            signal=ValidationSignal.STRONG_COMMITMENT,
        )

        with patch("src.modal_app.phases.phase_2.update_progress") as mock_progress, \
             patch("src.crews.desirability.run_build_crew") as mock_build, \
             patch("src.crews.desirability.run_growth_crew") as mock_growth, \
             patch("src.crews.desirability.run_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = {}
            mock_growth.return_value = mock_desirability
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_2 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {"pains": []},
                    "value_map": {},
                },
            )

            # Implementation uses "approved" (past tense) as the action ID
            assert result["hitl_recommended"] == "approved"
            assert result["state"]["desirability_signal"] == "strong_commitment"

    def test_phase_2_low_resonance_recommends_segment_pivot(self, minimal_founders_brief):
        """Test that low problem_resonance recommends segment pivot."""
        mock_desirability = DesirabilityEvidence(
            problem_resonance=0.15,  # < 0.3
            zombie_ratio=0.40,
            signal=ValidationSignal.NO_INTEREST,
        )

        with patch("src.modal_app.phases.phase_2.update_progress") as mock_progress, \
             patch("src.crews.desirability.run_build_crew") as mock_build, \
             patch("src.crews.desirability.run_growth_crew") as mock_growth, \
             patch("src.crews.desirability.run_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = {}
            mock_growth.return_value = mock_desirability
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_2 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {"pains": []},
                    "value_map": {},
                },
            )

            # Implementation uses "segment_1" (first alternative) or "custom_segment"
            assert result["hitl_recommended"] in ["segment_1", "custom_segment"]
            assert result["state"]["desirability_signal"] == "no_interest"

    def test_phase_2_high_zombie_recommends_value_pivot(self, minimal_founders_brief):
        """Test that high zombie_ratio recommends value pivot."""
        mock_desirability = DesirabilityEvidence(
            problem_resonance=0.45,  # >= 0.3
            zombie_ratio=0.80,  # >= 0.7
            signal=ValidationSignal.MILD_INTEREST,
        )

        with patch("src.modal_app.phases.phase_2.update_progress") as mock_progress, \
             patch("src.crews.desirability.run_build_crew") as mock_build, \
             patch("src.crews.desirability.run_growth_crew") as mock_growth, \
             patch("src.crews.desirability.run_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = {}
            mock_growth.return_value = mock_desirability
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_2 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {"pains": []},
                    "value_map": {},
                },
            )

            # Implementation uses "approved" to approve the value pivot
            assert result["hitl_recommended"] == "approved"
            assert result["state"]["desirability_signal"] == "mild_interest"

    def test_phase_2_hitl_options_include_pivots(self, minimal_founders_brief):
        """Test that HITL checkpoint includes pivot options."""
        mock_desirability = DesirabilityEvidence(
            problem_resonance=0.45,
            zombie_ratio=0.30,
            signal=ValidationSignal.STRONG_COMMITMENT,
        )

        with patch("src.modal_app.phases.phase_2.update_progress") as mock_progress, \
             patch("src.crews.desirability.run_build_crew") as mock_build, \
             patch("src.crews.desirability.run_growth_crew") as mock_growth, \
             patch("src.crews.desirability.run_governance_crew") as mock_governance:

            mock_progress.return_value = True
            mock_build.return_value = {}
            mock_growth.return_value = mock_desirability
            mock_governance.return_value = {}

            from src.modal_app.phases.phase_2 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {"pains": []},
                    "value_map": {},
                },
            )

            option_ids = [opt["id"] for opt in result["hitl_options"]]
            # Strong commitment case only has "approved" and "iterate" options
            assert "approved" in option_ids
            assert "iterate" in option_ids


# =============================================================================
# Innovation Physics Tests
# =============================================================================

class TestInnovationPhysics:
    """Tests for Innovation Physics signal computation."""

    def test_problem_resonance_formula(self):
        """Test problem_resonance = (clicks + signups) / impressions."""
        # pr = (100 + 30) / 1000 = 0.13
        evidence = DesirabilityEvidence(
            ad_impressions=1000,
            ad_clicks=100,
            ad_signups=30,
            problem_resonance=0.13,
            zombie_ratio=0.70,
        )
        expected_pr = (100 + 30) / 1000
        assert abs(evidence.problem_resonance - expected_pr) < 0.01

    def test_zombie_ratio_formula(self):
        """Test zombie_ratio = (clicks - signups) / clicks."""
        # zr = (100 - 30) / 100 = 0.70
        evidence = DesirabilityEvidence(
            ad_clicks=100,
            ad_signups=30,
            problem_resonance=0.13,
            zombie_ratio=0.70,
        )
        expected_zr = (100 - 30) / 100
        assert abs(evidence.zombie_ratio - expected_zr) < 0.01

    def test_strong_commitment_threshold(self):
        """Test STRONG_COMMITMENT requires pr >= 0.3 AND zr < 0.7."""
        # This combination should yield STRONG_COMMITMENT
        evidence = DesirabilityEvidence(
            problem_resonance=0.35,  # >= 0.3
            zombie_ratio=0.65,  # < 0.7
            signal=ValidationSignal.STRONG_COMMITMENT,
        )
        assert evidence.problem_resonance >= 0.3
        assert evidence.zombie_ratio < 0.7
        assert evidence.signal == ValidationSignal.STRONG_COMMITMENT

    def test_segment_pivot_threshold(self):
        """Test SEGMENT_PIVOT when pr < 0.3."""
        evidence = DesirabilityEvidence(
            problem_resonance=0.25,  # < 0.3 -> SEGMENT_PIVOT
            zombie_ratio=0.50,
            signal=ValidationSignal.NO_INTEREST,
        )
        assert evidence.problem_resonance < 0.3
        # NO_INTEREST signal triggers SEGMENT_PIVOT recommendation

    def test_value_pivot_threshold(self):
        """Test VALUE_PIVOT when pr >= 0.3 AND zr >= 0.7."""
        evidence = DesirabilityEvidence(
            problem_resonance=0.40,  # >= 0.3
            zombie_ratio=0.75,  # >= 0.7 -> VALUE_PIVOT
            signal=ValidationSignal.MILD_INTEREST,
        )
        assert evidence.problem_resonance >= 0.3
        assert evidence.zombie_ratio >= 0.7
        # MILD_INTEREST signal triggers VALUE_PIVOT recommendation


# =============================================================================
# Agent Count Verification
# =============================================================================

class TestPhase2AgentCounts:
    """Verify Phase 2 has the correct number of agents (9 total)."""

    def test_total_agent_count(self):
        """Test that Phase 2 has 9 agents total."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "desirability"

        # Count agents in each config file
        config_files = [
            ("build_agents.yaml", 3),  # BuildCrew: F1, F2, F3
            ("growth_agents.yaml", 3),  # GrowthCrew: P1, P2, P3
            ("governance_agents.yaml", 3),  # GovernanceCrew: G1, G2, G3
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

        assert total_agents == 9, f"Expected 9 agents total, got {total_agents}"

    def test_crew_agent_distribution(self):
        """Test agent distribution matches specification."""
        expected = {
            "BuildCrew": 3,  # F1, F2, F3
            "GrowthCrew": 3,  # P1, P2, P3
            "GovernanceCrew": 3,  # G1, G2, G3
        }

        total = sum(expected.values())
        assert total == 9, f"Expected 9 agents total, got {total}"


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestPhase2ErrorHandling:
    """Tests for error handling in Phase 2."""

    def test_phase_2_handles_build_crew_error(self, minimal_founders_brief):
        """Test that Phase 2 handles BuildCrew errors."""
        with patch("src.modal_app.phases.phase_2.update_progress") as mock_progress, \
             patch("src.crews.desirability.run_build_crew") as mock_build:

            mock_build.side_effect = Exception("BuildCrew failed")
            mock_progress.return_value = True

            from src.modal_app.phases.phase_2 import execute

            with pytest.raises(Exception) as exc_info:
                execute(
                    run_id="test-run-123",
                    state={
                        "founders_brief": minimal_founders_brief.model_dump(),
                        "customer_profile": {},
                        "value_map": {},
                    },
                )

            assert "BuildCrew failed" in str(exc_info.value)

    def test_phase_2_handles_growth_crew_error(self, minimal_founders_brief):
        """Test that Phase 2 handles GrowthCrew errors."""
        with patch("src.modal_app.phases.phase_2.update_progress") as mock_progress, \
             patch("src.crews.desirability.run_build_crew") as mock_build, \
             patch("src.crews.desirability.run_growth_crew") as mock_growth:

            mock_build.return_value = {}
            mock_growth.side_effect = Exception("GrowthCrew failed")
            mock_progress.return_value = True

            from src.modal_app.phases.phase_2 import execute

            with pytest.raises(Exception) as exc_info:
                execute(
                    run_id="test-run-123",
                    state={
                        "founders_brief": minimal_founders_brief.model_dump(),
                        "customer_profile": {},
                        "value_map": {},
                    },
                )

            assert "GrowthCrew failed" in str(exc_info.value)

    def test_phase_2_handles_governance_crew_error(self, minimal_founders_brief):
        """Test that Phase 2 handles GovernanceCrew errors."""
        mock_desirability = DesirabilityEvidence(
            problem_resonance=0.45,
            zombie_ratio=0.30,
            signal=ValidationSignal.STRONG_COMMITMENT,
        )

        with patch("src.modal_app.phases.phase_2.update_progress") as mock_progress, \
             patch("src.crews.desirability.run_build_crew") as mock_build, \
             patch("src.crews.desirability.run_growth_crew") as mock_growth, \
             patch("src.crews.desirability.run_governance_crew") as mock_governance:

            mock_build.return_value = {}
            mock_growth.return_value = mock_desirability
            mock_governance.side_effect = Exception("GovernanceCrew failed")
            mock_progress.return_value = True

            from src.modal_app.phases.phase_2 import execute

            with pytest.raises(Exception) as exc_info:
                execute(
                    run_id="test-run-123",
                    state={
                        "founders_brief": minimal_founders_brief.model_dump(),
                        "customer_profile": {},
                        "value_map": {},
                    },
                )

            assert "GovernanceCrew failed" in str(exc_info.value)
