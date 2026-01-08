"""
Phase execution modules for Modal serverless validation.

Each phase is a separate Modal function that can be checkpointed/resumed.

Phases:
    - Phase 0: Onboarding (Founder's Brief)
    - Phase 1: VPC Discovery (Customer Profile + Value Map)
    - Phase 2: Desirability (Ad campaigns, evidence collection)
    - Phase 3: Feasibility (Technical assessment)
    - Phase 4: Viability (Unit economics, final decision)
"""

# Import modules with standardized names for app.py
from . import phase_0 as phase_0_onboarding
from . import phase_1 as phase_1_vpc_discovery
from . import phase_2 as phase_2_desirability
from . import phase_3 as phase_3_feasibility
from . import phase_4 as phase_4_viability

# Also export with original names for backwards compatibility
from . import phase_0, phase_1, phase_2, phase_3, phase_4

__all__ = [
    # Standardized names (used by app.py)
    "phase_0_onboarding",
    "phase_1_vpc_discovery",
    "phase_2_desirability",
    "phase_3_feasibility",
    "phase_4_viability",
    # Original names (backwards compatibility)
    "phase_0",
    "phase_1",
    "phase_2",
    "phase_3",
    "phase_4",
]
