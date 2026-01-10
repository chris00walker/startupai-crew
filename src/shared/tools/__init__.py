"""
StartupAI Shared Tools.

Tools available to agents across all crews in the validation engine.

Tool Categories:
- Research: TavilySearchTool, CustomerResearchTool
- Governance: MethodologyCheckTool

Usage:
    from shared.tools import TavilySearchTool, MethodologyCheckTool

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["research_agent"],
            tools=[TavilySearchTool()],
            ...
        )
"""

from shared.tools.web_search import (
    TavilySearchTool,
    CustomerResearchTool,
    web_search,
    research_customers,
    SearchResult,
    WebSearchOutput,
)
from shared.tools.methodology_check import (
    MethodologyCheckTool,
    check_vpc,
    MethodologyCheckResult,
    MethodologyIssue,
    CheckSeverity,
    MethodologyType,
)

__all__ = [
    # Web Search Tools
    "TavilySearchTool",
    "CustomerResearchTool",
    "web_search",
    "research_customers",
    "SearchResult",
    "WebSearchOutput",
    # Methodology Check Tools
    "MethodologyCheckTool",
    "check_vpc",
    "MethodologyCheckResult",
    "MethodologyIssue",
    "CheckSeverity",
    "MethodologyType",
]
