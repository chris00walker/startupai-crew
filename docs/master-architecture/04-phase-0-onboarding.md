---
purpose: Phase 0 specification - Founder's Brief capture
status: active
last_reviewed: 2026-01-13
vpd_compliance: true
---

# Phase 0: Onboarding

> **Methodology Reference**: See [03-methodology.md](./03-methodology.md) for VPD framework patterns.

## Purpose

Transform the Founder's raw idea into a structured **Founder's Brief** - the prime artifact that informs all subsequent phases.

## Two-Layer Architecture

Phase 0 uses a **two-layer architecture** that separates conversational data collection from validation processing:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: "ALEX" CHAT (Product App - Vercel AI SDK)                         │
│                                                                              │
│  Technology: Vercel AI SDK + OpenAI (streaming chat)                        │
│  Location: app.startupai.site/onboarding/founder (or /consultant)           │
│  Purpose: Conversational data collection with real-time streaming           │
│                                                                              │
│  7 Conversational Stages:                                                    │
│  1. Welcome & Introduction                                                   │
│  2. Customer Discovery                                                       │
│  3. Problem Definition                                                       │
│  4. Solution Validation                                                      │
│  5. Competitive Analysis                                                     │
│  6. Resources & Constraints                                                  │
│  7. Goals & Next Steps                                                       │
│                                                                              │
│  Output: Raw conversation transcript + extracted business context            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (on completion)
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: ONBOARDING CREW (Modal - CrewAI)                                  │
│                                                                              │
│  Technology: CrewAI agents on Modal serverless                              │
│  Purpose: Validate, analyze gaps, and structure the collected data          │
│                                                                              │
│  4 Agents:                                                                   │
│  • O1: Interview Gap Analyzer - identifies missing/incomplete information   │
│  • GV1: Concept Validator - legitimacy screening                           │
│  • GV2: Intent Verification - ensures capture accuracy                     │
│  • S1: Brief Compiler - creates structured Founder's Brief                 │
│                                                                              │
│  Output: Validated Founder's Brief (prime artifact)                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why Two Layers?

| Concern | Layer 1 (Alex) | Layer 2 (CrewAI) |
|---------|----------------|------------------|
| **UX** | Real-time streaming chat | Batch processing (latency acceptable) |
| **Iteration** | Prompt changes deploy instantly | Agent changes require Modal redeploy |
| **Cost** | Direct OpenAI calls (cheaper) | CrewAI orchestration (heavier) |
| **Purpose** | Data collection | Validation & structuring |

**Key Principle**: Alex collects, CrewAI validates. The separation ensures best-in-class UX for the conversational interview while leveraging CrewAI's multi-agent orchestration for validation logic.

### What This Phase IS About

- Understanding what the Founder wants to build
- Capturing their hypotheses (not validating them)
- Ensuring the concept is legitimate
- Creating a structured brief for downstream work

### What This Phase Is NOT About

- Customer research
- Market validation
- Building anything
- Competitive analysis

### Entry Criteria

- Founder has a business idea they want to validate
- Founder is ready to commit time to the interview process

### Exit Criteria

- `approve_founders_brief` HITL checkpoint passed
- Founder's Brief artifact created and approved
- Concept legitimacy verified (legal, ethical, feasible, sane)

---

## CrewAI Pattern Mapping

> **Pattern Reference**: See [00-introduction.md](./00-introduction.md) for CrewAI pattern hierarchy.

| Pattern | This Phase |
|---------|------------|
| **Phase** | Phase 0: Onboarding (business concept) |
| **Flow** | `OnboardingFlow` (orchestrates the crew) |
| **Crew** | `OnboardingCrew` (4 collaborative agents) |
| **Agents** | O1, GV1, GV2, S1 |

---

## OnboardingFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ONBOARDING FLOW                                    │
│                                                                              │
│  Entry: Conversation transcript from "Alex" chat (product app)              │
│  Exit: Approved Founder's Brief ready for Phase 1                           │
│                                                                              │
│  Flow: OnboardingFlow                                                        │
│  Crew: OnboardingCrew (O1, GV1, GV2, S1)                                    │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 1: "ALEX" CHAT (Product App - NOT part of CrewAI)            │   │
│  │                                                                      │   │
│  │  Technology: Vercel AI SDK + OpenAI (streaming)                     │   │
│  │  Location: /onboarding/founder or /onboarding/consultant            │   │
│  │                                                                      │   │
│  │  Conversational interview covering 7 stages:                        │   │
│  │  • Welcome & Introduction                                           │   │
│  │  • Customer Discovery                                               │   │
│  │  • Problem Definition                                               │   │
│  │  • Solution Validation                                              │   │
│  │  • Competitive Analysis                                             │   │
│  │  • Resources & Constraints                                          │   │
│  │  • Goals & Next Steps                                               │   │
│  │                                                                      │   │
│  │  Output: Conversation transcript + extracted business context       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                          (on completion)                                     │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 2: ONBOARDING CREW (Modal - CrewAI)                          │   │
│  │                      (4 Collaborative Agents)                        │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  O1: INTERVIEW GAP ANALYZER AGENT                            │   │   │
│  │  │                                                              │   │   │
│  │  │  Analyzes Alex's conversation transcript for completeness:   │   │   │
│  │  │  • Are all 7 areas covered?                                  │   │   │
│  │  │  • Any gaps or ambiguities?                                  │   │   │
│  │  │  • Information quality sufficient?                           │   │   │
│  │  │                                                              │   │   │
│  │  │  Output: Gap Analysis Report (PROCEED or NEEDS_FOLLOWUP)     │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                    │                                │   │
│  │                                    ▼                                │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  GV1: CONCEPT VALIDATOR AGENT                                │   │   │
│  │  │                                                              │   │   │
│  │  │  Validates the concept is legitimate:                        │   │   │
│  │  │  • NOT illegal (drugs, weapons, fraud, etc.)                │   │   │
│  │  │  • NOT immoral (exploitation, harm, deception)              │   │   │
│  │  │  • NOT ridiculous (perpetual motion, time travel)           │   │   │
│  │  │  • NOT impossible with current technology                   │   │   │
│  │  │  • Passes basic business sanity checks                      │   │   │
│  │  │                                                              │   │   │
│  │  │  Output: Legitimacy Report (PASS/FAIL + reasons)            │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                    │                                │   │
│  │                                    ▼                                │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  GV2: INTENT VERIFICATION AGENT                              │   │   │
│  │  │                                                              │   │   │
│  │  │  Verifies the interview captured intent correctly:           │   │   │
│  │  │  • Does the summary reflect what Founder said?              │   │   │
│  │  │  • Are there gaps in understanding?                         │   │   │
│  │  │  • Are there contradictions to resolve?                     │   │   │
│  │  │  • Should we ask follow-up questions?                       │   │   │
│  │  │                                                              │   │   │
│  │  │  Output: Intent Verification Report (PASS/NEEDS FOLLOWUP)   │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                    │                                │   │
│  │                                    ▼                                │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  S1: BRIEF COMPILER AGENT                                    │   │   │
│  │  │                                                              │   │   │
│  │  │  Synthesizes all inputs into structured Founder's Brief:     │   │   │
│  │  │  • The Idea (concept, one-liner, description)               │   │   │
│  │  │  • Problem Hypothesis (who, what, current alternatives)     │   │   │
│  │  │  • Customer Hypothesis (segment, characteristics)           │   │   │
│  │  │  • Solution Hypothesis (approach, key features)             │   │   │
│  │  │  • Key Assumptions (what must be true)                      │   │   │
│  │  │  • Success Criteria (what would make this worth pursuing)   │   │   │
│  │  │  • QA Status (legitimacy + intent verification)             │   │   │
│  │  │                                                              │   │   │
│  │  │  Output: FOUNDER'S BRIEF (Prime Artifact)                   │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│                         ┌─────────────────────┐                             │
│                         │  @router()          │                             │
│                         │  intent_gate        │                             │
│                         └─────────┬───────────┘                             │
│                                   │                                          │
│                    ┌──────────────┼──────────────┐                          │
│                    │              │              │                           │
│             [NEEDS_FOLLOWUP]   [FAIL]      [PASS]                           │
│                    │              │              │                           │
│                    ▼              ▼              ▼                           │
│              Loop back      Reject with    Proceed to                       │
│              to O1 with     explanation    HITL approval                    │
│              questions                                                       │
│                    │                             │                           │
│                    └─────────────────────────────┘                          │
│                                    │                                         │
│                                    ▼                                         │
│                    ┌───────────────────────────────┐                        │
│                    │  HITL: approve_founders_brief │                        │
│                    │                               │                        │
│                    │  Founder reviews brief:       │                        │
│                    │  • Is this what I meant?      │                        │
│                    │  • Any corrections needed?    │                        │
│                    │  • Ready to proceed?          │                        │
│                    └───────────────────────────────┘                        │
│                                    │                                         │
│                          ┌─────────┴─────────┐                              │
│                          │                   │                               │
│                       REJECT              APPROVE                            │
│                          │                   │                               │
│                          ▼                   ▼                               │
│                   Loop back with       FOUNDER'S BRIEF                      │
│                   corrections          (Ready for Phase 1)                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Specifications

> **Full Reference**: See [reference/agent-specifications.md](./reference/agent-specifications.md) for complete 45-agent specifications.
> **Configuration Standard**: See [02-organization.md](./02-organization.md#agent-configuration-standard) for required attributes.

### O1: Interview Gap Analyzer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | O1 |
| **Name** | Interview Gap Analyzer Agent |
| **Founder** | Sage |
| **Persona** | Methodical analyst - thorough, detail-oriented, systematic |
| **Role** | Analyze Alex's conversation transcript to identify gaps, ambiguities, and missing information |
| **Goal** | Ensure the collected business context is complete enough to create a high-quality Founder's Brief |

> **Note**: The conversational interview is conducted by "Alex" (Vercel AI SDK) in the product app. O1 receives the completed conversation and analyzes it for completeness.

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - analysis through reasoning |
| `reasoning` | True | Complex gap detection requires deep reasoning |
| `inject_date` | True | Market timing context |
| `max_iter` | 15 | Focused analysis |
| `temperature` | 0.3 | Precise, consistent gap identification |
| `verbose` | True | Debug logging |
| `allow_delegation` | False | Predictable flow |

#### Tool Status

| Tool | Status | Notes |
|------|--------|-------|
| (none) | N/A | Pure LLM agent - analysis through reasoning |

**Backstory:**
```
You are a meticulous business analyst who reviews founder interviews for
completeness and quality. You've seen hundreds of interviews and know exactly
what information is needed to create a strong Founder's Brief. Your job is to
identify gaps, ambiguities, and areas where the founder's responses were
incomplete or unclear. You are thorough but practical - you flag real gaps,
not theoretical nice-to-haves.
```

**Tasks:**
1. `analyze_interview_completeness` - Review transcript for coverage of all 7 areas
2. `identify_information_gaps` - Flag missing or incomplete information
3. `generate_clarification_questions` - Create targeted questions for gaps (if needed)

#### Gap Analysis Framework (7 Areas)

O1 analyzes the Alex conversation transcript to ensure coverage of:

```
1. THE IDEA
   ✓ Is the concept clearly articulated?
   ✓ Is there a one-liner or elevator pitch?
   ✓ Is the scope bounded?

2. THE MOTIVATION
   ✓ Why is the founder pursuing this?
   ✓ Personal connection to the problem?
   ✓ Why now?

3. CUSTOMER HYPOTHESIS
   ✓ Who is the target customer?
   ✓ How specific is the segment definition?
   ✓ Where can they be found?

4. PROBLEM HYPOTHESIS
   ✓ What problem is being solved?
   ✓ Current alternatives mentioned?
   ✓ Pain points identified?

5. SOLUTION HYPOTHESIS
   ✓ How does the solution work?
   ✓ Key features defined?
   ✓ Differentiation articulated?

6. KEY ASSUMPTIONS
   ✓ What must be true?
   ✓ Riskiest assumptions identified?
   ✓ Deal-breakers mentioned?

7. SUCCESS CRITERIA
   ✓ What would make this worth pursuing?
   ✓ Metrics or indicators defined?
   ✓ Timeline expectations?
```

**Output Schema:**
```json
{
  "completeness_score": 0.85,
  "gaps_identified": [
    {
      "area": "CUSTOMER_HYPOTHESIS",
      "gap": "Segment size not estimated",
      "severity": "low",
      "clarification_question": "Roughly how many people do you think have this problem?"
    }
  ],
  "areas_well_covered": ["THE_IDEA", "PROBLEM_HYPOTHESIS", "SOLUTION_HYPOTHESIS"],
  "recommendation": "PROCEED" | "NEEDS_FOLLOWUP"
}
```

---

### GV1: Concept Validator Agent

| Attribute | Value |
|-----------|-------|
| **ID** | GV1 |
| **Name** | Concept Validator Agent |
| **Founder** | Guardian |
| **Role** | Validate that the concept is legitimate and worth pursuing |
| **Goal** | Screen out illegal, immoral, ridiculous, or impossible concepts before resources are invested |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - validation through reasoning |
| `reasoning` | True | Legal/ethical analysis requires deep reasoning |
| `inject_date` | True | Current regulatory context |
| `max_iter` | 15 | Focused validation checks |
| `temperature` | 0.1 | Strict compliance checking |
| `verbose` | True | Debug logging |
| `allow_delegation` | False | Predictable flow |

#### Tool Status

| Tool | Status | Notes |
|------|--------|-------|
| (none) | N/A | Pure LLM agent - validation through reasoning |

**Backstory:**
```
You are a seasoned business ethics advisor who has seen every type of startup
pitch imaginable. Your job is to be the responsible gatekeeper - not to crush
dreams, but to ensure founders aren't pursuing something that's fundamentally
flawed, harmful, or impossible. You apply rigorous but fair criteria to assess
whether a concept should proceed to validation.
```

**Tasks:**
1. `validate_concept_legitimacy` - Apply legitimacy screening criteria

**Legitimacy Criteria:**

```
LEGAL CHECK
├── Not involved in illegal goods/services (drugs, weapons, trafficking)
├── Not facilitating fraud or financial crimes
├── Not violating intellectual property laws
├── Not circumventing regulations (securities, healthcare, etc.)
└── Compliant with major jurisdiction laws (US, EU)

ETHICAL CHECK
├── Not exploiting vulnerable populations
├── Not causing environmental harm
├── Not enabling harassment or discrimination
├── Not spreading misinformation
├── Transparent about what it does
└── Not designed to deceive users

FEASIBILITY CHECK
├── Not requiring technology that doesn't exist
├── Not violating laws of physics
├── Not requiring resources that are impossible to obtain
└── Has some plausible path to execution

BUSINESS SANITY CHECK
├── Has identifiable potential customers
├── Solves a problem someone might have
├── Has some conceivable revenue model
└── Not already been tried and failed catastrophically
```

**Output Schema:**
```json
{
  "legitimacy_status": "PASS | FAIL | NEEDS_REVIEW",
  "legal_check": {
    "status": "PASS | FAIL",
    "flags": [],
    "notes": ""
  },
  "ethical_check": {
    "status": "PASS | FAIL",
    "flags": [],
    "notes": ""
  },
  "feasibility_check": {
    "status": "PASS | FAIL",
    "flags": [],
    "notes": ""
  },
  "business_sanity_check": {
    "status": "PASS | FAIL",
    "flags": [],
    "notes": ""
  },
  "overall_recommendation": "",
  "concerns_to_address": []
}
```

---

### GV2: Intent Verification Agent

| Attribute | Value |
|-----------|-------|
| **ID** | GV2 |
| **Name** | Intent Verification Agent |
| **Founder** | Guardian |
| **Role** | Verify that the interview accurately captured the Founder's intent |
| **Goal** | Ensure no miscommunication or gaps before creating the Brief |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - intent matching through reasoning |
| `reasoning` | True | Nuanced intent analysis |
| `inject_date` | True | Context freshness |
| `max_iter` | 15 | Focused verification |
| `temperature` | 0.1 | Precise intent matching |
| `verbose` | True | Debug logging |
| `allow_delegation` | False | Predictable flow |

#### Tool Status

| Tool | Status | Notes |
|------|--------|-------|
| (none) | N/A | Pure LLM agent - verification through reasoning |

**Backstory:**
```
You are a meticulous editor and fact-checker. You've seen how miscommunication
early in a project can lead to months of wasted work. Your job is to compare
what the Founder said with what was captured, identify any gaps, contradictions,
or areas of ambiguity, and flag them for clarification.
```

**Tasks:**
1. `verify_intent_capture` - Compare transcript to structured notes
2. `identify_gaps` - Find missing information
3. `flag_contradictions` - Identify inconsistencies
4. `generate_followup_questions` - Create targeted questions for gaps

**Verification Checklist:**
```
COMPLETENESS
├── All 7 interview areas covered?
├── Customer hypothesis captured?
├── Problem hypothesis captured?
├── Solution hypothesis captured?
├── Key assumptions identified?
└── Success criteria defined?

ACCURACY
├── Summary reflects what was said?
├── No words put in Founder's mouth?
├── Nuances preserved?
└── Enthusiasm level captured?

CLARITY
├── Ambiguous terms clarified?
├── Industry jargon explained?
├── Scope clearly bounded?
└── Target market defined?

CONSISTENCY
├── Customer and problem align?
├── Solution addresses stated problem?
├── Success criteria are measurable?
└── Assumptions are testable?
```

---

### S1: Brief Compiler Agent

| Attribute | Value |
|-----------|-------|
| **ID** | S1 |
| **Name** | Brief Compiler Agent |
| **Founder** | Sage |
| **Role** | Synthesize all inputs into the structured Founder's Brief |
| **Goal** | Create a clear, comprehensive, well-organized Brief that will guide all downstream work |

#### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `tools` | `[]` | Pure LLM - synthesis through reasoning |
| `reasoning` | True | Complex document synthesis |
| `inject_date` | True | Timestamp the brief |
| `max_iter` | 20 | Thorough compilation |
| `temperature` | 0.3 | Balanced synthesis |
| `verbose` | True | Debug logging |
| `allow_delegation` | False | Predictable flow |

#### Tool Status

| Tool | Status | Notes |
|------|--------|-------|
| (none) | N/A | Pure LLM agent - synthesis through reasoning |

**Backstory:**
```
You are a master synthesizer who can take messy, conversational input and
transform it into clear, structured documentation. You understand that the
Founder's Brief is the single most important document in the validation process -
it will inform every subsequent flow and crew. You take pride in creating Briefs
that are complete, accurate, and actionable.
```

**Tasks:**
1. `compile_founders_brief` - Create the structured Brief document
2. `highlight_key_assumptions` - Identify the riskiest assumptions
3. `define_validation_priorities` - Suggest what to validate first

---

## Output Schemas

### Founder's Brief (Prime Artifact)

```python
class FoundersBrief(BaseModel):
    """The prime artifact from Phase 0 - input to all downstream phases."""

    # Identity
    brief_id: str
    founder_id: str
    session_id: str
    created_at: datetime
    updated_at: datetime
    version: int = 1

    # The Idea
    the_idea: TheIdea

    # Hypotheses (NOT validated - captured for testing)
    problem_hypothesis: ProblemHypothesis
    customer_hypothesis: CustomerHypothesis
    solution_hypothesis: SolutionHypothesis

    # Assumptions & Success
    key_assumptions: List[Assumption]
    success_criteria: SuccessCriteria

    # Founder Context
    founder_context: FounderContext

    # QA Status
    qa_status: QAStatus

    # Metadata
    metadata: InterviewMetadata


class TheIdea(BaseModel):
    one_liner: str
    description: str
    inspiration: str
    unique_insight: str


class ProblemHypothesis(BaseModel):
    problem_statement: str
    who_has_this_problem: str
    frequency: str
    current_alternatives: str
    why_alternatives_fail: str
    evidence_of_problem: Optional[str] = None


class CustomerHypothesis(BaseModel):
    primary_segment: str
    segment_description: str
    characteristics: List[str]
    where_to_find_them: str
    estimated_size: Optional[str] = None
    validation_status: str = "HYPOTHESIS - NOT VALIDATED"


class SolutionHypothesis(BaseModel):
    proposed_solution: str
    key_features: List[str]
    differentiation: str
    unfair_advantage: Optional[str] = None
    validation_status: str = "HYPOTHESIS - NOT VALIDATED"


class Assumption(BaseModel):
    assumption: str
    category: Literal["customer", "problem", "solution", "business_model"]
    risk_level: Literal["high", "medium", "low"]
    how_to_test: str
    validated: bool = False


class SuccessCriteria(BaseModel):
    minimum_viable_signal: str
    deal_breakers: List[str]
    target_metrics: Dict[str, str]
    timeline: Optional[str] = None


class FounderContext(BaseModel):
    founder_background: str
    motivation: str
    time_commitment: Literal["full_time", "part_time", "exploring"]
    resources_available: str


class QAStatus(BaseModel):
    legitimacy_check: Literal["PASS", "FAIL", "NEEDS_REVIEW"]
    legitimacy_notes: str = ""
    intent_verification: Literal["PASS", "FAIL", "NEEDS_FOLLOWUP"]
    intent_notes: str = ""
    overall_status: Literal["APPROVED", "REJECTED", "PENDING"]


class InterviewMetadata(BaseModel):
    interview_duration_minutes: int
    interview_turns: int
    followup_questions_asked: int
    confidence_score: float
```

---

## HITL Checkpoint

### `approve_founders_brief`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `approve_founders_brief` |
| **Phase** | 0 |
| **Owner** | Founder (Human) + Sage |
| **Purpose** | Founder confirms the Brief accurately captures their intent |
| **Required for Exit** | Yes |

**Presentation to Founder:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     YOUR FOUNDER'S BRIEF                                     │
│                                                                              │
│  Please review this summary of your idea. We want to make sure we           │
│  understood you correctly before we begin validation.                        │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  THE IDEA                                                                    │
│  [One-liner and description displayed]                                      │
│                                                                              │
│  THE PROBLEM YOU'RE SOLVING                                                  │
│  [Problem hypothesis displayed]                                              │
│                                                                              │
│  WHO YOU'RE BUILDING FOR                                                     │
│  [Customer hypothesis displayed - marked as HYPOTHESIS]                     │
│                                                                              │
│  YOUR PROPOSED SOLUTION                                                      │
│  [Solution hypothesis displayed - marked as HYPOTHESIS]                     │
│                                                                              │
│  KEY ASSUMPTIONS WE'LL TEST                                                  │
│  [Ranked list of assumptions]                                               │
│                                                                              │
│  YOUR SUCCESS CRITERIA                                                       │
│  [What would make this worth pursuing]                                      │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [ ] This captures my idea correctly                                        │
│  [ ] I'd like to make corrections (please specify)                          │
│                                                                              │
│  [APPROVE & CONTINUE]     [REQUEST CHANGES]                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Decision Options:**
- `APPROVE` → Proceed to Phase 1: VPC Discovery
- `REJECT` → Loop back to Interview Agent with corrections

---

## Methodology Compliance

This phase implements VPD patterns from [03-methodology.md](./03-methodology.md):

| Pattern | Implementation |
|---------|----------------|
| **Hypothesis Capture** | All customer/problem/solution elements marked as "HYPOTHESIS - NOT VALIDATED" |
| **Assumptions Mapping** | S1 identifies and risk-ranks assumptions using 2×2 matrix logic |
| **Test Card Preparation** | Key assumptions include `how_to_test` field for Phase 1 |
| **SAY Focus** | This phase captures what Founder says; Phase 1 discovers what customers DO |

**Key Principle**: Phase 0 captures the Founder's beliefs. Phase 1+ tests them against reality. Never confuse hypothesis with validated truth.

---

## Summary

### CrewAI Pattern Summary

| Pattern | Implementation |
|---------|----------------|
| **Phase** | Phase 0: Onboarding |
| **Flow** | `OnboardingFlow` |
| **Crew** | `OnboardingCrew` (4 agents) |

### Agent Summary

| ID | Agent | Founder | Role | Output |
|----|-------|---------|------|--------|
| O1 | Interview Gap Analyzer Agent | Sage | Analyze Alex transcript for completeness | Gap Analysis Report |
| GV1 | Concept Validator Agent | Guardian | Legitimacy screening | Legitimacy Report |
| GV2 | Intent Verification Agent | Guardian | Verify capture accuracy | Intent Verification Report |
| S1 | Brief Compiler Agent | Sage | Synthesize into Brief | **Founder's Brief** |

> **Note**: The conversational interview is conducted by "Alex" (Vercel AI SDK) in the product app before CrewAI agents are invoked. See [Two-Layer Architecture](#two-layer-architecture) for details.

**Phase 0 Totals:**
- Flows: 1 (`OnboardingFlow`)
- Crews: 1 (`OnboardingCrew`)
- Agents: 4
- HITL Checkpoints: 1

---

## Related Documents

### Architecture
- [00-introduction.md](./00-introduction.md) - Quick start and orientation
- [01-ecosystem.md](./01-ecosystem.md) - Three-service architecture overview
- [02-organization.md](./02-organization.md) - 6 AI Founders and agents
- [03-methodology.md](./03-methodology.md) - VPD framework reference

### Phase Specifications
- **Phase 0: Onboarding** - (this document)
- [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md) - VPC Discovery (next phase)
- [06-phase-2-desirability.md](./06-phase-2-desirability.md) - Desirability validation
- [07-phase-3-feasibility.md](./07-phase-3-feasibility.md) - Feasibility validation
- [08-phase-4-viability.md](./08-phase-4-viability.md) - Viability + Decision

### Reference
- [09-status.md](./09-status.md) - Current implementation status
- [reference/api-contracts.md](./reference/api-contracts.md) - API specifications
- [reference/approval-workflows.md](./reference/approval-workflows.md) - HITL patterns
