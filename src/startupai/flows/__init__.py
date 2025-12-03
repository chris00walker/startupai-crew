"""CrewAI Flows for StartupAI validation system.

IMPORTANT: The unified flow (StartupAIUnifiedFlow) is imported FIRST and is
the PRIMARY flow for CrewAI AMP deployment. It routes to sub-flows based on
the 'flow_type' input parameter.

Sub-flows (FounderValidationFlow, ConsultantOnboardingFlow) should NOT be
instantiated directly by CrewAI AMP - they are called internally by the
unified flow dispatcher.
"""

# UNIFIED FLOW - Primary entry point for CrewAI AMP
# This MUST be imported first to ensure it's discovered first by AMP
from .a_unified_flow import (
    StartupAIUnifiedFlow,
    UnifiedFlowState,
    FlowType,
    create_unified_flow,
    kickoff as unified_kickoff,
    plot as unified_plot,
)

# Sub-flows (internal use only - called by unified flow)
from .founder_validation_flow import (
    FounderValidationFlow,
    create_founder_validation_flow,
    # Backwards compatibility aliases
    InternalValidationFlow,
    create_validation_flow,
)
from .consultant_onboarding_flow import (
    ConsultantOnboardingFlow,
    create_consultant_onboarding_flow,
    ConsultantOnboardingState,
    ConsultantPracticeData,
)

# State schemas
from .state_schemas import (
    ValidationState,
    ValidationPhase,
    EvidenceStrength,
    CommitmentType,
    FeasibilityStatus,
    UnitEconomicsStatus,
    PivotRecommendation,
)

__all__ = [
    # UNIFIED FLOW - Primary for AMP
    "StartupAIUnifiedFlow",
    "UnifiedFlowState",
    "FlowType",
    "create_unified_flow",
    "unified_kickoff",
    "unified_plot",
    # Founder validation flow (sub-flow)
    "FounderValidationFlow",
    "create_founder_validation_flow",
    # Backwards compatibility aliases
    "InternalValidationFlow",
    "create_validation_flow",
    # State schemas
    "ValidationState",
    "ValidationPhase",
    "EvidenceStrength",
    "CommitmentType",
    "FeasibilityStatus",
    "UnitEconomicsStatus",
    "PivotRecommendation",
    # Consultant onboarding flow (sub-flow)
    "ConsultantOnboardingFlow",
    "create_consultant_onboarding_flow",
    "ConsultantOnboardingState",
    "ConsultantPracticeData",
]