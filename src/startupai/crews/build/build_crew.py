"""
Build Crew - Led by Forge (CTO).
Handles technical feasibility assessment, resource estimation,
and MVP/landing page generation.

Now equipped with full landing page pipeline:
- Generation (LandingPageGeneratorTool)
- Validation (CodeValidatorTool)
- Deployment (LandingPageDeploymentTool)
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from startupai.tools.landing_page import LandingPageGeneratorTool
from startupai.tools.code_validator import CodeValidatorTool
from startupai.tools.landing_page_deploy import LandingPageDeploymentTool


@CrewBase
class BuildCrew:
    """
    Forge's Build Crew for technical assessment.

    This crew evaluates technical feasibility, designs prototypes,
    estimates development resources, and generates MVP/landing pages.

    Now uses the full landing page pipeline for:
    - Generating landing page variants (A/B testing)
    - Validating code before deployment
    - Deploying to Netlify for live experiments
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        """Initialize Build Crew with landing page tools."""
        self._landing_page_tool = LandingPageGeneratorTool()
        self._code_validator_tool = CodeValidatorTool()
        self._landing_page_deploy_tool = LandingPageDeploymentTool()

    @agent
    def technical_feasibility_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['technical_feasibility_agent'],
            verbose=True
        )

    @agent
    def prototype_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['prototype_designer'],
            tools=[
                self._landing_page_tool,
                self._code_validator_tool,
                self._landing_page_deploy_tool,
            ],
            verbose=True
        )

    @agent
    def resource_estimator(self) -> Agent:
        return Agent(
            config=self.agents_config['resource_estimator'],
            verbose=True
        )

    @task
    def assess_feasibility(self) -> Task:
        return Task(
            config=self.tasks_config['assess_feasibility']
        )

    @task
    def design_downgrade(self) -> Task:
        return Task(
            config=self.tasks_config['design_downgrade']
        )

    @task
    def reduce_scope(self) -> Task:
        return Task(
            config=self.tasks_config['reduce_scope']
        )

    @task
    def generate_landing_pages(self) -> Task:
        return Task(
            config=self.tasks_config['generate_landing_pages']
        )

    @task
    def validate_landing_pages(self) -> Task:
        return Task(
            config=self.tasks_config['validate_landing_pages']
        )

    @task
    def deploy_landing_pages(self) -> Task:
        return Task(
            config=self.tasks_config['deploy_landing_pages']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Build Crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
