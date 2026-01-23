"""
FeasibilityBuildCrew - Phase 3: Feasibility - Technical Assessment

This crew assesses technical feasibility of the validated value proposition.
Different from Phase 2 BuildCrew which builds landing pages.

Agents:
- F1: UX/UI Designer (Forge) - Map features to requirements, design lite variant
- F2: Frontend Developer (Forge) - Assess frontend complexity
- F3: Backend Developer (Forge) - Assess backend feasibility, set signal

@story US-AFB02
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.state.models import FeasibilityEvidence


@CrewBase
class FeasibilityBuildCrew:
    """
    FeasibilityBuildCrew assesses technical feasibility.

    Produces:
    - Feature requirements mapping
    - Complexity assessments
    - Cost estimates
    - Feasibility signal (GREEN/ORANGE/RED)
    """

    agents_config = "config/build_agents.yaml"
    tasks_config = "config/build_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def f1_requirements_analyst(self) -> Agent:
        """F1: Requirements Analyst - Maps VPC features to technical requirements."""
        return Agent(
            config=self.agents_config["f1_requirements_analyst"],
            tools=[],
            reasoning=False,  # Straightforward mapping
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.3),  # Analytical
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def f2_frontend_assessor(self) -> Agent:
        """F2: Frontend Assessor - Assesses frontend complexity."""
        return Agent(
            config=self.agents_config["f2_frontend_assessor"],
            tools=[],
            reasoning=False,  # Technical assessment
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.2),  # Technical
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def f3_backend_assessor(self) -> Agent:
        """F3: Backend Assessor - Assesses backend feasibility."""
        return Agent(
            config=self.agents_config["f3_backend_assessor"],
            tools=[],
            reasoning=False,  # Technical assessment
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.2),  # Technical
            verbose=True,
            allow_delegation=False,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def extract_feature_requirements(self) -> Task:
        """Extract features from VPC and map to technical requirements."""
        return Task(config=self.tasks_config["extract_feature_requirements"])

    @task
    def assess_ui_complexity(self) -> Task:
        """Score UI/UX complexity (1-10)."""
        return Task(config=self.tasks_config["assess_ui_complexity"])

    @task
    def design_lite_variant(self) -> Task:
        """Design minimal viable feature set for downgrade protocol."""
        return Task(config=self.tasks_config["design_lite_variant"])

    @task
    def assess_frontend_complexity(self) -> Task:
        """Evaluate frontend build difficulty."""
        return Task(config=self.tasks_config["assess_frontend_complexity"])

    @task
    def identify_framework_requirements(self) -> Task:
        """Identify required libraries and frameworks."""
        return Task(config=self.tasks_config["identify_framework_requirements"])

    @task
    def assess_backend_architecture(self) -> Task:
        """Evaluate backend architecture requirements."""
        return Task(config=self.tasks_config["assess_backend_architecture"])

    @task
    def evaluate_api_integrations(self) -> Task:
        """Evaluate required third-party services and APIs."""
        return Task(config=self.tasks_config["evaluate_api_integrations"])

    @task
    def estimate_costs(self) -> Task:
        """Estimate infrastructure and development costs."""
        return Task(config=self.tasks_config["estimate_costs"])

    @task
    def set_feasibility_signal(self) -> Task:
        """Set feasibility signal (GREEN/ORANGE/RED)."""
        return Task(
            config=self.tasks_config["set_feasibility_signal"],
            output_pydantic=FeasibilityEvidence,
        )

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the FeasibilityBuildCrew with sequential process.

        Task Flow:
        1. F1 extracts feature requirements from VPC
        2. F1 assesses UI complexity
        3. F1 designs lite variant (for downgrade protocol)
        4. F2 assesses frontend complexity
        5. F2 identifies framework requirements
        6. F3 assesses backend architecture
        7. F3 evaluates API integrations
        8. F3 estimates costs
        9. F3 sets feasibility signal
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
