"""
Pydantic output schemas for StartupAI Intake Crew tasks.

These models enforce structured outputs that align with Strategyzer methodologies
and enable reliable crew-to-crew data transfer.
"""

from typing import List, Optional, Dict, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# =======================================================================================
# ENUMERATIONS
# =======================================================================================


class RiskLevel(str, Enum):
    """Risk level for hypotheses and assumptions."""

    CRITICAL = "critical"  # Must be true or business fails
    HIGH = "high"  # Significant impact if wrong
    MEDIUM = "medium"  # Important but recoverable
    LOW = "low"  # Nice to validate


class PainSeverity(str, Enum):
    """Severity rating for customer pains."""

    EXTREME = "extreme"  # Constant, unbearable frustration
    HIGH = "high"  # Frequent, significant pain
    MODERATE = "moderate"  # Occasional, manageable
    LOW = "low"  # Minor inconvenience


class GainImportance(str, Enum):
    """Importance rating for customer gains."""

    ESSENTIAL = "essential"  # Must-have for solution adoption
    EXPECTED = "expected"  # Standard expectation
    DESIRED = "desired"  # Would be nice to have
    UNEXPECTED = "unexpected"  # Delighter if present


class JobType(str, Enum):
    """Types of jobs in JTBD framework."""

    FUNCTIONAL = "functional"  # What task they want done
    EMOTIONAL = "emotional"  # How they want to feel
    SOCIAL = "social"  # How they want to be perceived


class QAStatus(str, Enum):
    """QA gate status."""

    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"  # Pass with required changes


class ApprovalDecision(str, Enum):
    """Human approval decisions."""

    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


# =======================================================================================
# TASK 1: FOUNDER BRIEF OUTPUT
# =======================================================================================


class Hypothesis(BaseModel):
    """A testable business hypothesis."""

    statement: str = Field(..., description="Clear, testable hypothesis statement")
    risk_level: RiskLevel = Field(..., description="How critical this is to validate")
    validation_method: Optional[str] = Field(
        None, description="How to test this hypothesis"
    )


class FounderBrief(BaseModel):
    """
    Task 1 Output: Structured entrepreneur brief from raw input.

    This is the foundational document that guides all downstream validation.
    """

    # Core business description
    business_idea: str = Field(
        ..., min_length=20, description="Core product/service concept"
    )
    problem_statement: str = Field(
        ..., min_length=20, description="Pain points being addressed"
    )
    proposed_solution: str = Field(
        ..., min_length=20, description="How the product solves the problem"
    )

    # Target customers (will be expanded in Task 2)
    target_customers: List[str] = Field(
        ..., min_length=1, description="Primary customer segments"
    )

    # Hypotheses for validation
    key_hypotheses: List[Hypothesis] = Field(
        ..., min_length=1, description="Assumptions that need testing"
    )

    # Success criteria
    success_metrics: List[str] = Field(
        ..., min_length=1, description="How to measure desirability"
    )

    # Metadata
    parsed_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator("key_hypotheses")
    @classmethod
    def validate_hypotheses_count(cls, v):
        """Ensure at least 1 hypothesis for validation."""
        if len(v) < 1:
            raise ValueError("At least 1 hypothesis required")
        return v


# =======================================================================================
# TASK 2: CUSTOMER RESEARCH OUTPUT
# =======================================================================================


class CustomerJob(BaseModel):
    """A job-to-be-done for a customer segment."""

    job_type: JobType
    description: str = Field(..., min_length=10)
    frequency: Optional[str] = Field(None, description="How often this job occurs")
    importance: int = Field(ge=1, le=10, description="1-10 importance scale")


class CustomerPain(BaseModel):
    """A customer pain point."""

    description: str = Field(..., min_length=10)
    severity: PainSeverity
    frequency: Optional[str] = None
    current_workaround: Optional[str] = Field(
        None, description="How they cope today"
    )


class CustomerGain(BaseModel):
    """A customer gain (desired outcome)."""

    description: str = Field(..., min_length=10)
    importance: GainImportance
    current_satisfaction: Optional[int] = Field(
        None, ge=1, le=10, description="How well met today"
    )


class CustomerSegmentProfile(BaseModel):
    """Complete JTBD profile for a customer segment."""

    segment_name: str = Field(..., min_length=3)
    segment_description: str = Field(..., min_length=20)

    # Jobs-to-be-done
    jobs_to_be_done: List[CustomerJob] = Field(..., min_length=1)

    # Pains and gains
    pains: List[CustomerPain] = Field(..., min_length=1)
    gains: List[CustomerGain] = Field(..., min_length=1)

    # Research metadata
    research_sources: List[str] = Field(
        default_factory=list, description="Sources used in research"
    )


class CustomerResearchOutput(BaseModel):
    """
    Task 2 Output: Customer research using JTBD methodology.

    Contains detailed profiles for each target customer segment.
    """

    customer_segments: List[CustomerSegmentProfile] = Field(..., min_length=1)
    research_summary: str = Field(
        ..., min_length=50, description="High-level research findings"
    )
    researched_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# =======================================================================================
# TASK 3: VALUE PROPOSITION CANVAS OUTPUT
# =======================================================================================


class PainReliever(BaseModel):
    """How the product relieves a specific pain."""

    pain_addressed: str = Field(..., description="Which pain this relieves")
    reliever_description: str = Field(..., min_length=10)
    relief_strength: Literal["complete", "partial", "minimal"] = "partial"


class GainCreator(BaseModel):
    """How the product creates a specific gain."""

    gain_addressed: str = Field(..., description="Which gain this creates")
    creator_description: str = Field(..., min_length=10)
    creation_strength: Literal["strong", "moderate", "weak"] = "moderate"


class ValueMap(BaseModel):
    """Value Map side of the VPC."""

    products_services: List[str] = Field(..., min_length=1)
    pain_relievers: List[PainReliever] = Field(..., min_length=1)
    gain_creators: List[GainCreator] = Field(..., min_length=1)


class FitAnalysis(BaseModel):
    """Analysis of fit between customer profile and value map."""

    covered_jobs: List[str] = Field(default_factory=list)
    covered_pains: List[str] = Field(default_factory=list)
    covered_gains: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(
        default_factory=list, description="Unaddressed customer needs"
    )
    fit_score: float = Field(ge=0, le=1, description="0-1 score of problem-solution fit")


class ValuePropositionCanvas(BaseModel):
    """
    Task 3 Output: Complete Value Proposition Canvas.

    Links customer profile (from Task 2) to value map.
    """

    # Customer Profile side (reference to Task 2 output)
    primary_segment: str = Field(..., description="Which segment this VPC addresses")
    customer_jobs: List[str] = Field(..., min_length=1)
    customer_pains: List[str] = Field(..., min_length=1)
    customer_gains: List[str] = Field(..., min_length=1)

    # Value Map side
    value_map: ValueMap

    # Fit analysis
    fit_analysis: FitAnalysis

    # Summary statement
    value_proposition_statement: str = Field(
        ..., min_length=20, description="Clear, concise value proposition"
    )

    canvas_created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# =======================================================================================
# TASK 4: QA GATE OUTPUT
# =======================================================================================


class ReviewSection(BaseModel):
    """Review of a specific section."""

    status: QAStatus
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class QAGateOutput(BaseModel):
    """
    Task 4 Output: Quality assessment of all intake outputs.

    Guardian's review before human approval.
    """

    overall_status: QAStatus

    # Section reviews
    brief_review: ReviewSection
    customer_research_review: ReviewSection
    vpc_review: ReviewSection

    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    blocking_issues: List[str] = Field(
        default_factory=list, description="Issues that must be fixed before proceeding"
    )

    # Scores
    completeness_score: float = Field(ge=0, le=1)
    quality_score: float = Field(ge=0, le=1)
    methodology_compliance_score: float = Field(ge=0, le=1)

    # Ready state
    ready_for_human_review: bool = Field(
        ..., description="Whether outputs are ready for human approval"
    )

    reviewed_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# =======================================================================================
# TASK 5: HUMAN APPROVAL OUTPUT (HITL)
# =======================================================================================


class HumanApprovalInput(BaseModel):
    """
    Task 5 Output: Human approval decision for intake phase.

    This is a HITL task - the human provides the decision.
    """

    decision: ApprovalDecision
    comments: Optional[str] = Field(None, description="Human feedback or instructions")
    specific_feedback: List[str] = Field(
        default_factory=list, description="Specific items to address if revision needed"
    )
    approved_by: Optional[str] = Field(None, description="Identifier of approver")
    approved_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# =======================================================================================
# TASK 6: CREW INVOCATION OUTPUT
# =======================================================================================


class CrewInvocationResult(BaseModel):
    """
    Task 6 Output: Result of invoking Crew 2 (Validation Engine).

    Confirms successful handoff to the next crew.
    """

    success: bool
    crew_name: str = "Validation Crew"
    kickoff_id: Optional[str] = Field(
        None, description="Crew 2 execution ID for tracking"
    )

    # Data package sent
    data_sent: Dict[str, bool] = Field(
        default_factory=dict, description="Which data packages were included"
    )

    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0

    invoked_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# =======================================================================================
# EXPORT ALL
# =======================================================================================

__all__ = [
    # Enums
    "RiskLevel",
    "PainSeverity",
    "GainImportance",
    "JobType",
    "QAStatus",
    "ApprovalDecision",
    # Task 1
    "Hypothesis",
    "FounderBrief",
    # Task 2
    "CustomerJob",
    "CustomerPain",
    "CustomerGain",
    "CustomerSegmentProfile",
    "CustomerResearchOutput",
    # Task 3
    "PainReliever",
    "GainCreator",
    "ValueMap",
    "FitAnalysis",
    "ValuePropositionCanvas",
    # Task 4
    "ReviewSection",
    "QAGateOutput",
    # Task 5
    "HumanApprovalInput",
    # Task 6
    "CrewInvocationResult",
]
