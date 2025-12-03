"""
Finance Crew - Led by Ledger (CFO).
Handles unit economics and financial viability analysis.

Now equipped with:
- Industry benchmark tools for data-driven analysis
- HITL viability approval tool for strategic decisions
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from startupai.crews.crew_outputs import FinanceCrewOutput, OptimizedMetricsOutput

# Import financial tools
from startupai.tools.financial_data import (
    IndustryBenchmarkTool,
    UnitEconomicsCalculatorTool,
)
from startupai.tools.web_search import TavilySearchTool, MarketResearchTool

# Import HITL viability tool
from startupai.tools.viability_approval import ViabilityApprovalTool


@CrewBase
class FinanceCrew:
    """
    Ledger's Finance Crew for viability assessment.

    This crew calculates unit economics, builds financial models,
    and assesses business viability.

    Now uses:
    - Real benchmark data for CAC/LTV comparisons by industry
    - Unit economics calculations
    - Market size research
    - ViabilityApprovalTool for HITL strategic decisions
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        """Initialize crew with financial tools."""
        self._benchmark_tool = IndustryBenchmarkTool()
        self._calculator_tool = UnitEconomicsCalculatorTool()
        self._web_search_tool = TavilySearchTool()
        self._market_research_tool = MarketResearchTool()
        self._viability_approval_tool = ViabilityApprovalTool()

    @agent
    def unit_economics_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['unit_economics_analyst'],
            tools=[
                self._benchmark_tool,
                self._calculator_tool,
                self._viability_approval_tool,
            ],
            verbose=True
        )

    @agent
    def financial_modeler(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_modeler'],
            tools=[
                self._benchmark_tool,
                self._calculator_tool,
                self._market_research_tool,
            ],
            verbose=True
        )

    @agent
    def funding_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['funding_strategist'],
            tools=[
                self._web_search_tool,
                self._market_research_tool,
            ],
            verbose=True
        )

    @task
    def analyze_viability(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_viability'],
            output_pydantic=FinanceCrewOutput
        )

    @task
    def optimize_economics(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_economics'],
            output_pydantic=OptimizedMetricsOutput
        )

    @task
    def build_financial_model(self) -> Task:
        return Task(
            config=self.tasks_config['build_financial_model']
        )

    @task
    def prepare_viability_decision(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_viability_decision']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Finance Crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=10
        )
