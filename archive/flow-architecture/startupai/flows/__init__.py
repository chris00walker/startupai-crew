"""CrewAI Flows for StartupAI validation system.

IMPORTANT: Only AMPEntryFlow is exported for CrewAI AMP deployment.
Sub-flows are NOT exported to prevent AMP from discovering them.
They are called internally via late imports in AMPEntryFlow.
"""

# UNIFIED FLOW - ONLY entry point for CrewAI AMP
# This is the ONLY Flow class that should be discovered by AMP
from .a_unified_flow import (
    AMPEntryFlow,
    StartupAIUnifiedFlow,  # Backward compatibility alias
    UnifiedFlowState,
    FlowType,
    create_unified_flow,
    kickoff as unified_kickoff,
    plot as unified_plot,
)

# State schemas (NOT Flow classes, safe to export)
from .state_schemas import (
    ValidationState,
    ValidationPhase,
    EvidenceStrength,
    CommitmentType,
    FeasibilityStatus,
    UnitEconomicsStatus,
    PivotRecommendation,
)

# NOTE: Sub-flows are NOT exported here to prevent CrewAI AMP discovery.
# They are imported directly in a_unified_flow.py when needed.
# If you need to use them directly (e.g., for testing), import from:
#   from startupai.flows._founder_validation_flow import FounderValidationFlow
#   from startupai.flows._consultant_onboarding_flow import ConsultantOnboardingFlow

__all__ = [
    # UNIFIED FLOW - Only entry point for AMP
    "AMPEntryFlow",
    "StartupAIUnifiedFlow",  # Backward compatibility alias
    "UnifiedFlowState",
    "FlowType",
    "create_unified_flow",
    "unified_kickoff",
    "unified_plot",
    # State schemas (not Flow classes)
    "ValidationState",
    "ValidationPhase",
    "EvidenceStrength",
    "CommitmentType",
    "FeasibilityStatus",
    "UnitEconomicsStatus",
    "PivotRecommendation",
]