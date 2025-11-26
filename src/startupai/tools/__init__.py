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
from startupai.tools.landing_page_deploy import (
    LandingPageDeploymentTool,
    DeploymentResult,
    deploy_landing_page,
)
from startupai.tools.guardian_review import (
    GuardianReviewTool,
    GuardianReviewResult,
    ReviewDecision,
    review_landing_page,
    review_ad_creative,
)
from startupai.tools.methodology_check import (
    MethodologyCheckTool,
    MethodologyCheckResult,
    MethodologyType,
    check_vpc,
    check_bmc,
)
from startupai.tools.viability_approval import (
    ViabilityApprovalTool,
    ViabilityApprovalResult,
    ViabilityStatus,
    PivotRecommendation,
    analyze_viability,
    format_viability_for_dashboard,
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
    # Landing Page Deployment
    "LandingPageDeploymentTool",
    "DeploymentResult",
    "deploy_landing_page",
    # Guardian Review (HITL)
    "GuardianReviewTool",
    "GuardianReviewResult",
    "ReviewDecision",
    "review_landing_page",
    "review_ad_creative",
    # Methodology Check
    "MethodologyCheckTool",
    "MethodologyCheckResult",
    "MethodologyType",
    "check_vpc",
    "check_bmc",
    # Viability Approval (HITL)
    "ViabilityApprovalTool",
    "ViabilityApprovalResult",
    "ViabilityStatus",
    "PivotRecommendation",
    "analyze_viability",
    "format_viability_for_dashboard",
]
