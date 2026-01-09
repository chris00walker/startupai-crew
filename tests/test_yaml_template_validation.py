"""
YAML Template Validation Tests

Tests that YAML task files are valid and template variables are properly defined.
These tests catch Issues #2 and #4 from live Modal testing:
- Issue 2: Template var 'assumptions_to_test' not found
- Issue 4: Phase 2 'key_messaging' not found

All tests use mocks (no API keys required). These are static validation tests
that run at test time rather than runtime.
"""

import os
import re
import pytest
import yaml
from pathlib import Path
from typing import Set


# =============================================================================
# Test Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
CREWS_DIR = PROJECT_ROOT / "src" / "crews"

# Template variable pattern: {variable_name}
TEMPLATE_VAR_PATTERN = re.compile(r"\{([a-z_][a-z0-9_]*)\}")

# Expected input variables per crew (what the crew function provides)
# Note: These include both direct crew inputs AND variables that come from context references
CREW_INPUT_VARIABLES = {
    # Phase 0: Onboarding
    "onboarding": {"entrepreneur_input"},
    # Phase 1: VPC Discovery
    "discovery": {"founders_brief", "entrepreneur_input"},
    "customer_profile": {"founders_brief", "entrepreneur_input", "discovery_results"},
    "value_design": {"founders_brief", "customer_profile"},
    "wtp": {"founders_brief", "customer_profile", "value_map"},
    "fit_assessment": {"founders_brief", "customer_profile", "value_map", "wtp_insights", "wtp_results"},
    # Phase 2: Desirability
    "build": {"value_proposition", "customer_profile", "value_map"},
    "growth": {"ad_concepts", "landing_pages", "customer_pains", "value_proposition"},
    "governance": {"activities", "creative_assets", "experiment_data"},
    # Phase 3: Feasibility
    "feasibility_build": {
        "founders_brief", "value_map", "desirability_evidence",
        "feature_requirements", "customer_profile",  # Required by tasks
    },
    "feasibility_governance": {
        "feasibility_assessment", "technical_risks",
        "feasibility_signal", "integrations", "technical_architecture",  # Required by tasks
    },
    # Phase 4: Viability
    "finance": {
        "founders_brief", "desirability_evidence", "feasibility_evidence", "experiment_data",
        "business_model", "business_model_type", "pricing", "pricing_data",  # Required by tasks
        "customer_segment", "target_market", "business_description", "validated_assumptions",
    },
    "synthesis": {
        "founders_brief", "desirability_evidence", "feasibility_evidence", "viability_evidence", "vpc_evidence",
        "viability_signal", "decision_options", "validation_history", "human_decision",  # Required by tasks
    },
    "viability_governance": {
        "synthesis_report", "all_evidence", "validation_record",
        "validation_history", "learnings", "audit_trail",  # Required by tasks
    },
}

# Map config file names to their crew input variable set
# Note: Files that appear in multiple directories (build_tasks.yaml, governance_tasks.yaml)
# use None so the directory-based logic in get_crew_name_from_path handles them
CONFIG_FILE_TO_CREW = {
    "tasks.yaml": None,  # Use directory name
    "customer_profile_tasks.yaml": "customer_profile",
    "value_design_tasks.yaml": "value_design",
    "wtp_tasks.yaml": "wtp",
    "fit_assessment_tasks.yaml": "fit_assessment",
    "build_tasks.yaml": None,  # Exists in desirability and feasibility - use directory logic
    "growth_tasks.yaml": "growth",
    "governance_tasks.yaml": None,  # Exists in desirability, feasibility, viability - use directory logic
    "finance_tasks.yaml": "finance",
    "synthesis_tasks.yaml": "synthesis",
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_all_task_yaml_files() -> list[Path]:
    """Find all task YAML files across all crews."""
    task_files = []
    for crew_dir in CREWS_DIR.iterdir():
        if crew_dir.is_dir():
            config_dir = crew_dir / "config"
            if config_dir.exists():
                for yaml_file in config_dir.glob("*tasks*.yaml"):
                    task_files.append(yaml_file)
    return sorted(task_files)


def extract_template_variables(yaml_content: dict) -> dict[str, Set[str]]:
    """Extract template variables from each task in the YAML content."""
    task_vars = {}
    for task_name, task_config in yaml_content.items():
        if not isinstance(task_config, dict):
            continue
        vars_found = set()
        # Check description field
        desc = task_config.get("description", "")
        if isinstance(desc, str):
            vars_found.update(TEMPLATE_VAR_PATTERN.findall(desc))
        # Check expected_output field (less common but possible)
        expected = task_config.get("expected_output", "")
        if isinstance(expected, str):
            vars_found.update(TEMPLATE_VAR_PATTERN.findall(expected))
        task_vars[task_name] = vars_found
    return task_vars


def extract_task_context_references(yaml_content: dict) -> dict[str, list[str]]:
    """Extract context task references for each task."""
    task_contexts = {}
    for task_name, task_config in yaml_content.items():
        if not isinstance(task_config, dict):
            continue
        context = task_config.get("context", [])
        if isinstance(context, list):
            task_contexts[task_name] = context
        else:
            task_contexts[task_name] = []
    return task_contexts


def get_crew_name_from_path(yaml_path: Path) -> str:
    """Determine crew name from file path for input variable lookup."""
    # Get filename and parent directory
    filename = yaml_path.name
    crew_dir = yaml_path.parent.parent.name

    # Check if specific file mapping exists
    if filename in CONFIG_FILE_TO_CREW and CONFIG_FILE_TO_CREW[filename]:
        return CONFIG_FILE_TO_CREW[filename]

    # Handle phase-specific crews by directory
    if crew_dir == "desirability":
        if "build" in filename:
            return "build"
        elif "governance" in filename:
            return "governance"
        elif "growth" in filename:
            return "growth"
    elif crew_dir == "feasibility":
        if "build" in filename:
            return "feasibility_build"
        elif "governance" in filename:
            return "feasibility_governance"
    elif crew_dir == "viability":
        if "governance" in filename:
            return "viability_governance"
        elif "finance" in filename:
            return "finance"
        elif "synthesis" in filename:
            return "synthesis"

    # Default to directory name
    return crew_dir


# =============================================================================
# Test: All YAML Files Parse Successfully
# =============================================================================

class TestYamlParsing:
    """Tests that all YAML files are syntactically valid."""

    def test_all_task_yaml_files_exist(self):
        """Verify we have task YAML files to test."""
        task_files = get_all_task_yaml_files()
        assert len(task_files) > 0, "No task YAML files found"
        # We expect at least 10 files (14 crews, some combined)
        assert len(task_files) >= 10, f"Expected at least 10 task files, found {len(task_files)}"

    @pytest.mark.parametrize("yaml_file", get_all_task_yaml_files(), ids=lambda p: p.name)
    def test_yaml_file_parses_successfully(self, yaml_file: Path):
        """Test that each YAML file parses without syntax errors."""
        content = yaml_file.read_text()
        try:
            parsed = yaml.safe_load(content)
            assert parsed is not None, f"YAML file {yaml_file.name} is empty"
            assert isinstance(parsed, dict), f"YAML file {yaml_file.name} root is not a dict"
        except yaml.YAMLError as e:
            pytest.fail(f"YAML parse error in {yaml_file.name}: {e}")

    @pytest.mark.parametrize("yaml_file", get_all_task_yaml_files(), ids=lambda p: p.name)
    def test_yaml_tasks_have_required_fields(self, yaml_file: Path):
        """Test that each task has description, expected_output, and agent."""
        content = yaml.safe_load(yaml_file.read_text())
        required_fields = {"description", "expected_output", "agent"}

        for task_name, task_config in content.items():
            if not isinstance(task_config, dict):
                continue
            missing = required_fields - set(task_config.keys())
            assert not missing, (
                f"Task '{task_name}' in {yaml_file.name} missing required fields: {missing}"
            )


# =============================================================================
# Test: Template Variables Exist in Crew Inputs
# =============================================================================

class TestTemplateVariables:
    """Tests that template variables in task descriptions are provided by crews."""

    @pytest.mark.parametrize("yaml_file", get_all_task_yaml_files(), ids=lambda p: p.name)
    def test_template_variables_defined(self, yaml_file: Path):
        """Test that all template variables are defined in crew inputs or context."""
        content = yaml.safe_load(yaml_file.read_text())
        task_vars = extract_template_variables(content)
        task_contexts = extract_task_context_references(content)

        # Get expected inputs for this crew
        crew_name = get_crew_name_from_path(yaml_file)
        crew_inputs = CREW_INPUT_VARIABLES.get(crew_name, set())

        # Build set of all task names (for context reference validation)
        all_task_names = set(content.keys())

        # Variables that can be provided by previous tasks via context
        # These are implicitly available if a task has context references
        context_provided_vars = {
            # Interview output provides these
            "interview_output", "interview_notes",
            # Task outputs by convention
            "ad_variants", "copy_variants", "experiment_config", "experiment_results",
            "landing_page_concept", "ad_creative_concepts",
            # Analysis outputs
            "legitimacy_report", "intent_verification",
            # Feasibility outputs (from prior tasks in feasibility crews)
            "feasibility_assessment", "technical_assessment",
            "ui_complexity", "frontend_assessment", "backend_architecture",
            "cost_estimates", "lite_variant", "assessments", "all_assessments",
            "all_reviews",
            # Viability outputs (from prior tasks in viability crews)
            "ltv", "cac", "all_calculations", "all_analyses",
            "viability_signal", "evidence_synthesis", "decision_document",
            "all_outputs", "scrubbed_outputs",
        }

        for task_name, vars_found in task_vars.items():
            if not vars_found:
                continue

            # Collect all valid sources for this task
            valid_vars = crew_inputs.copy()

            # Add context-provided variables if task has context
            if task_contexts.get(task_name):
                valid_vars.update(context_provided_vars)

            # Check each variable
            for var in vars_found:
                # Skip if variable is in crew inputs or context-provided
                if var in valid_vars:
                    continue
                # Skip known safe variables that are always available
                if var in {"json", "text", "output"}:
                    continue

                # This is the key assertion - fail if variable source is unknown
                assert var in valid_vars, (
                    f"Template variable '{{{var}}}' in task '{task_name}' ({yaml_file.name}) "
                    f"not found in crew inputs {crew_inputs} or context references. "
                    f"Either add to CREW_INPUT_VARIABLES['{crew_name}'] or ensure "
                    f"task has context reference that provides this variable."
                )

    def test_no_runtime_dependent_variables_in_first_task(self):
        """Test that first tasks don't depend on context variables."""
        for yaml_file in get_all_task_yaml_files():
            content = yaml.safe_load(yaml_file.read_text())
            task_contexts = extract_task_context_references(content)
            task_vars = extract_template_variables(content)

            # Get first task (first key in ordered dict)
            first_task = next(iter(content.keys()), None)
            if not first_task:
                continue

            # First task should have no context dependencies
            first_context = task_contexts.get(first_task, [])
            if first_context:
                continue  # Some first tasks legitimately have context

            # Variables in first task must come from crew inputs
            crew_name = get_crew_name_from_path(yaml_file)
            crew_inputs = CREW_INPUT_VARIABLES.get(crew_name, set())
            first_task_vars = task_vars.get(first_task, set())

            for var in first_task_vars:
                assert var in crew_inputs or var in {"json", "text", "output"}, (
                    f"First task '{first_task}' in {yaml_file.name} has variable '{{{var}}}' "
                    f"but no context and not in crew inputs: {crew_inputs}"
                )


# =============================================================================
# Test: Context References are Valid
# =============================================================================

class TestContextReferences:
    """Tests that context task references point to valid tasks."""

    @pytest.mark.parametrize("yaml_file", get_all_task_yaml_files(), ids=lambda p: p.name)
    def test_context_references_valid_tasks(self, yaml_file: Path):
        """Test that context references point to tasks that exist in the file."""
        content = yaml.safe_load(yaml_file.read_text())
        all_task_names = set(content.keys())
        task_contexts = extract_task_context_references(content)

        for task_name, context_refs in task_contexts.items():
            for ref in context_refs:
                assert ref in all_task_names, (
                    f"Task '{task_name}' in {yaml_file.name} has context reference "
                    f"'{ref}' but that task doesn't exist. Available: {all_task_names}"
                )

    @pytest.mark.parametrize("yaml_file", get_all_task_yaml_files(), ids=lambda p: p.name)
    def test_no_circular_context_references(self, yaml_file: Path):
        """Test that there are no circular context dependencies."""
        content = yaml.safe_load(yaml_file.read_text())
        task_contexts = extract_task_context_references(content)

        def check_circular(task: str, visited: set):
            if task in visited:
                return True  # Circular!
            visited.add(task)
            for ref in task_contexts.get(task, []):
                if check_circular(ref, visited.copy()):
                    return True
            return False

        for task_name in content.keys():
            assert not check_circular(task_name, set()), (
                f"Circular context reference detected starting from '{task_name}' in {yaml_file.name}"
            )

    @pytest.mark.parametrize("yaml_file", get_all_task_yaml_files(), ids=lambda p: p.name)
    def test_context_references_ordered_correctly(self, yaml_file: Path):
        """Test that context references only point to earlier tasks (proper order)."""
        content = yaml.safe_load(yaml_file.read_text())
        task_order = list(content.keys())
        task_contexts = extract_task_context_references(content)

        for idx, task_name in enumerate(task_order):
            context_refs = task_contexts.get(task_name, [])
            for ref in context_refs:
                if ref not in task_order:
                    continue  # Already caught by other test
                ref_idx = task_order.index(ref)
                assert ref_idx < idx, (
                    f"Task '{task_name}' (position {idx}) references '{ref}' (position {ref_idx}) "
                    f"which comes later. Context must reference earlier tasks. File: {yaml_file.name}"
                )


# =============================================================================
# Test: Agent References are Valid
# =============================================================================

class TestAgentReferences:
    """Tests that agent references in tasks point to valid agents."""

    def _get_agents_for_crew(self, crew_dir: Path) -> Set[str]:
        """Get all agent names defined in a crew's agent YAML files."""
        agents = set()
        config_dir = crew_dir / "config"
        if not config_dir.exists():
            return agents

        for yaml_file in config_dir.glob("*agents*.yaml"):
            try:
                content = yaml.safe_load(yaml_file.read_text())
                if content:
                    agents.update(content.keys())
            except yaml.YAMLError:
                continue
        return agents

    @pytest.mark.parametrize("yaml_file", get_all_task_yaml_files(), ids=lambda p: p.name)
    def test_task_agents_exist(self, yaml_file: Path):
        """Test that each task references an agent that exists."""
        content = yaml.safe_load(yaml_file.read_text())
        crew_dir = yaml_file.parent.parent
        available_agents = self._get_agents_for_crew(crew_dir)

        # Skip if no agent files found (might be a different structure)
        if not available_agents:
            pytest.skip(f"No agent files found for {crew_dir.name}")

        for task_name, task_config in content.items():
            if not isinstance(task_config, dict):
                continue
            agent = task_config.get("agent")
            if agent:
                assert agent in available_agents, (
                    f"Task '{task_name}' in {yaml_file.name} references agent '{agent}' "
                    f"but agent not found. Available: {available_agents}"
                )


# =============================================================================
# Test: Specific Known Issues (Regression Tests)
# =============================================================================

class TestKnownIssueRegressions:
    """Regression tests for specific issues found during live testing."""

    def test_issue_2_assumptions_to_test_variable(self):
        """
        Issue #2: Template var 'assumptions_to_test' not found.

        If this variable is used, it must be provided by crew inputs or context.
        """
        for yaml_file in get_all_task_yaml_files():
            content = yaml.safe_load(yaml_file.read_text())
            task_vars = extract_template_variables(content)
            task_contexts = extract_task_context_references(content)

            for task_name, vars_found in task_vars.items():
                if "assumptions_to_test" in vars_found:
                    # Either crew inputs must include it OR task must have context
                    crew_name = get_crew_name_from_path(yaml_file)
                    crew_inputs = CREW_INPUT_VARIABLES.get(crew_name, set())
                    has_context = bool(task_contexts.get(task_name))

                    assert "assumptions_to_test" in crew_inputs or has_context, (
                        f"Issue #2 regression: 'assumptions_to_test' in task '{task_name}' "
                        f"({yaml_file.name}) requires either crew input or context reference"
                    )

    def test_issue_4_key_messaging_variable(self):
        """
        Issue #4: Phase 2 'key_messaging' not found.

        If this variable is used in Phase 2, it must be defined.
        """
        phase_2_crews = ["desirability"]

        for yaml_file in get_all_task_yaml_files():
            crew_dir = yaml_file.parent.parent.name
            if crew_dir not in phase_2_crews:
                continue

            content = yaml.safe_load(yaml_file.read_text())
            task_vars = extract_template_variables(content)

            for task_name, vars_found in task_vars.items():
                if "key_messaging" in vars_found:
                    crew_name = get_crew_name_from_path(yaml_file)
                    crew_inputs = CREW_INPUT_VARIABLES.get(crew_name, set())

                    assert "key_messaging" in crew_inputs, (
                        f"Issue #4 regression: 'key_messaging' in Phase 2 task '{task_name}' "
                        f"({yaml_file.name}) must be in crew inputs"
                    )


# =============================================================================
# Test: Comprehensive Variable Coverage
# =============================================================================

class TestVariableCoverage:
    """Tests for comprehensive template variable coverage."""

    def test_all_crews_have_defined_inputs(self):
        """Test that all crews have their input variables defined."""
        for yaml_file in get_all_task_yaml_files():
            crew_name = get_crew_name_from_path(yaml_file)
            assert crew_name in CREW_INPUT_VARIABLES, (
                f"Crew '{crew_name}' from {yaml_file.name} not in CREW_INPUT_VARIABLES. "
                f"Add it with its expected input variables."
            )

    def test_summarize_all_template_variables(self):
        """Report all unique template variables found (informational test)."""
        all_vars = set()
        vars_by_file = {}

        for yaml_file in get_all_task_yaml_files():
            content = yaml.safe_load(yaml_file.read_text())
            task_vars = extract_template_variables(content)
            file_vars = set()
            for vars_found in task_vars.values():
                file_vars.update(vars_found)
            vars_by_file[yaml_file.name] = file_vars
            all_vars.update(file_vars)

        # This test always passes but prints useful info
        print(f"\nTotal unique template variables: {len(all_vars)}")
        print(f"Variables: {sorted(all_vars)}")
        assert True
