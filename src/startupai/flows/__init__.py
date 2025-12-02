"""CrewAI Flows for StartupAI validation system."""

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
    # Founder validation flow (primary names)
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
    # Consultant onboarding flow
    "ConsultantOnboardingFlow",
    "create_consultant_onboarding_flow",
    "ConsultantOnboardingState",
    "ConsultantPracticeData",
]