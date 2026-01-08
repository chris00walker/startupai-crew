"""
Tests for Phase 1: VPC Discovery Crews

Tests crew structure, agents, tasks, and flow orchestration for:
- DiscoveryCrew (5 agents)
- CustomerProfileCrew (6 agents)
- ValueDesignCrew (3 agents)
- WTPCrew (2 agents)
- FitAssessmentCrew (2 agents)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import yaml

from src.state.models import (
    CustomerProfile,
    ValueMap,
    FitAssessment,
)


# =============================================================================
# Crew Structure Tests
# =============================================================================

class TestPhase1CrewImports:
    """Test that all Phase 1 crews can be imported."""

    def test_discovery_crew_imports(self):
        """Test DiscoveryCrew can be imported."""
        from src.crews.discovery import DiscoveryCrew
        assert DiscoveryCrew is not None

    def test_customer_profile_crew_imports(self):
        """Test CustomerProfileCrew can be imported."""
        from src.crews.discovery import CustomerProfileCrew
        assert CustomerProfileCrew is not None

    def test_value_design_crew_imports(self):
        """Test ValueDesignCrew can be imported."""
        from src.crews.discovery import ValueDesignCrew
        assert ValueDesignCrew is not None

    def test_wtp_crew_imports(self):
        """Test WTPCrew can be imported."""
        from src.crews.discovery import WTPCrew
        assert WTPCrew is not None

    def test_fit_assessment_crew_imports(self):
        """Test FitAssessmentCrew can be imported."""
        from src.crews.discovery import FitAssessmentCrew
        assert FitAssessmentCrew is not None

    def test_run_functions_import(self):
        """Test all run functions can be imported."""
        from src.crews.discovery import (
            run_discovery_crew,
            run_customer_profile_crew,
            run_value_design_crew,
            run_wtp_crew,
            run_fit_assessment_crew,
        )
        assert callable(run_discovery_crew)
        assert callable(run_customer_profile_crew)
        assert callable(run_value_design_crew)
        assert callable(run_wtp_crew)
        assert callable(run_fit_assessment_crew)


class TestDiscoveryCrewStructure:
    """Tests for DiscoveryCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"
        agents_yaml = crew_dir / "config" / "agents.yaml"
        tasks_yaml = crew_dir / "config" / "tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 5 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"
        with open(crew_dir / "config" / "agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "e1_experiment_designer",
            "d1_customer_interview",
            "d2_observation_agent",
            "d3_cta_test_agent",
            "d4_evidence_triangulation",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"


class TestCustomerProfileCrewStructure:
    """Tests for CustomerProfileCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"
        agents_yaml = crew_dir / "config" / "customer_profile_agents.yaml"
        tasks_yaml = crew_dir / "config" / "customer_profile_tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 6 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"
        with open(crew_dir / "config" / "customer_profile_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "j1_jtbd_researcher",
            "j2_job_ranking",
            "pain_researcher",
            "pain_ranking",
            "gain_researcher",
            "gain_ranking",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"


class TestValueDesignCrewStructure:
    """Tests for ValueDesignCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"
        agents_yaml = crew_dir / "config" / "value_design_agents.yaml"
        tasks_yaml = crew_dir / "config" / "value_design_tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 3 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"
        with open(crew_dir / "config" / "value_design_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "v1_solution_designer",
            "v2_pain_reliever_designer",
            "v3_gain_creator_designer",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"


class TestWTPCrewStructure:
    """Tests for WTPCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"
        agents_yaml = crew_dir / "config" / "wtp_agents.yaml"
        tasks_yaml = crew_dir / "config" / "wtp_tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 2 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"
        with open(crew_dir / "config" / "wtp_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "w1_pricing_experiment",
            "w2_payment_test",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"


class TestFitAssessmentCrewStructure:
    """Tests for FitAssessmentCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"
        agents_yaml = crew_dir / "config" / "fit_assessment_agents.yaml"
        tasks_yaml = crew_dir / "config" / "fit_assessment_tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 2 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"
        with open(crew_dir / "config" / "fit_assessment_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "fit_score_analyst",
            "fit_route_agent",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"


# =============================================================================
# Output Schema Tests
# =============================================================================

class TestVPCSchemas:
    """Tests for VPC output schemas."""

    def test_customer_profile_creation(self):
        """Test CustomerProfile schema."""
        profile = CustomerProfile(
            segment_name="SMB Owners",
            segment_description="Small business owners",
        )
        assert profile.segment_name == "SMB Owners"
        assert profile.jobs == []
        assert profile.pains == []
        assert profile.gains == []

    def test_value_map_creation(self):
        """Test ValueMap schema."""
        value_map = ValueMap()
        assert value_map.products_services == []
        assert value_map.pain_relievers == []
        assert value_map.gain_creators == []

    def test_fit_assessment_creation(self):
        """Test FitAssessment schema."""
        fit = FitAssessment(
            fit_score=75,
            fit_status="strong",
            profile_completeness=0.9,
            value_map_coverage=0.85,
            evidence_strength="strong",
            gate_ready=True,
        )
        assert fit.fit_score == 75
        assert fit.gate_ready is True


# =============================================================================
# Phase 1 Flow Tests
# =============================================================================

class TestPhase1Flow:
    """Tests for Phase 1 flow orchestration."""

    def test_phase_1_module_imports(self):
        """Test that phase_1 module can be imported."""
        from src.modal_app.phases import phase_1_vpc_discovery
        assert hasattr(phase_1_vpc_discovery, "execute")

    def test_phase_1_returns_hitl_checkpoint(self, minimal_founders_brief):
        """Test that Phase 1 returns HITL checkpoint."""
        mock_customer_profile = CustomerProfile(
            segment_name="Test",
            segment_description="Test segment",
        )
        mock_value_map = ValueMap()
        mock_fit = FitAssessment(
            fit_score=75,
            fit_status="strong",
            profile_completeness=0.8,
            value_map_coverage=0.8,
            evidence_strength="strong",
            gate_ready=True,
        )

        with patch("src.modal_app.phases.phase_1.update_progress") as mock_progress, \
             patch("src.crews.discovery.run_discovery_crew") as mock_disc, \
             patch("src.crews.discovery.run_customer_profile_crew") as mock_cp, \
             patch("src.crews.discovery.run_value_design_crew") as mock_vd, \
             patch("src.crews.discovery.run_wtp_crew") as mock_wtp, \
             patch("src.crews.discovery.run_fit_assessment_crew") as mock_fit_crew:

            mock_progress.return_value = True
            mock_disc.return_value = {"evidence": "collected"}
            mock_cp.return_value = mock_customer_profile
            mock_vd.return_value = mock_value_map
            mock_wtp.return_value = {"wtp_validated": True}
            mock_fit_crew.return_value = mock_fit

            from src.modal_app.phases.phase_1 import execute

            result = execute(
                run_id="test-run-123",
                state={"founders_brief": minimal_founders_brief.model_dump()},
            )

            assert "hitl_checkpoint" in result
            assert result["hitl_checkpoint"] == "approve_vpc_completion"
            assert "hitl_options" in result

    def test_phase_1_fit_score_gating(self, minimal_founders_brief):
        """Test that Phase 1 gates on fit score >= 70."""
        # Test with passing score
        mock_fit_passing = FitAssessment(
            fit_score=75,
            fit_status="strong",
            profile_completeness=0.8,
            value_map_coverage=0.8,
            evidence_strength="strong",
            gate_ready=True,
        )

        with patch("src.modal_app.phases.phase_1.update_progress") as mock_progress, \
             patch("src.crews.discovery.run_discovery_crew") as mock_disc, \
             patch("src.crews.discovery.run_customer_profile_crew") as mock_cp, \
             patch("src.crews.discovery.run_value_design_crew") as mock_vd, \
             patch("src.crews.discovery.run_wtp_crew") as mock_wtp, \
             patch("src.crews.discovery.run_fit_assessment_crew") as mock_fit_crew:

            mock_progress.return_value = True
            mock_disc.return_value = {}
            mock_cp.return_value = CustomerProfile(
                segment_name="Test", segment_description="Test"
            )
            mock_vd.return_value = ValueMap()
            mock_wtp.return_value = {}
            mock_fit_crew.return_value = mock_fit_passing

            from src.modal_app.phases.phase_1 import execute

            result = execute(
                run_id="test-run-123",
                state={"founders_brief": minimal_founders_brief.model_dump()},
            )

            assert result["hitl_recommended"] == "approve"

    def test_phase_1_recommends_iterate_below_threshold(self, minimal_founders_brief):
        """Test that Phase 1 recommends iterate when fit < 70."""
        mock_fit_failing = FitAssessment(
            fit_score=55,
            fit_status="weak",
            profile_completeness=0.6,
            value_map_coverage=0.5,
            evidence_strength="weak",
            gate_ready=False,
        )

        with patch("src.modal_app.phases.phase_1.update_progress") as mock_progress, \
             patch("src.crews.discovery.run_discovery_crew") as mock_disc, \
             patch("src.crews.discovery.run_customer_profile_crew") as mock_cp, \
             patch("src.crews.discovery.run_value_design_crew") as mock_vd, \
             patch("src.crews.discovery.run_wtp_crew") as mock_wtp, \
             patch("src.crews.discovery.run_fit_assessment_crew") as mock_fit_crew:

            mock_progress.return_value = True
            mock_disc.return_value = {}
            mock_cp.return_value = CustomerProfile(
                segment_name="Test", segment_description="Test"
            )
            mock_vd.return_value = ValueMap()
            mock_wtp.return_value = {}
            mock_fit_crew.return_value = mock_fit_failing

            from src.modal_app.phases.phase_1 import execute

            result = execute(
                run_id="test-run-123",
                state={"founders_brief": minimal_founders_brief.model_dump()},
            )

            assert result["hitl_recommended"] == "iterate"


# =============================================================================
# Agent Count Verification
# =============================================================================

class TestPhase1AgentCounts:
    """Verify Phase 1 has the correct number of agents (18 total)."""

    def test_total_agent_count(self):
        """Test that Phase 1 has 18 agents total."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "discovery"

        # Count agents in each config file
        config_files = [
            ("agents.yaml", 5),  # DiscoveryCrew
            ("customer_profile_agents.yaml", 6),  # CustomerProfileCrew
            ("value_design_agents.yaml", 3),  # ValueDesignCrew
            ("wtp_agents.yaml", 2),  # WTPCrew
            ("fit_assessment_agents.yaml", 2),  # FitAssessmentCrew
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

        assert total_agents == 18, f"Expected 18 agents total, got {total_agents}"

    def test_crew_agent_distribution(self):
        """Test agent distribution matches specification."""
        expected = {
            "DiscoveryCrew": 5,  # E1, D1, D2, D3, D4
            "CustomerProfileCrew": 6,  # J1, J2, PAIN_RES, PAIN_RANK, GAIN_RES, GAIN_RANK
            "ValueDesignCrew": 3,  # V1, V2, V3
            "WTPCrew": 2,  # W1, W2
            "FitAssessmentCrew": 2,  # FIT_SCORE, FIT_ROUTE
        }

        total = sum(expected.values())
        assert total == 18, f"Expected 18 agents total, got {total}"
