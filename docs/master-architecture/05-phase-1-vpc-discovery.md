---
purpose: Phase 1 specification - VPC Discovery (Customer Profile + Value Map)
status: active
last_reviewed: 2026-01-07
vpd_compliance: true
---

# Phase 1: VPC Discovery

> **Methodology Reference**: See [03-methodology.md](./03-methodology.md) for VPD framework patterns.

## Purpose

Discover **Customer Reality** (what customers actually need) and design a **Value Map** that addresses those needs. Transform the Founder's hypotheses from Phase 0 into evidence-backed knowledge using the Value Proposition Design framework.

### What This Phase IS About

- Discovering real Jobs, Pains, and Gains through research
- Designing Products, Pain Relievers, and Gain Creators
- Validating Problem-Solution Fit (VPC alignment)
- Testing Willingness to Pay with behavioral evidence
- Achieving Fit Score ≥ 70 to exit

### What This Phase Is NOT About

- Building MVPs or testable artifacts (Phase 2)
- Running ad campaigns or growth experiments (Phase 2)
- Technical feasibility analysis (Phase 3)
- Unit economics and business model validation (Phase 4)

### Entry Criteria

- Phase 0 complete: Founder's Brief approved
- `approve_founders_brief` HITL passed
- Customer segment hypothesis available

### Exit Criteria

- `approve_vpc_completion` HITL passed
- Fit Score ≥ 70
- Jobs addressed ≥ 75%
- Pains addressed ≥ 75%
- Gains addressed ≥ 70%
- WTP validated with behavioral evidence

---

## VPCDiscoveryFlow (Orchestrator)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VPC DISCOVERY FLOW (ORCHESTRATOR)                       │
│                                                                              │
│  Entry: Founder's Brief from Phase 0                                        │
│  Exit: Validated VPC with fit_score ≥ 70                                    │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────────┐                             │
│                         │   Founder's Brief   │                             │
│                         │   (From Phase 0)    │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│                                    ▼                                         │
│                         ┌─────────────────────┐                             │
│                         │  SEGMENT VALIDATION │                             │
│                         │      (Flow 1)       │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│                          ┌─────────┴─────────┐                              │
│                   [segment_exists]    [segment_not_found]                    │
│                          │                   │                               │
│                          │                   ▼                               │
│                          │          SEGMENT_PIVOT                            │
│                          │          (Loop to Brief)                          │
│                          │                                                   │
│                          ▼                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    CUSTOMER PROFILE DISCOVERY                         │  │
│  │                                                                       │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │  │
│  │  │  JOBS DISCOVERY │  │ PAINS DISCOVERY │  │ GAINS DISCOVERY │      │  │
│  │  │    (Flow 2)     │  │    (Flow 3)     │  │    (Flow 4)     │      │  │
│  │  │                 │  │                 │  │                 │      │  │
│  │  │  J1: Research   │  │  P1: Research   │  │  G1: Research   │      │  │
│  │  │  J2: Rank       │  │  P2: Rank       │  │  G2: Rank       │      │  │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │  │
│  │           │                    │                    │               │  │
│  │           └────────────────────┼────────────────────┘               │  │
│  │                                │                                     │  │
│  │                                ▼                                     │  │
│  │                    ┌─────────────────────┐                          │  │
│  │                    │  CUSTOMER PROFILE   │                          │  │
│  │                    │  (Ranked J/P/G)     │                          │  │
│  │                    └─────────────────────┘                          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    VALUE MAP DESIGN                                   │  │
│  │                       (Flow 5)                                        │  │
│  │                                                                       │  │
│  │  V1: Solution Designer     → Products & Services                     │  │
│  │  V2: Pain Reliever Designer → Pain Relievers                         │  │
│  │  V3: Gain Creator Designer  → Gain Creators                          │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│                         ┌─────────────────────┐                             │
│                         │  WILLINGNESS TO PAY │                             │
│                         │      (Flow 6)       │                             │
│                         │                     │                             │
│                         │  W1: Pricing        │                             │
│                         │  W2: Payment Tests  │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│                    ┌───────────────────────────────┐                        │
│                    │  HITL: approve_pricing_test   │                        │
│                    │  (if real $ involved)         │                        │
│                    └───────────────────────────────┘                        │
│                                    │                                         │
│                                    ▼                                         │
│                         ┌─────────────────────┐                             │
│                         │   FIT ASSESSMENT    │                             │
│                         │      (Flow 7)       │                             │
│                         │                     │                             │
│                         │  F1: Fit Analyst    │                             │
│                         │  F2: Iteration Rtr  │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│                      ┌─────────────┼─────────────┐                          │
│                      │             │             │                           │
│               [fit < 40]    [40 ≤ fit < 70]  [fit ≥ 70]                     │
│                      │             │             │                           │
│                      ▼             ▼             ▼                           │
│              SEGMENT_PIVOT   ITERATE      ┌─────────────────────┐          │
│              (wrong customer) (refine VPC) │  approve_vpc_compl  │          │
│                      │             │       │  (HITL)             │          │
│                      │             │       └──────────┬──────────┘          │
│                      │             │                  │                      │
│                      │             │           APPROVE│REJECT                │
│                      │             │                  │    │                 │
│                      │             │                  ▼    │                 │
│                      │             │         ───────────   │                 │
│                      └─────────────┴──────── To Phase 2 ◄──┘                │
│                                              Desirability                    │
│                                              ───────────                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Flow 1: Segment Validation

**Purpose**: Verify the customer segment from Founder's Brief actually exists and is reachable.

### Agents

#### E1: Experiment Designer

| Attribute | Value |
|-----------|-------|
| **ID** | E1 |
| **Name** | Experiment Designer |
| **Founder** | Sage |
| **Role** | Design experiment mix using Assumptions Mapping and Test Cards |
| **Goal** | Create optimal sequence of experiments to validate/invalidate key assumptions |

**Tasks:**
1. `map_assumptions` - Create 2×2 matrix (importance × evidence)
2. `design_test_cards` - Create Test Cards for top-left quadrant
3. `sequence_experiments` - Order by cost/reliability tradeoffs

**Tools:**
- `AssumptionMappingTool`
- `TestCardGeneratorTool`
- `ExperimentLibraryTool` (44 Strategyzer experiments)

---

#### D1: Customer Interview Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D1 |
| **Name** | Customer Interview Agent |
| **Founder** | Sage |
| **Role** | Conduct discovery interviews using The Mom Test methodology |
| **Goal** | Collect SAY evidence about customer problems and needs |

**Tasks:**
1. `identify_interview_candidates` - Find potential customers
2. `conduct_discovery_interviews` - Apply Mom Test rules
3. `analyze_interview_insights` - Extract Jobs, Pains, Gains

**Tools:**
- `InterviewGuide` (Mom Test prompts)
- `InsightExtractor` (NLP for theme identification)
- `TranscriptAnalyzer`

**Interview Rules (The Mom Test):**
```
DO:
- Ask about their life, not your idea
- Ask about specifics in the PAST
- Talk less, listen more (80/20)
- Ask "why" frequently
- Focus on FACTS not opinions

DON'T:
- Ask "Would you buy...?"
- Ask "Do you think...?"
- Offer solutions
- Fish for compliments
- Ask leading questions
```

---

#### D2: Observation Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D2 |
| **Name** | Observation Agent |
| **Founder** | Pulse |
| **Role** | Collect DO-indirect evidence from existing behavior |
| **Goal** | Observe what customers actually DO (not just what they say) |

**Tasks:**
1. `mine_social_discussions` - Forums, Reddit, X, LinkedIn
2. `mine_reviews` - App stores, G2, Capterra, Amazon
3. `analyze_search_trends` - Google Trends, keyword volumes
4. `collect_support_tickets` - If available from Founder

**Tools:**
- `TavilySearchTool`
- `SocialListenerTool`
- `ReviewMinerTool`
- `TrendAnalyzerTool`

**Evidence Collection:**
```
DISCUSSION FORUMS
├── What questions are they asking?
├── What problems are they discussing?
├── What solutions have they tried?
└── What language do they use?

REVIEWS
├── What do they love about alternatives?
├── What do they hate about alternatives?
├── What's missing from current solutions?
└── What would they pay more for?

SEARCH TRENDS
├── Is search volume growing?
├── What related terms are searched?
├── What questions are asked?
└── Seasonal patterns?
```

---

#### D3: CTA Test Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D3 |
| **Name** | CTA Test Agent |
| **Founder** | Pulse |
| **Role** | Collect DO-direct evidence through call-to-action experiments |
| **Goal** | Test behavioral commitment (not just stated interest) |

**Tasks:**
1. `design_smoke_tests` - Landing page experiments
2. `design_fake_door_tests` - Feature interest tests
3. `execute_cta_experiments` - Run and measure
4. `analyze_conversion_data` - Extract signals

**Experiment Types:**
```
SEGMENT EXISTS
├── Landing Page (Smoke Test)
│   - Measure: Signup rate
│   - Pass: 5% signup
│
├── Explainer Video
│   - Measure: Watch-through rate + CTA
│   - Pass: 40% complete, 10% CTA
│
└── Online Ad Campaign
    - Measure: CTR + Landing page conversion
    - Pass: 1% CTR, 5% conversion

SEGMENT REACHABLE
├── Social Media Targeting
│   - Measure: CPM, engagement rate
│   - Pass: CPM < $10, engagement > 2%
│
└── Email Outreach
    - Measure: Open rate, response rate
    - Pass: 30% open, 5% response
```

---

#### D4: Evidence Triangulation Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D4 |
| **Name** | Evidence Triangulation Agent |
| **Founder** | Guardian |
| **Role** | Synthesize SAY vs DO evidence and score confidence |
| **Goal** | Identify discrepancies between stated and behavioral evidence |

**Tasks:**
1. `collect_all_evidence` - Aggregate from D1, D2, D3
2. `weight_by_hierarchy` - Apply SAY/DO weights
3. `identify_discrepancies` - Flag SAY vs DO mismatches
4. `score_confidence` - Calculate overall confidence

**Triangulation Logic:**
```python
def triangulate_evidence(say_evidence, do_evidence):
    # Weight evidence by hierarchy
    weighted_say = sum(e.weight * 1.0 for e in say_evidence)
    weighted_do = sum(e.weight for e in do_evidence)

    # DO evidence worth more
    confidence = (weighted_do * 2 + weighted_say) / 3

    # Flag discrepancies
    discrepancies = []
    if say_positive and do_negative:
        discrepancies.append("SAYING_YES_DOING_NO")  # Major red flag
    if say_negative and do_positive:
        discrepancies.append("LATENT_DEMAND")  # Opportunity signal

    return confidence, discrepancies
```

---

## Flow 2: Jobs Discovery

**Purpose**: Discover what customers are trying to accomplish (Jobs-to-be-Done).

### Agents

#### J1: JTBD Researcher

| Attribute | Value |
|-----------|-------|
| **ID** | J1 |
| **Name** | JTBD Researcher |
| **Founder** | Sage |
| **Role** | Discover Jobs-to-be-Done using JTBD methodology |
| **Goal** | Identify all job types: functional, emotional, social, supporting |

**Tasks:**
1. `discover_functional_jobs` - Tasks they're trying to complete
2. `discover_emotional_jobs` - How they want to feel
3. `discover_social_jobs` - How they want to be perceived
4. `discover_supporting_jobs` - Buyer, co-creator, transferrer jobs
5. `compile_job_inventory` - Complete list with evidence

**JTBD Interview Questions:**
```
FUNCTIONAL JOBS
- "What are you trying to accomplish?"
- "Walk me through your typical [task] process"
- "What does success look like?"

EMOTIONAL JOBS
- "How do you feel when [task] goes well?"
- "What frustrates you most about [task]?"
- "What would make you feel confident about [task]?"

SOCIAL JOBS
- "Who else is involved in this decision?"
- "How do others perceive your approach to [task]?"
- "What would your [boss/peers/team] think if you solved this?"
```

---

#### J2: Job Ranking Agent

| Attribute | Value |
|-----------|-------|
| **ID** | J2 |
| **Name** | Job Ranking Agent |
| **Founder** | Sage |
| **Role** | Rank jobs by importance using evidence |
| **Goal** | Prioritize which jobs matter most to customers |

**Ranking Criteria:**
```
IMPORTANCE SCORE (1-10)
├── Frequency: How often does this job come up?
├── Significance: How important is it when it comes up?
├── Urgency: How pressing is the need?
├── Willingness to pay: Would they pay to solve this?
└── Competitive gap: How poorly served is this job?
```

---

## Flow 3: Pains Discovery

**Purpose**: Discover what customers want to avoid (Pains).

### Agents

#### P1: Pain Researcher

| Attribute | Value |
|-----------|-------|
| **ID** | P1 |
| **Name** | Pain Researcher |
| **Founder** | Sage |
| **Role** | Discover customer pains through research |
| **Goal** | Identify undesired outcomes, obstacles, and risks |

**Pain Categories:**
```
UNDESIRED OUTCOMES
├── What functional outcomes do they want to avoid?
├── What negative emotions do they experience?
├── What social consequences do they fear?

OBSTACLES
├── What prevents them from getting the job done?
├── What makes current solutions hard to use?
├── What slows them down?

RISKS
├── What could go wrong?
├── What are they afraid of?
├── What keeps them up at night?
```

---

#### P2: Pain Ranking Agent

| Attribute | Value |
|-----------|-------|
| **ID** | P2 |
| **Name** | Pain Ranking Agent |
| **Founder** | Sage |
| **Role** | Rank pains by severity |
| **Goal** | Prioritize which pains are most severe |

**Severity Scoring:**
```
EXTREME (10): Showstopper - they'll do anything to avoid
HIGH (7-9): Major frustration - actively seeking solutions
MODERATE (4-6): Annoying but tolerable
LOW (1-3): Mild inconvenience
```

---

## Flow 4: Gains Discovery

**Purpose**: Discover what customers desire (Gains).

### Agents

#### G1: Gain Researcher

| Attribute | Value |
|-----------|-------|
| **ID** | G1 |
| **Name** | Gain Researcher |
| **Founder** | Sage |
| **Role** | Discover customer gains through research |
| **Goal** | Identify required, expected, desired, and unexpected gains |

**Gain Categories:**
```
REQUIRED (Must-have)
├── What minimum outcomes must the solution produce?
├── What are the table-stakes features?

EXPECTED (Standard)
├── What outcomes do they expect from any solution?
├── What's considered normal/baseline?

DESIRED (Nice-to-have)
├── What would delight them?
├── What would exceed expectations?

UNEXPECTED (Delighters)
├── What could we offer beyond their imagination?
├── What innovations would surprise them?
```

---

#### G2: Gain Ranking Agent

| Attribute | Value |
|-----------|-------|
| **ID** | G2 |
| **Name** | Gain Ranking Agent |
| **Founder** | Sage |
| **Role** | Rank gains by importance |
| **Goal** | Prioritize which gains matter most |

---

## Flow 5: Value Map Design

**Purpose**: Design the Value Map side of the VPC to address discovered Customer Profile.

### Agents

#### V1: Solution Designer

| Attribute | Value |
|-----------|-------|
| **ID** | V1 |
| **Name** | Solution Designer |
| **Founder** | Forge |
| **Role** | Design Products & Services that address top-ranked Jobs |
| **Goal** | Create solution concepts that help customers get jobs done |

**Design Principles:**
```
1. Focus on top-ranked Jobs (not all jobs)
2. Address functional, emotional, AND social dimensions
3. Consider the full job lifecycle
4. Design for the job context, not features in isolation
```

---

#### V2: Pain Reliever Designer

| Attribute | Value |
|-----------|-------|
| **ID** | V2 |
| **Name** | Pain Reliever Designer |
| **Founder** | Forge |
| **Role** | Design Pain Relievers for top-ranked Pains |
| **Goal** | Create mechanisms that eliminate or reduce severe pains |

**Design Principles:**
```
1. Focus on extreme/high severity pains
2. A few excellent pain relievers > many mediocre ones
3. Be specific about which pain is addressed
4. Avoid features that don't relieve any pain
```

---

#### V3: Gain Creator Designer

| Attribute | Value |
|-----------|-------|
| **ID** | V3 |
| **Name** | Gain Creator Designer |
| **Founder** | Forge |
| **Role** | Design Gain Creators for top-ranked Gains |
| **Goal** | Create mechanisms that produce desired outcomes |

**Design Principles:**
```
1. Must address REQUIRED gains (table stakes)
2. Should address EXPECTED gains (baseline)
3. Could address DESIRED gains (differentiation)
4. Might address UNEXPECTED gains (delighters)
```

---

## Flow 6: Willingness to Pay

**Purpose**: Validate that customers will pay for the proposed value.

### Agents

#### W1: Pricing Experiment Agent

| Attribute | Value |
|-----------|-------|
| **ID** | W1 |
| **Name** | Pricing Experiment Agent |
| **Founder** | Ledger |
| **Role** | Design WTP experiments |
| **Goal** | Discover price sensitivity and optimal pricing |

**Experiment Types:**
```
DISCOVERY (Stated)
├── Van Westendorp Price Sensitivity
│   - Too expensive
│   - Expensive but would consider
│   - Good deal
│   - Too cheap (suspicious)
│
└── Conjoint Analysis
    - Trade-off between features and price

VALIDATION (Behavioral)
├── A/B Price Testing
│   - Same offer, different prices
│
├── Mock Sale
│   - Full checkout flow, payment not processed
│
└── Pre-sale / Crowdfunding
    - Actual payment collected
```

---

#### W2: Payment Test Agent

| Attribute | Value |
|-----------|-------|
| **ID** | W2 |
| **Name** | Payment Test Agent |
| **Founder** | Ledger |
| **Role** | Execute payment tests with real commitment |
| **Goal** | Collect behavioral evidence of willingness to pay |

**HITL Required**: `approve_pricing_test` before any real money is involved.

---

## Flow 7: Fit Assessment

**Purpose**: Score Problem-Solution Fit and route based on result.

### Agents

#### F1: Fit Analyst

| Attribute | Value |
|-----------|-------|
| **ID** | F1 |
| **Name** | Fit Analyst |
| **Founder** | Compass |
| **Role** | Score Problem-Solution Fit |
| **Goal** | Calculate whether Value Map adequately addresses Customer Profile |

**Fit Score Calculation:**
```python
class FitAssessment(BaseModel):
    jobs_addressed: float       # 0-100%
    pains_addressed: float      # 0-100%
    gains_addressed: float      # 0-100%
    wtp_validated: bool

    @property
    def fit_score(self) -> float:
        return (
            (self.jobs_addressed * 0.30) +
            (self.pains_addressed * 0.35) +
            (self.gains_addressed * 0.25) +
            (100.0 if self.wtp_validated else 0.0) * 0.10
        )

    @property
    def exit_ready(self) -> bool:
        return (
            self.fit_score >= 70 and
            self.jobs_addressed >= 75 and
            self.pains_addressed >= 75 and
            self.gains_addressed >= 70 and
            self.wtp_validated
        )
```

---

#### F2: Iteration Router

| Attribute | Value |
|-----------|-------|
| **ID** | F2 |
| **Name** | Iteration Router |
| **Founder** | Compass |
| **Role** | Route based on fit score |
| **Goal** | Direct flow to appropriate next step |

**Routing Logic:**
```python
def route_by_fit(fit_score: float) -> str:
    if fit_score < 40:
        # Wrong customer segment - radical change needed
        return "SEGMENT_PIVOT"

    elif fit_score < 70:
        # Right customer, wrong value - iterate
        if jobs_addressed < 75:
            return "ITERATE_JOBS"
        elif pains_addressed < 75:
            return "ITERATE_PAINS"
        elif gains_addressed < 70:
            return "ITERATE_GAINS"
        else:
            return "ITERATE_VALUE_MAP"

    else:
        # Fit achieved - proceed
        return "VPC_COMPLETE"
```

---

## Output Schemas

### Value Proposition Canvas (Phase 1 Prime Artifact)

```python
class ValuePropositionCanvas(BaseModel):
    """Complete VPC with Customer Profile and Value Map."""

    vpc_id: str
    project_id: str
    brief_id: str  # Link to Founder's Brief
    version: int = 1
    created_at: datetime
    updated_at: datetime

    # Right side: Customer Profile
    customer_profile: CustomerProfile

    # Left side: Value Map
    value_map: ValueMap

    # Fit assessment
    fit_assessment: FitAssessment

    # Evidence trail
    evidence_summary: EvidenceSummary


class CustomerProfile(BaseModel):
    segment_name: str
    segment_description: str
    segment_validated: bool

    jobs: List[Job]
    pains: List[Pain]
    gains: List[Gain]


class Job(BaseModel):
    job_id: str
    description: str
    job_type: Literal["functional", "emotional", "social", "supporting"]
    importance_rank: int
    importance_score: float  # 1-10
    evidence_sources: List[str]
    addressed_by: List[str]  # Product IDs


class Pain(BaseModel):
    pain_id: str
    description: str
    category: Literal["undesired_outcome", "obstacle", "risk"]
    severity_rank: int
    severity_score: float  # 1-10 (EXTREME=10, HIGH=7-9, etc.)
    evidence_sources: List[str]
    relieved_by: List[str]  # Pain Reliever IDs


class Gain(BaseModel):
    gain_id: str
    description: str
    category: Literal["required", "expected", "desired", "unexpected"]
    importance_rank: int
    importance_score: float  # 1-10
    evidence_sources: List[str]
    created_by: List[str]  # Gain Creator IDs


class ValueMap(BaseModel):
    products_and_services: List[Product]
    pain_relievers: List[PainReliever]
    gain_creators: List[GainCreator]


class Product(BaseModel):
    product_id: str
    name: str
    description: str
    addresses_jobs: List[str]  # Job IDs


class PainReliever(BaseModel):
    reliever_id: str
    description: str
    addresses_pains: List[str]  # Pain IDs
    effectiveness: Literal["eliminates", "reduces", "mitigates"]


class GainCreator(BaseModel):
    creator_id: str
    description: str
    creates_gains: List[str]  # Gain IDs
    level: Literal["produces", "increases", "exceeds"]


class FitAssessment(BaseModel):
    fit_score: float  # 0-100
    jobs_addressed_pct: float
    pains_addressed_pct: float
    gains_addressed_pct: float
    wtp_validated: bool
    wtp_evidence: str
    exit_ready: bool
    iteration_recommendation: Optional[str]


class EvidenceSummary(BaseModel):
    total_interviews: int
    total_observations: int
    total_cta_tests: int
    say_evidence_weight: float
    do_evidence_weight: float
    discrepancies: List[str]
    confidence_score: float
```

---

## HITL Checkpoints

### `approve_experiment_plan`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `approve_experiment_plan` |
| **Phase** | 1 |
| **Owner** | Sage (E1) |
| **Purpose** | Approve experiment mix before execution |
| **Required for Exit** | No (but required before running experiments) |

---

### `approve_pricing_test`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `approve_pricing_test` |
| **Phase** | 1 |
| **Owner** | Ledger (W1, W2) |
| **Purpose** | Approve tests involving real money |
| **Required for Exit** | Yes (if WTP tests involve payment) |

---

### `approve_vpc_completion`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `approve_vpc_completion` |
| **Phase** | 1 |
| **Owner** | Compass (F1) + Founder |
| **Purpose** | Confirm VPC ready for Phase 2 (fit ≥ 70) |
| **Required for Exit** | Yes |

**Presentation:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     VPC DISCOVERY COMPLETE                                   │
│                                                                              │
│  Your Value Proposition Canvas has achieved Problem-Solution Fit.            │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FIT SCORE: 73/100 ✓                                                        │
│  ├── Jobs Addressed: 78% ✓ (threshold: 75%)                                │
│  ├── Pains Addressed: 82% ✓ (threshold: 75%)                               │
│  ├── Gains Addressed: 71% ✓ (threshold: 70%)                               │
│  └── WTP Validated: Yes ✓                                                   │
│                                                                              │
│  CUSTOMER PROFILE (Discovered)                                               │
│  [Summary of validated Jobs, Pains, Gains]                                  │
│                                                                              │
│  VALUE MAP (Designed)                                                        │
│  [Summary of Products, Pain Relievers, Gain Creators]                       │
│                                                                              │
│  EVIDENCE SUMMARY                                                            │
│  [Interview count, observation count, CTA test results]                     │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Ready to proceed to Phase 2: Desirability Validation?                      │
│                                                                              │
│  [APPROVE & CONTINUE]     [REQUEST ITERATION]                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Summary

| ID | Agent | Founder | Flow | Role |
|----|-------|---------|------|------|
| E1 | Experiment Designer | Sage | 1 | Design experiment mix |
| D1 | Customer Interview Agent | Sage | 1 | SAY evidence collection |
| D2 | Observation Agent | Pulse | 1 | DO-indirect evidence |
| D3 | CTA Test Agent | Pulse | 1 | DO-direct evidence |
| D4 | Evidence Triangulation Agent | Guardian | 1 | Evidence synthesis |
| J1 | JTBD Researcher | Sage | 2 | Discover jobs |
| J2 | Job Ranking Agent | Sage | 2 | Rank jobs |
| P1 | Pain Researcher | Sage | 3 | Discover pains |
| P2 | Pain Ranking Agent | Sage | 3 | Rank pains |
| G1 | Gain Researcher | Sage | 4 | Discover gains |
| G2 | Gain Ranking Agent | Sage | 4 | Rank gains |
| V1 | Solution Designer | Forge | 5 | Design products/services |
| V2 | Pain Reliever Designer | Forge | 5 | Design pain relievers |
| V3 | Gain Creator Designer | Forge | 5 | Design gain creators |
| W1 | Pricing Experiment Agent | Ledger | 6 | Design WTP experiments |
| W2 | Payment Test Agent | Ledger | 6 | Execute payment tests |
| F1 | Fit Analyst | Compass | 7 | Score fit |
| F2 | Iteration Router | Compass | 7 | Route by fit score |

**Total Phase 1 Agents: 18**
**Total Phase 1 HITL Checkpoints: 3**

---

## Methodology Compliance

| Pattern | Implementation |
|---------|----------------|
| **VPD Canvas** | Full Customer Profile + Value Map structure |
| **SAY vs DO** | D1 (SAY), D2 (DO-indirect), D3 (DO-direct), D4 (triangulation) |
| **Test Cards** | E1 designs Test Cards before experiments |
| **Learning Cards** | Captured in evidence summary |
| **Assumptions Mapping** | E1 prioritizes assumptions by 2×2 matrix |
| **44 Experiment Library** | D3 uses Strategyzer experiment types |
| **The Mom Test** | D1 follows interview rules |
| **Fit Criteria** | F1 applies VPD fit thresholds |

---

## Related Documents

### Architecture
- [00-introduction.md](./00-introduction.md) - Quick start and orientation
- [01-ecosystem.md](./01-ecosystem.md) - Three-service architecture overview
- [02-organization.md](./02-organization.md) - 6 AI Founders and agents
- [03-methodology.md](./03-methodology.md) - VPD framework reference

### Phase Specifications
- [04-phase-0-onboarding.md](./04-phase-0-onboarding.md) - Founder's Brief capture (previous phase)
- **Phase 1: VPC Discovery** - (this document)
- [06-phase-2-desirability.md](./06-phase-2-desirability.md) - Desirability validation (next phase)
- [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) - Feasibility validation
- [08-phase-4-viability.md](./08-phase-4-viability.md) - Viability + Decision

### Reference
- [09-status.md](./09-status.md) - Current implementation status
- [reference/api-contracts.md](./reference/api-contracts.md) - API specifications
- [reference/approval-workflows.md](./reference/approval-workflows.md) - HITL patterns
