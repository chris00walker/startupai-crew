"""
Viability Approval Tool for HITL Unit Economics Decisions.

Surfaces LTV/CAC metrics and pivot options for human review when
unit economics need strategic decisions.

Used by Finance Crew to:
- Format unit economics for human dashboard display
- Generate pivot recommendations (price vs cost)
- Prepare decision context for /resume webhook
"""

import json
from typing import Dict, Any, Optional, List, ClassVar
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# =======================================================================================
# ENUMS AND MODELS
# =======================================================================================

class ViabilityStatus(str, Enum):
    """Overall viability assessment."""
    PROFITABLE = "profitable"        # LTV/CAC > 3 - proceed
    MARGINAL = "marginal"           # 1 < LTV/CAC < 3 - optimize
    UNDERWATER = "underwater"       # LTV/CAC < 1 - pivot required
    ZOMBIE = "zombie"               # Positive but TAM too small


class PivotRecommendation(str, Enum):
    """Recommended pivot type for underwater economics."""
    PRICE_PIVOT = "price_pivot"     # Increase price to improve LTV
    COST_PIVOT = "cost_pivot"       # Reduce CAC via feature cuts
    SEGMENT_PIVOT = "segment_pivot" # Different market with better economics
    KILL = "kill"                   # No viable path forward


class UnitEconomicsIssue(BaseModel):
    """An issue identified in unit economics analysis."""
    severity: str  # "critical", "warning", "info"
    metric: str
    current_value: float
    threshold_value: float
    message: str
    pivot_hint: Optional[str] = None


class PivotOption(BaseModel):
    """A pivot option for improving unit economics."""
    pivot_type: PivotRecommendation
    description: str
    expected_impact: str  # e.g., "+40% LTV" or "-30% CAC"
    confidence: float  # 0.0-1.0
    tradeoffs: List[str]
    actions: List[str]


class ViabilityApprovalResult(BaseModel):
    """Result from viability analysis for human review."""
    # Core metrics
    cac: float = Field(..., description="Customer Acquisition Cost")
    ltv: float = Field(..., description="Lifetime Value")
    ltv_cac_ratio: float = Field(..., description="LTV/CAC ratio")
    gross_margin: float = Field(..., description="Gross margin percentage")

    # Market context
    tam: Optional[float] = Field(None, description="Total Addressable Market")
    sam: Optional[float] = Field(None, description="Serviceable Addressable Market")

    # Assessment
    status: ViabilityStatus
    issues: List[UnitEconomicsIssue]

    # Pivot options (if needed)
    recommended_pivot: Optional[PivotRecommendation] = None
    pivot_options: List[PivotOption] = Field(default_factory=list)

    # Metadata
    analysis_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    confidence_score: float = 0.0
    summary: str = ""

    @property
    def needs_human_decision(self) -> bool:
        """Whether this requires a human strategic decision."""
        return self.status in [ViabilityStatus.UNDERWATER, ViabilityStatus.ZOMBIE]

    @property
    def critical_issues(self) -> List[UnitEconomicsIssue]:
        """Get only critical issues."""
        return [i for i in self.issues if i.severity == "critical"]


# =======================================================================================
# VIABILITY APPROVAL TOOL
# =======================================================================================

class ViabilityApprovalTool(BaseTool):
    """
    Tool for analyzing unit economics and surfacing pivot options.

    This tool:
    1. Analyzes CAC, LTV, margins, and market size
    2. Identifies viability issues and their severity
    3. Generates pivot recommendations when economics are underwater
    4. Formats results for human dashboard display

    Used by Finance Crew when unit economics need human decision.
    """

    name: str = "viability_approval"
    description: str = """Analyze unit economics and generate pivot recommendations for human review.

    Input: JSON with financial metrics:
    {
        "cac": 150.0,           # Customer Acquisition Cost
        "ltv": 100.0,           # Lifetime Value
        "gross_margin": 0.60,   # Gross margin (0-1)
        "tam": 1000000000,      # Total Addressable Market (optional)
        "monthly_revenue": 5000, # Current MRR (optional)
        "churn_rate": 0.05,     # Monthly churn (optional)
        "conversion_rate": 0.02, # Conversion rate (optional)
        "business_context": {   # Optional context
            "segment": "SMB",
            "pricing_model": "subscription"
        }
    }

    Returns a detailed viability analysis with pivot recommendations."""

    # Industry benchmarks for comparison
    BENCHMARKS: ClassVar[Dict[str, Dict[str, float]]] = {
        "saas": {"ltv_cac_min": 3.0, "gross_margin_min": 0.70, "churn_max": 0.05},
        "ecommerce": {"ltv_cac_min": 2.0, "gross_margin_min": 0.40, "churn_max": 0.10},
        "marketplace": {"ltv_cac_min": 2.5, "gross_margin_min": 0.50, "churn_max": 0.08},
        "default": {"ltv_cac_min": 2.5, "gross_margin_min": 0.50, "churn_max": 0.07},
    }

    def _run(self, input_data: str) -> str:
        """
        Analyze unit economics and generate viability assessment.

        Args:
            input_data: JSON string with financial metrics

        Returns:
            Formatted viability analysis for human review
        """
        try:
            data = json.loads(input_data) if isinstance(input_data, str) else input_data
        except json.JSONDecodeError:
            return "Error: Invalid JSON input. Please provide valid financial metrics."

        # Extract metrics
        cac = data.get("cac", 0)
        ltv = data.get("ltv", 0)
        gross_margin = data.get("gross_margin", 0)
        tam = data.get("tam")

        # Calculate LTV/CAC ratio
        ltv_cac_ratio = ltv / cac if cac > 0 else 0

        # Analyze and generate result
        result = self._analyze_viability(
            cac=cac,
            ltv=ltv,
            ltv_cac_ratio=ltv_cac_ratio,
            gross_margin=gross_margin,
            tam=tam,
            context=data.get("business_context", {})
        )

        return self._format_result(result)

    def analyze_with_result(
        self,
        cac: float,
        ltv: float,
        gross_margin: float,
        tam: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ViabilityApprovalResult:
        """
        Analyze viability and return structured result.

        Convenience method for programmatic use.
        """
        ltv_cac_ratio = ltv / cac if cac > 0 else 0
        return self._analyze_viability(
            cac=cac,
            ltv=ltv,
            ltv_cac_ratio=ltv_cac_ratio,
            gross_margin=gross_margin,
            tam=tam,
            context=context or {}
        )

    def _analyze_viability(
        self,
        cac: float,
        ltv: float,
        ltv_cac_ratio: float,
        gross_margin: float,
        tam: Optional[float],
        context: Dict[str, Any]
    ) -> ViabilityApprovalResult:
        """Perform full viability analysis."""
        issues = []
        pivot_options = []

        # Get benchmarks for business type
        business_type = context.get("business_type", "default")
        benchmarks = self.BENCHMARKS.get(business_type, self.BENCHMARKS["default"])

        # Determine status
        if ltv_cac_ratio >= 3.0:
            status = ViabilityStatus.PROFITABLE
        elif ltv_cac_ratio >= 1.0:
            status = ViabilityStatus.MARGINAL
        else:
            status = ViabilityStatus.UNDERWATER

        # Check for zombie market (profitable but TAM too small)
        if status == ViabilityStatus.PROFITABLE and tam and tam < 10_000_000:
            status = ViabilityStatus.ZOMBIE

        # Identify issues
        if ltv_cac_ratio < benchmarks["ltv_cac_min"]:
            severity = "critical" if ltv_cac_ratio < 1.0 else "warning"
            issues.append(UnitEconomicsIssue(
                severity=severity,
                metric="LTV/CAC Ratio",
                current_value=ltv_cac_ratio,
                threshold_value=benchmarks["ltv_cac_min"],
                message=f"LTV/CAC ratio ({ltv_cac_ratio:.1f}) is below target ({benchmarks['ltv_cac_min']:.1f})",
                pivot_hint="Consider price_pivot to increase LTV or cost_pivot to reduce CAC"
            ))

        if gross_margin < benchmarks["gross_margin_min"]:
            issues.append(UnitEconomicsIssue(
                severity="warning",
                metric="Gross Margin",
                current_value=gross_margin,
                threshold_value=benchmarks["gross_margin_min"],
                message=f"Gross margin ({gross_margin:.0%}) is below target ({benchmarks['gross_margin_min']:.0%})",
                pivot_hint="Review COGS and consider pricing adjustments"
            ))

        # Generate pivot options if needed
        if status in [ViabilityStatus.UNDERWATER, ViabilityStatus.MARGINAL]:
            pivot_options = self._generate_pivot_options(
                cac=cac,
                ltv=ltv,
                ltv_cac_ratio=ltv_cac_ratio,
                gross_margin=gross_margin,
                context=context
            )

        # Determine recommended pivot
        recommended_pivot = None
        if status == ViabilityStatus.UNDERWATER:
            # Prefer price pivot if conversion is strong, otherwise cost pivot
            conversion_rate = context.get("conversion_rate", 0.02)
            if conversion_rate > 0.03:  # Strong conversion suggests price elasticity
                recommended_pivot = PivotRecommendation.PRICE_PIVOT
            else:
                recommended_pivot = PivotRecommendation.COST_PIVOT
        elif status == ViabilityStatus.ZOMBIE:
            recommended_pivot = PivotRecommendation.SEGMENT_PIVOT

        # Calculate confidence score
        confidence = self._calculate_confidence(
            has_tam=tam is not None,
            has_context=bool(context),
            issues_count=len(issues)
        )

        # Generate summary
        summary = self._generate_summary(
            status=status,
            ltv_cac_ratio=ltv_cac_ratio,
            issues=issues,
            recommended_pivot=recommended_pivot
        )

        return ViabilityApprovalResult(
            cac=cac,
            ltv=ltv,
            ltv_cac_ratio=ltv_cac_ratio,
            gross_margin=gross_margin,
            tam=tam,
            status=status,
            issues=issues,
            recommended_pivot=recommended_pivot,
            pivot_options=pivot_options,
            confidence_score=confidence,
            summary=summary
        )

    def _generate_pivot_options(
        self,
        cac: float,
        ltv: float,
        ltv_cac_ratio: float,
        gross_margin: float,
        context: Dict[str, Any]
    ) -> List[PivotOption]:
        """Generate pivot options for improving unit economics."""
        options = []

        # Calculate required improvements
        target_ratio = 3.0
        ltv_increase_needed = (target_ratio * cac) - ltv if ltv > 0 else cac * target_ratio
        cac_reduction_needed = cac - (ltv / target_ratio) if ltv > 0 else cac * 0.5

        # Price pivot option
        price_increase_pct = (ltv_increase_needed / ltv * 100) if ltv > 0 else 50
        options.append(PivotOption(
            pivot_type=PivotRecommendation.PRICE_PIVOT,
            description=f"Increase pricing to improve LTV by ~{price_increase_pct:.0f}%",
            expected_impact=f"+{price_increase_pct:.0f}% LTV",
            confidence=0.6 if price_increase_pct < 30 else 0.4,
            tradeoffs=[
                "May reduce conversion rate",
                "Risk of losing price-sensitive customers",
                "Requires value justification"
            ],
            actions=[
                f"Test higher price point (current + {price_increase_pct:.0f}%)",
                "Add premium features to justify price",
                "Run A/B test on pricing page"
            ]
        ))

        # Cost pivot option
        cost_reduction_pct = (cac_reduction_needed / cac * 100) if cac > 0 else 30
        options.append(PivotOption(
            pivot_type=PivotRecommendation.COST_PIVOT,
            description=f"Reduce CAC by ~{cost_reduction_pct:.0f}% through scope/channel optimization",
            expected_impact=f"-{cost_reduction_pct:.0f}% CAC",
            confidence=0.7 if cost_reduction_pct < 40 else 0.5,
            tradeoffs=[
                "May reduce feature set",
                "Longer time to value for customers",
                "Potential churn increase"
            ],
            actions=[
                "Identify lowest-ROI marketing channels",
                "Simplify product to reduce support costs",
                "Optimize conversion funnel to reduce CAC"
            ]
        ))

        # Segment pivot option (if metrics suggest wrong market)
        if ltv_cac_ratio < 0.5:  # Very underwater
            options.append(PivotOption(
                pivot_type=PivotRecommendation.SEGMENT_PIVOT,
                description="Target different customer segment with better unit economics",
                expected_impact="Reset metrics with new segment",
                confidence=0.5,
                tradeoffs=[
                    "Requires market research",
                    "May invalidate existing learnings",
                    "Longer path to profitability"
                ],
                actions=[
                    "Analyze which customer cohorts have best LTV",
                    "Research adjacent markets with higher willingness to pay",
                    "Consider enterprise vs SMB pivot"
                ]
            ))

        return options

    def _calculate_confidence(
        self,
        has_tam: bool,
        has_context: bool,
        issues_count: int
    ) -> float:
        """Calculate confidence score for the analysis."""
        base_confidence = 0.7

        if has_tam:
            base_confidence += 0.1
        if has_context:
            base_confidence += 0.1

        # More issues = more uncertainty
        base_confidence -= min(0.2, issues_count * 0.05)

        return max(0.3, min(1.0, base_confidence))

    def _generate_summary(
        self,
        status: ViabilityStatus,
        ltv_cac_ratio: float,
        issues: List[UnitEconomicsIssue],
        recommended_pivot: Optional[PivotRecommendation]
    ) -> str:
        """Generate human-readable summary."""
        if status == ViabilityStatus.PROFITABLE:
            return f"Unit economics are healthy (LTV/CAC: {ltv_cac_ratio:.1f}). Proceed with confidence."
        elif status == ViabilityStatus.MARGINAL:
            return f"Unit economics are marginal (LTV/CAC: {ltv_cac_ratio:.1f}). Optimization recommended before scaling."
        elif status == ViabilityStatus.UNDERWATER:
            pivot_text = f"Recommended: {recommended_pivot.value}" if recommended_pivot else "Strategic pivot needed"
            return f"Unit economics are underwater (LTV/CAC: {ltv_cac_ratio:.1f}). {pivot_text}. Human decision required."
        else:  # ZOMBIE
            return f"Market may be too small for sustainable growth. Consider segment pivot."

    def _format_result(self, result: ViabilityApprovalResult) -> str:
        """Format result for display."""
        lines = [
            "## Viability Analysis Complete",
            "",
            f"**Status:** {result.status.value.upper()}",
            f"**Confidence:** {result.confidence_score:.0%}",
            "",
            "### Unit Economics",
            f"- **CAC:** ${result.cac:,.2f}",
            f"- **LTV:** ${result.ltv:,.2f}",
            f"- **LTV/CAC Ratio:** {result.ltv_cac_ratio:.2f}",
            f"- **Gross Margin:** {result.gross_margin:.0%}",
        ]

        if result.tam:
            lines.append(f"- **TAM:** ${result.tam:,.0f}")

        # Issues
        if result.issues:
            lines.extend(["", "### Issues Identified"])
            for issue in result.issues:
                icon = "🔴" if issue.severity == "critical" else "🟡"
                lines.append(f"{icon} **{issue.metric}**: {issue.message}")
        else:
            lines.extend(["", "### No Critical Issues"])

        # Pivot options
        if result.pivot_options:
            lines.extend(["", "### Pivot Options"])
            for i, option in enumerate(result.pivot_options, 1):
                lines.extend([
                    f"",
                    f"**Option {i}: {option.pivot_type.value.replace('_', ' ').title()}**",
                    f"- Impact: {option.expected_impact}",
                    f"- Confidence: {option.confidence:.0%}",
                    f"- Actions: {', '.join(option.actions[:2])}",
                ])

        # Summary
        lines.extend([
            "",
            "### Summary",
            result.summary,
        ])

        # Decision needed
        if result.needs_human_decision:
            lines.extend([
                "",
                "---",
                "**HUMAN DECISION REQUIRED**",
                "Please choose a pivot strategy or decide to proceed/kill.",
            ])

        return "\n".join(lines)


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def analyze_viability(
    cac: float,
    ltv: float,
    gross_margin: float,
    tam: Optional[float] = None,
    context: Optional[Dict[str, Any]] = None
) -> ViabilityApprovalResult:
    """
    Convenience function to analyze unit economics.

    Args:
        cac: Customer Acquisition Cost
        ltv: Lifetime Value
        gross_margin: Gross margin (0-1)
        tam: Total Addressable Market (optional)
        context: Business context dict (optional)

    Returns:
        ViabilityApprovalResult with full analysis
    """
    tool = ViabilityApprovalTool()
    return tool.analyze_with_result(
        cac=cac,
        ltv=ltv,
        gross_margin=gross_margin,
        tam=tam,
        context=context
    )


def format_viability_for_dashboard(result: ViabilityApprovalResult) -> Dict[str, Any]:
    """
    Format viability result for product app dashboard display.

    Returns a dict structure suitable for the dashboard UI.
    """
    return {
        "status": result.status.value,
        "needs_decision": result.needs_human_decision,
        "metrics": {
            "cac": result.cac,
            "ltv": result.ltv,
            "ltv_cac_ratio": result.ltv_cac_ratio,
            "gross_margin": result.gross_margin,
            "tam": result.tam,
        },
        "issues": [
            {
                "severity": issue.severity,
                "metric": issue.metric,
                "message": issue.message,
                "current": issue.current_value,
                "threshold": issue.threshold_value,
            }
            for issue in result.issues
        ],
        "pivot_options": [
            {
                "type": option.pivot_type.value,
                "description": option.description,
                "impact": option.expected_impact,
                "confidence": option.confidence,
                "tradeoffs": option.tradeoffs,
                "actions": option.actions,
            }
            for option in result.pivot_options
        ],
        "recommended_pivot": result.recommended_pivot.value if result.recommended_pivot else None,
        "summary": result.summary,
        "confidence": result.confidence_score,
        "timestamp": result.analysis_timestamp,
    }
