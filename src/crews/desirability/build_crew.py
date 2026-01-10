"""
BuildCrew - Phase 2: Desirability - Build Testable Artifacts

This crew builds landing pages and testable artifacts for desirability validation.
Reused in Phase 3 for feasibility assessment.

Agents:
- F1: UX/UI Designer (Forge) - Design landing page wireframes
- F2: Frontend Developer (Forge) - Build landing pages (Next.js)
- F3: Backend Developer (Forge) - Deploy artifacts (Netlify)
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from shared.tools import (
    CanvasBuilderTool,
    TestCardTool,
    LandingPageDeploymentTool,
)


@CrewBase
class BuildCrew:
    """
    BuildCrew builds testable artifacts for validation.

    Produces:
    - Landing page designs
    - Built landing pages
    - Deployed artifacts
    """

    agents_config = "config/build_agents.yaml"
    tasks_config = "config/build_tasks.yaml"

    # =========================================================================
    # AGENTS
    # =========================================================================

    @agent
    def f1_ux_designer(self) -> Agent:
        """F1: UX/UI Designer - Designs interfaces."""
        return Agent(
            config=self.agents_config["f1_ux_designer"],
            tools=[CanvasBuilderTool(), TestCardTool()],
            reasoning=False,  # Creative design work
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.8),  # Creative design
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def f2_frontend_developer(self) -> Agent:
        """F2: Frontend Developer - Builds UI."""
        return Agent(
            config=self.agents_config["f2_frontend_developer"],
            tools=[CanvasBuilderTool(), TestCardTool()],
            reasoning=False,  # Code generation
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.2),  # Code generation
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def f3_backend_developer(self) -> Agent:
        """F3: Backend Developer - Deploys artifacts."""
        return Agent(
            config=self.agents_config["f3_backend_developer"],
            tools=[LandingPageDeploymentTool()],  # Deploy to Netlify
            reasoning=False,  # Code generation
            inject_date=True,
            max_iter=25,
            llm=LLM(model="openai/gpt-4o", temperature=0.2),  # Code generation
            verbose=True,
            allow_delegation=False,
        )

    # =========================================================================
    # TASKS
    # =========================================================================

    @task
    def design_landing_page(self) -> Task:
        """Design landing page wireframes."""
        return Task(config=self.tasks_config["design_landing_page"])

    @task
    def build_landing_page(self) -> Task:
        """Build landing page (Next.js)."""
        return Task(config=self.tasks_config["build_landing_page"])

    @task
    def deploy_artifacts(self) -> Task:
        """Deploy testable artifacts."""
        return Task(config=self.tasks_config["deploy_artifacts"])

    # =========================================================================
    # CREW
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the BuildCrew with sequential process.

        Task Flow:
        1. F1 designs landing page wireframes
        2. F2 builds landing pages
        3. F3 deploys to Netlify
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
