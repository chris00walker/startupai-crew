#!/usr/bin/env python
"""
Seed Demo Project Script.

Creates a demo project with sample state for testing and development.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from startupai.flows.state_schemas import (
    StartupValidationState,
    Phase,
    RiskAxis,
    DesirabilitySignal,
    FeasibilitySignal,
    ViabilitySignal,
    PivotType,
    Assumption,
    AssumptionCategory,
    CustomerProfile,
    CustomerJob,
    ValueMap,
)
from startupai.persistence.state_repository import InMemoryStateRepository


def create_demo_state() -> StartupValidationState:
    """Create a demo state with realistic sample data."""

    # Create sample jobs
    jobs = [
        CustomerJob(
            functional="Manage supply chain costs",
            emotional="Feel in control of operations",
            social="Be seen as an efficient leader",
            importance=9,
        ),
        CustomerJob(
            functional="Predict inventory needs",
            emotional="Reduce stress from stockouts",
            social="Be recognized as forward-thinking",
            importance=8,
        ),
    ]

    # Create customer profile
    profile = CustomerProfile(
        segment_name="Supply Chain Directors",
        jobs=jobs,
        pains=[
            "Manual forecasting is time-consuming",
            "Stockouts lead to lost sales",
            "Data silos prevent visibility",
        ],
        gains=[
            "Automated demand forecasting",
            "Real-time inventory visibility",
            "Cost reduction of 15-20%",
        ],
        pain_intensity={"Manual forecasting is time-consuming": 8, "Stockouts lead to lost sales": 9},
        gain_importance={"Automated demand forecasting": 9, "Cost reduction of 15-20%": 8},
    )

    # Create value map
    value_map = ValueMap(
        products_services=["AI Forecasting Dashboard", "Inventory Alerts", "Analytics Reports"],
        pain_relievers={
            "Manual forecasting": "Automated ML predictions",
            "Data silos": "Integration with ERP systems",
        },
        gain_creators={
            "Cost reduction": "Optimization recommendations",
            "Real-time visibility": "Live dashboard with KPIs",
        },
        differentiators=["Industry-specific AI models", "5-minute setup", "ROI guarantee"],
    )

    # Create assumptions
    assumptions = [
        Assumption(
            id="asm_001",
            statement="Supply chain directors will pay $500/month for forecasting",
            category=AssumptionCategory.VIABILITY,
            priority=1,
            evidence_needed="Price sensitivity testing with landing page",
        ),
        Assumption(
            id="asm_002",
            statement="Manual forecasting is a top-3 pain point",
            category=AssumptionCategory.DESIRABILITY,
            priority=2,
            evidence_needed="Customer interviews (n=10)",
        ),
        Assumption(
            id="asm_003",
            statement="We can integrate with SAP in under 2 hours",
            category=AssumptionCategory.FEASIBILITY,
            priority=3,
            evidence_needed="Technical prototype",
        ),
    ]

    # Create the demo state
    state = StartupValidationState(
        project_id=f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        iteration=0,
        phase=Phase.DESIRABILITY,
        current_risk_axis=RiskAxis.DESIRABILITY,
        # Problem/Solution Fit
        current_segment="Supply Chain Directors",
        current_value_prop="AI-powered supply chain forecasting that reduces costs by 15-20%",
        # Signals (starting state)
        desirability_signal=DesirabilitySignal.NO_SIGNAL,
        feasibility_signal=FeasibilitySignal.UNKNOWN,
        viability_signal=ViabilitySignal.UNKNOWN,
        # Legacy fields for compatibility
        business_idea="AI-powered supply chain optimization platform",
        entrepreneur_input="I want to build an AI platform that helps mid-market companies optimize their supply chain operations.",
        target_segments=["Supply Chain Directors", "Operations Managers"],
        assumptions=assumptions,
        customer_profiles={"Supply Chain Directors": profile},
        value_maps={"Supply Chain Directors": value_map},
    )

    return state


async def seed_demo_project(use_supabase: bool = False):
    """Seed the demo project."""
    print("Creating demo project...")

    # Create demo state
    state = create_demo_state()
    # Handle both enum and string values
    phase_val = state.phase.value if hasattr(state.phase, 'value') else str(state.phase)
    print(f"  Project ID: {state.project_id}")
    print(f"  Phase: {phase_val}")
    print(f"  Segment: {state.current_segment}")

    # Save to repository
    if use_supabase:
        try:
            from startupai.persistence.state_repository import SupabaseStateRepository
            repo = SupabaseStateRepository()
            await repo.save_state(state)
            print("  Saved to Supabase!")
        except Exception as e:
            print(f"  Failed to save to Supabase: {e}")
            print("  Falling back to in-memory...")
            repo = InMemoryStateRepository()
            await repo.save_state(state)
    else:
        repo = InMemoryStateRepository()
        await repo.save_state(state)
        print("  Saved to in-memory repository (use --supabase for persistence)")

    print("\nDemo project created successfully!")
    print(f"\nState summary:")
    # Handle both enum and string values
    risk_val = state.current_risk_axis.value if hasattr(state.current_risk_axis, 'value') else str(state.current_risk_axis)
    print(f"  - Project ID: {state.project_id}")
    print(f"  - Phase: {phase_val}")
    print(f"  - Risk Axis: {risk_val}")
    print(f"  - Target Segments: {state.target_segments}")
    print(f"  - Assumptions: {len(state.assumptions)}")
    print(f"  - Value Proposition: {state.current_value_prop}")

    return state


if __name__ == "__main__":
    use_supabase = "--supabase" in sys.argv
    asyncio.run(seed_demo_project(use_supabase))
