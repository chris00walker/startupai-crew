"""
Crew definitions for StartupAI validation engine.

14 crews organized by phase:
- Phase 0: Pass-through (no crews - Quick Start flow)
- Phase 1: BriefGenerationCrew, DiscoveryCrew, CustomerProfileCrew, ValueDesignCrew, WTPCrew, FitAssessmentCrew (6 crews, 20 agents)
- Phase 2: BuildCrew, GrowthCrew, GovernanceCrew (3 crews, 9 agents)
- Phase 3: FeasibilityBuildCrew, FeasibilityGovernanceCrew (2 crews, 5 agents)
- Phase 4: FinanceCrew, SynthesisCrew, ViabilityGovernanceCrew (3 crews, 9 agents)

Total: 14 crews, 43 agents
"""

# Phase 1: VPC Discovery (includes BriefGenerationCrew for Stage A)
from src.crews.discovery import (
    BriefGenerationCrew,
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
    # Phase 1 (includes Stage A: BriefGenerationCrew)
    "BriefGenerationCrew",
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
