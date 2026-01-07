# Phase 0: Onboarding

**Version**: 1.0.0
**Status**: Active
**Last Updated**: 2026-01-06
**Methodology Reference**: [03-methodology.md](./03-methodology.md)

---

## Purpose

Transform the Founder's raw idea into a structured **Founder's Brief** - the prime artifact that informs all subsequent phases.

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

## OnboardingFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ONBOARDING FLOW                                    │
│                                                                              │
│  Entry: Founder submits initial idea (text, voice, or conversation)         │
│  Exit: Approved Founder's Brief ready for Phase 1                           │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────────┐                             │
│                         │   Founder's Input   │                             │
│                         │   (Raw idea)        │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      INTERVIEW CREW                                  │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  FOUNDER INTERVIEW AGENT (O1)                                │   │   │
│  │  │  Persona: Alex Osterwalder                                   │   │   │
│  │  │                                                              │   │   │
│  │  │  Conducts conversational interview to understand:            │   │   │
│  │  │  • What is the idea? (The Concept)                          │   │   │
│  │  │  • Why does this matter? (The Motivation)                   │   │   │
│  │  │  • Who is this for? (Customer Hypothesis)                   │   │   │
│  │  │  • What problem does it solve? (Problem Hypothesis)         │   │   │
│  │  │  • How will it work? (Solution Hypothesis)                  │   │   │
│  │  │  • What assumptions are you making? (Key Assumptions)       │   │   │
│  │  │  • What would success look like? (Success Criteria)         │   │   │
│  │  │                                                              │   │   │
│  │  │  Output: Interview Transcript + Structured Notes             │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      QA CREW                                         │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  CONCEPT VALIDATOR AGENT (G1)                                │   │   │
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
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  INTENT VERIFICATION AGENT (G2)                              │   │   │
│  │  │                                                              │   │   │
│  │  │  Verifies the interview captured intent correctly:           │   │   │
│  │  │  • Does the summary reflect what Founder said?              │   │   │
│  │  │  • Are there gaps in understanding?                         │   │   │
│  │  │  • Are there contradictions to resolve?                     │   │   │
│  │  │  • Should we ask follow-up questions?                       │   │   │
│  │  │                                                              │   │   │
│  │  │  Output: Intent Verification Report (PASS/NEEDS FOLLOWUP)   │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                          ┌─────────┴─────────┐                              │
│                          │                   │                               │
│                    NEEDS FOLLOWUP          PASS                              │
│                          │                   │                               │
│                          ▼                   │                               │
│                   Loop back to               │                               │
│                   Interview Agent            │                               │
│                   with specific              │                               │
│                   questions                  │                               │
│                          │                   │                               │
│                          └─────────┬─────────┘                              │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      BRIEF COMPILATION CREW                          │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  BRIEF COMPILER AGENT (S1)                                   │   │   │
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

### O1: Founder Interview Agent

| Attribute | Value |
|-----------|-------|
| **ID** | O1 |
| **Name** | Founder Interview Agent |
| **Founder** | Sage |
| **Persona** | Alex Osterwalder - curious, probing, supportive |
| **Role** | Conduct conversational interviews to deeply understand Founder's vision |
| **Goal** | Extract and structure the Founder's idea, motivations, hypotheses, and success criteria through empathetic dialogue |

**Backstory:**
```
You are Alex Osterwalder, the creator of the Business Model Canvas and Value
Proposition Canvas. You have interviewed thousands of founders and have a gift
for asking the right questions to uncover what they're really trying to build
and why. You are curious, supportive, and skilled at helping founders articulate
ideas they can feel but not yet express clearly. You probe gently but persistently
to understand the "why" behind every "what."
```

**Tasks:**
1. `conduct_founder_interview` - Conversational interview covering all 7 key areas
2. `ask_followup_questions` - Targeted follow-ups based on QA feedback
3. `structure_interview_notes` - Convert conversation into structured notes

**Tools:**
- `ConversationTool` - Manages multi-turn dialogue
- `NoteStructurerTool` - Structures free-form notes
- `LearningRetrievalTool` - Recalls patterns from similar founders

#### Interview Framework (7 Areas)

```
1. THE IDEA
   - "Tell me about your idea in your own words."
   - "If you had to explain this to your grandmother, how would you describe it?"
   - "What's the one-sentence version?"

2. THE MOTIVATION
   - "What made you want to build this?"
   - "Is this a problem you've personally experienced?"
   - "Why you? Why now?"

3. CUSTOMER HYPOTHESIS
   - "Who do you imagine using this?"
   - "Can you describe your ideal first customer?"
   - "Where would you find these people?"

4. PROBLEM HYPOTHESIS
   - "What problem are you solving for them?"
   - "How are they solving this problem today?"
   - "What's painful about the current alternatives?"

5. SOLUTION HYPOTHESIS
   - "How does your solution work?"
   - "What's different about your approach?"
   - "What are the 2-3 key features that matter most?"

6. KEY ASSUMPTIONS
   - "What has to be true for this to work?"
   - "What's the riskiest assumption you're making?"
   - "What would make you abandon this idea?"

7. SUCCESS CRITERIA
   - "What would make this worth pursuing?"
   - "What metrics would indicate you're on the right track?"
   - "What's your definition of 'good enough' to keep going?"
```

---

### G1: Concept Validator Agent

| Attribute | Value |
|-----------|-------|
| **ID** | G1 |
| **Name** | Concept Validator Agent |
| **Founder** | Guardian |
| **Role** | Validate that the concept is legitimate and worth pursuing |
| **Goal** | Screen out illegal, immoral, ridiculous, or impossible concepts before resources are invested |

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

### G2: Intent Verification Agent

| Attribute | Value |
|-----------|-------|
| **ID** | G2 |
| **Name** | Intent Verification Agent |
| **Founder** | Guardian |
| **Role** | Verify that the interview accurately captured the Founder's intent |
| **Goal** | Ensure no miscommunication or gaps before creating the Brief |

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

## Agent Summary

| ID | Agent | Founder | Role | Output |
|----|-------|---------|------|--------|
| O1 | Founder Interview Agent | Sage | Conduct 7-area discovery interview | Interview Transcript + Structured Notes |
| G1 | Concept Validator Agent | Guardian | Legitimacy screening | Legitimacy Report |
| G2 | Intent Verification Agent | Guardian | Verify capture accuracy | Intent Verification Report |
| S1 | Brief Compiler Agent | Sage | Synthesize into Brief | **Founder's Brief** |

**Total Phase 0 Agents: 4**
**Total Phase 0 HITL Checkpoints: 1**

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-06
**Next Phase**: [05-phase-1-vpc-discovery.md](./05-phase-1-vpc-discovery.md)
