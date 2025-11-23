"""
Analysis Crew - Led by Sage (CSO).
Handles customer research and competitive analysis.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class AnalysisCrew:
    """
    Sage's Analysis Crew for market research.

    This crew performs deep customer research using Jobs-to-be-Done
    framework and competitive landscape analysis.
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def customer_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_researcher'],
            verbose=True
        )

    @agent
    def competitor_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['competitor_analyst'],
            verbose=True
        )

    @task
    def analyze_customer_segment(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_customer_segment']
        )

    @task
    def analyze_competitors(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_competitors']
        )

    @task
    def iterate_value_proposition(self) -> Task:
        return Task(
            config=self.tasks_config['iterate_value_proposition']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Analysis Crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
