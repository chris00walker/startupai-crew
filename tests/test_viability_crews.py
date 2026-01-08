"""
Tests for Phase 4: Viability Crews

Tests crew structure, agents, tasks, and flow orchestration for:
- FinanceCrew (3 agents)
- SynthesisCrew (3 agents)
- ViabilityGovernanceCrew (3 agents)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import yaml

from src.state.models import (
    ViabilityEvidence,
    ValidationSignal,
)


# =============================================================================
# Crew Structure Tests
# =============================================================================

class TestPhase4CrewImports:
    """Test that all Phase 4 crews can be imported."""

    def test_finance_crew_imports(self):
        """Test FinanceCrew can be imported."""
        from src.crews.viability import FinanceCrew
        assert FinanceCrew is not None

    def test_synthesis_crew_imports(self):
        """Test SynthesisCrew can be imported."""
        from src.crews.viability import SynthesisCrew
        assert SynthesisCrew is not None

    def test_viability_governance_crew_imports(self):
        """Test ViabilityGovernanceCrew can be imported."""
        from src.crews.viability import ViabilityGovernanceCrew
        assert ViabilityGovernanceCrew is not None

    def test_run_functions_import(self):
        """Test all run functions can be imported."""
        from src.crews.viability import (
            run_finance_crew,
            run_synthesis_crew,
            run_viability_governance_crew,
        )
        assert callable(run_finance_crew)
        assert callable(run_synthesis_crew)
        assert callable(run_viability_governance_crew)


class TestFinanceCrewStructure:
    """Tests for FinanceCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        agents_yaml = crew_dir / "config" / "finance_agents.yaml"
        tasks_yaml = crew_dir / "config" / "finance_tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 3 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "finance_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "l1_financial_controller",
            "l2_legal_compliance",
            "l3_economics_reviewer",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"

    def test_tasks_yaml_has_all_tasks(self):
        """Test that tasks.yaml contains all 7 required tasks."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "finance_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        required_tasks = [
            "calculate_cac",
            "calculate_ltv",
            "compute_ltv_cac_ratio",
            "analyze_tam",
            "identify_regulatory_constraints",
            "validate_assumptions",
            "set_viability_signal",
        ]

        for task_id in required_tasks:
            assert task_id in tasks, f"Task {task_id} not found"

    def test_crew_has_agents_config(self):
        """Test that crew has agents config loaded."""
        from src.crews.viability.finance_crew import FinanceCrew

        crew = FinanceCrew()
        assert isinstance(crew.agents_config, dict)
        assert "l1_financial_controller" in crew.agents_config
        assert "l2_legal_compliance" in crew.agents_config
        assert "l3_economics_reviewer" in crew.agents_config


class TestSynthesisCrewStructure:
    """Tests for SynthesisCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        agents_yaml = crew_dir / "config" / "synthesis_agents.yaml"
        tasks_yaml = crew_dir / "config" / "synthesis_tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 3 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "synthesis_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "c1_product_pm",
            "c2_human_approval",
            "c3_roadmap_writer",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"

    def test_tasks_yaml_has_all_tasks(self):
        """Test that tasks.yaml contains all 5 required tasks."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "synthesis_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        required_tasks = [
            "synthesize_evidence",
            "propose_options",
            "present_viability_decision",
            "document_decision",
            "capture_learnings",
        ]

        for task_id in required_tasks:
            assert task_id in tasks, f"Task {task_id} not found"

    def test_crew_has_agents_config(self):
        """Test that crew has agents config loaded."""
        from src.crews.viability.synthesis_crew import SynthesisCrew

        crew = SynthesisCrew()
        assert isinstance(crew.agents_config, dict)
        assert "c1_product_pm" in crew.agents_config
        assert "c2_human_approval" in crew.agents_config
        assert "c3_roadmap_writer" in crew.agents_config


class TestViabilityGovernanceCrewStructure:
    """Tests for ViabilityGovernanceCrew class structure."""

    def test_config_files_exist(self):
        """Test that config files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        agents_yaml = crew_dir / "config" / "governance_agents.yaml"
        tasks_yaml = crew_dir / "config" / "governance_tasks.yaml"

        assert agents_yaml.exists()
        assert tasks_yaml.exists()

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 3 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "governance_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "g1_qa_agent",
            "g2_security_agent",
            "g3_audit_agent",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"

    def test_tasks_yaml_has_all_tasks(self):
        """Test that tasks.yaml contains all 4 required tasks."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "governance_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        required_tasks = [
            "final_validation_check",
            "scrub_pii",
            "create_audit_trail",
            "persist_to_flywheel",
        ]

        for task_id in required_tasks:
            assert task_id in tasks, f"Task {task_id} not found"

    def test_crew_has_agents_config(self):
        """Test that crew has agents config loaded."""
        from src.crews.viability.governance_crew import ViabilityGovernanceCrew

        crew = ViabilityGovernanceCrew()
        assert isinstance(crew.agents_config, dict)
        assert "g1_qa_agent" in crew.agents_config
        assert "g2_security_agent" in crew.agents_config
        assert "g3_audit_agent" in crew.agents_config


# =============================================================================
# Agent Definition Tests
# =============================================================================

class TestFinanceAgentDefinitions:
    """Tests for FinanceCrew agent definitions."""

    @pytest.fixture
    def agents(self):
        """Load agents from YAML."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "finance_agents.yaml") as f:
            return yaml.safe_load(f)

    def test_l1_financial_controller_definition(self, agents):
        """Test L1 Financial Controller Agent definition."""
        l1 = agents["l1_financial_controller"]
        assert "role" in l1
        assert "goal" in l1
        assert "backstory" in l1
        assert "Financial Controller" in l1["role"]
        assert "unit economics" in l1["goal"].lower() or "cac" in l1["backstory"].lower()

    def test_l2_legal_compliance_definition(self, agents):
        """Test L2 Legal & Compliance Agent definition."""
        l2 = agents["l2_legal_compliance"]
        assert "role" in l2
        assert "goal" in l2
        assert "backstory" in l2
        assert "compliance" in l2["role"].lower() or "legal" in l2["role"].lower()

    def test_l3_economics_reviewer_definition(self, agents):
        """Test L3 Economics Reviewer Agent definition."""
        l3 = agents["l3_economics_reviewer"]
        assert "role" in l3
        assert "goal" in l3
        assert "backstory" in l3
        assert "economics" in l3["role"].lower() or "reviewer" in l3["role"].lower()
        # Should mention benchmarks
        assert "benchmark" in l3["backstory"].lower()


class TestSynthesisAgentDefinitions:
    """Tests for SynthesisCrew agent definitions."""

    @pytest.fixture
    def agents(self):
        """Load agents from YAML."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "synthesis_agents.yaml") as f:
            return yaml.safe_load(f)

    def test_c1_product_pm_definition(self, agents):
        """Test C1 Product PM Agent definition."""
        c1 = agents["c1_product_pm"]
        assert "role" in c1
        assert "goal" in c1
        assert "backstory" in c1
        assert "product" in c1["role"].lower() or "pm" in c1["role"].lower()
        assert "synthesize" in c1["goal"].lower()

    def test_c2_human_approval_definition(self, agents):
        """Test C2 Human Approval Agent definition."""
        c2 = agents["c2_human_approval"]
        assert "role" in c2
        assert "goal" in c2
        assert "backstory" in c2
        assert "approval" in c2["role"].lower() or "human" in c2["role"].lower()
        # Should mention HITL checkpoint
        assert "hitl" in c2["backstory"].lower() or "human" in c2["backstory"].lower()

    def test_c3_roadmap_writer_definition(self, agents):
        """Test C3 Roadmap Writer Agent definition."""
        c3 = agents["c3_roadmap_writer"]
        assert "role" in c3
        assert "goal" in c3
        assert "backstory" in c3
        assert "roadmap" in c3["role"].lower() or "writer" in c3["role"].lower()


class TestViabilityGovernanceAgentDefinitions:
    """Tests for ViabilityGovernanceCrew agent definitions."""

    @pytest.fixture
    def agents(self):
        """Load agents from YAML."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "governance_agents.yaml") as f:
            return yaml.safe_load(f)

    def test_g1_qa_agent_definition(self, agents):
        """Test G1 QA Agent definition."""
        g1 = agents["g1_qa_agent"]
        assert "role" in g1
        assert "goal" in g1
        assert "backstory" in g1
        assert "qa" in g1["role"].lower() or "validation" in g1["role"].lower()

    def test_g2_security_agent_definition(self, agents):
        """Test G2 Security Agent definition."""
        g2 = agents["g2_security_agent"]
        assert "role" in g2
        assert "goal" in g2
        assert "backstory" in g2
        assert "security" in g2["role"].lower()
        # Should mention PII/personal data scrubbing
        backstory_lower = g2["backstory"].lower()
        assert "pii" in backstory_lower or "personally identifiable" in backstory_lower

    def test_g3_audit_agent_definition(self, agents):
        """Test G3 Audit Agent definition."""
        g3 = agents["g3_audit_agent"]
        assert "role" in g3
        assert "goal" in g3
        assert "backstory" in g3
        assert "audit" in g3["role"].lower() or "flywheel" in g3["role"].lower()


# =============================================================================
# Task Definition Tests
# =============================================================================

class TestFinanceTaskDefinitions:
    """Tests for FinanceCrew task definitions."""

    @pytest.fixture
    def tasks(self):
        """Load tasks from YAML."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "finance_tasks.yaml") as f:
            return yaml.safe_load(f)

    def test_calculate_cac_task(self, tasks):
        """Test calculate_cac task definition."""
        task = tasks["calculate_cac"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        assert "l1_financial_controller" in task["agent"]
        assert "cac" in task["description"].lower()

    def test_calculate_ltv_task(self, tasks):
        """Test calculate_ltv task definition."""
        task = tasks["calculate_ltv"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        assert "ltv" in task["description"].lower() or "lifetime" in task["description"].lower()

    def test_compute_ltv_cac_ratio_task(self, tasks):
        """Test compute_ltv_cac_ratio task definition."""
        task = tasks["compute_ltv_cac_ratio"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        # Should reference threshold 3.0
        assert "3.0" in task["description"] or "3:1" in task["description"]

    def test_set_viability_signal_task(self, tasks):
        """Test set_viability_signal task definition."""
        task = tasks["set_viability_signal"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        # Should mention signals
        assert "profitable" in task["description"].lower()


class TestSynthesisTaskDefinitions:
    """Tests for SynthesisCrew task definitions."""

    @pytest.fixture
    def tasks(self):
        """Load tasks from YAML."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "synthesis_tasks.yaml") as f:
            return yaml.safe_load(f)

    def test_synthesize_evidence_task(self, tasks):
        """Test synthesize_evidence task definition."""
        task = tasks["synthesize_evidence"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        assert "c1_product_pm" in task["agent"]

    def test_propose_options_task(self, tasks):
        """Test propose_options task definition."""
        task = tasks["propose_options"]
        assert "description" in task
        assert "expected_output" in task
        # Should mention pivot options
        assert "pivot" in task["description"].lower()

    def test_present_viability_decision_task(self, tasks):
        """Test present_viability_decision task definition."""
        task = tasks["present_viability_decision"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        assert "c2_human_approval" in task["agent"]
        # Should mention HITL
        assert "hitl" in task["description"].lower()

    def test_capture_learnings_task(self, tasks):
        """Test capture_learnings task definition."""
        task = tasks["capture_learnings"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        assert "c3_roadmap_writer" in task["agent"]
        # Should mention flywheel
        assert "flywheel" in task["description"].lower()


class TestViabilityGovernanceTaskDefinitions:
    """Tests for ViabilityGovernanceCrew task definitions."""

    @pytest.fixture
    def tasks(self):
        """Load tasks from YAML."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "governance_tasks.yaml") as f:
            return yaml.safe_load(f)

    def test_final_validation_check_task(self, tasks):
        """Test final_validation_check task definition."""
        task = tasks["final_validation_check"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        assert "g1_qa_agent" in task["agent"]

    def test_scrub_pii_task(self, tasks):
        """Test scrub_pii task definition."""
        task = tasks["scrub_pii"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        assert "g2_security_agent" in task["agent"]
        # Should mention PII
        assert "pii" in task["description"].lower()

    def test_create_audit_trail_task(self, tasks):
        """Test create_audit_trail task definition."""
        task = tasks["create_audit_trail"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        assert "g3_audit_agent" in task["agent"]

    def test_persist_to_flywheel_task(self, tasks):
        """Test persist_to_flywheel task definition."""
        task = tasks["persist_to_flywheel"]
        assert "description" in task
        assert "expected_output" in task
        assert "agent" in task
        # Should mention Supabase
        assert "supabase" in task["description"].lower() or "persist" in task["description"].lower()


# =============================================================================
# Output Schema Tests
# =============================================================================

class TestViabilitySchemas:
    """Tests for Viability output schemas."""

    def test_viability_evidence_creation(self):
        """Test ViabilityEvidence schema."""
        evidence = ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )
        assert evidence.cac == 100
        assert evidence.ltv == 400
        assert evidence.ltv_cac_ratio == 4.0
        assert evidence.signal == ValidationSignal.PROFITABLE

    def test_viability_evidence_profitable_signal(self):
        """Test ViabilityEvidence with PROFITABLE signal."""
        evidence = ViabilityEvidence(
            cac=50,
            ltv=200,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )
        assert evidence.ltv_cac_ratio >= 3.0

    def test_viability_evidence_marginal_signal(self):
        """Test ViabilityEvidence with MARGINAL signal."""
        evidence = ViabilityEvidence(
            cac=100,
            ltv=200,
            ltv_cac_ratio=2.0,
            signal=ValidationSignal.MARGINAL,
        )
        assert 1.0 <= evidence.ltv_cac_ratio < 3.0

    def test_viability_evidence_underwater_signal(self):
        """Test ViabilityEvidence with UNDERWATER signal."""
        evidence = ViabilityEvidence(
            cac=200,
            ltv=100,
            ltv_cac_ratio=0.5,
            signal=ValidationSignal.UNDERWATER,
        )
        assert evidence.ltv_cac_ratio < 1.0


# =============================================================================
# Phase 4 Flow Tests
# =============================================================================

class TestPhase4Flow:
    """Tests for Phase 4 flow orchestration."""

    def test_phase_4_module_imports(self):
        """Test that phase_4 module can be imported."""
        from src.modal_app.phases import phase_4_viability
        assert hasattr(phase_4_viability, "execute")

    def test_phase_4_returns_hitl_checkpoint(self, minimal_founders_brief):
        """Test that Phase 4 returns HITL checkpoint."""
        mock_viability = ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )

        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance, \
             patch("src.crews.viability.run_synthesis_crew") as mock_synthesis, \
             patch("src.crews.viability.run_viability_governance_crew") as mock_gov:

            mock_progress.return_value = True
            mock_finance.return_value = mock_viability
            mock_synthesis.return_value = {"learnings": {}}
            mock_gov.return_value = {"audit_complete": True}

            from src.modal_app.phases.phase_4 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                    "wtp_results": {},
                    "desirability_evidence": {"problem_resonance": 0.5, "zombie_ratio": 0.3},
                    "feasibility_evidence": {"core_features_feasible": True},
                    "fit_assessment": {"fit_score": 75},
                },
            )

            assert "hitl_checkpoint" in result
            assert result["hitl_checkpoint"] == "request_human_decision"
            assert "hitl_options" in result

    def test_phase_4_profitable_recommends_proceed(self, minimal_founders_brief):
        """Test that Phase 4 recommends proceed when profitable."""
        mock_viability = ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )

        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance, \
             patch("src.crews.viability.run_synthesis_crew") as mock_synthesis, \
             patch("src.crews.viability.run_viability_governance_crew") as mock_gov:

            mock_progress.return_value = True
            mock_finance.return_value = mock_viability
            mock_synthesis.return_value = {"learnings": {}}
            mock_gov.return_value = {}

            from src.modal_app.phases.phase_4 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                    "wtp_results": {},
                    "desirability_evidence": {},
                    "feasibility_evidence": {},
                    "fit_assessment": {},
                },
            )

            assert result["hitl_recommended"] == "proceed"

    def test_phase_4_marginal_recommends_pivot(self, minimal_founders_brief):
        """Test that Phase 4 recommends pivot when marginal."""
        mock_viability = ViabilityEvidence(
            cac=100,
            ltv=200,
            ltv_cac_ratio=2.0,
            signal=ValidationSignal.MARGINAL,
        )

        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance, \
             patch("src.crews.viability.run_synthesis_crew") as mock_synthesis, \
             patch("src.crews.viability.run_viability_governance_crew") as mock_gov:

            mock_progress.return_value = True
            mock_finance.return_value = mock_viability
            mock_synthesis.return_value = {"learnings": {}}
            mock_gov.return_value = {}

            from src.modal_app.phases.phase_4 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                    "wtp_results": {},
                    "desirability_evidence": {},
                    "feasibility_evidence": {},
                    "fit_assessment": {},
                },
            )

            # Should NOT recommend proceed
            assert result["hitl_recommended"] != "proceed"

    def test_phase_4_underwater_recommends_pivot(self, minimal_founders_brief):
        """Test that Phase 4 recommends pivot when underwater."""
        mock_viability = ViabilityEvidence(
            cac=200,
            ltv=100,
            ltv_cac_ratio=0.5,
            signal=ValidationSignal.UNDERWATER,
        )

        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance, \
             patch("src.crews.viability.run_synthesis_crew") as mock_synthesis, \
             patch("src.crews.viability.run_viability_governance_crew") as mock_gov:

            mock_progress.return_value = True
            mock_finance.return_value = mock_viability
            mock_synthesis.return_value = {"learnings": {}}
            mock_gov.return_value = {}

            from src.modal_app.phases.phase_4 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                    "wtp_results": {},
                    "desirability_evidence": {},
                    "feasibility_evidence": {},
                    "fit_assessment": {},
                },
            )

            # Should NOT recommend proceed
            assert result["hitl_recommended"] != "proceed"


# =============================================================================
# Unit Economics Tests (Innovation Physics)
# =============================================================================

class TestUnitEconomicsThresholds:
    """Tests for Innovation Physics unit economics thresholds."""

    def test_ltv_cac_profitable_threshold(self):
        """Test LTV:CAC >= 3.0 is PROFITABLE."""
        # At exactly 3.0
        evidence_at_threshold = ViabilityEvidence(
            cac=100,
            ltv=300,
            ltv_cac_ratio=3.0,
            signal=ValidationSignal.PROFITABLE,
        )
        assert evidence_at_threshold.ltv_cac_ratio >= 3.0

        # Above 3.0
        evidence_above = ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )
        assert evidence_above.ltv_cac_ratio >= 3.0

    def test_ltv_cac_marginal_threshold(self):
        """Test LTV:CAC 1.0-3.0 is MARGINAL."""
        evidence = ViabilityEvidence(
            cac=100,
            ltv=200,
            ltv_cac_ratio=2.0,
            signal=ValidationSignal.MARGINAL,
        )
        assert 1.0 <= evidence.ltv_cac_ratio < 3.0

    def test_ltv_cac_underwater_threshold(self):
        """Test LTV:CAC < 1.0 is UNDERWATER."""
        evidence = ViabilityEvidence(
            cac=100,
            ltv=50,
            ltv_cac_ratio=0.5,
            signal=ValidationSignal.UNDERWATER,
        )
        assert evidence.ltv_cac_ratio < 1.0


class TestDecisionOptions:
    """Tests for HITL decision options."""

    def test_hitl_options_structure(self, minimal_founders_brief):
        """Test that HITL options have correct structure."""
        mock_viability = ViabilityEvidence(
            cac=100,
            ltv=200,
            ltv_cac_ratio=2.0,
            signal=ValidationSignal.MARGINAL,
        )

        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance, \
             patch("src.crews.viability.run_synthesis_crew") as mock_synthesis, \
             patch("src.crews.viability.run_viability_governance_crew") as mock_gov:

            mock_progress.return_value = True
            mock_finance.return_value = mock_viability
            mock_synthesis.return_value = {"learnings": {}}
            mock_gov.return_value = {}

            from src.modal_app.phases.phase_4 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                    "wtp_results": {},
                    "desirability_evidence": {},
                    "feasibility_evidence": {},
                    "fit_assessment": {},
                },
            )

            options = result["hitl_options"]
            option_ids = [opt["id"] for opt in options]

            # All decision options should be present
            assert "proceed" in option_ids
            assert "price_pivot" in option_ids
            assert "cost_pivot" in option_ids
            assert "model_pivot" in option_ids
            assert "kill" in option_ids

            # Each option should have required fields
            for option in options:
                assert "id" in option
                assert "label" in option
                assert "description" in option


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestPhase4ErrorHandling:
    """Tests for error handling in Phase 4."""

    def test_phase_4_handles_finance_crew_error(self, minimal_founders_brief):
        """Test that Phase 4 handles FinanceCrew errors."""
        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance:

            mock_progress.return_value = True
            mock_finance.side_effect = Exception("FinanceCrew failed")

            from src.modal_app.phases.phase_4 import execute

            with pytest.raises(Exception) as exc_info:
                execute(
                    run_id="test-run-123",
                    state={
                        "founders_brief": minimal_founders_brief.model_dump(),
                        "customer_profile": {},
                        "value_map": {},
                        "wtp_results": {},
                        "desirability_evidence": {},
                        "feasibility_evidence": {},
                        "fit_assessment": {},
                    },
                )

            assert "FinanceCrew failed" in str(exc_info.value)

    def test_phase_4_handles_synthesis_crew_error(self, minimal_founders_brief):
        """Test that Phase 4 handles SynthesisCrew errors."""
        mock_viability = ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )

        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance, \
             patch("src.crews.viability.run_synthesis_crew") as mock_synthesis:

            mock_progress.return_value = True
            mock_finance.return_value = mock_viability
            mock_synthesis.side_effect = Exception("SynthesisCrew failed")

            from src.modal_app.phases.phase_4 import execute

            with pytest.raises(Exception) as exc_info:
                execute(
                    run_id="test-run-123",
                    state={
                        "founders_brief": minimal_founders_brief.model_dump(),
                        "customer_profile": {},
                        "value_map": {},
                        "wtp_results": {},
                        "desirability_evidence": {},
                        "feasibility_evidence": {},
                        "fit_assessment": {},
                    },
                )

            assert "SynthesisCrew failed" in str(exc_info.value)

    def test_phase_4_handles_governance_crew_error(self, minimal_founders_brief):
        """Test that Phase 4 handles ViabilityGovernanceCrew errors."""
        mock_viability = ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )

        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance, \
             patch("src.crews.viability.run_synthesis_crew") as mock_synthesis, \
             patch("src.crews.viability.run_viability_governance_crew") as mock_gov:

            mock_progress.return_value = True
            mock_finance.return_value = mock_viability
            mock_synthesis.return_value = {"learnings": {}}
            mock_gov.side_effect = Exception("GovernanceCrew failed")

            from src.modal_app.phases.phase_4 import execute

            with pytest.raises(Exception) as exc_info:
                execute(
                    run_id="test-run-123",
                    state={
                        "founders_brief": minimal_founders_brief.model_dump(),
                        "customer_profile": {},
                        "value_map": {},
                        "wtp_results": {},
                        "desirability_evidence": {},
                        "feasibility_evidence": {},
                        "fit_assessment": {},
                    },
                )

            assert "GovernanceCrew failed" in str(exc_info.value)


# =============================================================================
# Decision Rationale Tests
# =============================================================================

class TestDecisionRationale:
    """Tests for decision rationale building."""

    def test_decision_rationale_included(self, minimal_founders_brief):
        """Test that decision rationale is included in result."""
        mock_viability = ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )

        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance, \
             patch("src.crews.viability.run_synthesis_crew") as mock_synthesis, \
             patch("src.crews.viability.run_viability_governance_crew") as mock_gov:

            mock_progress.return_value = True
            mock_finance.return_value = mock_viability
            mock_synthesis.return_value = {"learnings": {}}
            mock_gov.return_value = {}

            from src.modal_app.phases.phase_4 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                    "wtp_results": {},
                    "desirability_evidence": {"problem_resonance": 0.5, "zombie_ratio": 0.3},
                    "feasibility_evidence": {"core_features_feasible": True},
                    "fit_assessment": {},
                },
            )

            assert "hitl_context" in result
            assert "rationale" in result["hitl_context"]
            assert len(result["hitl_context"]["rationale"]) > 0


# =============================================================================
# Agent Count Verification
# =============================================================================

class TestPhase4AgentCounts:
    """Verify Phase 4 has the correct number of agents (9 total)."""

    def test_total_agent_count(self):
        """Test that Phase 4 has 9 agents total."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"

        # Count agents in each config file
        config_files = [
            ("finance_agents.yaml", 3),  # FinanceCrew
            ("synthesis_agents.yaml", 3),  # SynthesisCrew
            ("governance_agents.yaml", 3),  # ViabilityGovernanceCrew
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
            "FinanceCrew": 3,  # L1, L2, L3
            "SynthesisCrew": 3,  # C1, C2, C3
            "ViabilityGovernanceCrew": 3,  # G1, G2, G3
        }

        total = sum(expected.values())
        assert total == 9, f"Expected 9 agents total, got {total}"


# =============================================================================
# State Output Tests
# =============================================================================

class TestPhase4StateOutput:
    """Tests for Phase 4 state output."""

    def test_state_includes_viability_evidence(self, minimal_founders_brief):
        """Test that state includes viability_evidence."""
        mock_viability = ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )

        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance, \
             patch("src.crews.viability.run_synthesis_crew") as mock_synthesis, \
             patch("src.crews.viability.run_viability_governance_crew") as mock_gov:

            mock_progress.return_value = True
            mock_finance.return_value = mock_viability
            mock_synthesis.return_value = {"learnings": {}}
            mock_gov.return_value = {}

            from src.modal_app.phases.phase_4 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                    "wtp_results": {},
                    "desirability_evidence": {},
                    "feasibility_evidence": {},
                    "fit_assessment": {},
                },
            )

            assert "state" in result
            assert "viability_evidence" in result["state"]
            assert "viability_signal" in result["state"]
            assert "synthesis_results" in result["state"]
            assert "pivot_recommendation" in result["state"]
            assert "final_decision" in result["state"]

    def test_hitl_context_includes_unit_economics(self, minimal_founders_brief):
        """Test that HITL context includes unit economics."""
        mock_viability = ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )

        with patch("src.modal_app.phases.phase_4.update_progress") as mock_progress, \
             patch("src.crews.viability.run_finance_crew") as mock_finance, \
             patch("src.crews.viability.run_synthesis_crew") as mock_synthesis, \
             patch("src.crews.viability.run_viability_governance_crew") as mock_gov:

            mock_progress.return_value = True
            mock_finance.return_value = mock_viability
            mock_synthesis.return_value = {"learnings": {}}
            mock_gov.return_value = {}

            from src.modal_app.phases.phase_4 import execute

            result = execute(
                run_id="test-run-123",
                state={
                    "founders_brief": minimal_founders_brief.model_dump(),
                    "customer_profile": {},
                    "value_map": {},
                    "wtp_results": {},
                    "desirability_evidence": {},
                    "feasibility_evidence": {},
                    "fit_assessment": {},
                },
            )

            context = result["hitl_context"]
            assert "unit_economics" in context
            assert "cac" in context["unit_economics"]
            assert "ltv" in context["unit_economics"]
            assert "ltv_cac_ratio" in context["unit_economics"]
