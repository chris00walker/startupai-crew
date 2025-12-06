"""
Web Search Tools for StartupAI.

Provides real web search capabilities using Tavily API for market research,
competitor analysis, and customer discovery.

Tavily is an AI-optimized search API that returns relevant, structured results
ideal for agent workloads ($0.01/search).
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from crewai.tools import BaseTool
from pydantic import Field, BaseModel

from startupai.models.tool_contracts import ToolResult, ToolStatus


# =======================================================================================
# SEARCH RESULT MODELS
# =======================================================================================

class SearchResult(BaseModel):
    """Individual search result from Tavily."""
    title: str
    url: str
    content: str
    score: float = 0.0
    published_date: Optional[str] = None


class WebSearchOutput(BaseModel):
    """Structured output from web search."""
    query: str
    results: List[SearchResult]
    answer: Optional[str] = None  # Tavily can provide a synthesized answer
    response_time_ms: int = 0
    result_count: int = 0


class CompetitorSearchOutput(BaseModel):
    """Structured output for competitor research."""
    competitor_name: str
    website: Optional[str] = None
    description: Optional[str] = None
    key_features: List[str] = Field(default_factory=list)
    pricing_info: Optional[str] = None
    target_market: Optional[str] = None
    sources: List[str] = Field(default_factory=list)


class MarketResearchOutput(BaseModel):
    """Structured output for market research."""
    topic: str
    market_size: Optional[str] = None
    growth_rate: Optional[str] = None
    key_trends: List[str] = Field(default_factory=list)
    key_players: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)


# =======================================================================================
# TAVILY SEARCH TOOL
# =======================================================================================

class TavilySearchTool(BaseTool):
    """
    Web search tool using Tavily API for AI-optimized search results.

    Tavily provides:
    - Relevance-scored search results
    - Content extraction from web pages
    - Optional synthesized answers
    - Fast response times (~1-2 seconds)

    Requires TAVILY_API_KEY environment variable.
    """

    name: str = "web_search"
    description: str = """
    Search the web for current information about markets, competitors, customers,
    trends, and business topics. Returns relevant search results with content excerpts.

    Use this tool to:
    - Research target customer segments and their behaviors
    - Find information about competitors and their offerings
    - Discover market trends and industry insights
    - Validate assumptions with real-world data
    - Find pricing benchmarks and business model examples

    Input should be a clear search query describing what you want to find.
    """

    search_depth: str = Field(
        default="advanced",
        description="Search depth: 'basic' for faster results, 'advanced' for more comprehensive"
    )
    max_results: int = Field(
        default=5,
        description="Maximum number of search results to return"
    )
    include_answer: bool = Field(
        default=True,
        description="Whether to include a synthesized answer from Tavily"
    )

    def _get_client(self):
        """Get Tavily client with API key from environment."""
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable not set")

        try:
            from tavily import TavilyClient
            return TavilyClient(api_key=api_key)
        except ImportError:
            raise ImportError("tavily-python package not installed. Run: pip install tavily-python")

    def _run(self, query: str) -> str:
        """
        Execute web search and return formatted results.

        Args:
            query: The search query string

        Returns:
            Formatted string with search results
        """
        try:
            start_time = datetime.now()

            # Get Tavily client
            client = self._get_client()

            # Execute search
            response = client.search(
                query=query,
                search_depth=self.search_depth,
                max_results=self.max_results,
                include_answer=self.include_answer,
            )

            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Parse results
            results = []
            for item in response.get("results", []):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                    published_date=item.get("published_date"),
                ))

            output = WebSearchOutput(
                query=query,
                results=results,
                answer=response.get("answer"),
                response_time_ms=elapsed_ms,
                result_count=len(results),
            )

            # Format output for agent consumption
            return self._format_results(output)

        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except ImportError as e:
            return f"Dependency error: {str(e)}"
        except Exception as e:
            return f"Search failed: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Async version - delegates to sync for now."""
        return self._run(query)

    def _format_results(self, output: WebSearchOutput) -> str:
        """Format search results for agent consumption."""
        lines = [
            f"## Web Search Results for: {output.query}",
            f"Found {output.result_count} results in {output.response_time_ms}ms",
            "",
        ]

        # Include synthesized answer if available
        if output.answer:
            lines.extend([
                "### Summary",
                output.answer,
                "",
            ])

        # Include individual results
        lines.append("### Sources")
        for i, result in enumerate(output.results, 1):
            lines.extend([
                f"**{i}. {result.title}**",
                f"URL: {result.url}",
                f"Relevance: {result.score:.2f}",
                f"{result.content[:500]}..." if len(result.content) > 500 else result.content,
                "",
            ])

        return "\n".join(lines)

    def search_with_result(self, query: str) -> ToolResult[WebSearchOutput]:
        """
        Execute search and return structured ToolResult.

        Use this method when you need programmatic access to results
        rather than formatted text.
        """
        try:
            start_time = datetime.now()
            client = self._get_client()

            response = client.search(
                query=query,
                search_depth=self.search_depth,
                max_results=self.max_results,
                include_answer=self.include_answer,
            )

            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            results = [
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                    published_date=item.get("published_date"),
                )
                for item in response.get("results", [])
            ]

            output = WebSearchOutput(
                query=query,
                results=results,
                answer=response.get("answer"),
                response_time_ms=elapsed_ms,
                result_count=len(results),
            )

            return ToolResult.success(output, execution_time_ms=elapsed_ms)

        except Exception as e:
            return ToolResult.failure(str(e), code="SEARCH_ERROR")


# =======================================================================================
# SPECIALIZED SEARCH TOOLS
# =======================================================================================

class CompetitorResearchTool(BaseTool):
    """
    Specialized tool for researching competitors.

    Performs targeted searches to gather competitor intelligence including
    features, pricing, target markets, and positioning.
    """

    name: str = "competitor_research"
    description: str = """
    Research a specific competitor to gather intelligence about their business.

    Returns structured information about:
    - Company description and positioning
    - Key features and capabilities
    - Pricing information (if publicly available)
    - Target market and customer segments

    Input should be the competitor name or company to research.
    """

    def _run(self, competitor_name: str) -> str:
        """
        Research a competitor and return structured findings.

        Args:
            competitor_name: Name of the competitor to research

        Returns:
            Formatted competitor analysis
        """
        try:
            search_tool = TavilySearchTool(max_results=8, search_depth="advanced")

            # Search for general info
            general_results = search_tool.search_with_result(
                f"{competitor_name} company overview features pricing"
            )

            if not general_results.is_usable:
                return f"Failed to research {competitor_name}: {general_results.error_message}"

            # Extract information from results
            all_content = "\n".join([
                r.content for r in general_results.data.results
            ])
            sources = [r.url for r in general_results.data.results]

            # Find website
            website = None
            for result in general_results.data.results:
                if competitor_name.lower().replace(" ", "") in result.url.lower():
                    website = result.url
                    break

            output = CompetitorSearchOutput(
                competitor_name=competitor_name,
                website=website,
                description=general_results.data.answer or "No description available",
                sources=sources[:5],
            )

            return self._format_output(output, all_content)

        except Exception as e:
            return f"Competitor research failed: {str(e)}"

    async def _arun(self, competitor_name: str) -> str:
        """Async version - delegates to sync."""
        return self._run(competitor_name)

    def _format_output(self, output: CompetitorSearchOutput, raw_content: str) -> str:
        """Format competitor research output."""
        lines = [
            f"## Competitor Analysis: {output.competitor_name}",
            "",
            f"**Website:** {output.website or 'Not found'}",
            "",
            "### Overview",
            output.description or "No overview available.",
            "",
            "### Raw Research Data",
            raw_content[:2000] + "..." if len(raw_content) > 2000 else raw_content,
            "",
            "### Sources",
        ]
        for source in output.sources:
            lines.append(f"- {source}")

        return "\n".join(lines)


class MarketResearchTool(BaseTool):
    """
    Specialized tool for market research and industry analysis.

    Performs targeted searches to gather market intelligence including
    market size, trends, key players, and opportunities.
    """

    name: str = "market_research"
    description: str = """
    Research a market or industry to gather intelligence for validation.

    Returns structured information about:
    - Market size and growth rates
    - Key trends and developments
    - Major players and competitors
    - Challenges and opportunities

    Input should describe the market or industry to research
    (e.g., "B2B SaaS for HR", "Electric vehicle charging market").
    """

    def _run(self, market_topic: str) -> str:
        """
        Research a market and return structured findings.

        Args:
            market_topic: Description of the market to research

        Returns:
            Formatted market analysis
        """
        try:
            search_tool = TavilySearchTool(max_results=10, search_depth="advanced")

            # Search for market information
            market_results = search_tool.search_with_result(
                f"{market_topic} market size trends growth 2024 2025"
            )

            if not market_results.is_usable:
                return f"Failed to research market: {market_results.error_message}"

            # Search for key players
            players_results = search_tool.search_with_result(
                f"{market_topic} top companies competitors leaders"
            )

            sources = [r.url for r in market_results.data.results]
            if players_results.is_usable:
                sources.extend([r.url for r in players_results.data.results[:3]])

            output = MarketResearchOutput(
                topic=market_topic,
                sources=list(set(sources))[:8],
            )

            # Combine content for analysis
            all_content = "\n".join([
                r.content for r in market_results.data.results
            ])
            if players_results.is_usable:
                all_content += "\n" + "\n".join([
                    r.content for r in players_results.data.results
                ])

            return self._format_output(output, market_results.data.answer, all_content)

        except Exception as e:
            return f"Market research failed: {str(e)}"

    async def _arun(self, market_topic: str) -> str:
        """Async version - delegates to sync."""
        return self._run(market_topic)

    def _format_output(
        self,
        output: MarketResearchOutput,
        summary: Optional[str],
        raw_content: str
    ) -> str:
        """Format market research output."""
        lines = [
            f"## Market Research: {output.topic}",
            "",
        ]

        if summary:
            lines.extend([
                "### Summary",
                summary,
                "",
            ])

        lines.extend([
            "### Research Data",
            raw_content[:3000] + "..." if len(raw_content) > 3000 else raw_content,
            "",
            "### Sources",
        ])
        for source in output.sources:
            lines.append(f"- {source}")

        return "\n".join(lines)


class CustomerResearchTool(BaseTool):
    """
    Specialized tool for customer segment research.

    Performs targeted searches to understand customer segments,
    their pain points, behaviors, and where they gather online.
    """

    name: str = "customer_research"
    description: str = """
    Research a customer segment to understand their needs and behaviors.

    Returns information about:
    - Common pain points and challenges
    - Where this audience gathers online (communities, forums)
    - How they currently solve the problem
    - What they value in solutions

    Input should describe the customer segment to research
    (e.g., "early-stage startup founders", "HR managers at mid-size companies").
    """

    def _run(self, customer_segment: str) -> str:
        """
        Research a customer segment.

        Args:
            customer_segment: Description of the customer segment

        Returns:
            Formatted customer research findings
        """
        try:
            search_tool = TavilySearchTool(max_results=8, search_depth="advanced")

            # Search for pain points and challenges
            pain_results = search_tool.search_with_result(
                f"{customer_segment} challenges pain points problems struggles"
            )

            # Search for communities and gathering places
            community_results = search_tool.search_with_result(
                f"{customer_segment} communities forums Reddit LinkedIn groups"
            )

            sources = []
            content_parts = []

            if pain_results.is_usable:
                sources.extend([r.url for r in pain_results.data.results])
                content_parts.append("## Pain Points & Challenges")
                if pain_results.data.answer:
                    content_parts.append(pain_results.data.answer)
                content_parts.append("")
                for r in pain_results.data.results[:3]:
                    content_parts.append(f"- {r.content[:300]}...")

            if community_results.is_usable:
                sources.extend([r.url for r in community_results.data.results])
                content_parts.append("\n## Communities & Gathering Places")
                if community_results.data.answer:
                    content_parts.append(community_results.data.answer)
                content_parts.append("")
                for r in community_results.data.results[:3]:
                    content_parts.append(f"- **{r.title}**: {r.url}")

            content_parts.append("\n## Sources")
            for source in list(set(sources))[:6]:
                content_parts.append(f"- {source}")

            return f"# Customer Research: {customer_segment}\n\n" + "\n".join(content_parts)

        except Exception as e:
            return f"Customer research failed: {str(e)}"

    async def _arun(self, customer_segment: str) -> str:
        """Async version - delegates to sync."""
        return self._run(customer_segment)


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def web_search(query: str, max_results: int = 5) -> str:
    """
    Convenience function for quick web searches.

    Args:
        query: Search query
        max_results: Maximum results to return

    Returns:
        Formatted search results
    """
    tool = TavilySearchTool(max_results=max_results)
    return tool._run(query)


def research_competitor(competitor_name: str) -> str:
    """
    Convenience function for competitor research.

    Args:
        competitor_name: Name of competitor to research

    Returns:
        Formatted competitor analysis
    """
    tool = CompetitorResearchTool()
    return tool._run(competitor_name)


def research_market(market_topic: str) -> str:
    """
    Convenience function for market research.

    Args:
        market_topic: Market or industry to research

    Returns:
        Formatted market analysis
    """
    tool = MarketResearchTool()
    return tool._run(market_topic)


def research_customers(customer_segment: str) -> str:
    """
    Convenience function for customer research.

    Args:
        customer_segment: Customer segment to research

    Returns:
        Formatted customer research
    """
    tool = CustomerResearchTool()
    return tool._run(customer_segment)
