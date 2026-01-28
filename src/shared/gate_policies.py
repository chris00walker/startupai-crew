"""
Gate Policy Evaluation Module

Fetches user-configured gate policies from Supabase and evaluates
gate readiness against configurable criteria.

@story US-AD10, US-ADB05, US-AFB03, US-AVB03
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import os
from supabase import create_client, Client


@dataclass
class GatePolicy:
    """User-configurable gate policy for phase transitions."""

    gate: str
    min_experiments: int = 3
    required_fit_types: list[str] = field(default_factory=lambda: ["Desirability"])
    min_weak_evidence: int = 0
    min_medium_evidence: int = 1
    min_strong_evidence: int = 1
    thresholds: dict[str, float] = field(default_factory=dict)
    override_roles: list[str] = field(default_factory=lambda: ["admin", "senior_consultant"])
    requires_approval: bool = True


# Default policies used when no custom policy exists
DEFAULT_POLICIES: dict[str, GatePolicy] = {
    "DESIRABILITY": GatePolicy(
        gate="DESIRABILITY",
        min_experiments=3,
        required_fit_types=["Desirability"],
        min_weak_evidence=0,
        min_medium_evidence=1,
        min_strong_evidence=1,
        thresholds={"fit_score": 70.0, "ctr": 0.02},
        requires_approval=True,
    ),
    "FEASIBILITY": GatePolicy(
        gate="FEASIBILITY",
        min_experiments=2,
        required_fit_types=["Feasibility"],
        min_weak_evidence=0,
        min_medium_evidence=1,
        min_strong_evidence=0,
        thresholds={"monthly_cost_max": 10000.0},
        requires_approval=True,
    ),
    "VIABILITY": GatePolicy(
        gate="VIABILITY",
        min_experiments=2,
        required_fit_types=["Viability"],
        min_weak_evidence=0,
        min_medium_evidence=0,
        min_strong_evidence=1,
        thresholds={"ltv_cac_ratio": 3.0},
        requires_approval=True,
    ),
}


def get_supabase_client() -> Client:
    """Create Supabase client from environment variables."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

    return create_client(url, key)


def get_gate_policy(
    user_id: str,
    gate: str,
    supabase: Optional[Client] = None,
) -> GatePolicy:
    """
    Fetch user's gate policy from Supabase, falling back to defaults.

    Args:
        user_id: The user's UUID
        gate: Gate type (DESIRABILITY, FEASIBILITY, VIABILITY)
        supabase: Optional Supabase client (creates one if not provided)

    Returns:
        GatePolicy with user's custom settings or defaults
    """
    gate_upper = gate.upper()

    if gate_upper not in DEFAULT_POLICIES:
        raise ValueError(f"Invalid gate: {gate}. Must be one of: {list(DEFAULT_POLICIES.keys())}")

    defaults = DEFAULT_POLICIES[gate_upper]

    try:
        client = supabase or get_supabase_client()

        result = client.table("gate_policies").select("*").eq(
            "user_id", user_id
        ).eq(
            "gate", gate_upper
        ).maybe_single().execute()

        if not result.data:
            return defaults

        row = result.data
        return GatePolicy(
            gate=gate_upper,
            min_experiments=row.get("min_experiments", defaults.min_experiments),
            required_fit_types=row.get("required_fit_types", defaults.required_fit_types),
            min_weak_evidence=row.get("min_weak_evidence") or defaults.min_weak_evidence,
            min_medium_evidence=row.get("min_medium_evidence") or defaults.min_medium_evidence,
            min_strong_evidence=row.get("min_strong_evidence") or defaults.min_strong_evidence,
            thresholds=row.get("thresholds") or defaults.thresholds,
            override_roles=row.get("override_roles") or defaults.override_roles,
            requires_approval=row.get("requires_approval", defaults.requires_approval),
        )

    except Exception as e:
        # Log error but return defaults to avoid blocking validation
        print(f"[gate_policies] Error fetching policy for user {user_id}, gate {gate}: {e}")
        return defaults


@dataclass
class GateEvaluationResult:
    """Result of gate evaluation."""

    gate_ready: bool
    blockers: list[str] = field(default_factory=list)
    policy: Optional[GatePolicy] = None
    evidence_summary: Optional[dict[str, Any]] = None


def evaluate_gate(
    policy: GatePolicy,
    evidence_summary: dict[str, Any],
    signal: Optional[str] = None,
) -> GateEvaluationResult:
    """
    Evaluate gate readiness against policy criteria.

    Args:
        policy: The gate policy to evaluate against
        evidence_summary: Summary of evidence collected, expected keys:
            - experiments_run: int
            - experiments_passed: int
            - weak_evidence_count: int
            - medium_evidence_count: int
            - strong_evidence_count: int
            - fit_score: float (for DESIRABILITY)
            - ctr: float (for DESIRABILITY)
            - monthly_cost: float (for FEASIBILITY)
            - ltv_cac_ratio: float (for VIABILITY)
        signal: Optional signal value (strong_commitment, green, profitable, etc.)

    Returns:
        GateEvaluationResult with gate_ready status and blockers list
    """
    blockers: list[str] = []

    # Check experiment count
    experiments_run = evidence_summary.get("experiments_run", 0)
    if experiments_run < policy.min_experiments:
        blockers.append(
            f"Need {policy.min_experiments} experiments, have {experiments_run}"
        )

    # Check evidence strength mix
    weak_count = evidence_summary.get("weak_evidence_count", 0)
    medium_count = evidence_summary.get("medium_evidence_count", 0)
    strong_count = evidence_summary.get("strong_evidence_count", 0)

    if weak_count < policy.min_weak_evidence:
        blockers.append(
            f"Need {policy.min_weak_evidence} weak evidence, have {weak_count}"
        )

    if medium_count < policy.min_medium_evidence:
        blockers.append(
            f"Need {policy.min_medium_evidence} medium evidence, have {medium_count}"
        )

    if strong_count < policy.min_strong_evidence:
        blockers.append(
            f"Need {policy.min_strong_evidence} strong evidence, have {strong_count}"
        )

    # Check thresholds
    for threshold_key, min_value in policy.thresholds.items():
        # Handle max thresholds (e.g., monthly_cost_max)
        if threshold_key.endswith("_max"):
            actual_key = threshold_key.replace("_max", "")
            actual = evidence_summary.get(actual_key, 0)
            if actual > min_value:
                blockers.append(
                    f"{actual_key} exceeds threshold: {actual} > {min_value}"
                )
        else:
            # Normal threshold (must be >= min_value)
            actual = evidence_summary.get(threshold_key, 0)
            if actual < min_value:
                blockers.append(
                    f"{threshold_key} below threshold: {actual} < {min_value}"
                )

    # Signal-based checks (for compatibility with existing code)
    if signal:
        signal_lower = signal.lower()

        # DESIRABILITY gate
        if policy.gate == "DESIRABILITY":
            if signal_lower not in ["strong_commitment", "green"]:
                blockers.append(f"Desirability signal not strong: {signal}")

        # FEASIBILITY gate
        elif policy.gate == "FEASIBILITY":
            if signal_lower not in ["green", "green_feasible"]:
                blockers.append(f"Feasibility signal not green: {signal}")

        # VIABILITY gate
        elif policy.gate == "VIABILITY":
            if signal_lower not in ["profitable", "green", "proceed"]:
                blockers.append(f"Viability signal not profitable: {signal}")

    return GateEvaluationResult(
        gate_ready=len(blockers) == 0,
        blockers=blockers,
        policy=policy,
        evidence_summary=evidence_summary,
    )


def evaluate_gate_for_user(
    user_id: str,
    gate: str,
    evidence_summary: dict[str, Any],
    signal: Optional[str] = None,
    supabase: Optional[Client] = None,
) -> GateEvaluationResult:
    """
    Convenience function to fetch policy and evaluate gate in one call.

    Args:
        user_id: The user's UUID
        gate: Gate type (DESIRABILITY, FEASIBILITY, VIABILITY)
        evidence_summary: Evidence data for evaluation
        signal: Optional signal value
        supabase: Optional Supabase client

    Returns:
        GateEvaluationResult with complete evaluation
    """
    policy = get_gate_policy(user_id, gate, supabase)
    return evaluate_gate(policy, evidence_summary, signal)
