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
from startupai.tools.flywheel_insights import (
    FlywheelInsightsTool,
    OutcomeTrackerTool,
    StartupStage,
    IndustryVertical,
    PredictionType,
    ValidationContext,
    PatternLearning,
    OutcomePrediction,
    FlywheelInsight,
    get_flywheel_insights,
    capture_flywheel_pattern,
    track_prediction,
    record_prediction_outcome,
)
from startupai.tools.privacy_guard import (
    PrivacyGuardTool,
    SensitivityLevel,
    ComplianceFramework,
    PrivacyViolation,
    PrivacyAuditRecord,
    PrivacyCheckResult,
    check_privacy,
    is_safe_for_storage,
    sanitize_for_flywheel,
    classify_sensitivity,
)
# Area 3: Policy Versioning
from startupai.tools.policy_bandit import (
    PolicyBandit,
    PolicyWeight,
    PolicySelectionResult,
    select_experiment_policy,
    record_experiment_outcome,
)
from startupai.tools.experiment_config_resolver import (
    ExperimentConfigResolver,
    ExperimentConfig,
    ResolverResult,
    resolve_ad_config,
    resolve_landing_page_config,
    create_ad_variant_from_config,
    update_state_with_policy,
)
# Area 6: Budget Guardrails
from startupai.tools.budget_guardrails import (
    BudgetGuardrails,
    BudgetCheckResult,
    EscalationInfo,
    check_spend_allowed,
    record_budget_override,
)
# Area 7: Business Model Viability
from startupai.tools.business_model_classifier import (
    BusinessModelClassifier,
    ClassificationResult,
    ClassificationSignals,
    classify_from_state,
    update_state_with_classification,
)
from startupai.tools.unit_economics_models import (
    UnitEconomicsModel,
    UnitEconomicsInput,
    BenchmarkData,
    SaaSB2BSMBModel,
    SaaSB2BMidMarketModel,
    SaaSB2BEnterpriseModel,
    EcommerceDTCModel,
    EcommerceMarketplaceModel,
    FintechB2BModel,
    FintechB2CModel,
    ConsultingModel,
    MODEL_REGISTRY,
    get_model_for_type,
    calculate_unit_economics as calculate_model_unit_economics,
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
    # Flywheel Insights
    "FlywheelInsightsTool",
    "OutcomeTrackerTool",
    "StartupStage",
    "IndustryVertical",
    "PredictionType",
    "ValidationContext",
    "PatternLearning",
    "OutcomePrediction",
    "FlywheelInsight",
    "get_flywheel_insights",
    "capture_flywheel_pattern",
    "track_prediction",
    "record_prediction_outcome",
    # Privacy Guard
    "PrivacyGuardTool",
    "SensitivityLevel",
    "ComplianceFramework",
    "PrivacyViolation",
    "PrivacyAuditRecord",
    "PrivacyCheckResult",
    "check_privacy",
    "is_safe_for_storage",
    "sanitize_for_flywheel",
    "classify_sensitivity",
    # Area 3: Policy Versioning
    "PolicyBandit",
    "PolicyWeight",
    "PolicySelectionResult",
    "select_experiment_policy",
    "record_experiment_outcome",
    "ExperimentConfigResolver",
    "ExperimentConfig",
    "ResolverResult",
    "resolve_ad_config",
    "resolve_landing_page_config",
    "create_ad_variant_from_config",
    "update_state_with_policy",
    # Area 6: Budget Guardrails
    "BudgetGuardrails",
    "BudgetCheckResult",
    "EscalationInfo",
    "check_spend_allowed",
    "record_budget_override",
    # Area 7: Business Model Viability
    "BusinessModelClassifier",
    "ClassificationResult",
    "ClassificationSignals",
    "classify_from_state",
    "update_state_with_classification",
    "UnitEconomicsModel",
    "UnitEconomicsInput",
    "BenchmarkData",
    "SaaSB2BSMBModel",
    "SaaSB2BMidMarketModel",
    "SaaSB2BEnterpriseModel",
    "EcommerceDTCModel",
    "EcommerceMarketplaceModel",
    "FintechB2BModel",
    "FintechB2CModel",
    "ConsultingModel",
    "MODEL_REGISTRY",
    "get_model_for_type",
    "calculate_model_unit_economics",
]
