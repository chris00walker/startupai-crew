"""
State management for Modal serverless validation.

Provides Pydantic models for validation state and Supabase persistence.
"""

from .models import (
    # Full state models
    ValidationRunState,
    PhaseState,
    # Founder's Brief and sub-models
    FoundersBrief,
    TheIdea,
    ProblemHypothesis,
    CustomerHypothesis,
    SolutionHypothesis,
    Assumption,
    AssumptionCategory,
    SuccessCriteria,
    FounderContext,
    QAStatus,
    InterviewMetadata,
    # VPC models
    CustomerProfile,
    ValueMap,
    FitAssessment,
    # Evidence models
    DesirabilityEvidence,
    FeasibilityEvidence,
    ViabilityEvidence,
    # Checkpoints and signals
    HITLCheckpoint,
    ValidationSignal,
    PivotRecommendation,
)
from .persistence import (
    checkpoint_state,
    resume_state,
    update_progress,
    create_hitl_request,
    get_hitl_decision,
)

__all__ = [
    # Full state models
    "ValidationRunState",
    "PhaseState",
    # Founder's Brief and sub-models
    "FoundersBrief",
    "TheIdea",
    "ProblemHypothesis",
    "CustomerHypothesis",
    "SolutionHypothesis",
    "Assumption",
    "AssumptionCategory",
    "SuccessCriteria",
    "FounderContext",
    "QAStatus",
    "InterviewMetadata",
    # VPC models
    "CustomerProfile",
    "ValueMap",
    "FitAssessment",
    # Evidence models
    "DesirabilityEvidence",
    "FeasibilityEvidence",
    "ViabilityEvidence",
    # Checkpoints and signals
    "HITLCheckpoint",
    "ValidationSignal",
    "PivotRecommendation",
    # Persistence functions
    "checkpoint_state",
    "resume_state",
    "update_progress",
    "create_hitl_request",
    "get_hitl_decision",
]
