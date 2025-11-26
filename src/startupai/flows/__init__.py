"""CrewAI Flows for StartupAI validation system."""

from .internal_validation_flow import InternalValidationFlow, create_validation_flow
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
    # Founder validation flow
    "InternalValidationFlow",
    "create_validation_flow",
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