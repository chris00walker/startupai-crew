"""
Service Crew - Led by Sage (CSO).
Handles entrepreneur onboarding and initial brief capture.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from startupai.crews.crew_outputs import ServiceCrewOutput, SegmentPivotOutput


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
            config=self.tasks_config['capture_entrepreneur_brief'],
            output_pydantic=ServiceCrewOutput
        )

    @task
    def segment_pivot_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['segment_pivot_analysis'],
            output_pydantic=SegmentPivotOutput
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Service Crew for founder intake only.

        Uses only capture_entrepreneur_brief task to avoid template
        variable conflicts with segment_pivot_analysis.
        """
        return Crew(
            agents=[self.founder_onboarding_agent()],
            tasks=[self.capture_entrepreneur_brief()],
            process=Process.sequential,
            verbose=True,
            max_rpm=10
        )

    def pivot_crew(self) -> Crew:
        """Creates a crew for segment pivot analysis.

        Separate crew to handle different template variables:
        - current_segment, evidence, business_idea
        """
        return Crew(
            agents=[self.founder_onboarding_agent()],
            tasks=[self.segment_pivot_analysis()],
            process=Process.sequential,
            verbose=True,
            max_rpm=10
        )
