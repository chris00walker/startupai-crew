"""
StartupAI Shared Tools.

Tools available to agents across all crews in the validation engine.

Tool Categories:
- Research: TavilySearchTool, CustomerResearchTool
- Customer Research: ForumSearchTool, ReviewAnalysisTool, SocialListeningTool, TrendAnalysisTool
- Advanced Analysis: TranscriptionTool, InsightExtractorTool, BehaviorPatternTool, ABTestTool
- Analytics & Privacy: AnalyticsTool, AnonymizerTool, AdPlatformTool, CalendarTool
- Deployment: LandingPageDeploymentTool
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
from shared.tools.advanced_analysis import (
    TranscriptionTool,
    InsightExtractorTool,
    BehaviorPatternTool,
    ABTestTool,
    transcribe_audio,
    extract_insights,
    identify_patterns,
    run_ab_test,
    TranscriptionOutput,
    InsightExtractionOutput,
    BehaviorPatternOutput,
    ABTestResult,
)
from shared.tools.analytics_privacy import (
    AnalyticsTool,
    AnonymizerTool,
    AdPlatformTool,
    CalendarTool,
    get_analytics,
    anonymize_data,
    get_ad_metrics,
    find_interview_slots,
    AnalyticsOutput,
    AnonymizationResult,
    AdPlatformOutput,
    CalendarOutput,
)
from shared.tools.llm_tools import (
    CanvasBuilderTool,
    TestCardTool,
    LearningCardTool,
    build_canvas_element,
    design_test_card,
    capture_learning,
    CanvasBuilderOutput,
    TestCardOutput,
    LearningCardOutput,
    CanvasElement,
    TestCard,
    LearningCard,
    CanvasElementType,
    ExperimentType,
    EvidenceType,
    SignalStrength,
)
from shared.tools.landing_page_deploy import (
    LandingPageDeploymentTool,
    deploy_landing_page,
    DeploymentResult,
    LandingPageDeployInput,
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
    # Advanced Analysis Tools (Phase B)
    "TranscriptionTool",
    "InsightExtractorTool",
    "BehaviorPatternTool",
    "ABTestTool",
    "transcribe_audio",
    "extract_insights",
    "identify_patterns",
    "run_ab_test",
    "TranscriptionOutput",
    "InsightExtractionOutput",
    "BehaviorPatternOutput",
    "ABTestResult",
    # Analytics & Privacy Tools (Phase C)
    "AnalyticsTool",
    "AnonymizerTool",
    "AdPlatformTool",
    "CalendarTool",
    "get_analytics",
    "anonymize_data",
    "get_ad_metrics",
    "find_interview_slots",
    "AnalyticsOutput",
    "AnonymizationResult",
    "AdPlatformOutput",
    "CalendarOutput",
    # LLM-Based Tools (Phase D)
    "CanvasBuilderTool",
    "TestCardTool",
    "LearningCardTool",
    "build_canvas_element",
    "design_test_card",
    "capture_learning",
    "CanvasBuilderOutput",
    "TestCardOutput",
    "LearningCardOutput",
    "CanvasElement",
    "TestCard",
    "LearningCard",
    "CanvasElementType",
    "ExperimentType",
    "EvidenceType",
    "SignalStrength",
    # Deployment Tools
    "LandingPageDeploymentTool",
    "deploy_landing_page",
    "DeploymentResult",
    "LandingPageDeployInput",
]
