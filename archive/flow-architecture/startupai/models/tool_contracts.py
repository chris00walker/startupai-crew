"""
Tool Contracts for StartupAI.

This module defines the standard envelope pattern for all tool outputs,
ensuring consistent error handling and response formats across the system.
"""

from typing import Generic, TypeVar, Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

from startupai.flows.state_schemas import (
    Assumption,
    CustomerProfile,
    ValueMap,
    CompetitorReport,
    AssumptionCategory,
)


# =======================================================================================
# TOOL RESULT ENVELOPE
# =======================================================================================

T = TypeVar('T')


class ToolStatus(str, Enum):
    """Status of a tool execution"""
    SUCCESS = "success"           # Tool completed successfully
    PARTIAL = "partial"           # Tool partially completed (some data missing)
    FAILURE = "failure"           # Tool failed completely
    RATE_LIMITED = "rate_limited"  # External API rate limited
    TIMEOUT = "timeout"           # Tool execution timed out
    INVALID_INPUT = "invalid_input"  # Input validation failed


class ToolResult(BaseModel, Generic[T]):
    """
    Standard envelope for all tool outputs.

    This provides consistent error handling and metadata tracking
    across all tools in the system.

    Usage:
        # Success case
        return ToolResult.success(data=my_data, execution_time_ms=150)

        # Failure case
        return ToolResult.failure("API connection failed", code="API_ERROR")

        # Partial success
        return ToolResult.partial(
            data=partial_data,
            warnings=["Missing 2 of 5 records"]
        )
    """
    status: ToolStatus
    data: Optional[T] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)

    @classmethod
    def success(cls, data: T, **metadata) -> "ToolResult[T]":
        """Create a successful result"""
        return cls(
            status=ToolStatus.SUCCESS,
            data=data,
            metadata=metadata
        )

    @classmethod
    def failure(
        cls,
        message: str,
        code: str = "UNKNOWN",
        **metadata
    ) -> "ToolResult[T]":
        """Create a failure result"""
        return cls(
            status=ToolStatus.FAILURE,
            error_message=message,
            error_code=code,
            metadata=metadata
        )

    @classmethod
    def partial(
        cls,
        data: T,
        warnings: List[str],
        **metadata
    ) -> "ToolResult[T]":
        """Create a partial success result"""
        return cls(
            status=ToolStatus.PARTIAL,
            data=data,
            warnings=warnings,
            metadata=metadata
        )

    @property
    def is_success(self) -> bool:
        """Check if the result is a complete success"""
        return self.status == ToolStatus.SUCCESS

    @property
    def is_usable(self) -> bool:
        """Check if the result has usable data (success or partial)"""
        return self.status in (ToolStatus.SUCCESS, ToolStatus.PARTIAL)

    @property
    def is_retryable(self) -> bool:
        """Check if the operation should be retried"""
        return self.status in (ToolStatus.RATE_LIMITED, ToolStatus.TIMEOUT)

    def unwrap(self) -> T:
        """
        Get the data or raise an error if not successful.

        Raises:
            FlowExecutionError: If the tool result is not usable
        """
        if not self.is_usable:
            raise FlowExecutionError(
                f"Tool failed: {self.error_message}",
                error_code=self.error_code
            )
        return self.data

    def unwrap_or(self, default: T) -> T:
        """Get the data or return a default value if not usable"""
        return self.data if self.is_usable else default


# =======================================================================================
# CUSTOM EXCEPTIONS
# =======================================================================================

class FlowExecutionError(Exception):
    """
    Exception raised when a flow step fails.

    Carries error code and context for debugging and recovery.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        phase: Optional[str] = None,
        crew: Optional[str] = None,
        recoverable: bool = False,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.error_code = error_code or "FLOW_ERROR"
        self.phase = phase
        self.crew = crew
        self.recoverable = recoverable
        self.context = context or {}

    def __str__(self):
        parts = [f"[{self.error_code}] {super().__str__()}"]
        if self.phase:
            parts.append(f"Phase: {self.phase}")
        if self.crew:
            parts.append(f"Crew: {self.crew}")
        return " | ".join(parts)


# =======================================================================================
# CREW OUTPUT CONTRACTS
# =======================================================================================

class ServiceCrewOutput(BaseModel):
    """
    Output contract for Service Crew intake task.

    This is what the flow expects from the Service Crew after
    processing entrepreneur input.
    """
    business_idea: str = Field(
        description="One-sentence value proposition"
    )
    target_segments: List[str] = Field(
        description="List of identified customer segments"
    )
    problem_statement: str = Field(
        description="The core problem being solved"
    )
    solution_description: str = Field(
        description="How the product/service solves the problem"
    )
    revenue_model: str = Field(
        description="How the business will make money"
    )
    assumptions: List[Assumption] = Field(
        default_factory=list,
        description="Critical assumptions to test"
    )


class AnalysisCrewOutput(BaseModel):
    """
    Output contract for Analysis Crew research tasks.

    Contains customer profiles and value maps generated from research.
    """
    customer_profiles: Dict[str, CustomerProfile] = Field(
        default_factory=dict,
        description="Customer profiles keyed by segment name"
    )
    value_maps: Dict[str, ValueMap] = Field(
        default_factory=dict,
        description="Value maps keyed by segment name"
    )
    competitor_report: Optional[CompetitorReport] = Field(
        default=None,
        description="Competitive analysis report"
    )
    primary_segment: str = Field(
        description="Recommended primary segment to test first"
    )


class BuildCrewOutput(BaseModel):
    """Output contract for Build Crew feasibility assessment."""
    feasibility_status: str = Field(
        description="Overall feasibility: possible, constrained, or impossible"
    )
    build_id: str = Field(
        description="Unique identifier for this build assessment"
    )
    core_features_feasible: Dict[str, str] = Field(
        default_factory=dict,
        description="Feature name -> feasibility status"
    )
    removed_features: List[str] = Field(
        default_factory=list,
        description="Features that cannot be built"
    )
    estimated_monthly_cost_usd: float = Field(
        default=0.0,
        description="Estimated monthly infrastructure cost"
    )
    technical_complexity_score: int = Field(
        ge=1, le=10, default=5,
        description="Overall complexity 1-10"
    )
    notes: str = Field(
        default="",
        description="Additional notes and constraints"
    )


class GrowthCrewOutput(BaseModel):
    """Output contract for Growth Crew experiment results."""
    experiment_id: str = Field(
        description="Unique identifier for this experiment run"
    )
    platform: str = Field(
        description="Platform used (meta, google, etc.)"
    )
    impressions: int = Field(default=0)
    clicks: int = Field(default=0)
    signups: int = Field(default=0)
    spend_usd: float = Field(default=0.0)
    ctr: float = Field(
        default=0.0,
        description="Click-through rate"
    )
    conversion_rate: float = Field(
        default=0.0,
        description="Signup/click conversion rate"
    )
    desirability_signal: str = Field(
        default="no_signal",
        description="Interpreted signal: no_signal, no_interest, weak_interest, strong_commitment"
    )


class FinanceCrewOutput(BaseModel):
    """Output contract for Finance Crew viability analysis."""
    cac_usd: float = Field(
        default=0.0,
        description="Customer Acquisition Cost"
    )
    ltv_usd: float = Field(
        default=0.0,
        description="Lifetime Value"
    )
    ltv_cac_ratio: float = Field(
        default=0.0,
        description="LTV/CAC ratio"
    )
    gross_margin_pct: float = Field(
        default=0.0,
        description="Gross margin percentage"
    )
    payback_months: float = Field(
        default=0.0,
        description="Months to payback CAC"
    )
    viability_signal: str = Field(
        default="unknown",
        description="Interpreted signal: unknown, profitable, underwater, zombie_market"
    )
    recommendation: str = Field(
        default="",
        description="Recommendation: proceed, price_pivot, cost_pivot, or kill"
    )


class GovernanceCrewOutput(BaseModel):
    """Output contract for Governance Crew QA review."""
    status: str = Field(
        description="QA status: passed, failed, conditional, escalated"
    )
    framework_compliance: bool = Field(
        default=False,
        description="Whether output follows Strategyzer frameworks"
    )
    logical_consistency: bool = Field(
        default=False,
        description="Whether arguments are internally consistent"
    )
    completeness: bool = Field(
        default=False,
        description="Whether all required elements are present"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of identified issues"
    )
    required_changes: List[str] = Field(
        default_factory=list,
        description="Changes needed to pass"
    )
    confidence_score: float = Field(
        ge=0, le=1, default=0.5,
        description="Confidence in the assessment"
    )


class SynthesisCrewOutput(BaseModel):
    """Output contract for Synthesis Crew evidence integration."""
    evidence_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of all evidence across phases"
    )
    pivot_recommendation: str = Field(
        default="no_pivot",
        description="Recommended pivot type or no_pivot"
    )
    pivot_rationale: str = Field(
        default="",
        description="Reasoning for the recommendation"
    )
    confidence_level: str = Field(
        default="low",
        description="Confidence: low, medium, high"
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Recommended next actions"
    )
    human_input_required: bool = Field(
        default=False,
        description="Whether human approval is needed"
    )
