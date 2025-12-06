"""
Growth Crew - Led by Pulse (CGO).
Handles experiment design and customer signal analysis.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from startupai.crews.crew_outputs import (
    GrowthCrewOutput,
    PricingTestOutput,
    DegradationTestOutput,
)


@CrewBase
class GrowthCrew:
    """
    Pulse's Growth Crew for experimentation.

    This crew designs and analyzes experiments to test desirability
    assumptions and measure customer commitment signals.
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def experiment_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['experiment_designer'],
            cache=False,
            verbose=True
        )

    @agent
    def signal_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['signal_analyst'],
            cache=False,
            verbose=True
        )

    @agent
    def channel_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['channel_strategist'],
            cache=False,
            verbose=True
        )

    @task
    def test_desirability(self) -> Task:
        return Task(
            config=self.tasks_config['test_desirability'],
            output_pydantic=GrowthCrewOutput
        )

    @task
    def test_pricing(self) -> Task:
        return Task(
            config=self.tasks_config['test_pricing'],
            output_pydantic=PricingTestOutput
        )

    @task
    def test_degraded(self) -> Task:
        return Task(
            config=self.tasks_config['test_degraded'],
            output_pydantic=DegradationTestOutput
        )

    @task
    def refine_experiments(self) -> Task:
        return Task(
            config=self.tasks_config['refine_experiments'],
            output_pydantic=GrowthCrewOutput
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Growth Crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=10
        )
