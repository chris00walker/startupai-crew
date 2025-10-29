"""
Gate Scoring Module

Calculates whether a project passes evidence-led stage gates based on:
- Evidence quality scores
- Minimum experiment counts
- Evidence strength mix (weak/medium/strong)
- Required evidence types (interview, analytics, experiment)
"""

from typing import Dict, List, Literal, TypedDict
from enum import Enum


class GateStage(str, Enum):
    """Stage gates in evidence-led development"""
    DESIRABILITY = "DESIRABILITY"
    FEASIBILITY = "FEASIBILITY"
    VIABILITY = "VIABILITY"
    SCALE = "SCALE"


class EvidenceStrength(str, Enum):
    """Evidence strength classification"""
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"


class GateStatus(str, Enum):
    """Gate pass/fail status"""
    PENDING = "Pending"
    PASSED = "Passed"
    FAILED = "Failed"


class Evidence(TypedDict):
    """Evidence item structure"""
    type: Literal["interview", "desk", "analytics", "experiment"]
    strength: EvidenceStrength
    quality_score: float  # 0.0-1.0


class GateCriteria(TypedDict):
    """Gate passing criteria"""
    min_experiments: int
    min_evidence_quality: float  # 0.0-1.0
    min_total_evidence: int
    required_evidence_types: List[str]
    strength_mix: Dict[str, int]  # min count per strength level


# Default gate criteria for each stage
DEFAULT_GATE_CRITERIA: Dict[GateStage, GateCriteria] = {
    GateStage.DESIRABILITY: {
        "min_experiments": 5,
        "min_evidence_quality": 0.70,
        "min_total_evidence": 10,
        "required_evidence_types": ["interview", "analytics"],
        "strength_mix": {
            "weak": 0,
            "medium": 3,
            "strong": 2,
        },
    },
    GateStage.FEASIBILITY: {
        "min_experiments": 10,
        "min_evidence_quality": 0.75,
        "min_total_evidence": 20,
        "required_evidence_types": ["interview", "analytics", "experiment"],
        "strength_mix": {
            "weak": 0,
            "medium": 5,
            "strong": 3,
        },
    },
    GateStage.VIABILITY: {
        "min_experiments": 15,
        "min_evidence_quality": 0.80,
        "min_total_evidence": 30,
        "required_evidence_types": ["interview", "analytics", "experiment", "desk"],
        "strength_mix": {
            "weak": 0,
            "medium": 8,
            "strong": 5,
        },
    },
    GateStage.SCALE: {
        "min_experiments": 20,
        "min_evidence_quality": 0.85,
        "min_total_evidence": 50,
        "required_evidence_types": ["interview", "analytics", "experiment", "desk"],
        "strength_mix": {
            "weak": 0,
            "medium": 12,
            "strong": 8,
        },
    },
}


def calculate_evidence_quality(evidence_list: List[Evidence]) -> float:
    """
    Calculate overall evidence quality score.
    
    Args:
        evidence_list: List of evidence items with quality scores
        
    Returns:
        Average quality score (0.0-1.0)
    """
    if not evidence_list:
        return 0.0
    
    total_quality = sum(e["quality_score"] for e in evidence_list)
    return total_quality / len(evidence_list)


def count_experiments(evidence_list: List[Evidence]) -> int:
    """Count number of experiment evidence items"""
    return sum(1 for e in evidence_list if e["type"] == "experiment")


def get_evidence_types(evidence_list: List[Evidence]) -> set:
    """Get set of unique evidence types present"""
    return {e["type"] for e in evidence_list}


def count_strength_mix(evidence_list: List[Evidence]) -> Dict[str, int]:
    """
    Count evidence by strength level.
    
    Returns:
        Dictionary with counts for weak/medium/strong
    """
    counts = {"weak": 0, "medium": 0, "strong": 0}
    
    for evidence in evidence_list:
        strength = evidence["strength"].value if isinstance(evidence["strength"], EvidenceStrength) else evidence["strength"]
        if strength in counts:
            counts[strength] += 1
    
    return counts


def evaluate_gate(
    stage: GateStage,
    evidence_list: List[Evidence],
    criteria: GateCriteria | None = None,
) -> tuple[GateStatus, List[str]]:
    """
    Evaluate if a project passes a stage gate.
    
    Args:
        stage: The stage gate being evaluated
        evidence_list: List of evidence items
        criteria: Custom criteria (uses defaults if None)
        
    Returns:
        Tuple of (gate_status, failure_reasons)
    """
    if criteria is None:
        criteria = DEFAULT_GATE_CRITERIA[stage]
    
    failure_reasons: List[str] = []
    
    # Check minimum total evidence
    if len(evidence_list) < criteria["min_total_evidence"]:
        failure_reasons.append(
            f"Insufficient total evidence: {len(evidence_list)} "
            f"(need {criteria['min_total_evidence']})"
        )
    
    # Check evidence quality
    quality_score = calculate_evidence_quality(evidence_list)
    if quality_score < criteria["min_evidence_quality"]:
        failure_reasons.append(
            f"Evidence quality too low: {quality_score:.2f} "
            f"(need {criteria['min_evidence_quality']:.2f})"
        )
    
    # Check minimum experiments
    experiment_count = count_experiments(evidence_list)
    if experiment_count < criteria["min_experiments"]:
        failure_reasons.append(
            f"Insufficient experiments: {experiment_count} "
            f"(need {criteria['min_experiments']})"
        )
    
    # Check required evidence types
    present_types = get_evidence_types(evidence_list)
    missing_types = set(criteria["required_evidence_types"]) - present_types
    if missing_types:
        failure_reasons.append(
            f"Missing required evidence types: {', '.join(sorted(missing_types))}"
        )
    
    # Check strength mix
    strength_counts = count_strength_mix(evidence_list)
    for strength, min_count in criteria["strength_mix"].items():
        actual_count = strength_counts.get(strength, 0)
        if actual_count < min_count:
            failure_reasons.append(
                f"Insufficient {strength} evidence: {actual_count} "
                f"(need {min_count})"
            )
    
    # Determine status
    if not failure_reasons:
        return GateStatus.PASSED, []
    
    return GateStatus.FAILED, failure_reasons


def can_progress_to_next_stage(
    current_stage: GateStage,
    current_gate_status: GateStatus,
) -> bool:
    """
    Check if project can progress to next stage.
    
    Args:
        current_stage: Current project stage
        current_gate_status: Current gate pass/fail status
        
    Returns:
        True if project can progress
    """
    # Can only progress if current gate is passed
    if current_gate_status != GateStatus.PASSED:
        return False
    
    # Check if there's a next stage
    stages = list(GateStage)
    try:
        current_index = stages.index(current_stage)
        return current_index < len(stages) - 1
    except ValueError:
        return False


def get_next_stage(current_stage: GateStage) -> GateStage | None:
    """Get the next stage after current stage"""
    stages = list(GateStage)
    try:
        current_index = stages.index(current_stage)
        if current_index < len(stages) - 1:
            return stages[current_index + 1]
    except ValueError:
        pass
    
    return None


def calculate_gate_readiness_score(
    stage: GateStage,
    evidence_list: List[Evidence],
    criteria: GateCriteria | None = None,
) -> float:
    """
    Calculate readiness score for a gate (0.0-1.0).
    
    Shows how close a project is to passing, useful for progress indicators.
    
    Returns:
        Score from 0.0 (far from passing) to 1.0 (passing all criteria)
    """
    if criteria is None:
        criteria = DEFAULT_GATE_CRITERIA[stage]
    
    scores = []
    
    # Evidence count score
    evidence_score = min(1.0, len(evidence_list) / criteria["min_total_evidence"])
    scores.append(evidence_score)
    
    # Quality score
    quality = calculate_evidence_quality(evidence_list)
    quality_score = min(1.0, quality / criteria["min_evidence_quality"])
    scores.append(quality_score)
    
    # Experiment count score
    experiments = count_experiments(evidence_list)
    experiment_score = min(1.0, experiments / criteria["min_experiments"])
    scores.append(experiment_score)
    
    # Evidence types score
    present_types = get_evidence_types(evidence_list)
    required_types = set(criteria["required_evidence_types"])
    type_score = len(present_types & required_types) / len(required_types) if required_types else 1.0
    scores.append(type_score)
    
    # Strength mix score
    strength_counts = count_strength_mix(evidence_list)
    strength_scores = []
    for strength, min_count in criteria["strength_mix"].items():
        if min_count > 0:
            actual = strength_counts.get(strength, 0)
            strength_scores.append(min(1.0, actual / min_count))
    
    if strength_scores:
        scores.append(sum(strength_scores) / len(strength_scores))
    
    # Average all scores
    return sum(scores) / len(scores) if scores else 0.0
