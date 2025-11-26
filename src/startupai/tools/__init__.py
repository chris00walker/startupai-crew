"""
StartupAI Tools Package.

Provides specialized tools for the validation flow including
anonymization, learning capture, retrieval, web research, and financial data.
"""

from startupai.tools.anonymizer import AnonymizerTool, anonymize_text
from startupai.tools.learning_capture import LearningCaptureTool
from startupai.tools.learning_retrieval import LearningRetrievalTool
from startupai.tools.web_search import (
    TavilySearchTool,
    CompetitorResearchTool,
    MarketResearchTool,
    CustomerResearchTool,
    web_search,
    research_competitor,
    research_market,
    research_customers,
)
from startupai.tools.financial_data import (
    IndustryBenchmarkTool,
    UnitEconomicsCalculatorTool,
    get_industry_benchmarks,
    calculate_unit_economics,
)
from startupai.tools.landing_page import (
    LandingPageGeneratorTool,
    LandingPageVariant,
    LandingPageStyle,
    generate_landing_pages,
)
from startupai.tools.code_validator import (
    CodeValidatorTool,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    ValidationCategory,
    validate_html,
    is_deployment_ready,
)

__all__ = [
    # Anonymization
    "AnonymizerTool",
    "anonymize_text",
    # Learning
    "LearningCaptureTool",
    "LearningRetrievalTool",
    # Web Research
    "TavilySearchTool",
    "CompetitorResearchTool",
    "MarketResearchTool",
    "CustomerResearchTool",
    "web_search",
    "research_competitor",
    "research_market",
    "research_customers",
    # Financial Data
    "IndustryBenchmarkTool",
    "UnitEconomicsCalculatorTool",
    "get_industry_benchmarks",
    "calculate_unit_economics",
    # Landing Page Generation
    "LandingPageGeneratorTool",
    "LandingPageVariant",
    "LandingPageStyle",
    "generate_landing_pages",
    # Code Validation
    "CodeValidatorTool",
    "ValidationResult",
    "ValidationIssue",
    "ValidationSeverity",
    "ValidationCategory",
    "validate_html",
    "is_deployment_ready",
]
