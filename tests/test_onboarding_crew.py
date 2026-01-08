"""
Tests for OnboardingCrew (Phase 0: Founder's Brief Creation).

Tests the crew structure, agents, tasks, and output schema validation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.state.models import (
    FoundersBrief,
    TheIdea,
    ProblemHypothesis,
    CustomerHypothesis,
    SolutionHypothesis,
    QAStatus,
)


# =============================================================================
# Crew Structure Tests
# =============================================================================

class TestOnboardingCrewStructure:
    """Tests for OnboardingCrew class structure."""

    def test_crew_imports(self):
        """Test that OnboardingCrew can be imported."""
        from src.crews.onboarding import OnboardingCrew
        assert OnboardingCrew is not None

    def test_run_function_imports(self):
        """Test that run_onboarding_crew can be imported."""
        from src.crews.onboarding import run_onboarding_crew
        assert callable(run_onboarding_crew)

    def test_crew_has_agents_config(self):
        """Test that crew has agents config loaded."""
        from src.crews.onboarding.crew import OnboardingCrew

        crew = OnboardingCrew()
        # CrewAI @CrewBase decorator parses the YAML and stores content
        assert isinstance(crew.agents_config, dict)
        assert "o1_founder_interview" in crew.agents_config
        assert "gv1_concept_validator" in crew.agents_config

    def test_config_files_exist(self):
        """Test that config files exist on disk."""
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "onboarding"
        agents_yaml = crew_dir / "config" / "agents.yaml"
        tasks_yaml = crew_dir / "config" / "tasks.yaml"

        assert agents_yaml.exists(), f"agents.yaml not found at {agents_yaml}"
        assert tasks_yaml.exists(), f"tasks.yaml not found at {tasks_yaml}"


# =============================================================================
# Agent Definition Tests
# =============================================================================

class TestOnboardingAgents:
    """Tests for OnboardingCrew agent definitions."""

    def test_agent_yaml_has_all_agents(self):
        """Test that agents.yaml contains all 4 required agents."""
        import yaml
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "onboarding"
        agents_yaml = crew_dir / "config" / "agents.yaml"

        with open(agents_yaml) as f:
            agents = yaml.safe_load(f)

        required_agents = [
            "o1_founder_interview",
            "gv1_concept_validator",
            "gv2_intent_verification",
            "s1_brief_compiler",
        ]

        for agent_id in required_agents:
            assert agent_id in agents, f"Agent {agent_id} not found in agents.yaml"

    def test_o1_agent_definition(self):
        """Test O1 Founder Interview Agent definition."""
        import yaml
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "onboarding"
        with open(crew_dir / "config" / "agents.yaml") as f:
            agents = yaml.safe_load(f)

        o1 = agents["o1_founder_interview"]
        assert "role" in o1
        assert "goal" in o1
        assert "backstory" in o1
        assert "Alex Osterwalder" in o1["backstory"]

    def test_gv1_agent_definition(self):
        """Test GV1 Concept Validator Agent definition."""
        import yaml
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "onboarding"
        with open(crew_dir / "config" / "agents.yaml") as f:
            agents = yaml.safe_load(f)

        gv1 = agents["gv1_concept_validator"]
        assert "Legitimacy" in gv1["role"] or "Validator" in gv1["role"]
        assert "illegal" in gv1["backstory"].lower() or "legal" in gv1["backstory"].lower()

    def test_gv2_agent_definition(self):
        """Test GV2 Intent Verification Agent definition."""
        import yaml
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "onboarding"
        with open(crew_dir / "config" / "agents.yaml") as f:
            agents = yaml.safe_load(f)

        gv2 = agents["gv2_intent_verification"]
        assert "role" in gv2
        assert "verification" in gv2["role"].lower() or "intent" in gv2["role"].lower()

    def test_s1_agent_definition(self):
        """Test S1 Brief Compiler Agent definition."""
        import yaml
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "onboarding"
        with open(crew_dir / "config" / "agents.yaml") as f:
            agents = yaml.safe_load(f)

        s1 = agents["s1_brief_compiler"]
        assert "Brief" in s1["role"] or "Compiler" in s1["role"]
        assert "synthesize" in s1["backstory"].lower() or "synthesizer" in s1["backstory"].lower()


# =============================================================================
# Task Definition Tests
# =============================================================================

class TestOnboardingTasks:
    """Tests for OnboardingCrew task definitions."""

    def test_tasks_yaml_has_all_tasks(self):
        """Test that tasks.yaml contains all 4 required tasks."""
        import yaml
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "onboarding"
        tasks_yaml = crew_dir / "config" / "tasks.yaml"

        with open(tasks_yaml) as f:
            tasks = yaml.safe_load(f)

        required_tasks = [
            "conduct_founder_interview",
            "validate_concept_legitimacy",
            "verify_intent_capture",
            "compile_founders_brief",
        ]

        for task_id in required_tasks:
            assert task_id in tasks, f"Task {task_id} not found in tasks.yaml"

    def test_interview_task_covers_7_areas(self):
        """Test that interview task covers all 7 interview areas."""
        import yaml
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "onboarding"
        with open(crew_dir / "config" / "tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        interview = tasks["conduct_founder_interview"]
        description = interview["description"]

        # Check for 7 interview areas
        areas = [
            "IDEA",
            "MOTIVATION",
            "CUSTOMER",
            "PROBLEM",
            "SOLUTION",
            "ASSUMPTION",
            "SUCCESS",
        ]
        for area in areas:
            assert area.lower() in description.lower(), f"Interview area {area} not found"

    def test_legitimacy_task_has_all_checks(self):
        """Test that legitimacy task includes all check categories."""
        import yaml
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "onboarding"
        with open(crew_dir / "config" / "tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        legitimacy = tasks["validate_concept_legitimacy"]
        description = legitimacy["description"]

        checks = ["LEGAL", "ETHICAL", "FEASIBILITY", "BUSINESS"]
        for check in checks:
            assert check in description, f"Check category {check} not found in legitimacy task"

    def test_compile_task_has_context(self):
        """Test that compile task has all required context tasks."""
        import yaml
        crew_dir = Path(__file__).parent.parent / "src" / "crews" / "onboarding"
        with open(crew_dir / "config" / "tasks.yaml") as f:
            tasks = yaml.safe_load(f)

        compile_task = tasks["compile_founders_brief"]
        # compile_founders_brief should have context from all prior tasks
        context = compile_task.get("context", [])
        assert "conduct_founder_interview" in context
        assert "validate_concept_legitimacy" in context
        assert "verify_intent_capture" in context


# =============================================================================
# Output Schema Tests
# =============================================================================

class TestFoundersBriefSchema:
    """Tests for Founder's Brief output schema."""

    def test_founders_brief_required_fields(self):
        """Test FoundersBrief requires core fields."""
        with pytest.raises(Exception):  # Pydantic validation error
            FoundersBrief()  # Missing required fields

    def test_founders_brief_minimal(self, minimal_founders_brief):
        """Test creating minimal valid Founder's Brief."""
        assert minimal_founders_brief.the_idea.one_liner == "AI-powered supply chain optimizer"
        assert minimal_founders_brief.version == 1

    def test_founders_brief_serialization(self, minimal_founders_brief):
        """Test JSON serialization roundtrip."""
        data = minimal_founders_brief.model_dump(mode="json")
        restored = FoundersBrief(**data)
        assert restored.the_idea.one_liner == minimal_founders_brief.the_idea.one_liner

    def test_qa_status_defaults(self, minimal_founders_brief):
        """Test QA status has correct defaults."""
        assert minimal_founders_brief.qa_status.legitimacy_check == "pending"
        assert minimal_founders_brief.qa_status.intent_verification == "pending"
        assert minimal_founders_brief.qa_status.overall_status == "pending"

    def test_validation_status_markers(self, minimal_founders_brief):
        """Test hypotheses are marked as NOT VALIDATED."""
        assert "NOT VALIDATED" in minimal_founders_brief.problem_hypothesis.validation_status
        assert "NOT VALIDATED" in minimal_founders_brief.customer_hypothesis.validation_status
        assert "NOT VALIDATED" in minimal_founders_brief.solution_hypothesis.validation_status


# =============================================================================
# Phase 0 Integration Tests
# =============================================================================

class TestPhase0Integration:
    """Tests for Phase 0 flow integration."""

    def test_phase_0_module_imports(self):
        """Test that phase_0 module can be imported."""
        from src.modal_app.phases import phase_0_onboarding
        assert hasattr(phase_0_onboarding, "execute")

    def test_phase_0_returns_hitl_checkpoint(self, minimal_founders_brief):
        """Test that Phase 0 returns HITL checkpoint."""
        # Patch at the module where the function is bound (top-level import)
        # and where it's imported dynamically (inside the function)
        with patch("src.modal_app.phases.phase_0.update_progress") as mock_progress, \
             patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            mock_crew.return_value = minimal_founders_brief
            mock_progress.return_value = True

            from src.modal_app.phases.phase_0 import execute

            result = execute(
                run_id="test-run-123",
                state={"entrepreneur_input": "Test business idea"},
            )

            assert "hitl_checkpoint" in result
            assert result["hitl_checkpoint"] == "approve_founders_brief"
            assert "hitl_title" in result
            assert "hitl_options" in result

    def test_phase_0_state_includes_brief(self, minimal_founders_brief):
        """Test that Phase 0 state includes founders_brief."""
        with patch("src.modal_app.phases.phase_0.update_progress") as mock_progress, \
             patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            mock_crew.return_value = minimal_founders_brief
            mock_progress.return_value = True

            from src.modal_app.phases.phase_0 import execute

            result = execute(
                run_id="test-run-123",
                state={"entrepreneur_input": "Test business idea"},
            )

            assert "state" in result
            assert "founders_brief" in result["state"]

    def test_phase_0_hitl_options(self, minimal_founders_brief):
        """Test that HITL checkpoint has correct options."""
        with patch("src.modal_app.phases.phase_0.update_progress") as mock_progress, \
             patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            mock_crew.return_value = minimal_founders_brief
            mock_progress.return_value = True

            from src.modal_app.phases.phase_0 import execute

            result = execute(
                run_id="test-run-123",
                state={"entrepreneur_input": "Test business idea"},
            )

            options = result["hitl_options"]
            option_ids = [opt["id"] for opt in options]

            assert "approve" in option_ids
            assert "revise" in option_ids or "reject" in option_ids


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestOnboardingErrorHandling:
    """Tests for error handling in OnboardingCrew."""

    def test_phase_0_handles_crew_error(self):
        """Test that Phase 0 handles crew execution errors."""
        with patch("src.modal_app.phases.phase_0.update_progress") as mock_progress, \
             patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            mock_crew.side_effect = Exception("Crew execution failed")
            mock_progress.return_value = True

            from src.modal_app.phases.phase_0 import execute

            with pytest.raises(Exception) as exc_info:
                execute(
                    run_id="test-run-123",
                    state={"entrepreneur_input": "Test business idea"},
                )

            assert "Crew execution failed" in str(exc_info.value)

    def test_empty_input_handling(self, minimal_founders_brief):
        """Test handling of empty entrepreneur input."""
        with patch("src.modal_app.phases.phase_0.update_progress") as mock_progress, \
             patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            mock_crew.return_value = minimal_founders_brief
            mock_progress.return_value = True

            from src.modal_app.phases.phase_0 import execute

            # Should handle empty string gracefully
            result = execute(
                run_id="test-run-123",
                state={"entrepreneur_input": ""},
            )

            # Crew should still be called
            mock_crew.assert_called_once()
