"""
Webhook Payload Contracts.

Pydantic models defining the structure of webhook payloads sent to the product app.
These serve as the contract between CrewAI backend and product app frontend.

The product app should validate incoming webhooks against equivalent Zod schemas.
See: docs/testing-contracts.md for the full cross-repo contract specification.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ===========================================================================
# EVIDENCE PAYLOADS
# ===========================================================================

class DesirabilityEvidencePayload(BaseModel):
    """Evidence from desirability phase - maps to gate_scores.desirability."""

    problem_resonance: float = Field(
        ge=0, le=1,
        description="Fraction of visitors resonating with the problem (0-1)"
    )
    conversion_rate: float = Field(
        ge=0, le=1,
        description="Signup/click conversion rate"
    )
    commitment_depth: str = Field(
        description="Level of commitment: 'none', 'verbal', 'skin_in_game'"
    )
    zombie_ratio: float = Field(
        ge=0, le=1,
        description="Fraction of interested-but-not-committed users"
    )
    traffic_quality: Optional[str] = Field(
        default=None,
        description="Traffic quality assessment: 'High', 'Medium', 'Low'"
    )
    key_learnings: List[str] = Field(
        default_factory=list,
        description="Key insights from experiments"
    )
    tested_segments: List[str] = Field(
        default_factory=list,
        description="Customer segments tested"
    )
    impressions: int = Field(default=0, description="Total ad impressions")
    clicks: int = Field(default=0, description="Total clicks")
    signups: int = Field(default=0, description="Total signups")
    spend_usd: float = Field(default=0.0, description="Total ad spend in USD")


class FeasibilityEvidencePayload(BaseModel):
    """Evidence from feasibility phase - maps to gate_scores.feasibility."""

    core_features_feasible: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of feature -> feasibility status"
    )
    technical_risks: List[str] = Field(
        default_factory=list,
        description="Identified technical risks"
    )
    skill_requirements: List[str] = Field(
        default_factory=list,
        description="Required team skills"
    )
    estimated_effort: Optional[str] = Field(
        default=None,
        description="Estimated build effort (e.g., '3-4 months')"
    )
    downgrade_required: bool = Field(
        default=False,
        description="Whether feature downgrade is needed"
    )
    downgrade_impact: Optional[str] = Field(
        default=None,
        description="Impact of downgrade on value proposition"
    )
    removed_features: List[str] = Field(
        default_factory=list,
        description="Features removed due to constraints"
    )
    alternative_approaches: List[str] = Field(
        default_factory=list,
        description="Alternative technical approaches considered"
    )
    monthly_cost_estimate_usd: float = Field(
        default=0.0,
        description="Estimated monthly infrastructure cost"
    )


class ViabilityEvidencePayload(BaseModel):
    """Evidence from viability phase - maps to gate_scores.viability."""

    cac: float = Field(ge=0, description="Customer Acquisition Cost in USD")
    ltv: float = Field(ge=0, description="Lifetime Value in USD")
    ltv_cac_ratio: float = Field(ge=0, description="LTV/CAC ratio")
    gross_margin: float = Field(
        ge=0, le=1,
        description="Gross margin as decimal (0-1)"
    )
    payback_months: float = Field(
        ge=0,
        description="Months to recover CAC"
    )
    break_even_customers: int = Field(
        ge=0,
        description="Number of customers needed to break even"
    )
    tam_usd: float = Field(
        ge=0,
        description="Total Addressable Market in USD"
    )
    market_share_target: float = Field(
        ge=0, le=1,
        description="Target market share as decimal"
    )
    viability_assessment: Optional[str] = Field(
        default=None,
        description="Summary assessment of viability"
    )


class EvidencePayload(BaseModel):
    """Combined evidence from all three validation phases."""

    desirability: Optional[DesirabilityEvidencePayload] = None
    feasibility: Optional[FeasibilityEvidencePayload] = None
    viability: Optional[ViabilityEvidencePayload] = None


# ===========================================================================
# VALIDATION REPORT PAYLOAD
# ===========================================================================

class ValidationReportPayload(BaseModel):
    """Validation report - maps to reports table."""

    id: str = Field(description="Report ID")
    business_idea: Optional[str] = Field(
        default=None,
        description="The business idea being validated"
    )
    validation_outcome: Optional[str] = Field(
        default=None,
        description="Final recommendation: 'PROCEED', 'PIVOT', 'KILL'"
    )
    evidence_summary: Optional[str] = Field(
        default=None,
        description="Summary of all evidence gathered"
    )
    pivot_recommendation: Optional[str] = Field(
        default=None,
        description="Type of pivot recommended if any"
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Recommended next actions"
    )


# ===========================================================================
# QA REPORT PAYLOAD
# ===========================================================================

class QAReportPayload(BaseModel):
    """QA report from Guardian - maps to qa_reports."""

    status: str = Field(description="'passed', 'failed', 'conditional', 'escalated'")
    framework_compliance: bool = Field(default=True)
    logical_consistency: bool = Field(default=True)
    completeness: bool = Field(default=True)
    specific_issues: List[str] = Field(default_factory=list)
    required_changes: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1)


# ===========================================================================
# MAIN WEBHOOK PAYLOADS
# ===========================================================================

class FounderValidationPayload(BaseModel):
    """
    Complete webhook payload for founder validation results.

    Sent to: POST /api/crewai/webhook
    Product app should:
    1. Parse and validate this payload
    2. Write to: reports, evidence, gate_scores, entrepreneur_briefs tables
    3. Return 200 with {report_id, evidence_created} on success
    """

    flow_type: str = Field(
        default="founder_validation",
        description="Identifies the flow type for routing"
    )
    project_id: str = Field(description="UUID of the project")
    user_id: str = Field(description="UUID of the user/founder")
    kickoff_id: str = Field(default="", description="CrewAI kickoff ID")
    session_id: Optional[str] = Field(
        default=None,
        description="Onboarding session ID"
    )
    validation_report: ValidationReportPayload = Field(
        description="Main validation report"
    )
    value_proposition_canvas: Dict[str, Any] = Field(
        default_factory=dict,
        description="VPC by segment"
    )
    evidence: EvidencePayload = Field(
        description="Evidence from all phases"
    )
    qa_report: Optional[QAReportPayload] = Field(
        default=None,
        description="Guardian QA report"
    )
    completed_at: str = Field(
        description="ISO timestamp of completion"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "flow_type": "founder_validation",
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-3bc4-d567-890123456789",
                "kickoff_id": "kick_abc123",
                "validation_report": {
                    "id": "rpt_001",
                    "business_idea": "AI supply chain optimizer",
                    "validation_outcome": "PROCEED",
                    "next_steps": ["Build MVP", "Find first customer"]
                },
                "evidence": {
                    "desirability": {
                        "problem_resonance": 0.75,
                        "zombie_ratio": 0.15,
                        "commitment_depth": "skin_in_game"
                    },
                    "viability": {
                        "cac": 150.0,
                        "ltv": 1800.0,
                        "ltv_cac_ratio": 12.0
                    }
                },
                "completed_at": "2024-01-15T10:30:00Z"
            }
        }


class CreativeApprovalNeededPayload(BaseModel):
    """Webhook payload when creative approval is needed (HITL pause point)."""

    flow_type: str = Field(default="creative_approval_needed")
    kickoff_id: str
    project_id: str
    user_id: str
    creatives_needing_review: List[Dict[str, Any]] = Field(
        description="List of creatives that need human review"
    )
    auto_approved_creatives: List[str] = Field(
        default_factory=list,
        description="Creatives auto-approved by system"
    )


class ViabilityDecisionNeededPayload(BaseModel):
    """Webhook payload when viability decision is needed (HITL pause point)."""

    flow_type: str = Field(default="viability_decision_needed")
    kickoff_id: str
    project_id: str
    user_id: str
    viability_analysis: Dict[str, Any] = Field(
        description="Analysis and recommendations"
    )
    current_metrics: Dict[str, float] = Field(
        description="Current unit economics metrics"
    )


# ===========================================================================
# WEBHOOK RESPONSE CONTRACTS
# ===========================================================================

class WebhookSuccessResponse(BaseModel):
    """Expected response from product app on successful persistence."""

    report_id: str = Field(description="ID of created/updated report")
    evidence_created: int = Field(
        default=0,
        description="Number of evidence rows created"
    )
    gate_scores_created: int = Field(
        default=0,
        description="Number of gate_score rows created"
    )


# ===========================================================================
# VALIDATION HELPERS
# ===========================================================================

def validate_founder_validation_payload(payload: dict) -> FounderValidationPayload:
    """
    Validate a founder validation webhook payload.

    Raises:
        pydantic.ValidationError: If payload doesn't match contract
    """
    return FounderValidationPayload(**payload)


def create_payload_from_deliverables(
    project_id: str,
    user_id: str,
    kickoff_id: str,
    session_id: Optional[str],
    deliverables: Dict[str, Any]
) -> FounderValidationPayload:
    """
    Create a validated payload from flow deliverables.

    This ensures the payload matches the contract before sending.
    """
    return FounderValidationPayload(
        project_id=project_id,
        user_id=user_id,
        kickoff_id=kickoff_id or "",
        session_id=session_id,
        validation_report=ValidationReportPayload(
            **deliverables.get("validation_report", {})
        ),
        value_proposition_canvas=deliverables.get("value_proposition_canvas", {}),
        evidence=EvidencePayload(
            desirability=DesirabilityEvidencePayload(
                **deliverables.get("evidence", {}).get("desirability", {})
            ) if deliverables.get("evidence", {}).get("desirability") else None,
            feasibility=FeasibilityEvidencePayload(
                **deliverables.get("evidence", {}).get("feasibility", {})
            ) if deliverables.get("evidence", {}).get("feasibility") else None,
            viability=ViabilityEvidencePayload(
                **deliverables.get("evidence", {}).get("viability", {})
            ) if deliverables.get("evidence", {}).get("viability") else None,
        ),
        qa_report=QAReportPayload(
            **deliverables.get("qa_report", {})
        ) if deliverables.get("qa_report") else None,
        completed_at=datetime.now().isoformat(),
    )
