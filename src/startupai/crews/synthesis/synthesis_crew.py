"""
Synthesis Crew - Led by Compass (CPO).

This crew is responsible for evidence synthesis and strategic pivot decisions
based on the Innovation Physics framework.
"""

from typing import Dict, Any
from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, task, crew
import yaml
from pathlib import Path

from startupai.crews.crew_outputs import SynthesisCrewOutput, PivotDecisionOutput


class SynthesisCrew(CrewBase):
    """
    Compass's Synthesis Crew for strategic decision-making.

    Integrates evidence from all validation phases and makes pivot/proceed
    recommendations based on Innovation Physics logic.
    """

    def __init__(self):
        """Initialize the Synthesis Crew."""
        self.config_dir = Path(__file__).parent / "config"
        self.agents_config = self._load_config("agents.yaml")
        self.tasks_config = self._load_config("tasks.yaml")

    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_path = self.config_dir / filename
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    @agent
    def project_manager(self) -> Agent:
        """Create the Project Manager agent (Compass's primary agent)."""
        config = self.agents_config.get("project_manager", {})
        return Agent(
            role=config.get("role", "Project Manager"),
            goal=config.get("goal", "Synthesize evidence and make strategic decisions"),
            backstory=config.get("backstory", "Expert in startup validation and pivot decisions"),
            verbose=True
        )

    @task
    def evidence_synthesis_task(self) -> Task:
        """Task for synthesizing all validation evidence."""
        config = self.tasks_config.get("evidence_synthesis", {})
        return Task(
            description=config.get("description", ""),
            expected_output=config.get("expected_output", ""),
            agent=self.project_manager(),
            output_pydantic=SynthesisCrewOutput
        )

    @task
    def strategic_pivot_task(self) -> Task:
        """Task for designing strategic pivots when CAC > LTV."""
        config = self.tasks_config.get("strategic_pivot", {})
        return Task(
            description=config.get("description", ""),
            expected_output=config.get("expected_output", ""),
            agent=self.project_manager(),
            output_pydantic=PivotDecisionOutput
        )

    @task
    def final_synthesis_task(self) -> Task:
        """Task for comprehensive final synthesis."""
        config = self.tasks_config.get("final_synthesis", {})
        return Task(
            description=config.get("description", ""),
            expected_output=config.get("expected_output", ""),
            agent=self.project_manager(),
            output_pydantic=SynthesisCrewOutput
        )

    @task
    def experiment_design_task(self) -> Task:
        """Task for designing validation experiments."""
        config = self.tasks_config.get("experiment_design", {})
        return Task(
            description=config.get("description", ""),
            expected_output=config.get("expected_output", ""),
            agent=self.project_manager()
        )

    @crew
    def crew(self) -> Crew:
        """Create the Synthesis Crew."""
        # Determine which task to execute based on context
        # This will be set by the Flow when calling the crew
        return Crew(
            agents=[self.project_manager()],
            tasks=[
                self.evidence_synthesis_task(),
                self.strategic_pivot_task(),
                self.final_synthesis_task(),
                self.experiment_design_task()
            ],
            verbose=True,
            process="sequential",  # Tasks run in order as needed
            max_rpm=10
        )