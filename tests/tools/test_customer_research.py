"""
Tests for Customer Research Tools (Phase A).

Tests ForumSearchTool, ReviewAnalysisTool, SocialListeningTool, and TrendAnalysisTool.
Uses mocking to avoid actual Tavily API calls.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

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


# ===========================================================================
# TEST FIXTURES
# ===========================================================================


@pytest.fixture
def mock_tavily_response():
    """Mock Tavily search response."""
    return """## Web Search Results for: test query
Found 5 results in 234ms

### Summary
This is a synthesized answer about the topic.

### Sources
**1. Test Result Title**
URL: https://example.com/test
Relevance: 0.95
This is the content of the test result that provides relevant information."""


@pytest.fixture
def forum_tool():
    """Create a ForumSearchTool instance."""
    return ForumSearchTool(max_results=5)


@pytest.fixture
def review_tool():
    """Create a ReviewAnalysisTool instance."""
    return ReviewAnalysisTool(max_results=5)


@pytest.fixture
def social_tool():
    """Create a SocialListeningTool instance."""
    return SocialListeningTool(max_results=5)


@pytest.fixture
def trend_tool():
    """Create a TrendAnalysisTool instance."""
    return TrendAnalysisTool(max_results=5)


# ===========================================================================
# FORUM SEARCH TOOL TESTS
# ===========================================================================


class TestForumSearchTool:
    """Tests for ForumSearchTool."""

    def test_tool_has_correct_name(self, forum_tool):
        """Tool should have correct name."""
        assert forum_tool.name == "forum_search"

    def test_tool_has_description(self, forum_tool):
        """Tool should have a description."""
        assert len(forum_tool.description) > 50
        assert "forum" in forum_tool.description.lower()

    def test_default_platforms(self, forum_tool):
        """Tool should have default platforms."""
        assert "reddit" in forum_tool.default_platforms
        assert "stackoverflow" in forum_tool.default_platforms

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_constructs_query_with_platforms(self, mock_tavily_class, mock_tavily_response):
        """Tool should construct query with platform filters."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        tool = ForumSearchTool()
        result = tool._run("startup challenges", platforms="reddit,hackernews")

        # Verify search was called
        assert mock_instance._run.called
        call_args = mock_instance._run.call_args[0][0]

        # Verify platform filters in query
        assert "site:reddit.com" in call_args
        assert "site:news.ycombinator.com" in call_args
        assert "startup challenges" in call_args

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_returns_formatted_output(self, mock_tavily_class, mock_tavily_response):
        """Tool should return formatted output with header."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        tool = ForumSearchTool()
        result = tool._run("test query")

        assert "# Forum Search: test query" in result
        assert "## Discussion Threads Found" in result
        assert "## Key Observations" in result

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_handles_exception(self, mock_tavily_class):
        """Tool should handle exceptions gracefully."""
        mock_instance = MagicMock()
        mock_instance._run.side_effect = Exception("API error")
        mock_tavily_class.return_value = mock_instance

        tool = ForumSearchTool()
        result = tool._run("test query")

        assert "Forum search failed" in result
        assert "API error" in result


# ===========================================================================
# REVIEW ANALYSIS TOOL TESTS
# ===========================================================================


class TestReviewAnalysisTool:
    """Tests for ReviewAnalysisTool."""

    def test_tool_has_correct_name(self, review_tool):
        """Tool should have correct name."""
        assert review_tool.name == "analyze_reviews"

    def test_tool_has_description(self, review_tool):
        """Tool should have a description."""
        assert len(review_tool.description) > 50
        assert "review" in review_tool.description.lower()

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_searches_multiple_categories(self, mock_tavily_class, mock_tavily_response):
        """Tool should search for negative, feature, and positive reviews."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        tool = ReviewAnalysisTool()
        result = tool._run("CRM software")

        # Should make 3 search calls (negative, feature, positive)
        assert mock_instance._run.call_count == 3

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_includes_review_sites(self, mock_tavily_class, mock_tavily_response):
        """Tool should search review sites like G2, Capterra."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        tool = ReviewAnalysisTool()
        tool._run("project management tools")

        # Check that review sites are included in search queries
        calls = [str(call) for call in mock_instance._run.call_args_list]
        combined = " ".join(calls)
        assert "g2.com" in combined
        assert "capterra.com" in combined

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_returns_structured_sections(self, mock_tavily_class, mock_tavily_response):
        """Tool should return sections for complaints, features, and positives."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        tool = ReviewAnalysisTool()
        result = tool._run("test product")

        assert "# Review Analysis: test product" in result
        assert "## Common Complaints & Pain Points" in result
        assert "## Feature Requests & Wishes" in result
        assert "## What Customers Love" in result


# ===========================================================================
# SOCIAL LISTENING TOOL TESTS
# ===========================================================================


class TestSocialListeningTool:
    """Tests for SocialListeningTool."""

    def test_tool_has_correct_name(self, social_tool):
        """Tool should have correct name."""
        assert social_tool.name == "social_listen"

    def test_tool_has_description(self, social_tool):
        """Tool should have a description."""
        assert len(social_tool.description) > 50
        assert "social" in social_tool.description.lower()

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_searches_multiple_platforms(self, mock_tavily_class, mock_tavily_response):
        """Tool should search Twitter, LinkedIn, and blogs."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        tool = SocialListeningTool()
        result = tool._run("remote work")

        # Should make 3 search calls (twitter, linkedin, mentions)
        assert mock_instance._run.call_count == 3

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_returns_platform_sections(self, mock_tavily_class, mock_tavily_response):
        """Tool should return sections per platform."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        tool = SocialListeningTool()
        result = tool._run("AI tools")

        assert "# Social Listening: AI tools" in result
        assert "## Twitter/X Discussions" in result
        assert "## LinkedIn Conversations" in result
        assert "## Industry Mentions" in result


# ===========================================================================
# TREND ANALYSIS TOOL TESTS
# ===========================================================================


class TestTrendAnalysisTool:
    """Tests for TrendAnalysisTool."""

    def test_tool_has_correct_name(self, trend_tool):
        """Tool should have correct name."""
        assert trend_tool.name == "analyze_trends"

    def test_tool_has_description(self, trend_tool):
        """Tool should have a description."""
        assert len(trend_tool.description) > 50
        assert "trend" in trend_tool.description.lower()

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_searches_multiple_aspects(self, mock_tavily_class, mock_tavily_response):
        """Tool should search trends, market size, innovation, and challenges."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        tool = TrendAnalysisTool()
        result = tool._run("SaaS market")

        # Should make 4 search calls
        assert mock_instance._run.call_count == 4

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_includes_current_year(self, mock_tavily_class, mock_tavily_response):
        """Tool should include current year in trend searches."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        tool = TrendAnalysisTool()
        tool._run("fintech")

        # Check that current year appears in queries
        current_year = str(datetime.now().year)
        calls = [str(call) for call in mock_instance._run.call_args_list]
        combined = " ".join(calls)
        assert current_year in combined

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_run_returns_trend_sections(self, mock_tavily_class, mock_tavily_response):
        """Tool should return sections for different trend aspects."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        tool = TrendAnalysisTool()
        result = tool._run("cloud computing")

        assert "# Trend Analysis: cloud computing" in result
        assert "## Market Trends & Forecasts" in result
        assert "## Market Size & Opportunity" in result
        assert "## Emerging Innovations & Disruption" in result
        assert "## Challenges & Headwinds" in result


# ===========================================================================
# CONVENIENCE FUNCTION TESTS
# ===========================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_search_forums(self, mock_tavily_class, mock_tavily_response):
        """search_forums() convenience function should work."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        result = search_forums("startup advice", "reddit")
        assert "# Forum Search:" in result

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_analyze_reviews(self, mock_tavily_class, mock_tavily_response):
        """analyze_reviews() convenience function should work."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        result = analyze_reviews("project management")
        assert "# Review Analysis:" in result

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_listen_social(self, mock_tavily_class, mock_tavily_response):
        """listen_social() convenience function should work."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        result = listen_social("AI automation")
        assert "# Social Listening:" in result

    @patch("shared.tools.customer_research.TavilySearchTool")
    def test_analyze_trends(self, mock_tavily_class, mock_tavily_response):
        """analyze_trends() convenience function should work."""
        mock_instance = MagicMock()
        mock_instance._run.return_value = mock_tavily_response
        mock_tavily_class.return_value = mock_instance

        result = analyze_trends("no-code platforms")
        assert "# Trend Analysis:" in result


# ===========================================================================
# PYDANTIC MODEL TESTS
# ===========================================================================


class TestPydanticModels:
    """Tests for Pydantic output models."""

    def test_forum_search_output_model(self):
        """ForumSearchOutput model should be valid."""
        output = ForumSearchOutput(
            query="test",
            platforms=["reddit", "stackoverflow"],
            posts=[],
            pain_points_found=["pain 1", "pain 2"],
        )
        assert output.query == "test"
        assert len(output.platforms) == 2
        assert output.timestamp is not None

    def test_review_analysis_output_model(self):
        """ReviewAnalysisOutput model should be valid."""
        output = ReviewAnalysisOutput(
            query="CRM",
            sources_analyzed=10,
            pain_points=["slow UI"],
            positive_feedback=["great support"],
            feature_requests=["mobile app"],
            competitor_mentions=["Salesforce"],
        )
        assert output.sources_analyzed == 10
        assert len(output.pain_points) == 1

    def test_social_listening_output_model(self):
        """SocialListeningOutput model should be valid."""
        output = SocialListeningOutput(
            topic="remote work",
            platforms=["twitter", "linkedin"],
            mentions=[],
            sentiment_summary="mostly positive",
            key_themes=["flexibility", "collaboration"],
        )
        assert output.topic == "remote work"
        assert len(output.key_themes) == 2

    def test_trend_analysis_output_model(self):
        """TrendAnalysisOutput model should be valid."""
        output = TrendAnalysisOutput(
            topic="SaaS",
            trends=[],
            market_signals=["growing demand"],
            opportunities=["vertical SaaS"],
        )
        assert output.topic == "SaaS"
        assert len(output.market_signals) == 1


# ===========================================================================
# IMPORT TESTS
# ===========================================================================


class TestImports:
    """Tests to verify imports work correctly."""

    def test_can_import_from_shared_tools(self):
        """Should be able to import from shared.tools."""
        from shared.tools import (
            ForumSearchTool,
            ReviewAnalysisTool,
            SocialListeningTool,
            TrendAnalysisTool,
        )

        assert ForumSearchTool is not None
        assert ReviewAnalysisTool is not None
        assert SocialListeningTool is not None
        assert TrendAnalysisTool is not None

    def test_can_import_convenience_functions(self):
        """Should be able to import convenience functions."""
        from shared.tools import (
            search_forums,
            analyze_reviews,
            listen_social,
            analyze_trends,
        )

        assert callable(search_forums)
        assert callable(analyze_reviews)
        assert callable(listen_social)
        assert callable(analyze_trends)

    def test_can_import_output_models(self):
        """Should be able to import output models."""
        from shared.tools import (
            ForumSearchOutput,
            ReviewAnalysisOutput,
            SocialListeningOutput,
            TrendAnalysisOutput,
        )

        assert ForumSearchOutput is not None
        assert ReviewAnalysisOutput is not None
        assert SocialListeningOutput is not None
        assert TrendAnalysisOutput is not None
