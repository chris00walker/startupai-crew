#!/usr/bin/env python
"""
Simulate Flow Script.

Runs the validation flow with mocked crews for local testing.
Demonstrates the Innovation Physics routing logic without actual LLM calls.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, patch

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
)


class MockCrewResult:
    """Mock result from a crew kickoff."""

    def __init__(self, data: Dict[str, Any]):
        self.pydantic = Mock()
        for key, value in data.items():
            setattr(self.pydantic, key, value)
        self.raw = str(data)


def simulate_desirability_phase(state: StartupValidationState, scenario: str) -> str:
    """
    Simulate desirability testing and return routing decision.

    Scenarios:
    - "strong": Strong customer interest with commitment
    - "weak": Weak interest (zombie detected)
    - "none": No customer interest
    """
    print(f"\n{'='*60}")
    print("PHASE 1: DESIRABILITY TESTING")
    print(f"{'='*60}")
    print(f"Testing segment: {state.current_segment}")

    if scenario == "strong":
        state.desirability_signal = DesirabilitySignal.STRONG_COMMITMENT
        print("Result: Strong commitment detected!")
        print("  - Problem resonance: 72%")
        print("  - Conversion rate: 15%")
        print("  - Zombie ratio: 21%")
        return "proceed_to_feasibility"

    elif scenario == "weak":
        state.desirability_signal = DesirabilitySignal.WEAK_INTEREST
        print("Result: Weak interest (zombie market detected)")
        print("  - Problem resonance: 45%")
        print("  - Conversion rate: 3%")
        print("  - Zombie ratio: 67%")
        state.pending_pivot_type = PivotType.VALUE_PIVOT
        return "value_pivot_required"

    else:  # scenario == "none"
        state.desirability_signal = DesirabilitySignal.NO_INTEREST
        print("Result: No customer interest")
        print("  - Problem resonance: 12%")
        print("  - Conversion rate: 0.5%")
        state.pending_pivot_type = PivotType.SEGMENT_PIVOT
        return "segment_pivot_required"


def simulate_feasibility_phase(state: StartupValidationState, scenario: str) -> str:
    """
    Simulate feasibility testing and return routing decision.

    Scenarios:
    - "green": Fully feasible
    - "orange": Constrained, needs downgrade
    - "red": Impossible to build
    """
    print(f"\n{'='*60}")
    print("PHASE 2: FEASIBILITY TESTING")
    print(f"{'='*60}")

    if scenario == "green":
        state.feasibility_signal = FeasibilitySignal.GREEN
        state.phase = Phase.FEASIBILITY
        print("Result: Fully feasible!")
        print("  - All features buildable")
        print("  - Technical complexity: 5/10")
        print("  - Monthly cost estimate: $150")
        return "proceed_to_viability"

    elif scenario == "orange":
        state.feasibility_signal = FeasibilitySignal.ORANGE_CONSTRAINED
        state.phase = Phase.FEASIBILITY
        print("Result: Constrained feasibility")
        print("  - 2 features need downgrade")
        print("  - Technical complexity: 7/10")
        print("  - Downgrade impact: Reduced automation")
        return "test_degraded_desirability"

    else:  # scenario == "red"
        state.feasibility_signal = FeasibilitySignal.RED_IMPOSSIBLE
        state.phase = Phase.FEASIBILITY
        print("Result: Impossible to build!")
        print("  - Core AI feature not achievable with current tech")
        print("  - Would require 18+ months R&D")
        state.pending_pivot_type = PivotType.KILL
        return "compass_synthesis_required"


def simulate_viability_phase(state: StartupValidationState, scenario: str) -> str:
    """
    Simulate viability testing and return routing decision.

    Scenarios:
    - "profitable": LTV/CAC > 3
    - "marginal": 1 < LTV/CAC < 3
    - "underwater": LTV/CAC < 1
    - "zombie": High CAC, low market
    """
    print(f"\n{'='*60}")
    print("PHASE 3: VIABILITY TESTING")
    print(f"{'='*60}")

    if scenario == "profitable":
        state.viability_signal = ViabilitySignal.PROFITABLE
        state.phase = Phase.VIABILITY
        print("Result: Profitable unit economics!")
        print("  - CAC: $120")
        print("  - LTV: $480")
        print("  - LTV/CAC: 4.0")
        print("  - Payback: 3 months")
        return "validation_complete"

    elif scenario == "marginal":
        state.viability_signal = ViabilitySignal.PROFITABLE  # Marginal is still profitable
        state.phase = Phase.VIABILITY
        print("Result: Marginal unit economics")
        print("  - CAC: $200")
        print("  - LTV: $350")
        print("  - LTV/CAC: 1.75")
        print("  - Needs optimization")
        return "optimize_economics"

    elif scenario == "underwater":
        state.viability_signal = ViabilitySignal.UNDERWATER
        state.phase = Phase.VIABILITY
        print("Result: Underwater unit economics!")
        print("  - CAC: $300")
        print("  - LTV: $180")
        print("  - LTV/CAC: 0.6")
        print("  - CRITICAL: Losing money on every customer")
        state.pending_pivot_type = PivotType.PRICE_PIVOT
        return "strategic_pivot_required"

    else:  # scenario == "zombie"
        state.viability_signal = ViabilitySignal.ZOMBIE_MARKET
        state.phase = Phase.VIABILITY
        print("Result: Zombie market detected!")
        print("  - CAC: $50")
        print("  - LTV: $100")
        print("  - LTV/CAC: 2.0")
        print("  - BUT: TAM only $500K/year")
        print("  - Market too small to scale")
        state.pending_pivot_type = PivotType.SEGMENT_PIVOT
        return "compass_synthesis_required"


def run_simulation(
    desirability_scenario: str = "strong",
    feasibility_scenario: str = "green",
    viability_scenario: str = "profitable",
):
    """Run a full flow simulation with specified scenarios."""

    print("\n" + "="*70)
    print("INNOVATION PHYSICS FLOW SIMULATION")
    print("="*70)

    # Create initial state
    state = StartupValidationState(
        project_id=f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        entrepreneur_input="AI-powered supply chain optimization platform",
        phase=Phase.IDEATION,
        current_segment="Supply Chain Directors",
        target_segments=["Supply Chain Directors", "Operations Managers"],
    )

    # Get phase value (handle both enum and string)
    phase_value = state.phase.value if hasattr(state.phase, 'value') else str(state.phase)

    print(f"\nProject ID: {state.project_id}")
    print(f"Starting Phase: {phase_value}")
    print(f"Target Segment: {state.current_segment}")

    # Track pivots
    pivots = []

    # Phase 1: Desirability
    state.phase = Phase.DESIRABILITY
    decision = simulate_desirability_phase(state, desirability_scenario)
    print(f"\nRouter Decision: {decision}")

    if decision == "segment_pivot_required":
        pivots.append("Segment Pivot")
        print("\n>>> PIVOT: Changing customer segment")
        # In real flow, would loop back
        return state, pivots

    if decision == "value_pivot_required":
        pivots.append("Value Pivot")
        print("\n>>> PIVOT: Iterating value proposition")
        # In real flow, would loop back
        return state, pivots

    # Phase 2: Feasibility
    state.phase = Phase.FEASIBILITY
    decision = simulate_feasibility_phase(state, feasibility_scenario)
    print(f"\nRouter Decision: {decision}")

    if decision == "compass_synthesis_required":
        print("\n>>> SYNTHESIS: Major pivot or kill required")
        return state, pivots

    if decision == "test_degraded_desirability":
        print("\n>>> DOWNGRADE: Testing customer acceptance of reduced features")
        # In real flow, would loop back to desirability

    # Phase 3: Viability
    state.phase = Phase.VIABILITY
    decision = simulate_viability_phase(state, viability_scenario)
    print(f"\nRouter Decision: {decision}")

    if decision == "strategic_pivot_required":
        pivots.append("Price/Cost Pivot")
        print("\n>>> PIVOT: Strategic pricing or cost adjustment needed")
        return state, pivots

    if decision == "validation_complete":
        state.phase = Phase.VALIDATED
        print(f"\n{'='*60}")
        print("VALIDATION COMPLETE!")
        print(f"{'='*60}")
        print("Final State:")
        # Handle both enum and string values
        phase_val = state.phase.value if hasattr(state.phase, 'value') else str(state.phase)
        des_val = state.desirability_signal.value if hasattr(state.desirability_signal, 'value') else str(state.desirability_signal)
        feas_val = state.feasibility_signal.value if hasattr(state.feasibility_signal, 'value') else str(state.feasibility_signal)
        via_val = state.viability_signal.value if hasattr(state.viability_signal, 'value') else str(state.viability_signal)
        print(f"  - Phase: {phase_val}")
        print(f"  - Desirability: {des_val}")
        print(f"  - Feasibility: {feas_val}")
        print(f"  - Viability: {via_val}")
        print(f"  - Pivots Executed: {len(pivots)}")

    return state, pivots


if __name__ == "__main__":
    # Default: Happy path
    print("\n" + "#"*70)
    print("# SCENARIO 1: Happy Path (Strong -> Green -> Profitable)")
    print("#"*70)
    run_simulation("strong", "green", "profitable")

    # Pivot scenario
    print("\n" + "#"*70)
    print("# SCENARIO 2: Zombie Market (Strong -> Green -> Zombie)")
    print("#"*70)
    run_simulation("strong", "green", "zombie")

    # Failure scenario
    print("\n" + "#"*70)
    print("# SCENARIO 3: No Interest (None -> N/A -> N/A)")
    print("#"*70)
    run_simulation("none", "green", "profitable")
