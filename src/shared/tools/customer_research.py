"""
Customer Research Tools for StartupAI Validation Engine.

Phase A tools for collecting DO-indirect evidence from forums, reviews,
social media, and trend data. These tools enable research agents (D2, J1,
PAIN_RES, GAIN_RES) to gather real customer insights instead of hallucinations.

Tools:
- ForumSearchTool: Search Reddit, StackOverflow, etc. for pain points
- ReviewAnalysisTool: Analyze product reviews for patterns
- SocialListeningTool: Monitor social platforms for mentions
- TrendAnalysisTool: Analyze market trends and search patterns

All tools leverage TavilySearchTool with domain-specific query construction.
"""

from typing import List, Optional
from datetime import datetime

from crewai.tools import BaseTool
from pydantic import Field, BaseModel

from shared.tools.web_search import TavilySearchTool


# =======================================================================================
# RESULT MODELS
# =======================================================================================


class ForumPost(BaseModel):
    """Represents a forum post or discussion thread."""

    platform: str
    title: str
    url: str
    content: str
    relevance_score: float = 0.0


class ForumSearchOutput(BaseModel):
    """Structured output from forum search."""

    query: str
    platforms: List[str]
    posts: List[ForumPost]
    pain_points_found: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ReviewInsight(BaseModel):
    """Insight extracted from product reviews."""

    category: str  # pain_point, praise, feature_request, workaround
    content: str
    frequency: str  # common, occasional, rare


class ReviewAnalysisOutput(BaseModel):
    """Structured output from review analysis."""

    query: str
    sources_analyzed: int
    pain_points: List[str]
    positive_feedback: List[str]
    feature_requests: List[str]
    competitor_mentions: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SocialMention(BaseModel):
    """Represents a social media mention or discussion."""

    platform: str
    content: str
    url: str
    sentiment: str  # positive, negative, neutral


class SocialListeningOutput(BaseModel):
    """Structured output from social listening."""

    topic: str
    platforms: List[str]
    mentions: List[SocialMention]
    sentiment_summary: str
    key_themes: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class TrendData(BaseModel):
    """Represents trend information."""

    trend_name: str
    direction: str  # rising, stable, declining
    context: str


class TrendAnalysisOutput(BaseModel):
    """Structured output from trend analysis."""

    topic: str
    trends: List[TrendData]
    market_signals: List[str]
    opportunities: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# =======================================================================================
# FORUM SEARCH TOOL
# =======================================================================================


class ForumSearchTool(BaseTool):
    """
    Search forums and community platforms for customer discussions.

    Targets Reddit, StackOverflow, Discourse forums, and other discussion
    platforms where customers share pain points, workarounds, and frustrations.

    Ideal for:
    - Discovering unmet needs
    - Finding workarounds customers use
    - Understanding customer language and terminology
    - Validating problem hypotheses with real discussions
    """

    name: str = "forum_search"
    description: str = """
    Search forums (Reddit, StackOverflow, Discourse, etc.) for customer discussions
    about problems, solutions, and pain points.

    Use this tool to:
    - Find real customer discussions about a problem space
    - Discover pain points expressed in customer's own words
    - Identify workarounds people are using
    - Understand how customers describe their challenges

    Input: A search query describing what you want to find discussions about.
    Optional: Specify platforms as comma-separated list (default: reddit,stackoverflow).

    Example: "small business accounting challenges"
    """

    max_results: int = Field(
        default=10, description="Maximum number of results to return"
    )
    default_platforms: str = Field(
        default="reddit,stackoverflow,quora",
        description="Default platforms to search if none specified",
    )

    def _run(self, query: str, platforms: Optional[str] = None) -> str:
        """
        Search forums for customer discussions.

        Args:
            query: The search query
            platforms: Comma-separated list of platforms (e.g., "reddit,stackoverflow")

        Returns:
            Formatted forum search results with pain points highlighted
        """
        try:
            search = TavilySearchTool(max_results=self.max_results, search_depth="advanced")

            # Use provided platforms or defaults
            platform_list = (platforms or self.default_platforms).split(",")
            platform_list = [p.strip() for p in platform_list]

            # Build domain filter for the query
            domain_filters = []
            for platform in platform_list:
                if platform.lower() == "reddit":
                    domain_filters.append("site:reddit.com")
                elif platform.lower() == "stackoverflow":
                    domain_filters.append("site:stackoverflow.com")
                elif platform.lower() == "quora":
                    domain_filters.append("site:quora.com")
                elif platform.lower() == "discourse":
                    domain_filters.append("site:discourse.org")
                elif platform.lower() == "hackernews":
                    domain_filters.append("site:news.ycombinator.com")
                else:
                    domain_filters.append(f"site:{platform}.com")

            # Construct forum-specific query
            domain_filter = " OR ".join(domain_filters)
            forum_query = f"{query} ({domain_filter})"

            # Execute search
            results = search._run(forum_query)

            # Format output
            output_lines = [
                f"# Forum Search: {query}",
                f"**Platforms searched**: {', '.join(platform_list)}",
                "",
                "## Discussion Threads Found",
                "",
                results,
                "",
                "## Key Observations",
                "",
                "Look for recurring themes in the discussions above:",
                "- What problems do people describe most often?",
                "- What workarounds are they using?",
                "- What language do they use to describe their pain?",
                "- What solutions have they tried and rejected?",
            ]

            return "\n".join(output_lines)

        except Exception as e:
            return f"Forum search failed: {str(e)}"

    async def _arun(self, query: str, platforms: Optional[str] = None) -> str:
        """Async version - delegates to sync."""
        return self._run(query, platforms)


# =======================================================================================
# REVIEW ANALYSIS TOOL
# =======================================================================================


class ReviewAnalysisTool(BaseTool):
    """
    Analyze product reviews to identify pain points and feature requests.

    Searches for reviews across G2, Capterra, TrustRadius, Amazon, and other
    review platforms to understand what customers love and hate about existing
    solutions.

    Ideal for:
    - Competitor analysis
    - Identifying gaps in existing solutions
    - Understanding customer expectations
    - Finding opportunities for differentiation
    """

    name: str = "analyze_reviews"
    description: str = """
    Analyze product reviews from G2, Capterra, TrustRadius, and other review sites
    to identify patterns in customer feedback.

    Use this tool to:
    - Find what customers hate about competitor products
    - Discover features customers wish existed
    - Understand pricing sensitivity and expectations
    - Identify common complaints and pain points

    Input: Product category or specific product name to analyze reviews for.

    Example: "CRM software for small businesses"
    """

    max_results: int = Field(
        default=12, description="Maximum number of review sources to analyze"
    )

    def _run(self, product_or_category: str) -> str:
        """
        Analyze reviews for a product or category.

        Args:
            product_or_category: Product name or category to research

        Returns:
            Formatted review analysis with pain points and feature requests
        """
        try:
            search = TavilySearchTool(max_results=self.max_results, search_depth="advanced")

            # Search for negative reviews (pain points)
            negative_query = (
                f"{product_or_category} reviews complaints problems issues "
                "(site:g2.com OR site:capterra.com OR site:trustradius.com OR "
                "site:amazon.com/review OR site:producthunt.com)"
            )
            negative_results = search._run(negative_query)

            # Search for feature requests and wishes
            feature_query = (
                f"{product_or_category} reviews \"wish\" OR \"missing\" OR \"needs\" OR "
                "\"feature request\" "
                "(site:g2.com OR site:capterra.com OR site:trustradius.com)"
            )
            feature_results = search._run(feature_query)

            # Search for positive feedback (to understand what works)
            positive_query = (
                f"{product_or_category} reviews best features love great "
                "(site:g2.com OR site:capterra.com OR site:trustradius.com)"
            )
            positive_results = search._run(positive_query)

            # Format output
            output_lines = [
                f"# Review Analysis: {product_or_category}",
                "",
                "## Common Complaints & Pain Points",
                "",
                negative_results,
                "",
                "---",
                "",
                "## Feature Requests & Wishes",
                "",
                feature_results,
                "",
                "---",
                "",
                "## What Customers Love (Competitive Table Stakes)",
                "",
                positive_results,
                "",
                "---",
                "",
                "## Analysis Framework",
                "",
                "When reading the reviews above, identify:",
                "1. **Must-Have Features**: What do all positive reviews mention?",
                "2. **Pain Points**: What frustrations appear repeatedly?",
                "3. **Opportunities**: What gaps exist that no product fills?",
                "4. **Pricing Signals**: Any mentions of value vs cost?",
            ]

            return "\n".join(output_lines)

        except Exception as e:
            return f"Review analysis failed: {str(e)}"

    async def _arun(self, product_or_category: str) -> str:
        """Async version - delegates to sync."""
        return self._run(product_or_category)


# =======================================================================================
# SOCIAL LISTENING TOOL
# =======================================================================================


class SocialListeningTool(BaseTool):
    """
    Monitor social media platforms for mentions and discussions.

    Searches Twitter/X, LinkedIn, and other social platforms for conversations
    about topics, brands, or problems. Useful for understanding sentiment and
    trending discussions.

    Ideal for:
    - Tracking brand mentions
    - Understanding market sentiment
    - Finding influencers and thought leaders
    - Discovering emerging conversations
    """

    name: str = "social_listen"
    description: str = """
    Monitor social media platforms (Twitter/X, LinkedIn, etc.) for mentions
    and discussions about a topic, brand, or problem space.

    Use this tool to:
    - Find what people are saying about a topic on social media
    - Identify sentiment (positive/negative) around a subject
    - Discover influencers discussing the topic
    - Find trending conversations and hashtags

    Input: Topic, brand, or problem to monitor.

    Example: "remote team collaboration challenges"
    """

    max_results: int = Field(
        default=10, description="Maximum number of results to return"
    )

    def _run(self, topic: str) -> str:
        """
        Search social platforms for discussions about a topic.

        Args:
            topic: Topic, brand, or problem to monitor

        Returns:
            Formatted social listening results with sentiment analysis
        """
        try:
            search = TavilySearchTool(max_results=self.max_results, search_depth="advanced")

            # Search Twitter/X discussions
            twitter_query = (
                f"{topic} (site:twitter.com OR site:x.com) "
                "discussion opinion thoughts"
            )
            twitter_results = search._run(twitter_query)

            # Search LinkedIn discussions
            linkedin_query = (
                f"{topic} site:linkedin.com "
                "post article discussion"
            )
            linkedin_results = search._run(linkedin_query)

            # Search for news and blog mentions
            mentions_query = (
                f"{topic} mention discussion trend "
                "(site:medium.com OR site:substack.com OR site:techcrunch.com)"
            )
            mentions_results = search._run(mentions_query)

            # Format output
            output_lines = [
                f"# Social Listening: {topic}",
                "",
                "## Twitter/X Discussions",
                "",
                twitter_results,
                "",
                "---",
                "",
                "## LinkedIn Conversations",
                "",
                linkedin_results,
                "",
                "---",
                "",
                "## Industry Mentions (Blogs, News)",
                "",
                mentions_results,
                "",
                "---",
                "",
                "## Sentiment Analysis Guide",
                "",
                "Review the social mentions above and assess:",
                "- **Overall Sentiment**: Is discussion mostly positive, negative, or neutral?",
                "- **Key Themes**: What topics come up repeatedly?",
                "- **Influencers**: Who is driving the conversation?",
                "- **Pain Points**: What frustrations are people expressing?",
            ]

            return "\n".join(output_lines)

        except Exception as e:
            return f"Social listening failed: {str(e)}"

    async def _arun(self, topic: str) -> str:
        """Async version - delegates to sync."""
        return self._run(topic)


# =======================================================================================
# TREND ANALYSIS TOOL
# =======================================================================================


class TrendAnalysisTool(BaseTool):
    """
    Analyze market trends and search patterns for a topic.

    Searches for trend reports, market analysis, and industry forecasts to
    understand market direction and timing.

    Ideal for:
    - Market sizing and opportunity assessment
    - Understanding industry direction
    - Validating market timing
    - Identifying emerging opportunities
    """

    name: str = "analyze_trends"
    description: str = """
    Analyze market trends, industry direction, and emerging opportunities
    for a topic or market segment.

    Use this tool to:
    - Understand if a market is growing, stable, or declining
    - Find industry reports and forecasts
    - Identify emerging trends and opportunities
    - Validate market timing for an idea

    Input: Topic, market, or industry to analyze trends for.

    Example: "AI-powered customer service tools"
    """

    max_results: int = Field(
        default=10, description="Maximum number of trend sources to analyze"
    )

    def _run(self, topic: str) -> str:
        """
        Analyze trends for a topic or market.

        Args:
            topic: Topic, market, or industry to analyze

        Returns:
            Formatted trend analysis with market signals
        """
        try:
            search = TavilySearchTool(max_results=self.max_results, search_depth="advanced")

            # Get current year for time-relevant searches
            current_year = datetime.now().year

            # Search for market trends and forecasts
            trends_query = (
                f"{topic} market trends {current_year} forecast growth "
                "industry report analysis"
            )
            trends_results = search._run(trends_query)

            # Search for market size and opportunity
            market_query = (
                f"{topic} market size TAM SAM opportunity {current_year} "
                "billion million revenue"
            )
            market_results = search._run(market_query)

            # Search for emerging technologies and innovations
            innovation_query = (
                f"{topic} emerging innovation new technology {current_year} "
                "startup disruption"
            )
            innovation_results = search._run(innovation_query)

            # Search for challenges and headwinds
            challenges_query = (
                f"{topic} challenges obstacles barriers {current_year} "
                "decline risk problem"
            )
            challenges_results = search._run(challenges_query)

            # Format output
            output_lines = [
                f"# Trend Analysis: {topic}",
                "",
                "## Market Trends & Forecasts",
                "",
                trends_results,
                "",
                "---",
                "",
                "## Market Size & Opportunity",
                "",
                market_results,
                "",
                "---",
                "",
                "## Emerging Innovations & Disruption",
                "",
                innovation_results,
                "",
                "---",
                "",
                "## Challenges & Headwinds",
                "",
                challenges_results,
                "",
                "---",
                "",
                "## Trend Interpretation Guide",
                "",
                "From the data above, assess:",
                "- **Market Direction**: Is this market growing, stable, or declining?",
                "- **Timing**: Is now a good time to enter this market?",
                "- **Opportunities**: What gaps exist that could be filled?",
                "- **Risks**: What headwinds or challenges exist?",
                "- **Competition**: How crowded is this space?",
            ]

            return "\n".join(output_lines)

        except Exception as e:
            return f"Trend analysis failed: {str(e)}"

    async def _arun(self, topic: str) -> str:
        """Async version - delegates to sync."""
        return self._run(topic)


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================


def search_forums(query: str, platforms: str = "reddit,stackoverflow") -> str:
    """
    Convenience function for forum search.

    Args:
        query: Search query
        platforms: Comma-separated list of platforms

    Returns:
        Formatted forum search results
    """
    tool = ForumSearchTool()
    return tool._run(query, platforms)


def analyze_reviews(product_or_category: str) -> str:
    """
    Convenience function for review analysis.

    Args:
        product_or_category: Product or category to analyze

    Returns:
        Formatted review analysis
    """
    tool = ReviewAnalysisTool()
    return tool._run(product_or_category)


def listen_social(topic: str) -> str:
    """
    Convenience function for social listening.

    Args:
        topic: Topic to monitor

    Returns:
        Formatted social listening results
    """
    tool = SocialListeningTool()
    return tool._run(topic)


def analyze_trends(topic: str) -> str:
    """
    Convenience function for trend analysis.

    Args:
        topic: Topic or market to analyze

    Returns:
        Formatted trend analysis
    """
    tool = TrendAnalysisTool()
    return tool._run(topic)
