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
]
