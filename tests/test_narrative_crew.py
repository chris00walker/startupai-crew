"""
Tests for NarrativeSynthesisCrew (Phase 4: Pitch Narrative Generation)

Tests crew structure, Pydantic schemas, YAML configs, and wrapper function.

@story US-NL01
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import yaml


# =============================================================================
# Crew Structure Tests
# =============================================================================


class TestNarrativeCrewImports:
    """Test that NarrativeSynthesisCrew can be imported."""

    def test_narrative_crew_imports(self):
        """Test NarrativeSynthesisCrew can be imported."""
        from src.crews.viability import NarrativeSynthesisCrew

        assert NarrativeSynthesisCrew is not None

    def test_run_function_imports(self):
        """Test run_narrative_synthesis_crew can be imported."""
        from src.crews.viability import run_narrative_synthesis_crew

        assert callable(run_narrative_synthesis_crew)

    def test_narrative_crew_in_all(self):
        """Test NarrativeSynthesisCrew is in __all__."""
        from src.crews.viability import __all__

        assert "NarrativeSynthesisCrew" in __all__
        assert "run_narrative_synthesis_crew" in __all__


class TestNarrativeCrewStructure:
    """Tests for NarrativeSynthesisCrew class structure."""

    def test_config_files_exist(self):
        """Test that config YAML files exist."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        agents_yaml = crew_dir / "config" / "narrative_agents.yaml"
        tasks_yaml = crew_dir / "config" / "narrative_tasks.yaml"

        assert agents_yaml.exists(), "narrative_agents.yaml not found"
        assert tasks_yaml.exists(), "narrative_tasks.yaml not found"

    def test_agents_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 3 required agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_agents.yaml") as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "n1_narrative_architect",
            "n2_evidence_mapper",
            "n3_claim_guardian",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found"

    def test_agents_yaml_has_required_fields(self):
        """Test each agent has role, goal, backstory."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_agents.yaml") as f:
            agents = yaml.safe_load(f)

        for agent_id, config in agents.items():
            if isinstance(config, dict):
                assert "role" in config, f"{agent_id} missing role"
                assert "goal" in config, f"{agent_id} missing goal"
                assert "backstory" in config, f"{agent_id} missing backstory"

    def test_tasks_yaml_has_all_tasks(self):
        """Test that tasks.yaml contains all 4 required tasks."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        required_tasks = [
            "map_evidence_to_slides",
            "compose_narrative",
            "validate_claims",
            "finalize_narrative",
        ]

        for task_id in required_tasks:
            assert task_id in tasks, f"Task {task_id} not found"

    def test_tasks_yaml_has_required_fields(self):
        """Test each task has description, expected_output, agent."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        for task_id, config in tasks.items():
            if isinstance(config, dict):
                assert "description" in config, f"{task_id} missing description"
                assert "expected_output" in config, f"{task_id} missing expected_output"
                assert "agent" in config, f"{task_id} missing agent"

    def test_task_context_dependencies(self):
        """Test task context references are valid."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        task_ids = set(tasks.keys())

        for task_id, config in tasks.items():
            if isinstance(config, dict) and "context" in config:
                for dep in config["context"]:
                    assert dep in task_ids, (
                        f"Task {task_id} references unknown context '{dep}'"
                    )

    def test_task_agent_references_valid(self):
        """Test task agent references match defined agents."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"

        with open(crew_dir / "config" / "narrative_agents.yaml") as f:
            agents = yaml.safe_load(f)

        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        agent_ids = set(agents.keys())

        for task_id, config in tasks.items():
            if isinstance(config, dict) and "agent" in config:
                assert config["agent"] in agent_ids, (
                    f"Task {task_id} references unknown agent '{config['agent']}'"
                )


# =============================================================================
# Pydantic Schema Tests
# =============================================================================


class TestPitchNarrativeContentSchema:
    """Tests for PitchNarrativeContent Pydantic schema."""

    def test_schema_imports(self):
        """Test PitchNarrativeContent can be imported."""
        from src.shared.schemas.narrative import PitchNarrativeContent

        assert PitchNarrativeContent is not None

    def test_schema_has_all_sections(self):
        """Test schema has all required sections."""
        from src.shared.schemas.narrative import PitchNarrativeContent

        fields = PitchNarrativeContent.model_fields
        required_sections = [
            "version",
            "cover",
            "overview",
            "opportunity",
            "problem",
            "solution",
            "traction",
            "customer",
            "competition",
            "business_model",
            "team",
            "use_of_funds",
            "metadata",
        ]

        for section in required_sections:
            assert section in fields, f"Missing section: {section}"

    def test_evidence_category_enum(self):
        """Test EvidenceCategory enum values match TypeScript."""
        from src.shared.schemas.narrative import EvidenceCategory

        assert EvidenceCategory.DO_DIRECT == "DO-direct"
        assert EvidenceCategory.DO_INDIRECT == "DO-indirect"
        assert EvidenceCategory.SAY == "SAY"

    def test_market_size_constraints(self):
        """Test MarketSize model has proper constraints."""
        from src.shared.schemas.narrative import MarketSize

        # Valid construction
        ms = MarketSize(
            value=1000000.0,
            unit="USD",
            timeframe="annual",
            source="Research firm",
            confidence="estimated",
        )
        assert ms.value == 1000000.0

    def test_evidence_item_weight_bounds(self):
        """Test EvidenceItem weight is constrained 0-1."""
        from src.shared.schemas.narrative import EvidenceItem
        from pydantic import ValidationError

        # Valid weight
        item = EvidenceItem(
            type="DO-direct",
            description="User signed up",
            source="Landing page",
            weight=0.8,
        )
        assert item.weight == 0.8

        # Invalid weight (too high)
        with pytest.raises(ValidationError):
            EvidenceItem(
                type="DO-direct",
                description="Test",
                source="Test",
                weight=1.5,
            )

    def test_cover_section_fields(self):
        """Test CoverSection has all required fields."""
        from src.shared.schemas.narrative import CoverSection, ContactInfo

        contact = ContactInfo(
            founder_name="Jane Doe",
            email="jane@example.com",
        )
        cover = CoverSection(
            venture_name="TestCo",
            tagline="We test things",
            document_type="Pitch Deck",
            presentation_date="2026-02-05",
            contact=contact,
        )
        assert cover.venture_name == "TestCo"
        assert cover.contact.founder_name == "Jane Doe"

    def test_traction_section_evidence_arrays(self):
        """Test TractionSection has DO/SAY evidence arrays."""
        from src.shared.schemas.narrative import TractionSection

        fields = TractionSection.model_fields
        assert "do_direct" in fields
        assert "do_indirect" in fields
        assert "say_evidence" in fields
        assert "evidence_summary" in fields
        assert "display_config" in fields

    def test_narrative_metadata_fields(self):
        """Test NarrativeMetadata has required fields."""
        from src.shared.schemas.narrative import NarrativeMetadata

        fields = NarrativeMetadata.model_fields
        assert "methodology" in fields
        assert "evidence_strength" in fields
        assert "overall_fit_score" in fields
        assert "validation_stage" in fields
        assert "pivot_count" in fields
        assert "evidence_gaps" in fields


class TestNarrativeSynthesisCrewOutputSchema:
    """Tests for NarrativeSynthesisCrewOutput schema."""

    def test_output_schema_imports(self):
        """Test NarrativeSynthesisCrewOutput can be imported."""
        from src.shared.schemas import NarrativeSynthesisCrewOutput

        assert NarrativeSynthesisCrewOutput is not None

    def test_output_extends_crew_output(self):
        """Test it extends CrewOutput base class."""
        from src.shared.schemas import NarrativeSynthesisCrewOutput, CrewOutput

        assert issubclass(NarrativeSynthesisCrewOutput, CrewOutput)

    def test_output_has_narrative_fields(self):
        """Test output has pitch_narrative_content and alignment fields."""
        from src.shared.schemas import NarrativeSynthesisCrewOutput

        fields = NarrativeSynthesisCrewOutput.model_fields
        assert "pitch_narrative_content" in fields
        assert "alignment_status" in fields
        assert "alignment_issues" in fields
        assert "evidence_gaps" in fields
        assert "evidence_sources_used" in fields

    def test_output_defaults(self):
        """Test output has correct defaults."""
        from src.shared.schemas import NarrativeSynthesisCrewOutput

        output = NarrativeSynthesisCrewOutput(
            pitch_narrative_content={"version": "1.0"},
        )
        assert output.crew_name == "NarrativeSynthesisCrew"
        assert output.phase == 4
        assert output.alignment_status == "verified"
        assert output.alignment_issues == []
        assert output.evidence_gaps == {}
        assert output.success is True


# =============================================================================
# YAML Template Variable Tests
# =============================================================================


class TestNarrativeYAMLTemplateVariables:
    """Test that YAML template variables match wrapper function inputs."""

    def test_map_evidence_input_variables(self):
        """Test map_evidence_to_slides uses expected input variables."""
        import re

        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        description = tasks["map_evidence_to_slides"]["description"]

        # Extract {variable} patterns
        vars_found = set(re.findall(r"\{([a-z_][a-z0-9_]*)\}", description))

        # These should match the inputs passed to the crew
        expected_inputs = {
            "founders_brief",
            "customer_profile",
            "value_map",
            "desirability_evidence",
            "feasibility_evidence",
            "viability_evidence",
            "fit_assessment",
            "competitor_map",
            "experiment_results",
            "founder_profile",
        }

        for var in expected_inputs:
            assert var in vars_found, (
                f"Expected input variable '{var}' not found in "
                f"map_evidence_to_slides description"
            )

    def test_compose_narrative_context_variables(self):
        """Test compose_narrative references context from previous task."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        # compose_narrative should depend on map_evidence_to_slides
        context = tasks["compose_narrative"].get("context", [])
        assert "map_evidence_to_slides" in context

    def test_validate_claims_context_variables(self):
        """Test validate_claims references correct context."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        context = tasks["validate_claims"].get("context", [])
        assert "compose_narrative" in context
        assert "map_evidence_to_slides" in context

    def test_finalize_narrative_context_variables(self):
        """Test finalize_narrative references correct context."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        context = tasks["finalize_narrative"].get("context", [])
        assert "compose_narrative" in context
        assert "validate_claims" in context


# =============================================================================
# Task Dependency Chain Tests
# =============================================================================


class TestNarrativeTaskDependencyChain:
    """Test the 4-task dependency chain is correct."""

    def test_first_task_has_no_context(self):
        """map_evidence_to_slides should have no context (first task)."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        context = tasks["map_evidence_to_slides"].get("context")
        assert context is None or context == [], (
            "First task should have no context dependencies"
        )

    def test_dependency_chain_is_dag(self):
        """Test that task dependencies form a valid DAG (no cycles)."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        # Build adjacency list
        deps = {}
        for task_id, config in tasks.items():
            if isinstance(config, dict):
                deps[task_id] = config.get("context", []) or []

        # Topological sort should succeed (no cycles)
        visited = set()
        in_progress = set()

        def has_cycle(node):
            if node in in_progress:
                return True
            if node in visited:
                return False
            in_progress.add(node)
            for dep in deps.get(node, []):
                if has_cycle(dep):
                    return True
            in_progress.remove(node)
            visited.add(node)
            return False

        for task_id in deps:
            assert not has_cycle(task_id), f"Cycle detected involving {task_id}"

    def test_last_task_agent_is_architect(self):
        """finalize_narrative should use the narrative architect agent."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        assert tasks["finalize_narrative"]["agent"] == "n1_narrative_architect"

    def test_guardian_validates_before_finalize(self):
        """validate_claims should run before finalize_narrative."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "viability"
        with open(crew_dir / "config" / "narrative_tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        finalize_context = tasks["finalize_narrative"].get("context", [])
        assert "validate_claims" in finalize_context


# =============================================================================
# Crew Agent Configuration Tests
# =============================================================================


class TestNarrativeAgentConfigurations:
    """Test agent LLM and behavior configurations."""

    def test_guardian_uses_low_temperature(self):
        """N3 claim guardian should use low temperature for strict validation."""
        from src.crews.viability.narrative_crew import NarrativeSynthesisCrew

        crew = NarrativeSynthesisCrew()
        guardian = crew.n3_claim_guardian()
        assert guardian.llm.temperature <= 0.2

    def test_architect_uses_higher_temperature(self):
        """N1 narrative architect should use higher temperature for creativity."""
        from src.crews.viability.narrative_crew import NarrativeSynthesisCrew

        crew = NarrativeSynthesisCrew()
        architect = crew.n1_narrative_architect()
        assert architect.llm.temperature >= 0.5

    def test_evidence_mapper_uses_low_temperature(self):
        """N2 evidence mapper should use low temperature for precision."""
        from src.crews.viability.narrative_crew import NarrativeSynthesisCrew

        crew = NarrativeSynthesisCrew()
        mapper = crew.n2_evidence_mapper()
        assert mapper.llm.temperature <= 0.5

    def test_no_agents_allow_delegation(self):
        """No agents should allow delegation (isolated specialist pattern)."""
        from src.crews.viability.narrative_crew import NarrativeSynthesisCrew

        crew = NarrativeSynthesisCrew()
        for agent_method in [crew.n1_narrative_architect, crew.n2_evidence_mapper, crew.n3_claim_guardian]:
            agent = agent_method()
            assert not agent.allow_delegation


# =============================================================================
# Crew Output Pydantic Configuration Tests
# =============================================================================


class TestNarrativeCrewOutputPydantic:
    """Test that finalize_narrative task produces structured output."""

    def test_finalize_task_has_output_pydantic(self):
        """finalize_narrative should specify output_pydantic."""
        from src.crews.viability.narrative_crew import NarrativeSynthesisCrew
        from src.shared.schemas.narrative import PitchNarrativeContent

        crew = NarrativeSynthesisCrew()
        task = crew.finalize_narrative()
        assert task.output_pydantic == PitchNarrativeContent

    def test_crew_uses_sequential_process(self):
        """Crew should use sequential process."""
        from crewai import Process
        from src.crews.viability.narrative_crew import NarrativeSynthesisCrew

        crew_instance = NarrativeSynthesisCrew()
        built_crew = crew_instance.crew()
        assert built_crew.process == Process.sequential
