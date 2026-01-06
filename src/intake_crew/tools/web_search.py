"""
Web Search Tools for StartupAI Intake Crew.

Provides real web search capabilities using Tavily API for market research,
competitor analysis, and customer discovery.

Tavily is an AI-optimized search API that returns relevant, structured results
ideal for agent workloads.

Simplified from: archive/flow-architecture/startupai/tools/web_search.py
"""

import os
from typing import List, Optional
from datetime import datetime

from crewai.tools import BaseTool
from pydantic import Field, BaseModel


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
    answer: Optional[str] = None
    response_time_ms: int = 0
    result_count: int = 0


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
        description="Search depth: 'basic' for faster results, 'advanced' for more comprehensive",
    )
    max_results: int = Field(
        default=5, description="Maximum number of search results to return"
    )
    include_answer: bool = Field(
        default=True, description="Whether to include a synthesized answer from Tavily"
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
            raise ImportError(
                "tavily-python package not installed. Run: pip install tavily-python"
            )

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
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        content=item.get("content", ""),
                        score=item.get("score", 0.0),
                        published_date=item.get("published_date"),
                    )
                )

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
            lines.extend(
                [
                    "### Summary",
                    output.answer,
                    "",
                ]
            )

        # Include individual results
        lines.append("### Sources")
        for i, result in enumerate(output.results, 1):
            lines.extend(
                [
                    f"**{i}. {result.title}**",
                    f"URL: {result.url}",
                    f"Relevance: {result.score:.2f}",
                    (
                        f"{result.content[:500]}..."
                        if len(result.content) > 500
                        else result.content
                    ),
                    "",
                ]
            )

        return "\n".join(lines)


# =======================================================================================
# CUSTOMER RESEARCH TOOL
# =======================================================================================


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
            pain_query = f"{customer_segment} challenges pain points problems struggles"
            pain_results = search_tool._run(pain_query)

            # Search for communities and gathering places
            community_query = (
                f"{customer_segment} communities forums Reddit LinkedIn groups"
            )
            community_results = search_tool._run(community_query)

            # Combine results
            output = [
                f"# Customer Research: {customer_segment}",
                "",
                "## Pain Points & Challenges",
                pain_results,
                "",
                "## Communities & Gathering Places",
                community_results,
            ]

            return "\n".join(output)

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
