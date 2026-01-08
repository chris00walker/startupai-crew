"""
Crew definitions for StartupAI validation engine.

14 crews organized by phase:
- Phase 0: OnboardingCrew (1 crew, 4 agents)
- Phase 1: DiscoveryCrew, CustomerProfileCrew, ValueDesignCrew, WTPCrew, FitAssessmentCrew (5 crews, 18 agents)
- Phase 2: BuildCrew, GrowthCrew, GovernanceCrew (3 crews, 9 agents)
- Phase 3: FeasibilityBuildCrew, FeasibilityGovernanceCrew (2 crews, 5 agents)
- Phase 4: FinanceCrew, SynthesisCrew, ViabilityGovernanceCrew (3 crews, 9 agents)

Total: 14 crews, 45 agents
"""

# Phase 0: Onboarding
from src.crews.onboarding import OnboardingCrew

# Phase 1: VPC Discovery
from src.crews.discovery import (
    DiscoveryCrew,
    CustomerProfileCrew,
    ValueDesignCrew,
    WTPCrew,
    FitAssessmentCrew,
)

# Phase 2: Desirability
from src.crews.desirability import BuildCrew, GrowthCrew, GovernanceCrew

# Phase 3: Feasibility
from src.crews.feasibility import FeasibilityBuildCrew, FeasibilityGovernanceCrew

# Phase 4: Viability
from src.crews.viability import FinanceCrew, SynthesisCrew, ViabilityGovernanceCrew

__all__ = [
    # Phase 0
    "OnboardingCrew",
    # Phase 1
    "DiscoveryCrew",
    "CustomerProfileCrew",
    "ValueDesignCrew",
    "WTPCrew",
    "FitAssessmentCrew",
    # Phase 2
    "BuildCrew",
    "GrowthCrew",
    "GovernanceCrew",
    # Phase 3
    "FeasibilityBuildCrew",
    "FeasibilityGovernanceCrew",
    # Phase 4
    "FinanceCrew",
    "SynthesisCrew",
    "ViabilityGovernanceCrew",
]
