# StartupAI Internal Validation System - Technical Specification

## Document Purpose

This document provides the complete technical specification for building StartupAI's internal validation system using CrewAI Flows. The goal is for StartupAI to "eat its own dog food" - validating its own business model before offering the service to clients.

**Status**: Planning Complete
**Created**: 2025-11-21
**Context Source**: organizational-structure.md contains the conceptual organization this spec implements

---

## Background & Rationale

### Why Build for Ourselves First

StartupAI's value proposition is helping startups validate desirability, feasibility, and viability through AI-powered analysis. If we cannot use our own system to validate our own business model, we cannot credibly offer it to clients.

**The Flywheel Effect**:
- StartupAI validates its own VPC and BMC using the system
- System captures learnings from our validation cycles
- Methodology improves based on real experience
- Clients benefit from battle-tested process
- Client learnings feed back into methodology

### Key Insight: Gated Validation

Validation is **gated**, not parallel:

```
[Test Cycles] → DESIRABILITY GATE → [Test Cycles] → FEASIBILITY GATE → [Test Cycles] → VIABILITY GATE
```

StartupAI's first product iteration focuses on **desirability validation** - the first gate all startups must pass. Feasibility and viability capabilities come later.

---

## Organizational Structure Summary

Reference `docs/master-architecture/organizational-structure.md` for complete details.

### Service/Commercial Model

```
                    GUARDIAN (Board Chair)
                    Accountability for governance
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
SERVICE SIDE            COMPASS             COMMERCIAL SIDE
(Customer-Facing)      (Balance)           (Value Delivery)

Sage owns:            Project Manager      Sage, Forge, Pulse, Ledger
• Customer Service                         (flat peers)
• Founder Onboarding
• Consultant Onboarding
        │
        └──→ [Client Brief] ──────→
```

### The 6 AI Founders

| Founder | Role | Primary Domain |
|---------|------|----------------|
| **Sage** | CSO | Strategy, VPC design, owns Service Side |
| **Forge** | CTO | Build, technical feasibility |
| **Pulse** | CGO | Growth, market signals, desirability evidence |
| **Compass** | CPO | Balance, synthesis, pivot/proceed |
| **Guardian** | CGO | Governance, accountability, oversight |
| **Ledger** | CFO | Finance, viability, compliance |

### 18 Specialist Agents

**Service Side (Sage owns)**: Customer Service, Founder Onboarding, Consultant Onboarding

**Commercial Side**:
- Sage: Customer Researcher, Competitor Analyst
- Forge: UX/UI Designer, Frontend Developer, Backend Developer
- Pulse: Ad Creative, Communications, Social Media Analyst
- Compass: Project Manager
- Ledger: Financial Controller, Legal & Compliance

**Governance (Guardian)**: Audit Agent, Security Agent, Quality Assurance Agent

---

## CrewAI Architecture Decisions

### Why Flows + Crews

CrewAI provides two complementary systems:

- **Crews**: Autonomous agent teams that collaborate on tasks
- **Flows**: Event-driven orchestration that coordinates multiple crews

For StartupAI's Service/Commercial model:
- Each "side" or founder domain = separate Crew
- Flow orchestrates handoffs between crews
- Routers implement Guardian's governance gates
- Structured state carries the Client Brief through the system

### Key CrewAI Features Used

| Requirement | CrewAI Feature |
|-------------|----------------|
| Service → Commercial handoff | `@listen()` decorators chain crews |
| Guardian governance gates | `@router()` with conditional routing |
| Client Brief schema | Structured State with Pydantic |
| Audit trail | `@persist` decorator for SQLite storage |
| Founder as manager | `manager_agent` in hierarchical process |
| Compass synthesis | Router that evaluates all outcomes |

### Process Types

- **Sequential**: Tasks flow in order within a crew
- **Hierarchical**: Manager agent delegates and validates (used where founders oversee agents)
- **Flows**: Orchestrate between crews with routing logic

---

## Phase 1: Service Side + Desirability Validation

**Objective**: Intake StartupAI's own business context → Analyze customers/competitors → Validate desirability assumptions

### Crews to Build

#### 1. Service Crew (Sage owns)

**Purpose**: Onboard StartupAI itself as the "client"

**Agents**:
- Customer Service Agent - Not needed for internal use
- Founder Onboarding Agent - Captures StartupAI's business context
- Consultant Onboarding Agent - Not needed for internal use

**For internal validation, simplify to**:
- Internal Onboarding Agent - Structured interview for StartupAI's own VPC/BMC

**Output**: StartupAI Client Brief

**Client Brief Schema**:
```python
class StartupAIBrief(BaseModel):
    id: str
    business_idea: str = "AI-powered startup validation platform"
    customer_segments: List[str] = ["Founders", "Consultants/Agencies"]
    problem_statement: str
    current_stage: str
    key_assumptions: List[Assumption]
    validation_goals: List[str]

class Assumption(BaseModel):
    statement: str
    category: str  # desirability, feasibility, viability
    priority: int
    evidence_needed: str
```

#### 2. Analysis Crew (Sage)

**Purpose**: Analyze StartupAI's customers and competitors

**Agents**:
- Customer Researcher
  - Analyze Founders segment: Jobs, Pains, Gains
  - Analyze Consultants segment: Jobs, Pains, Gains
  - Output: Customer Profiles for both segments

- Competitor Analyst
  - Traditional consulting ($3-10K, 2-4 weeks)
  - DIY tool stack ($300+/mo, 80+ hrs/mo)
  - Other AI validation tools
  - Output: Competitive positioning map

**Output**: VPC components ready for testing

#### 3. Governance Crew (Guardian) - Phase 1 Version

**Purpose**: Validate analysis quality before proceeding

**Agents**:
- QA Agent
  - Framework compliance check (VPC structure)
  - Logical consistency
  - Completeness validation

**Output**: QA Pass/Fail with feedback

### Phase 1 Flow Structure

```python
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel

class InternalValidationState(BaseModel):
    id: str
    brief: StartupAIBrief
    founder_profile: CustomerProfile = None
    consultant_profile: CustomerProfile = None
    competitor_analysis: CompetitorReport = None
    qa_status: str = "pending"
    qa_feedback: str = ""

class Phase1Flow(Flow[InternalValidationState]):

    @start()
    def capture_startupai_brief(self):
        """Onboard StartupAI as our own client"""
        result = ServiceCrew().crew().kickoff(
            inputs={"context": "StartupAI internal validation"}
        )
        self.state.brief = result.pydantic

    @listen(capture_startupai_brief)
    def analyze_founder_segment(self):
        """Customer research for Founders"""
        result = AnalysisCrew().crew().kickoff(
            inputs={
                "segment": "Founders",
                "brief": self.state.brief.dict()
            }
        )
        self.state.founder_profile = result.pydantic

    @listen(capture_startupai_brief)
    def analyze_consultant_segment(self):
        """Customer research for Consultants"""
        result = AnalysisCrew().crew().kickoff(
            inputs={
                "segment": "Consultants",
                "brief": self.state.brief.dict()
            }
        )
        self.state.consultant_profile = result.pydantic

    @listen(analyze_founder_segment, analyze_consultant_segment)
    def analyze_competitors(self):
        """Competitive landscape analysis"""
        result = AnalysisCrew().crew().kickoff(
            inputs={
                "task": "competitor_analysis",
                "brief": self.state.brief.dict()
            }
        )
        self.state.competitor_analysis = result.pydantic

    @listen(analyze_competitors)
    def governance_review(self):
        """Guardian QA gate"""
        result = GovernanceCrew().crew().kickoff(
            inputs={
                "brief": self.state.brief.dict(),
                "founder_profile": self.state.founder_profile.dict(),
                "consultant_profile": self.state.consultant_profile.dict(),
                "competitor_analysis": self.state.competitor_analysis.dict()
            }
        )
        self.state.qa_status = result.status
        self.state.qa_feedback = result.feedback

    @router(governance_review)
    def qa_gate(self):
        if self.state.qa_status == "passed":
            return "approved"
        return "needs_revision"

    @listen("needs_revision")
    def revise_analysis(self):
        """Loop back with QA feedback"""
        # Re-run analysis with feedback
        pass

    @listen("approved")
    def output_phase1_deliverables(self):
        """Compile Phase 1 outputs"""
        return {
            "vpc_founders": self.state.founder_profile,
            "vpc_consultants": self.state.consultant_profile,
            "competitor_map": self.state.competitor_analysis,
            "assumptions_to_test": self.state.brief.key_assumptions
        }
```

### Phase 1 Success Criteria

- [ ] StartupAI Brief captured with business context
- [ ] Customer Profile for Founders (Jobs/Pains/Gains)
- [ ] Customer Profile for Consultants (Jobs/Pains/Gains)
- [ ] Competitor Analysis with positioning
- [ ] Key assumptions identified and prioritized
- [ ] Guardian QA passes analysis quality
- [ ] Desirability experiment designs ready

### Phase 1 Deliverables

1. **StartupAI VPC** - Value Proposition Canvas for both segments
2. **Assumption Backlog** - Prioritized list of desirability assumptions
3. **Experiment Designs** - How to test each assumption
4. **QA Report** - Guardian's validation of analysis quality

---

## Phase 2: Commercial Side + Build/Test Capabilities

**Objective**: Build testable artifacts → Run desirability experiments → Synthesize evidence → Pivot/Proceed

### Crews to Build

#### 4. Build Crew (Forge)

**Purpose**: Create testable artifacts for desirability validation

**Agents**:
- UX/UI Designer
  - Design landing pages for Founders
  - Design landing pages for Consultants
  - Design key user flows

- Frontend Developer
  - Implement landing pages
  - Build interactive prototypes

- Backend Developer
  - API for data collection
  - Analytics integration

**Output**: Deployed testable artifacts with tracking

#### 5. Growth Crew (Pulse)

**Purpose**: Run experiments and collect desirability signals

**Agents**:
- Ad Creative Agent
  - Ad copy variations for Founders
  - Ad copy variations for Consultants
  - Landing page copy

- Communications Agent
  - Email sequences
  - Content marketing pieces

- Social Media Analyst
  - Track engagement signals
  - Sentiment analysis
  - Conversion metrics

**Output**: Desirability evidence (quantitative + qualitative)

#### 6. Synthesis Crew (Compass)

**Purpose**: Integrate evidence and recommend pivot/proceed

**Agents**:
- Project Manager
  - Aggregate evidence across experiments
  - Track against assumptions
  - Prepare pivot/proceed analysis

**Output**: Evidence synthesis with recommendation

### Phase 2 Flow Structure

```python
class Phase2Flow(Flow[InternalValidationState]):

    @listen("approved")  # From Phase 1
    def design_experiments(self):
        """Design desirability experiments"""
        result = SynthesisCrew().crew().kickoff(
            inputs={
                "task": "experiment_design",
                "assumptions": self.state.brief.key_assumptions,
                "segments": ["Founders", "Consultants"]
            }
        )
        self.state.experiment_designs = result.pydantic

    @listen(design_experiments)
    def build_test_artifacts(self):
        """Forge builds MVPs for testing"""
        result = BuildCrew().crew().kickoff(
            inputs={
                "experiments": self.state.experiment_designs,
                "segments": ["Founders", "Consultants"]
            }
        )
        self.state.artifacts = result.pydantic

    @listen(build_test_artifacts)
    def run_growth_experiments(self):
        """Pulse runs desirability tests"""
        result = GrowthCrew().crew().kickoff(
            inputs={
                "artifacts": self.state.artifacts,
                "experiments": self.state.experiment_designs,
                "budget": "$450-525 per segment"
            }
        )
        self.state.evidence = result.pydantic

    @listen(run_growth_experiments)
    def synthesize_evidence(self):
        """Compass synthesizes and recommends"""
        result = SynthesisCrew().crew().kickoff(
            inputs={
                "task": "evidence_synthesis",
                "evidence": self.state.evidence,
                "assumptions": self.state.brief.key_assumptions
            }
        )
        self.state.synthesis = result.pydantic
        self.state.recommendation = result.recommendation

    @router(synthesize_evidence)
    def pivot_proceed_gate(self):
        if self.state.recommendation == "proceed":
            return "proceed_to_feasibility"
        elif self.state.recommendation == "pivot":
            return "pivot_and_retry"
        return "need_more_evidence"

    @listen("pivot_and_retry")
    def design_pivot(self):
        """Redesign VPC based on evidence and retry"""
        # Loop back to Phase 1 with pivot insights
        pass

    @listen("proceed_to_feasibility")
    def output_phase2_deliverables(self):
        """Compile Phase 2 outputs"""
        return {
            "evidence_report": self.state.evidence,
            "synthesis": self.state.synthesis,
            "recommendation": self.state.recommendation,
            "validated_assumptions": [...],
            "invalidated_assumptions": [...]
        }
```

### Phase 2 Success Criteria

- [ ] Landing pages deployed for both segments
- [ ] Ad campaigns run with real spend
- [ ] Quantitative signals collected (CTR, conversions)
- [ ] Qualitative feedback gathered
- [ ] Evidence synthesized against assumptions
- [ ] Compass delivers pivot/proceed recommendation
- [ ] If pivot: clear direction for VPC iteration

### Phase 2 Deliverables

1. **Test Artifacts** - Landing pages, ads, prototypes
2. **Evidence Report** - All signals collected with analysis
3. **Assumption Validation** - Which assumptions validated/invalidated
4. **Pivot/Proceed Recommendation** - Compass's synthesis

---

## Phase 3: Governance + Viability + Full Loop

**Objective**: Complete governance oversight → Viability validation → Flywheel capture

### Crews to Build

#### 7. Finance Crew (Ledger)

**Purpose**: Validate viability of StartupAI's business model

**Agents**:
- Financial Controller
  - Track actual costs of validation cycles
  - Calculate unit economics
  - Model pricing scenarios

- Legal & Compliance Agent
  - Terms of service
  - Data privacy compliance
  - Regulatory requirements

**Output**: Viability assessment with financial model

#### 8. Enhanced Governance Crew (Guardian)

**Purpose**: Full audit trail and compliance

**Agents**:
- Audit Agent
  - Process compliance verification
  - Decision trail documentation
  - Accountability tracking

- Security Agent
  - Data privacy review
  - Security assessment
  - Risk monitoring

- QA Agent (enhanced)
  - Cross-crew quality checks
  - Methodology compliance

**Output**: Audit report with compliance status

### Phase 3 Flow Structure

```python
class Phase3Flow(Flow[InternalValidationState]):

    @listen("proceed_to_feasibility")  # From Phase 2
    def feasibility_assessment(self):
        """Can we build what we're promising?"""
        result = BuildCrew().crew().kickoff(
            inputs={
                "task": "feasibility_assessment",
                "validated_vp": self.state.synthesis.validated_value_prop
            }
        )
        self.state.feasibility = result.pydantic

    @listen(feasibility_assessment)
    def viability_analysis(self):
        """Can we make money doing this?"""
        result = FinanceCrew().crew().kickoff(
            inputs={
                "costs": self.state.actual_costs,
                "pricing": self.state.pricing_tests,
                "market_size": self.state.market_analysis
            }
        )
        self.state.viability = result.pydantic

    @listen(viability_analysis)
    def final_governance_audit(self):
        """Guardian's comprehensive review"""
        result = GovernanceCrew().crew().kickoff(
            inputs={
                "task": "final_audit",
                "full_state": self.state.dict()
            }
        )
        self.state.audit_report = result.pydantic

    @router(final_governance_audit)
    def guardian_final_gate(self):
        if self.state.audit_report.passed:
            return "validated"
        return "remediation_needed"

    @listen("validated")
    def capture_flywheel_learnings(self):
        """Record learnings for methodology improvement"""
        # Store in persistent knowledge base
        self.state.flywheel_entry = {
            "cycle_id": self.state.id,
            "assumptions_tested": [...],
            "evidence_patterns": [...],
            "methodology_improvements": [...],
            "timestamp": datetime.now()
        }
        return self.state
```

### Phase 3 Success Criteria

- [ ] Feasibility confirmed for core value proposition
- [ ] Unit economics calculated and viable
- [ ] Pricing validated with willingness-to-pay data
- [ ] Full audit trail documented
- [ ] Security and compliance verified
- [ ] Flywheel learnings captured
- [ ] Methodology improvements documented

### Phase 3 Deliverables

1. **Feasibility Report** - Can we build this?
2. **Viability Model** - Unit economics, pricing, runway
3. **Audit Trail** - Full compliance documentation
4. **Flywheel Entry** - Learnings for methodology improvement
5. **Methodology Updates** - Improvements based on experience

---

## Implementation File Structure

```
src/startupai/
├── flows/
│   ├── __init__.py
│   ├── internal_validation_flow.py    # Combined flow
│   └── state_schemas.py               # Pydantic models
│
├── crews/
│   ├── service/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── service_crew.py
│   │
│   ├── analysis/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── analysis_crew.py
│   │
│   ├── governance/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── governance_crew.py
│   │
│   ├── build/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── build_crew.py
│   │
│   ├── growth/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── growth_crew.py
│   │
│   ├── synthesis/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── synthesis_crew.py
│   │
│   └── finance/
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       └── finance_crew.py
│
├── tools/
│   ├── web_search.py
│   ├── analytics.py
│   └── report_generator.py
│
└── knowledge/
    └── flywheel_learnings.json
```

---

## Marketing Site AI Integration

The marketing site (startupai.site) requires AI integration to embody our transparency values and demonstrate the AI Founders' capabilities before conversion.

### Customer Service Agent

**Dual Placement Strategy**:

#### 1. Floating Chat Widget
- Persistent bottom-right bubble available on all pages
- General support agent answering questions about StartupAI, pricing, features
- Implemented in site `layout.tsx` for global availability
- Uses Vercel AI SDK for streaming responses

#### 2. Founder-Specific Chat in Modals
- Extend `FounderProfileCard.tsx` with tabbed interface: "Profile" | "Chat"
- Each founder responds in character based on their role:
  - **Sage**: Strategy questions, VPC design, customer insights
  - **Forge**: Technical feasibility, build considerations
  - **Pulse**: Growth tactics, market signals
  - **Compass**: Synthesis, tradeoffs, decision support
  - **Guardian**: Governance, risk, accountability
  - **Ledger**: Financial viability, unit economics
- System prompts derived from founder personality/role in `aiFounders` data

#### Backend Architecture
- Netlify function: `/.netlify/functions/chat`
- Input: `{ message: string, founderId?: string, context?: string }`
- Routes to AI model with founder-specific system prompts
- Stores conversation history in Supabase for continuity

### Live Data Integration

Replace all hardcoded mock data with live platform metrics to demonstrate transparency.

#### Supabase Schema (New Tables)

```sql
-- Aggregated platform statistics
CREATE TABLE platform_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_name TEXT NOT NULL,          -- 'validations_completed', 'mvps_built', etc.
  metric_value INTEGER NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Anonymized recent agent activities
CREATE TABLE public_activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  founder_id TEXT NOT NULL,           -- 'sage', 'forge', etc.
  activity_type TEXT NOT NULL,        -- 'analysis', 'build', 'validation'
  description TEXT NOT NULL,          -- Anonymized activity description
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Per-founder performance metrics
CREATE TABLE founder_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  founder_id TEXT NOT NULL UNIQUE,
  analyses_completed INTEGER DEFAULT 0,
  accuracy_rate DECIMAL(5,2),
  avg_response_time INTERVAL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Netlify Functions (Data Layer)

**`/.netlify/functions/metrics`**
- Returns: platform stats + founder stats
- Caches responses (5-10 min TTL)
- Reduces Supabase load

**`/.netlify/functions/activities`**
- Returns: recent anonymized activities
- Filterable by founder
- Paginated results

#### Frontend Data Flow

**Current State** (to replace):
```typescript
// src/data/agentActivity.ts - hardcoded
export const aiFounders = [
  { name: "Guardian", stats: { analyses: 142, accuracy: "94%" } },
  // ...
];
```

**Target State**:
```typescript
// src/data/agentActivity.ts - fetches live data
export async function getFounderStats(): Promise<FounderStats[]> {
  const response = await fetch('/.netlify/functions/metrics');
  return response.json();
}

// Components use React Query or SWR for caching
const { data: founders, isLoading } = useQuery('founders', getFounderStats);
```

#### Mock Data Locations to Replace

| File | Data | Replacement |
|------|------|-------------|
| `src/data/agentActivity.ts:45-192` | `aiFounders` stats | `/.netlify/functions/metrics` |
| `src/data/agentActivity.ts:195-265` | `recentActivities` | `/.netlify/functions/activities` |
| `src/data/agentActivity.ts` | `dashboardMetrics` | `/.netlify/functions/metrics` |
| `src/app/demo/dashboard/page.tsx:29-65` | `activeWorkflows` | Keep demo data (not production) |

**Note**: Static data (names, roles, avatars, personalities) remains hardcoded. Only dynamic metrics and activities fetch from API.

### Implementation Sequence

1. **Supabase schema** - Create tables for metrics and activities
2. **Netlify functions** - Build data fetching endpoints with caching
3. **Update agentActivity.ts** - Export async fetch functions instead of static arrays
4. **Component updates** - Add loading states, error handling, async data fetching
5. **Shared chat component** - Build reusable chat UI
6. **Floating widget** - Implement global chat bubble
7. **Founder modal chat** - Add chat tab to existing modals
8. **Chat backend** - Create Netlify function with founder-specific prompts

### Data Architecture Decision

**Recommended: Netlify Functions → Supabase**

Rationale:
- Keeps marketing site self-contained and deployable
- Enables caching to reduce Supabase load
- Allows rate limiting and security at function layer
- Can be upgraded to call product app API later if needed
- Consistent with existing `/.netlify/functions/contact` pattern

---

## Product App Smart Artifact Architecture

### Vision: Reimagining Strategyzer Frameworks

Traditional Strategyzer tools (VPC, BMC, Testing Business Ideas) rely on static formats: PDFs, posters, whiteboards, sticky notes. While helpful for ideation, these are a "horror show to maintain" - disconnected, unversioned, and divorced from actual validation evidence.

**The StartupAI reimagining**:
- Transform canvases from static documents into **living digital artifacts**
- Wire frameworks together so insights flow between VPC, BMC, and TBI
- Connect canvases to real testing assets and evidence
- Enable both human DIY entry and AI agent population
- Keep humans in the loop with configurable approval checkpoints

### Human/AI Mode Configuration

All four interaction modes are configurable in dashboard settings:

| Mode | Scope | Behavior |
|------|-------|----------|
| **Global toggle** | Project-level | Set DIY or AI-assisted mode for entire project |
| **Per-canvas toggle** | Canvas-level | VPC, BMC, TBI can each be independently DIY or AI |
| **Per-section hybrid** | Section-level | Within a canvas, some sections DIY, others AI-populated |
| **Suggestion-based** | Entry-level | AI always suggests, human confirms/edits before save |

**Default behavior**: AI does initial heavy lifting (populating canvases from onboarding brief and analysis), but all modes are selectable. Users choose their level of control.

### Approval Checkpoints

Six categories of actions require explicit human approval before AI proceeds:

#### 1. Spend Increases
- Any experiment or test that costs money beyond current budget
- Ad spend, user testing incentives, tool subscriptions
- Shows projected cost, ROI estimate, and alternatives

#### 2. Campaign Launch
- All advertising and marketing campaigns before they go live
- **Critical control point**: Content leaves StartupAI's ecosystem and enters the broader internet/social media
- Includes: ad creative, copy, targeting parameters, landing pages, email sequences
- Client reviews and signs off on everything that will represent their brand publicly

#### 3. Stage Gate Progression
- Moving between validation stages: Desirability → Feasibility → Viability
- Guardian QA must pass before gate unlock is offered
- Human reviews evidence synthesis and confirms readiness

#### 4. Pivot Recommendations
- When evidence suggests significant VPC/BMC changes
- Compass synthesizes invalidated assumptions
- Human approves pivot direction before AI updates canvases

#### 5. Direct Customer Contact
- Before AI initiates contact with real people (interview requests, survey outreach, user testing recruitment)
- Different from broadcast campaigns - this is 1:1 or 1:few contact representing the client
- Includes: email outreach, LinkedIn messages, phone call scripts
- Client reviews messaging and target list before contact begins

#### 6. Third-Party Data Sharing
- When system needs to share client project data with external tools or services
- Connecting to new APIs, uploading data to testing platforms, analytics integrations
- Shows: what data will be shared, with whom, for what purpose, retention policy
- Client retains control over where their business data goes

**Approval UI**: Modal with clear context, evidence summary, and approve/reject/modify options.

### Approval Workflow Architecture

#### Approval Types & Default Behaviors

| Approval Type | Default Behavior | Rationale |
|---------------|------------------|-----------|
| Campaign Launch | **Blocking** | High risk - content goes public |
| Direct Customer Contact | **Blocking** | Represents client to real people |
| Spend Increases | **Blocking** | Financial commitment |
| Third-Party Data Sharing | Parallel | Can queue while AI continues |
| Stage Gate Progression | **Blocking** | Major strategic decision |
| Pivot Recommendations | **Blocking** | Major strategic direction change |

Users can override defaults per project via delegation settings.

#### Notification Escalation

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Immediate  │ ──→ │   +15 min   │ ──→ │   +24 hrs   │ ──→ │   +48 hrs   │
│   In-app    │     │    Email    │     │  SMS/Push   │     │  Escalate   │
│ notification│     │    alert    │     │ (if urgent) │     │ to backup   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

- **Urgency classification**: System assigns urgency based on approval type and context
- **Time-sensitive examples**: Campaign with scheduled launch, expiring ad credits
- **Escalation path**: Secondary approver (if configured) or project pause

#### Delegation Control System

Both Founders and Consultants can configure approval delegation:

**Auto-Approve Rules**:
- Per approval type (e.g., "auto-approve spend under $50")
- Per project phase (e.g., "auto-approve all desirability experiments")
- Per evidence strength (e.g., "auto-proceed if Guardian QA passes with >90%")

**Consultant-Specific Options**:
- **Operational vs. Client-Facing**: Consultants can auto-approve operational decisions while routing brand-facing decisions to clients
- **Approval Summaries**: Batch low-risk auto-approvals into daily digest for client awareness
- **Override Authority**: Define which approvals consultant can make on client's behalf

**Presets**:
- "High Control" - All approvals require explicit sign-off
- "Balanced" - Block campaigns/contact/gates, parallel for data/spend-under-threshold
- "High Autonomy" - Auto-approve within budget, only block campaigns and gates
- "Custom" - Full configuration control

#### Approval Queue Interface

**Dashboard View**:
- Pending approvals sorted by urgency
- Grouped by project and type
- Quick-approve for low-risk items
- Bulk actions for similar approvals

**Approval Detail Modal**:
- Context: What AI wants to do and why
- Evidence: Supporting data and analysis
- Risk assessment: What could go wrong
- Alternatives: Other options considered
- Actions: Approve / Reject / Modify / Delegate

**Audit Trail**:
- All approvals logged with timestamp, user, decision, and any modifications
- Required for Guardian governance reporting
- Exportable for compliance

#### Database Schema Additions

```sql
-- Approval requests
CREATE TABLE approval_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  approval_type TEXT NOT NULL,  -- 'campaign', 'spend', 'contact', etc.
  status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'modified'
  urgency TEXT DEFAULT 'normal', -- 'low', 'normal', 'high', 'critical'
  blocks_workflow BOOLEAN DEFAULT true,

  -- Request details
  title TEXT NOT NULL,
  description TEXT,
  context JSONB,                 -- AI's reasoning and evidence
  requested_action JSONB,        -- What AI wants to do
  alternatives JSONB,            -- Other options considered

  -- Resolution
  resolved_by UUID REFERENCES users(id),
  resolved_at TIMESTAMPTZ,
  resolution_notes TEXT,
  modifications JSONB,           -- Changes made by approver

  -- Escalation
  escalation_level INTEGER DEFAULT 0,
  escalated_to UUID REFERENCES users(id),

  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User delegation preferences
CREATE TABLE approval_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  project_id UUID REFERENCES projects(id), -- NULL for global defaults

  approval_type TEXT NOT NULL,
  auto_approve BOOLEAN DEFAULT false,
  auto_approve_conditions JSONB,  -- e.g., {"max_spend": 50, "min_qa_score": 0.9}
  notification_channels TEXT[],   -- ['in_app', 'email', 'sms']
  escalation_contact UUID REFERENCES users(id),

  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, project_id, approval_type)
);
```

#### Key Implementation Files

**Approval System**:
- New: `frontend/src/components/approvals/ApprovalQueue.tsx`
- New: `frontend/src/components/approvals/ApprovalDetailModal.tsx`
- New: `frontend/src/components/settings/DelegationSettings.tsx`
- New: `frontend/src/hooks/useApprovals.ts`

**Notifications**:
- New: `frontend/src/services/notifications.ts`
- New: `backend/src/jobs/approval-escalation.ts` (cron job)

**Database**:
- New: `frontend/src/db/schema/approvals.ts`
- New: `frontend/src/db/schema/approval-preferences.ts`

### Framework Wiring Logic

#### Stage-Based BMC Population

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS MODEL CANVAS                        │
├─────────────┬─────────────┬───────────────┬─────────────────────┤
│ Key         │ Key         │ Value         │ Customer      │ Customer   │
│ Partners    │ Activities  │ Propositions  │ Relationships │ Segments   │
│ [FEAS]      │ [FEAS]      │ [DESIR]       │ [DESIR/FEAS]  │ [DESIR]    │
├─────────────┴─────────────┼───────────────┼───────────────┴─────┤
│ Key Resources             │               │ Channels            │
│ [FEAS]                    │               │ [DESIR/FEAS]        │
├───────────────────────────┴───────────────┴─────────────────────┤
│ Cost Structure [VIAB]           │ Revenue Streams [DESIR/VIAB]  │
└─────────────────────────────────┴───────────────────────────────┘
```

#### Validation Flow

**1. Desirability Stage (VPC-Driven)**
```
VPC Customer Profile    →   TBI Experiments    →   BMC Population
  - Customer Jobs           - "Do they want it?"    - Customer Segments
  - Pains                   - "Will they pay?"      - Value Propositions
  - Gains                                           - Revenue Streams (pricing)

VPC Value Map
  - Products & Services
  - Pain Relievers
  - Gain Creators
```

**2. Channel & Relationship Testing (Desirability/Feasibility Overlap)**
- *Desirability lens*: Which channels do customers prefer? What relationship type do they want?
- *Feasibility lens*: Can we use those channels cost-effectively? Can we deliver that relationship at scale?
- Evidence populates BMC: Channels, Customer Relationships

**3. Feasibility Stage**
- Key Activities, Key Resources, Key Partners
- Operational capability validation
- Technical feasibility (Forge's domain)

**4. Viability Stage**
- Cost Structure vs Revenue Streams = unit economics
- Sustainable business model validation
- Ledger's financial analysis

#### Bidirectional Evidence Flow

Evidence doesn't just validate canvases - it updates them:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     VPC     │ ←──→│     TBI     │ ←──→│     BMC     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────┬───────┴───────┬───────────┘
                   │               │
            ┌──────▼───────┐ ┌─────▼──────┐
            │   Evidence   │ │ Hypotheses │
            │   (Vector)   │ │  Tracking  │
            └──────────────┘ └────────────┘
```

- **Evidence validates hypotheses** → Updates hypothesis status across all canvases
- **Contradicting evidence** → Triggers pivot recommendation (requires approval)
- **Strong evidence** → Auto-strengthens related canvas sections
- **Weak evidence** → Suggests additional experiments

### Current Implementation Status

**Infrastructure Complete (~55-60%)**:
- ✅ Canvas components (VPC, BMC, TBI) with guided modes
- ✅ Data models (projects, hypotheses, experiments, evidence)
- ✅ Vector embeddings (pgvector 1536 dims for semantic search)
- ✅ AI onboarding (Vercel AI SDK with quality scoring)
- ✅ CrewAI integration (strategic analysis)
- ✅ Stage-gate validation model

**Missing: Bidirectional Sync Layer**:
- ❌ AI insights → canvas auto-population
- ❌ Evidence → hypothesis validation visualization
- ❌ Canvas sections showing validation status (tested/untested/contradicted)
- ❌ Approval workflow UI for spend/gates/pivots
- ❌ Mode configuration dashboard

### Implementation Priorities

1. **Mode configuration UI** - Dashboard settings for all 4 interaction modes
2. **Approval workflow** - Modal system for spend/gates/pivots
3. **AI → Canvas bridge** - CrewAI output populates canvas sections
4. **Evidence → Canvas linking** - Visual indicators of validation status
5. **Hypothesis tracking UI** - Connect experiments to hypotheses to evidence
6. **Framework wiring** - VPC changes cascade to BMC, evidence updates all

### Key Files to Modify

**Dashboard Settings**:
- New: `frontend/src/components/settings/AIAssistanceSettings.tsx`
- New: `frontend/src/components/settings/ApprovalPreferences.tsx`

**Canvas Components** (add AI population + validation status):
- `frontend/src/components/canvas/ValuePropositionCanvas.tsx`
- `frontend/src/components/canvas/BusinessModelCanvas.tsx`
- `frontend/src/components/canvas/TestingBusinessIdeasCanvas.tsx`

**Approval Workflow**:
- New: `frontend/src/components/approvals/ApprovalModal.tsx`
- New: `frontend/src/components/approvals/SpendApproval.tsx`
- New: `frontend/src/components/approvals/CampaignApproval.tsx`
- New: `frontend/src/components/approvals/GateApproval.tsx`
- New: `frontend/src/components/approvals/PivotApproval.tsx`

**Evidence Integration**:
- Modify: `frontend/src/db/schema/evidence.ts` (add canvas_section linking)
- New: `frontend/src/components/canvas/ValidationIndicator.tsx`

---

## Development Sequence

### Immediate Next Steps (Phase 1)

1. **Create state schemas** (`state_schemas.py`)
   - StartupAIBrief
   - CustomerProfile
   - CompetitorAnalysis
   - QAReport

2. **Build Service Crew**
   - agents.yaml with Internal Onboarding Agent
   - tasks.yaml with brief capture task
   - service_crew.py

3. **Build Analysis Crew**
   - agents.yaml with Customer Researcher, Competitor Analyst
   - tasks.yaml with research tasks
   - analysis_crew.py

4. **Build Governance Crew (Phase 1)**
   - agents.yaml with QA Agent
   - tasks.yaml with validation task
   - governance_crew.py

5. **Create Phase 1 Flow**
   - internal_validation_flow.py
   - Wire up crews with @listen and @router

6. **Run StartupAI through Phase 1**
   - Execute flow with our own business context
   - Capture VPC for Founders and Consultants
   - Iterate until Guardian QA passes

### Dependencies

- CrewAI 1.2.1+ (installed)
- OpenAI API key (for LLM)
- Pydantic for state schemas

---

## Success Metrics

### Phase 1
- VPC completeness score (Guardian QA)
- Assumption clarity score
- Time to complete analysis

### Phase 2
- Experiments run per assumption
- Evidence quality score
- Pivot/proceed confidence level

### Phase 3
- Unit economics viability
- Audit compliance score
- Flywheel entries captured

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| 18 agents too complex | Start with core agents, expand later |
| LLM costs high | Use efficient models, cache results |
| Quality inconsistent | Guardian gates at each phase |
| Learnings not captured | Structured flywheel entry format |

---

## References

- `docs/master-architecture/organizational-structure.md` - Conceptual org structure
- `docs/master-architecture/ecosystem.md` - Three-service architecture
- CrewAI Flows documentation
- Value Proposition Design (Osterwalder)
- Testing Business Ideas (Bland)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-11-21 | Initial spec created | Claude + Chris |
| 2025-11-21 | Added Marketing Site AI Integration section | Claude + Chris |
| 2025-11-21 | Added Product App Smart Artifact Architecture section | Claude + Chris |
| 2025-11-21 | Expanded to 6 approval checkpoints with full workflow architecture | Claude + Chris |

---

**Next Session Pickup Point**: Begin implementing Phase 1 state schemas and Service Crew.
