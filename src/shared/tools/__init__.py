"""
StartupAI Shared Tools.

Tools available to agents across all crews in the validation engine.

Tool Categories:
- Research: TavilySearchTool, CustomerResearchTool
- Customer Research: ForumSearchTool, ReviewAnalysisTool, SocialListeningTool, TrendAnalysisTool
- Governance: MethodologyCheckTool

Usage:
    from shared.tools import TavilySearchTool, ForumSearchTool, MethodologyCheckTool

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["research_agent"],
            tools=[TavilySearchTool(), ForumSearchTool()],
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
from shared.tools.customer_research import (
    ForumSearchTool,
    ReviewAnalysisTool,
    SocialListeningTool,
    TrendAnalysisTool,
    search_forums,
    analyze_reviews,
    listen_social,
    analyze_trends,
    ForumSearchOutput,
    ReviewAnalysisOutput,
    SocialListeningOutput,
    TrendAnalysisOutput,
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
    # Customer Research Tools (Phase A)
    "ForumSearchTool",
    "ReviewAnalysisTool",
    "SocialListeningTool",
    "TrendAnalysisTool",
    "search_forums",
    "analyze_reviews",
    "listen_social",
    "analyze_trends",
    "ForumSearchOutput",
    "ReviewAnalysisOutput",
    "SocialListeningOutput",
    "TrendAnalysisOutput",
    # Methodology Check Tools
    "MethodologyCheckTool",
    "check_vpc",
    "MethodologyCheckResult",
    "MethodologyIssue",
    "CheckSeverity",
    "MethodologyType",
]
