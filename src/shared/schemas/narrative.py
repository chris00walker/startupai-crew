"""
Pydantic models for Pitch Narrative content.

These models define the output_pydantic schema for the narrative synthesis crew.
They mirror the TypeScript PitchNarrativeContent interface from the product app
(frontend/src/lib/narrative/types.ts) to ensure type-safe serialization across
the Python (CrewAI) and TypeScript (Next.js) boundary.

@story US-NL01
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# String Enums
# -----------------------------------------------------------------------------


class DocumentType(str, Enum):
    """Allowed document types for the cover slide."""

    INVESTOR_BRIEFING = "Investor Briefing"
    INVESTOR_PRESENTATION = "Investor Presentation"
    PITCH_DECK = "Pitch Deck"


class InstrumentType(str, Enum):
    """Financial instrument types for the ask."""

    SAFE = "SAFE"
    EQUITY = "equity"
    CONVERTIBLE_NOTE = "convertible_note"


class AskType(str, Enum):
    """Ask types for use of funds (superset of InstrumentType)."""

    SAFE = "SAFE"
    EQUITY = "equity"
    CONVERTIBLE_NOTE = "convertible_note"
    OTHER = "other"


class EvidenceCategory(str, Enum):
    """Evidence hierarchy categories (SAY vs DO)."""

    DO_DIRECT = "DO-direct"
    DO_INDIRECT = "DO-indirect"
    SAY = "SAY"


class MarketSizeUnit(str, Enum):
    """Units for market size measurements."""

    USD = "USD"
    USERS = "users"
    TRANSACTIONS = "transactions"


class MarketSizeTimeframe(str, Enum):
    """Timeframe for market size measurements."""

    ANNUAL = "annual"
    MONTHLY = "monthly"


class MarketSizeConfidence(str, Enum):
    """Confidence levels for market size estimates."""

    ESTIMATED = "estimated"
    RESEARCHED = "researched"
    VERIFIED = "verified"


class SegmentPriority(str, Enum):
    """Priority levels for customer segments."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class GrowthTrend(str, Enum):
    """Growth metric trend directions."""

    ACCELERATING = "accelerating"
    LINEAR = "linear"
    FLAT = "flat"


class DemoAssetType(str, Enum):
    """Types of demo assets."""

    VIDEO = "video"
    SCREENSHOT = "screenshot"
    PROTOTYPE = "prototype"
    ILLUSTRATION = "illustration"


class EvidenceGapType(str, Enum):
    """Types of evidence gaps."""

    MISSING = "missing"
    WEAK = "weak"
    STALE = "stale"


class VisualEmphasis(str, Enum):
    """Visual emphasis levels for evidence display."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


# -----------------------------------------------------------------------------
# Shared Supporting Models
# -----------------------------------------------------------------------------


class MetricSnapshot(BaseModel):
    """A single metric data point with evidence provenance."""

    label: str
    value: str
    evidence_type: EvidenceCategory


class MarketSize(BaseModel):
    """Market size estimate with source and confidence metadata."""

    value: float
    unit: MarketSizeUnit
    timeframe: MarketSizeTimeframe
    source: str
    confidence: MarketSizeConfidence
    normalized_usd_annual: Optional[float] = None


class EvidenceItem(BaseModel):
    """A single piece of evidence in the SAY/DO hierarchy."""

    type: EvidenceCategory
    description: str
    metric_value: Optional[str] = None
    source: str
    weight: float = Field(ge=0.0, le=1.0)


class CustomerSegment(BaseModel):
    """A customer segment with VPD-derived attributes."""

    name: str
    description: str
    size_estimate: int
    priority: SegmentPriority
    jobs_to_be_done: list[str] = Field(default_factory=list)
    key_pains: list[str] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Slide Section Models
# -----------------------------------------------------------------------------


class ContactInfo(BaseModel):
    """Founder contact information for the cover slide."""

    founder_name: str
    email: str
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None


class CoverSection(BaseModel):
    """Cover slide -- title card preceding the essential ten."""

    venture_name: str
    tagline: str = Field(description="Tagline, 10 words or fewer")
    logo_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    document_type: DocumentType
    presentation_date: str = Field(description="ISO date string")
    contact: ContactInfo


class AskInfo(BaseModel):
    """Fundraising ask details."""

    amount: float
    instrument: InstrumentType
    use_summary: str


class OverviewSection(BaseModel):
    """Slide 1: Overview -- thesis, one-liner, and key metrics."""

    thesis: str = Field(description="3-sentence narrative arc")
    one_liner: str = Field(description="'We do X for Y by Z' format")
    industry: str
    novel_insight: str
    key_metrics: list[MetricSnapshot] = Field(default_factory=list)
    ask: Optional[AskInfo] = None


class OpportunitySection(BaseModel):
    """Slide 2: Opportunity -- market sizing and tailwinds."""

    tam: MarketSize
    sam: MarketSize
    som: MarketSize
    growth_trajectory: str
    why_now: str
    market_tailwinds: list[str] = Field(default_factory=list)
    market_confusion: Optional[str] = None


class CustomerStory(BaseModel):
    """An illustrative customer story for the problem slide."""

    name: str
    context: str
    struggle: str


class ProblemSection(BaseModel):
    """Slide 3: Problem -- pain narrative with evidence."""

    primary_pain: str
    pain_narrative: str
    affected_population: str
    customer_story: Optional[CustomerStory] = None
    why_exists: str
    status_quo: str
    severity_score: float = Field(ge=0.0, le=1.0)
    evidence_quotes: list[str] = Field(default_factory=list)


class DemoAsset(BaseModel):
    """A demo asset linked to the solution slide."""

    type: DemoAssetType
    url: str
    caption: Optional[str] = None


class SolutionSection(BaseModel):
    """Slide 4: Solution -- value proposition and differentiation."""

    value_proposition: str
    how_it_works: str
    key_differentiator: str
    use_cases: list[str] = Field(default_factory=list)
    demo_assets: Optional[list[DemoAsset]] = None
    ip_defensibility: Optional[str] = None
    fit_score: float = Field(ge=0.0, le=1.0)


class GrowthMetricDataPoint(BaseModel):
    """A single data point in a growth metric time series."""

    date: str = Field(description="ISO date string")
    value: float


class GrowthMetric(BaseModel):
    """A growth metric with time series data and trend."""

    metric_name: str
    values: list[GrowthMetricDataPoint] = Field(default_factory=list)
    trend: GrowthTrend


class ValidatedAssumption(BaseModel):
    """An assumption that has been validated with evidence."""

    assumption: str
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)


class SalesProcess(BaseModel):
    """Sales funnel stages."""

    attract: str
    educate: str
    qualify: str
    close: str
    service: str


class VisualEmphasisConfig(BaseModel):
    """Visual emphasis levels for each evidence category."""

    do_direct: str = "primary"
    do_indirect: str = "secondary"
    say_evidence: str = "tertiary"


class DisplayConfig(BaseModel):
    """Display configuration for evidence presentation."""

    evidence_order: list[str] = Field(
        default_factory=lambda: ["do_direct", "do_indirect", "say_evidence"]
    )
    show_weights: bool = True
    visual_emphasis: VisualEmphasisConfig = Field(
        default_factory=VisualEmphasisConfig
    )


class TractionSection(BaseModel):
    """Slide 5: Traction -- evidence summary with SAY/DO hierarchy."""

    evidence_summary: str
    growth_metrics: list[GrowthMetric] = Field(default_factory=list)
    assumptions_validated: list[ValidatedAssumption] = Field(default_factory=list)
    sales_process: Optional[SalesProcess] = None
    do_direct: list[EvidenceItem] = Field(default_factory=list)
    do_indirect: list[EvidenceItem] = Field(default_factory=list)
    say_evidence: list[EvidenceItem] = Field(default_factory=list)
    interview_count: int = 0
    experiment_count: int = 0
    hitl_completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    display_config: DisplayConfig = Field(default_factory=DisplayConfig)


class Demographics(BaseModel):
    """Customer demographics summary."""

    location: str
    behaviors: str


class PayingCustomers(BaseModel):
    """Paying customer traction data."""

    count: int
    revenue: float
    example_story: Optional[str] = None


class CustomerSection(BaseModel):
    """Slide 6: Customer -- segments, demographics, and acquisition."""

    segments: list[CustomerSegment] = Field(default_factory=list)
    persona_summary: str
    demographics: Demographics
    willingness_to_pay: str
    market_size: float
    target_percentage: float = Field(ge=0.0, le=1.0)
    target_first: str
    acquisition_channel: str
    acquisition_cost: Optional[float] = None
    paying_customers: Optional[PayingCustomers] = None
    behavioral_insights: list[str] = Field(default_factory=list)
    segment_prioritization: str


class PrimaryCompetitor(BaseModel):
    """A primary competitor with detailed strengths/weaknesses."""

    name: str
    how_they_compete: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class SecondaryCompetitor(BaseModel):
    """A secondary competitor with summary positioning."""

    name: str
    how_they_compete: str


class CompetitorPosition(BaseModel):
    """A competitor's position on the positioning map."""

    name: str
    x: float
    y: float


class PositioningMap(BaseModel):
    """2D positioning map for competitive landscape."""

    x_axis: str
    y_axis: str
    your_position: CompetitorPosition
    competitor_positions: list[CompetitorPosition] = Field(default_factory=list)


class CompetitionSection(BaseModel):
    """Slide 7: Competition -- landscape, differentiators, and moat."""

    landscape_summary: str
    primary_competitors: list[PrimaryCompetitor] = Field(default_factory=list)
    secondary_competitors: list[SecondaryCompetitor] = Field(default_factory=list)
    potential_threats: Optional[list[str]] = None
    positioning_map: Optional[PositioningMap] = None
    differentiators: list[str] = Field(default_factory=list)
    unfair_advantage: str
    incumbent_defense: str


class CostBreakdownItem(BaseModel):
    """A line item in a cost or revenue breakdown."""

    category: str
    amount: float


class UnitEconomics(BaseModel):
    """Unit economics breakdown."""

    cost_per_unit: float
    revenue_per_unit: float
    margin_per_unit: float
    breakdown: list[CostBreakdownItem] = Field(default_factory=list)


class MonthlyCosts(BaseModel):
    """Monthly cost breakdown."""

    total: float
    breakdown: list[CostBreakdownItem] = Field(default_factory=list)


class RevenueProjection(BaseModel):
    """A single revenue projection data point."""

    period: str
    amount: float


class BusinessModelSection(BaseModel):
    """Slide 8: Business Model -- unit economics, pricing, and financials."""

    revenue_model: str
    cac: float
    ltv: float
    ltv_cac_ratio: float
    unit_economics: UnitEconomics
    pricing_strategy: str
    market_context: str
    # Optional founder-supplied financials (excluded from evidence integrity hash)
    monthly_costs: Optional[MonthlyCosts] = None
    burn_rate: Optional[float] = None
    gross_profit: Optional[float] = None
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    cash_flow: Optional[float] = None
    revenue_projections: Optional[list[RevenueProjection]] = None
    path_to_profitability: Optional[str] = None


class TeamMember(BaseModel):
    """A team member's profile."""

    name: str
    current_role: str
    bio: str = Field(description="75 words or fewer")
    prior_experience: list[str] = Field(default_factory=list)
    accomplishments: list[str] = Field(default_factory=list)
    education: Optional[str] = None
    domain_expertise: str
    linkedin_url: Optional[str] = None


class Advisor(BaseModel):
    """An advisor's profile."""

    name: str
    title: str
    relevance: str


class Investor(BaseModel):
    """An existing investor."""

    name: str
    firm: Optional[str] = None


class TeamSection(BaseModel):
    """Slide 9: Team -- members, advisors, and coachability."""

    members: list[TeamMember] = Field(default_factory=list)
    advisors: Optional[list[Advisor]] = None
    investors: Optional[list[Investor]] = None
    hiring_gaps: Optional[list[str]] = None
    team_culture: Optional[str] = None
    coachability_score: float = Field(ge=0.0, le=1.0)


class FundAllocation(BaseModel):
    """A single allocation in the use-of-funds plan."""

    category: str
    amount: float
    percentage: float = Field(ge=0.0, le=100.0)
    validation_experiment: Optional[str] = None


class Milestone(BaseModel):
    """A milestone tied to the funding plan."""

    description: str
    target_date: str = Field(description="ISO date string")
    success_criteria: str


class OtherParticipant(BaseModel):
    """Another participant in the funding round."""

    name: str
    amount: Optional[float] = None
    confirmed: bool = False


class UseOfFundsSection(BaseModel):
    """Slide 10: Use of Funds -- allocations, milestones, and timeline."""

    ask_amount: float
    ask_type: AskType
    allocations: list[FundAllocation] = Field(default_factory=list)
    milestones: list[Milestone] = Field(default_factory=list)
    timeline_weeks: int
    other_participants: Optional[list[OtherParticipant]] = None


# -----------------------------------------------------------------------------
# Metadata
# -----------------------------------------------------------------------------


class PivotInfo(BaseModel):
    """Details about the latest pivot."""

    original_hypothesis: str
    invalidation_evidence: str
    new_direction: str
    pivot_date: str = Field(description="ISO date string")


class EvidenceGap(BaseModel):
    """A gap in the evidence for a specific slide."""

    gap_type: EvidenceGapType
    description: str
    recommended_action: str
    blocking_publish: bool = False


class NarrativeMetadata(BaseModel):
    """Metadata about the narrative generation and evidence quality."""

    methodology: str = Field(default="VPD", pattern="^VPD$")
    evidence_strength: EvidenceCategory
    overall_fit_score: float = Field(ge=0.0, le=1.0)
    validation_stage: str
    pivot_count: int = 0
    latest_pivot: Optional[PivotInfo] = None
    evidence_gaps: Optional[dict[str, EvidenceGap]] = None


# -----------------------------------------------------------------------------
# Top-Level Narrative Content
# -----------------------------------------------------------------------------


class PitchNarrativeContent(BaseModel):
    """
    Complete pitch narrative content.

    This is the output_pydantic schema for the narrative synthesis crew.
    Serialized to JSON and stored in pitch_narratives.narrative_data (JSONB).
    Mirrors the TypeScript PitchNarrativeContent interface from the product app.

    @story US-NL01
    """

    version: str = Field(default="1.0", description="Schema version")

    # Cover (title card preceding the essential ten)
    cover: CoverSection

    # Slide 1: Overview
    overview: OverviewSection

    # Slide 2: Opportunity
    opportunity: OpportunitySection

    # Slide 3: Problem
    problem: ProblemSection

    # Slide 4: Solution
    solution: SolutionSection

    # Slide 5: Traction
    traction: TractionSection

    # Slide 6: Customer
    customer: CustomerSection

    # Slide 7: Competition
    competition: CompetitionSection

    # Slide 8: Business Model
    business_model: BusinessModelSection

    # Slide 9: Team
    team: TeamSection

    # Slide 10: Use of Funds
    use_of_funds: UseOfFundsSection

    # Metadata
    metadata: NarrativeMetadata
