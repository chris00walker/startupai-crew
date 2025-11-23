"""
Service Crew - Led by Sage (CSO).
Handles entrepreneur onboarding and initial brief capture.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class ServiceCrew:
    """
    Sage's Service Crew for client onboarding.

    This crew captures entrepreneur input and structures it into a
    comprehensive brief for validation analysis.
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def founder_onboarding_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['founder_onboarding_agent'],
            verbose=True
        )

    @agent
    def consultant_onboarding_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['consultant_onboarding_agent'],
            verbose=True
        )

    @agent
    def customer_service_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_service_agent'],
            verbose=True
        )

    @task
    def capture_entrepreneur_brief(self) -> Task:
        return Task(
            config=self.tasks_config['capture_entrepreneur_brief']
        )

    @task
    def segment_pivot_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['segment_pivot_analysis']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Service Crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
