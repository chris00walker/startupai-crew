"""
Analysis Crew - Led by Sage (CSO).
Handles customer research and competitive analysis.

Now equipped with real web search tools for market research!
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from startupai.crews.crew_outputs import (
    AnalysisCrewOutput,
    CompetitorAnalysisOutput,
    ValuePropIterationOutput,
)

# Import web research tools
from startupai.tools.web_search import (
    TavilySearchTool,
    CustomerResearchTool,
    CompetitorResearchTool,
    MarketResearchTool,
)


@CrewBase
class AnalysisCrew:
    """
    Sage's Analysis Crew for market research.

    This crew performs deep customer research using Jobs-to-be-Done
    framework and competitive landscape analysis.

    Now uses real web search via Tavily API for:
    - Customer segment research
    - Competitor analysis
    - Market intelligence
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        """Initialize crew with web research tools."""
        # Create tool instances
        self._web_search_tool = TavilySearchTool()
        self._customer_research_tool = CustomerResearchTool()
        self._competitor_research_tool = CompetitorResearchTool()
        self._market_research_tool = MarketResearchTool()

    @agent
    def customer_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_researcher'],
            tools=[
                self._web_search_tool,
                self._customer_research_tool,
                self._market_research_tool,
            ],
            verbose=True
        )

    @agent
    def competitor_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['competitor_analyst'],
            tools=[
                self._web_search_tool,
                self._competitor_research_tool,
                self._market_research_tool,
            ],
            verbose=True
        )

    @task
    def analyze_customer_segment(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_customer_segment'],
            output_pydantic=AnalysisCrewOutput
        )

    @task
    def analyze_competitors(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_competitors'],
            output_pydantic=CompetitorAnalysisOutput
        )

    @task
    def iterate_value_proposition(self) -> Task:
        return Task(
            config=self.tasks_config['iterate_value_proposition'],
            output_pydantic=ValuePropIterationOutput
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Analysis Crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=10
        )
