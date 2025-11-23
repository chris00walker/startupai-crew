"""
Finance Crew - Led by Ledger (CFO).
Handles unit economics and financial viability analysis.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class FinanceCrew:
    """
    Ledger's Finance Crew for viability assessment.

    This crew calculates unit economics, builds financial models,
    and assesses business viability.
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def unit_economics_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['unit_economics_analyst'],
            verbose=True
        )

    @agent
    def financial_modeler(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_modeler'],
            verbose=True
        )

    @agent
    def funding_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['funding_strategist'],
            verbose=True
        )

    @task
    def analyze_viability(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_viability']
        )

    @task
    def optimize_economics(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_economics']
        )

    @task
    def build_financial_model(self) -> Task:
        return Task(
            config=self.tasks_config['build_financial_model']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Finance Crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
