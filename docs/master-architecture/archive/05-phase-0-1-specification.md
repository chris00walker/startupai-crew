# Phase 0 & Phase 1: Foundation Specification

**Version**: 1.1.0
**Status**: VPD Compliant
**Last Updated**: 2026-01-05
**VPD Review**: Validated against Osterwalder's Value Proposition Design framework

---

## Overview

This document specifies the first two phases of the StartupAI Validation Engine:

- **Phase 0: Onboarding** - Understanding the Founder's intent and creating the Founder's Brief
- **Phase 1: VPC Discovery** - Experiment-driven Customer Discovery to fill and validate the Value Proposition Canvas

These phases lay the foundation for all subsequent validation work.

---

# PHASE 0: ONBOARDING

## Purpose

Transform the Founder's raw idea into a structured **Founder's Brief** - the prime artifact that informs all subsequent flows and crews.

**This phase is NOT about:**
- Customer research
- Market validation
- Building anything
- Competitive analysis

**This phase IS about:**
- Understanding what the Founder wants to build
- Capturing their hypotheses (not validating them)
- Ensuring the concept is legitimate
- Creating a structured brief for downstream work

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

## Phase 0 Agent Specifications

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
1. `conduct_founder_interview` - Conversational interview covering all key areas
2. `ask_followup_questions` - Targeted follow-ups based on QA feedback
3. `structure_interview_notes` - Convert conversation into structured notes

**Tools:**
- `ConversationTool` - Manages multi-turn dialogue
- `NoteStructurerTool` - Structures free-form notes
- `LearningRetrievalTool` - Recalls patterns from similar founders

**Interview Framework:**

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

## Founder's Brief Schema (Prime Artifact)

```json
{
  "brief_id": "uuid",
  "founder_id": "uuid",
  "session_id": "uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "version": 1,

  "the_idea": {
    "one_liner": "A brief description in one sentence",
    "description": "A fuller description of the concept",
    "inspiration": "What prompted this idea",
    "unique_insight": "What the Founder sees that others don't"
  },

  "problem_hypothesis": {
    "problem_statement": "Clear statement of the problem",
    "who_has_this_problem": "Description of who experiences this",
    "frequency": "How often they encounter this problem",
    "current_alternatives": "How they solve it today",
    "why_alternatives_fail": "Pain points with current solutions",
    "evidence_of_problem": "Any evidence the Founder has seen"
  },

  "customer_hypothesis": {
    "primary_segment": "The main customer segment hypothesis",
    "segment_description": "Detailed description of this segment",
    "characteristics": ["trait1", "trait2", "trait3"],
    "where_to_find_them": "Channels to reach them",
    "estimated_size": "Founder's guess at market size",
    "validation_status": "HYPOTHESIS - NOT VALIDATED"
  },

  "solution_hypothesis": {
    "proposed_solution": "How the Founder plans to solve it",
    "key_features": ["feature1", "feature2", "feature3"],
    "differentiation": "What makes this different from alternatives",
    "unfair_advantage": "Why the Founder is positioned to build this",
    "validation_status": "HYPOTHESIS - NOT VALIDATED"
  },

  "key_assumptions": [
    {
      "assumption": "Description of the assumption",
      "category": "customer | problem | solution | business_model",
      "risk_level": "high | medium | low",
      "how_to_test": "Suggested way to validate",
      "validated": false
    }
  ],

  "success_criteria": {
    "minimum_viable_signal": "What would indicate this is worth pursuing",
    "deal_breakers": "What would make the Founder abandon this",
    "target_metrics": {
      "signups": "X signups in Y days",
      "conversion": "X% conversion rate",
      "willingness_to_pay": "X people willing to pay $Y"
    },
    "timeline": "How long the Founder is willing to test"
  },

  "founder_context": {
    "founder_background": "Relevant experience",
    "motivation": "Why this matters to them",
    "time_commitment": "Full-time / Part-time / Exploring",
    "resources_available": "Budget, skills, network"
  },

  "qa_status": {
    "legitimacy_check": "PASS | FAIL",
    "legitimacy_notes": "",
    "intent_verification": "PASS | FAIL",
    "intent_notes": "",
    "overall_status": "APPROVED | REJECTED | PENDING"
  },

  "metadata": {
    "interview_duration_minutes": 30,
    "interview_turns": 15,
    "followup_questions_asked": 3,
    "confidence_score": 0.85
  }
}
```

---

## Phase 0 HITL Checkpoint

### `approve_founders_brief`

| Attribute | Value |
|-----------|-------|
| **Checkpoint ID** | `approve_founders_brief` |
| **Flow** | OnboardingFlow |
| **Owner** | Founder (Human) |
| **Purpose** | Founder confirms the Brief accurately captures their intent |

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

---

# PHASE 1: VPC DISCOVERY

## Purpose

Use experiment-driven Customer Discovery to fill in and validate the **Value Proposition Canvas** - understanding what customers actually want, not just what the Founder thinks they want.

**This phase produces:**
- Validated Customer Segments (with evidence)
- Jobs-to-be-Done (ranked by importance)
- Pains (ranked by severity)
- Gains (ranked by importance)
- Value Map (Products, Pain Relievers, Gain Creators)
- Problem-Solution Fit Score

**Key Principle:**
> What customers SAY and what they DO are two different things.
> Use experiments with CTAs to produce behavioral evidence, not just opinions.

---

## VPC Discovery Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VPC DISCOVERY ORCHESTRATOR                             │
│                                                                              │
│  Manages the iterative loop through VPC components                          │
│  Decides which flow to invoke next based on current state                   │
│  Tracks evidence strength and fit score                                     │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────────┐                             │
│                         │   Founder's Brief   │                             │
│                         │   (from Phase 0)    │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    VPC DISCOVERY LOOP                                │   │
│  │                                                                      │   │
│  │           ┌─────────────────────────────────────────┐               │   │
│  │           │         RIGHT SIDE (Customer)           │               │   │
│  │           │                                         │               │   │
│  │   ┌───────┴───────┐                                 │               │   │
│  │   │   Segment     │◀────────────────────────────┐   │               │   │
│  │   │  Discovery    │                             │   │               │   │
│  │   │    Flow       │                             │   │               │   │
│  │   └───────┬───────┘                             │   │               │   │
│  │           │                                     │   │               │   │
│  │           ▼                                     │   │               │   │
│  │   ┌───────────────┐                             │   │               │   │
│  │   │     Jobs      │                             │   │               │   │
│  │   │  Discovery    │                             │   │               │   │
│  │   │    Flow       │                             │   │               │   │
│  │   └───────┬───────┘                             │   │               │   │
│  │           │                                     │   │               │   │
│  │           ▼                                     │   │               │   │
│  │   ┌───────────────┐                             │   │               │   │
│  │   │    Pains      │                             │   │               │   │
│  │   │  Discovery    │                             │   │               │   │
│  │   │    Flow       │                             │   │               │   │
│  │   └───────┬───────┘                             │   │               │   │
│  │           │                                     │   │               │   │
│  │           ▼                                     │   │               │   │
│  │   ┌───────────────┐                             │   │               │   │
│  │   │    Gains      │                             │   │               │   │
│  │   │  Discovery    │        ITERATE              │   │               │   │
│  │   │    Flow       │      if fit low             │   │               │   │
│  │   └───────┬───────┘                             │   │               │   │
│  │           │                                     │   │               │   │
│  │           └─────────────────────────────────────┘   │               │   │
│  │                                                     │               │   │
│  │           ┌─────────────────────────────────────────┘               │   │
│  │           │         LEFT SIDE (Value)                               │   │
│  │           │                                                         │   │
│  │           ▼                                                         │   │
│  │   ┌───────────────┐                                                 │   │
│  │   │  Value Map    │                                                 │   │
│  │   │   Design      │                                                 │   │
│  │   │    Flow       │                                                 │   │
│  │   └───────┬───────┘                                                 │   │
│  │           │                                                         │   │
│  │           ▼                                                         │   │
│  │   ┌───────────────┐                                                 │   │
│  │   │ Willingness   │                                                 │   │
│  │   │   To Pay      │                                                 │   │
│  │   │    Flow       │                                                 │   │
│  │   └───────┬───────┘                                                 │   │
│  │           │                                                         │   │
│  │           ▼                                                         │   │
│  │   ┌───────────────┐                                                 │   │
│  │   │     Fit       │─────────────────────────────────────────────┐   │   │
│  │   │  Assessment   │                                             │   │   │
│  │   │    Flow       │             IF FIT LOW                      │   │   │
│  │   └───────┬───────┘                │                            │   │   │
│  │           │                        │                            │   │   │
│  │           │                        └────────────────────────────┘   │   │
│  │           │                                                         │   │
│  │           ▼                                                         │   │
│  │      FIT HIGH                                                       │   │
│  │           │                                                         │   │
│  └───────────┼─────────────────────────────────────────────────────────┘   │
│              │                                                              │
│              ▼                                                              │
│     ┌─────────────────────┐                                                │
│     │  VALIDATED VPC      │                                                │
│     │  Ready for Phase 2  │                                                │
│     │  (Desirability)     │                                                │
│     └─────────────────────┘                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## SegmentDiscoveryFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SEGMENT DISCOVERY FLOW                                  │
│                                                                              │
│  Purpose: Validate customer segment hypothesis through multi-source         │
│           evidence - not just interviews                                     │
│                                                                              │
│  Input: Customer Hypothesis from Founder's Brief                            │
│  Output: Validated Segment(s) with evidence strength scores                 │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  EXPERIMENT DESIGNER AGENT (E1)                                      │   │
│  │                                                                      │   │
│  │  Designs experiment mix for segment validation:                      │   │
│  │  • What do we need to learn?                                        │   │
│  │  • Budget and timeline constraints                                  │   │
│  │  • Balance SAY vs DO evidence                                       │   │
│  │  • Balance Direct vs Indirect methods                               │   │
│  │                                                                      │   │
│  │  Output: Experiment Plan                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         ▼                          ▼                          ▼            │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐        │
│  │ INTERVIEW   │          │ OBSERVATION │          │ CTA TEST    │        │
│  │   AGENT     │          │   AGENT     │          │   AGENT     │        │
│  │    (D1)     │          │    (D2)     │          │    (D3)     │        │
│  │             │          │             │          │             │        │
│  │ Direct/SAY  │          │ Indirect/DO │          │ Indirect/DO │        │
│  │             │          │             │          │    + CTA    │        │
│  │ • Problem   │          │ • Social    │          │             │        │
│  │   interviews│          │   listening │          │ • Smoke     │        │
│  │ • Customer  │          │ • Forum     │          │   test LP   │        │
│  │   discovery │          │   analysis  │          │ • Ad tests  │        │
│  │             │          │ • Review    │          │ • Signup    │        │
│  │             │          │   mining    │          │   pages     │        │
│  │             │          │             │          │             │        │
│  │ Output:     │          │ Output:     │          │ Output:     │        │
│  │ Qualitative │          │ Behavioral  │          │ Quantitative│        │
│  │ insights    │          │ patterns    │          │ metrics     │        │
│  └──────┬──────┘          └──────┬──────┘          └──────┬──────┘        │
│         │                        │                        │                │
│         └────────────────────────┼────────────────────────┘                │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  EVIDENCE TRIANGULATION AGENT (D4)                                   │   │
│  │                                                                      │   │
│  │  Combines evidence from all sources:                                 │   │
│  │  • Do interviews align with behavior?                               │   │
│  │  • Do CTAs confirm stated interest?                                 │   │
│  │  • Where is SAY ≠ DO?                                               │   │
│  │                                                                      │   │
│  │  Output: Validated Segment(s) with evidence strength                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Segment Discovery Agents

#### E1: Experiment Designer Agent

| Attribute | Value |
|-----------|-------|
| **ID** | E1 |
| **Name** | Experiment Designer Agent |
| **Founder** | Sage |
| **Role** | Design the optimal mix of experiments for current learning goals |
| **Goal** | Create an experiment plan that balances speed, cost, and evidence quality |

**Backstory:**
```
You are trained in Strategyzer's Testing Business Ideas methodology with access to
the 44 experiment library. You understand that 7 out of 10 new products fail because
assumptions aren't tested. You use Assumptions Mapping to prioritize what to test,
and Test Cards to design rigorous experiments with clear pass/fail criteria.
```

**Step 1: Assumptions Mapping (CRITICAL - Do First)**

```
ASSUMPTIONS MAPPING PROCESS:
1. List all hypotheses about the business idea
2. Categorize by type:
   ├── DESIRABILITY: Will customers want it?
   ├── FEASIBILITY: Can we build/deliver it?
   ├── VIABILITY: Can we profit from it?
   └── ADAPTABILITY: Can it survive change?
3. Map each hypothesis on a 2x2 matrix:
   ├── X-axis: Evidence strength (weak → strong)
   └── Y-axis: Importance to success (low → high)
4. FOCUS on top-right quadrant: High importance + Weak evidence
5. Ask: "Which hypothesis, if proven wrong, will cause the idea to fail?"

OUTPUT: Prioritized list of hypotheses to test
```

**Step 2: Test Card Design (Strategyzer Format)**

```
TEST CARD SCHEMA:
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: HYPOTHESIS                                                          │
│  "We believe that [customer segment] will [expected behavior]               │
│   because [reason/assumption]"                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  STEP 2: TEST                                                                │
│  To verify, we will: [specific experiment description]                       │
│  Cost: [budget]  Duration: [timeline]  Reliability: [low/medium/high]       │
├─────────────────────────────────────────────────────────────────────────────┤
│  STEP 3: METRIC                                                              │
│  We will measure: [specific metric]                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  STEP 4: CRITERIA (SET IN ADVANCE!)                                          │
│  We are right if: [specific threshold]                                       │
│  Example: "8 out of 100 landing page visitors sign up for waitlist"         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Step 3: Learning Card Capture (Post-Experiment)**

```
LEARNING CARD SCHEMA:
┌─────────────────────────────────────────────────────────────────────────────┐
│  HYPOTHESIS                                                                  │
│  "We believed that..."                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  OBSERVATION                                                                 │
│  "We observed..."  [include actual data/metrics]                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  LEARNINGS                                                                   │
│  "From that we learned that..."                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  DECISIONS & ACTIONS                                                         │
│  "Therefore we will..."                                                      │
│  Owner: [who]  Deadline: [when]                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Strategyzer Experiment Library (44 Experiments):**

```
DISCOVERY EXPERIMENTS (Weak-Moderate Evidence, Fast, Cheap):
├── Customer Interviews - Talk to potential customers about problems
├── Discovery Surveys - Open-ended exploration questions
├── Discussion Forums - Monitor existing community discussions
├── Search Trend Analysis - Analyze Google Trends, keyword volumes
├── Follow-Me-Home - Observe customers in natural context
├── Sales Force Feedback - Gather insights from sales team
└── Data Analysis - Analyze existing customer data

VALIDATION EXPERIMENTS (Stronger Evidence, More Investment):
├── Landing Page (Smoke Test) - Simple page with signup CTA
├── Fake Door Test - UI elements for features that don't exist
├── Explainer Video - Video describing the concept + CTA
├── A/B Split Test - Compare two variants
├── Email Campaign - Test message resonance
├── Social Media Campaign - Test audience targeting
├── Online Ad Campaign - Test messaging and audience
├── Crowdfunding - Validate with financial commitment
├── Pre-sale - Collect payment before building
├── Wizard of Oz - Manual service behind automated facade
├── Concierge MVP - Manual, transparent personal service
├── Single Feature MVP - Build one core feature only
├── Clickable Prototype - Interactive mockup
├── Paper Prototype - Hand-drawn interface testing
├── Pop-Up Store - Temporary physical presence
├── Mock Sale - Simulate the purchase process
└── Buy a Feature - Prioritization exercise with customers
```

**Experiment Selection Framework:**

```
LEARNING GOAL → EXPERIMENT TYPES

"Does this segment exist?"
├── Discussion Forums (Indirect/DO) - Are they asking about this?
├── Search Trend Analysis (Indirect/DO) - Are they searching for this?
├── Data Analysis (Indirect/DO) - Do we have existing evidence?
└── Customer Interviews (Direct/SAY) - Can we find and talk to them?

"Is this segment reachable?"
├── Online Ad Campaign (Indirect/DO) - Can we target them?
├── Social Media Campaign (Indirect/DO) - Where do they respond?
└── Email Campaign (Direct/DO) - Can we reach them directly?

"Is this segment interested?"
├── Landing Page/Smoke Test (Indirect/DO+CTA) - Do they sign up?
├── Fake Door Test (Indirect/DO+CTA) - Do they click on features?
├── Explainer Video (Indirect/DO+CTA) - Do they watch and act?
└── A/B Split Test (Indirect/DO) - Which message resonates?

"Is this segment willing to pay?"
├── Pre-sale (Indirect/DO+$$) - Will they pay before it exists?
├── Crowdfunding (Indirect/DO+$$) - Will they pledge money?
├── Mock Sale (Indirect/DO) - Will they go through checkout?
└── Wizard of Oz (Direct/DO) - Will they pay for manual service?
```

---

#### D1: Customer Interview Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D1 |
| **Name** | Customer Interview Agent |
| **Founder** | Sage |
| **Role** | Conduct discovery interviews with potential customers |
| **Goal** | Uncover WHY customers behave the way they do (qualitative insights) |

**Backstory:**
```
You are a master interviewer trained in The Mom Test methodology and Strategyzer's
customer discovery techniques. You understand that what customers SAY and what they
DO are different things. You never pitch solutions during discovery. You focus on
past behavior, not future intentions. You ask about specifics, not generics.
```

**The Mom Test Rules (CRITICAL):**
```
RULE 1: Talk about their life, not your idea
RULE 2: Ask about specifics in the PAST, not generics or opinions about the FUTURE
RULE 3: Talk less, listen more (they talk 80%, you talk 20%)

NEVER ASK (hypothetical/opinion questions):
✗ "Would you buy a product that did X?"
✗ "Do you think this is a good idea?"
✗ "Would you use this?"
✗ "How much would you pay for this?"

ALWAYS ASK (fact-based questions about past behavior):
✓ "Talk me through what happened the last time X came up"
✓ "Show me how you currently do this"
✓ "When is the last time you struggled with this?"
✓ "What have you already tried? What happened?"
✓ "Are you actively searching for a solution? What's the sticking point?"
```

**Strategyzer's 8 Ground Rules:**
```
1. Listen more, talk less
2. Use open-ended follow-up questions ("Can you expand on that...")
3. Focus on FACTS, not opinions (ask "When is the last time..." not "Would you...")
4. Ask "why" frequently ("Why is that important to you?")
5. Don't ask about buying decisions directly
6. NEVER offer solutions during discovery interviews
7. Keep your value proposition in the background
8. Ask for referrals at the end
```

**Interview Types:**

```
PROBLEM INTERVIEW (Discovery)
├── Goal: Validate the problem exists through PAST BEHAVIOR
├── Questions (fact-based, past tense):
│   ├── "Tell me about the last time you experienced [problem]..."
│   ├── "Walk me through exactly what happened..."
│   ├── "How did that make you feel?"
│   ├── "What did you do about it? What was the outcome?"
│   ├── "How often does this happen?"
│   ├── "What have you already tried? Why didn't that work?"
│   └── "Are you actively looking for a solution right now?"
├── AVOID: Asking about hypothetical future behavior
└── Output: Problem validation evidence (behavioral)

CUSTOMER DISCOVERY INTERVIEW
├── Goal: Understand the customer's world and context
├── Questions:
│   ├── "Walk me through a typical day when you're dealing with [area]..."
│   ├── "What tools and processes do you currently use?"
│   ├── "What's the most frustrating part of this?"
│   ├── "Show me how you do this today"
│   ├── "What other solutions have you tried before settling on this one?"
│   └── "Who else should I talk to about this?"
└── Output: Customer context and behavioral patterns

SOLUTION INTERVIEW (Only AFTER Problem Interview validates problem)
├── Goal: Test solution concept AFTER establishing problem validity
├── Prerequisite: Problem interview confirmed the problem is real
├── Approach:
│   ├── Use card sorting with value propositions
│   ├── Show prototype/mockup (don't just describe)
│   ├── Observe behavior, don't ask opinions
│   └── Ask them to repeat the value prop in their own words
├── Questions:
│   ├── "Here's what we're thinking... [show prototype]"
│   ├── "What stands out to you?"
│   ├── "What would you use this for?" (not "Would you use this?")
│   └── "What's confusing or missing?"
└── Output: Solution feedback (observed reactions, not stated opinions)
```

**Strategyzer Trigger Questions for Interviews:**

```
JOBS DISCOVERY:
├── "What tasks are you trying to get done in [context]?"
├── "What's the one thing you couldn't live without accomplishing?"
├── "What functional problems are you trying to solve?"
├── "How do you want to be perceived by others in this role?"
├── "What gives you a sense of satisfaction when accomplished?"
└── "How do your goals change depending on the situation?"

PAINS DISCOVERY:
├── "How do you define 'too costly'? (time, money, effort)"
├── "What makes you feel bad about the current situation?"
├── "What are your frustrations, annoyances, headaches?"
├── "How is your current solution underperforming?"
├── "Which features are missing that you wish existed?"
├── "What risks worry you? (financial, social, technical)"
└── "What barriers prevent you from switching to something better?"

GAINS DISCOVERY:
├── "Which savings would make you happy? (time, money, effort)"
├── "What quality levels do you expect? What would you wish for more?"
├── "How do current solutions delight you? Which features do you enjoy?"
├── "What would make this easier for you?"
├── "What positive social outcomes are you looking for?"
└── "What would increase the likelihood you'd adopt a new solution?"
```

**Tools:**
- `InterviewSchedulerTool` - Schedule and manage interviews
- `TranscriptionTool` - Transcribe and structure interviews
- `InsightExtractorTool` - Pull key insights from transcripts
- `BehaviorPatternTool` - Identify SAY vs DO discrepancies

---

#### D2: Observation Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D2 |
| **Name** | Observation Agent |
| **Founder** | Pulse |
| **Role** | Observe customer behavior in natural settings (without direct interaction) |
| **Goal** | Collect behavioral evidence that isn't biased by researcher presence |

**Observation Methods:**

```
SOCIAL LISTENING
├── Monitor Twitter/X, LinkedIn, Reddit for topic mentions
├── Track sentiment and volume
├── Identify influencers and communities
└── Output: Social signals report

FORUM ANALYSIS
├── Mine Reddit, Quora, StackExchange, niche forums
├── Identify common questions and complaints
├── Analyze solution attempts
└── Output: Community insights report

REVIEW MINING
├── Analyze reviews of competing products
├── Extract praised features and complaints
├── Identify unmet needs
└── Output: Competitor review analysis

SEARCH BEHAVIOR
├── Analyze Google Trends data
├── Research keyword volumes
├── Identify search patterns
└── Output: Search demand report

COMPETITOR BEHAVIOR
├── Observe how competitors' customers behave
├── Analyze competitor pricing and positioning
├── Identify gaps in market
└── Output: Competitive behavior analysis
```

**Tools:**
- `SocialListeningTool` - Monitor social platforms
- `ForumScraperTool` - Extract forum discussions
- `ReviewAnalysisTool` - Analyze product reviews
- `TrendAnalysisTool` - Analyze search trends

---

#### D3: CTA Test Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D3 |
| **Name** | CTA Test Agent |
| **Founder** | Pulse |
| **Role** | Design and run experiments with calls-to-action to measure real behavior |
| **Goal** | Produce quantitative evidence of customer interest through actions, not words |

**Backstory:**
```
You run validation experiments from the Strategyzer 44 Experiment Library. You understand
that behavioral evidence (what customers DO) is stronger than stated intentions (what
they SAY). You always create a Test Card before running experiments, and capture
results in a Learning Card afterward. You set pass/fail criteria IN ADVANCE.
```

**CTA Experiment Types (Strategyzer Naming):**

```
LANDING PAGE / SMOKE TEST
├── Strategyzer Type: Landing Page
├── Description: Simple page describing the concept
├── CTA: Email signup for early access
├── Metrics: Visitors, Signups, Conversion Rate
├── Evidence Strength: MODERATE
└── Test Card Required: Yes

ONLINE AD CAMPAIGN
├── Strategyzer Type: Online Ad Campaign
├── Description: Run ads targeting hypothesized segment
├── CTA: Click to landing page
├── Metrics: Impressions, Clicks, CTR, CPC
├── Evidence Strength: MODERATE
└── Test Card Required: Yes

FAKE DOOR TEST
├── Strategyzer Type: Fake Door Test
├── Description: UI elements for features that don't exist yet
├── CTA: Click to learn more / Join waitlist
├── Metrics: Click rate per feature
├── Evidence Strength: MODERATE
└── Test Card Required: Yes

EXPLAINER VIDEO
├── Strategyzer Type: Explainer Video
├── Description: Video describing the concept + CTA
├── CTA: Sign up, Learn more, Pre-order
├── Metrics: Views, Watch time, CTA clicks
├── Evidence Strength: MODERATE
└── Test Card Required: Yes

PRE-SALE
├── Strategyzer Type: Pre-sale
├── Description: Present the product with pricing, collect payment
├── CTA: Pre-order / Reserve / Pay deposit
├── Metrics: Pre-order count, Revenue, Conversion rate
├── Evidence Strength: STRONG (actual money)
└── Test Card Required: Yes

CROWDFUNDING
├── Strategyzer Type: Crowdfunding
├── Description: Campaign on Kickstarter/Indiegogo
├── CTA: Back this project / Pledge
├── Metrics: Backers, Amount pledged, Funding %
├── Evidence Strength: STRONG (actual money)
└── Test Card Required: Yes
```

**Test Card Output Schema:**

```json
{
  "test_card_id": "uuid",
  "experiment_type": "landing_page | fake_door | pre_sale | crowdfunding | ad_campaign | explainer_video",
  "hypothesis": {
    "customer_segment": "Early-stage SaaS founders",
    "expected_behavior": "sign up for waitlist",
    "reason": "they struggle with customer validation"
  },
  "test_description": "Landing page with 3-step value prop and email capture",
  "cost": "$500 (ad spend) + $0 (landing page)",
  "duration": "7 days",
  "reliability": "medium",
  "metric": "Conversion rate (signups / unique visitors)",
  "success_criteria": {
    "threshold": "5% conversion rate",
    "minimum_sample": 500,
    "confidence_level": "95%"
  },
  "status": "planned | running | completed",
  "created_at": "timestamp"
}
```

**Learning Card Output Schema:**

```json
{
  "learning_card_id": "uuid",
  "test_card_id": "uuid",
  "hypothesis": "We believed that early-stage SaaS founders would sign up for waitlist because they struggle with customer validation",
  "observation": {
    "sample_size": 523,
    "conversions": 31,
    "conversion_rate": 0.059,
    "raw_data": "See analytics report"
  },
  "result": "VALIDATED | INVALIDATED | INCONCLUSIVE",
  "learnings": [
    "Founders respond strongly to 'save time' messaging",
    "Mobile conversion 2x lower than desktop",
    "Price sensitivity higher than expected"
  ],
  "decisions": [
    {
      "action": "Run A/B test on pricing page",
      "owner": "Pulse team",
      "deadline": "2024-02-15"
    }
  ],
  "created_at": "timestamp"
}
```

**Tools:**
- `LandingPageBuilderTool` - Create test pages (Netlify deployment)
- `AdPlatformTool` - Run ads on Meta, Google
- `AnalyticsTool` - Collect and analyze metrics
- `ABTestTool` - Run split tests
- `TestCardTool` - Generate and track Test Cards
- `LearningCardTool` - Capture and store Learning Cards

---

#### D4: Evidence Triangulation Agent

| Attribute | Value |
|-----------|-------|
| **ID** | D4 |
| **Name** | Evidence Triangulation Agent |
| **Founder** | Guardian |
| **Role** | Synthesize evidence from multiple sources and identify patterns |
| **Goal** | Create a unified view of what we actually know, accounting for evidence quality |

**Triangulation Framework:**

```
EVIDENCE SYNTHESIS
├── Collect evidence from all sources
├── Weight by evidence type:
│   ├── PAID (weight 5) - Actually paid money
│   ├── HIGH-COMMITMENT CTA (weight 4) - Demo request, application
│   ├── MEDIUM-COMMITMENT CTA (weight 3) - Email signup, form fill
│   ├── LOW-COMMITMENT CTA (weight 2) - Click, view
│   ├── STATED (weight 1) - Said they would
│   └── IMPLIED (weight 0.5) - Didn't say no
└── Calculate weighted evidence score

SAY vs DO ANALYSIS
├── Compare stated preferences (interviews, surveys)
├── vs actual behavior (CTAs, payments)
├── Flag discrepancies (important signal!)
└── Investigate root cause of gaps

CONFIDENCE SCORING
├── Evidence volume (N = sample size)
├── Evidence diversity (multiple methods)
├── Evidence consistency (do sources agree?)
└── Output: Confidence level (Low/Medium/High)
```

**Output Schema:**
```json
{
  "segment_id": "uuid",
  "segment_name": "Early-stage SaaS founders",
  "validation_status": "VALIDATED | PARTIALLY_VALIDATED | INVALIDATED",
  "evidence_strength_score": 3.7,
  "confidence_level": "HIGH | MEDIUM | LOW",
  "evidence_summary": {
    "interviews_conducted": 12,
    "observations_collected": 45,
    "cta_experiments_run": 3,
    "total_cta_conversions": 127
  },
  "say_vs_do_analysis": {
    "alignment": "STRONG | MODERATE | WEAK",
    "discrepancies": [
      {
        "topic": "Willingness to pay",
        "said": "Would definitely pay $50/month",
        "did": "2% converted on $29/month pricing page",
        "implication": "Stated WTP inflated, actual WTP lower"
      }
    ]
  },
  "key_insights": [],
  "recommended_next_steps": []
}
```

---

## JobsDiscoveryFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      JOBS DISCOVERY FLOW                                     │
│                                                                              │
│  Purpose: Discover and rank Jobs-to-be-Done for the validated segment      │
│                                                                              │
│  Input: Validated Segment(s) from SegmentDiscoveryFlow                      │
│  Output: Ranked Jobs (Functional, Emotional, Social)                        │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  JTBD RESEARCHER AGENT (J1)                                          │   │
│  │                                                                      │   │
│  │  Discover jobs through:                                              │   │
│  │  • JTBD Interviews ("What were you trying to accomplish?")          │   │
│  │  • Search Query Analysis (What are they searching for?)             │   │
│  │  • Forum Mining (What questions do they ask?)                       │   │
│  │  • Competitor Analysis (What jobs do alternatives address?)         │   │
│  │                                                                      │   │
│  │  Categorize jobs:                                                    │   │
│  │  • Functional Jobs (tasks to complete)                              │   │
│  │  • Emotional Jobs (how they want to feel)                           │   │
│  │  • Social Jobs (how they want to be perceived)                      │   │
│  │  • Supporting Jobs - Buyer (comparing, purchasing, delivery)        │   │
│  │  • Supporting Jobs - Co-creator (feedback, customization)           │   │
│  │  • Supporting Jobs - Transferrer (canceling, disposing, reselling)  │   │
│  │                                                                      │   │
│  │  Use JTBD Timeline Technique:                                        │   │
│  │  • First Thought → Event One → Event Two → Purchase                 │   │
│  │  • Four Forces: Push/Pull toward change vs Habit/Anxiety resistance │   │
│  │                                                                      │   │
│  │  Output: Job Inventory                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  JOB RANKING AGENT (J2)                                              │   │
│  │                                                                      │   │
│  │  Rank jobs by importance through:                                    │   │
│  │  • Interview ranking ("Which is most important?")                   │   │
│  │  • Max-Diff Survey (forced ranking)                                 │   │
│  │  • Job-focused Ad Tests (which job messaging gets clicks?)          │   │
│  │  • Content Engagement (which job content resonates?)                │   │
│  │                                                                      │   │
│  │  Output: Ranked Job List with importance scores                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Jobs Output Schema:**
```json
{
  "segment_id": "uuid",
  "jobs": [
    {
      "job_id": "uuid",
      "job_statement": "When [situation], I want to [motivation], so I can [outcome]",
      "job_type": "functional | emotional | social | supporting_buyer | supporting_cocreator | supporting_transferrer",
      "job_context": "Specific situation/trigger when this job arises",
      "importance_score": 4.5,
      "importance_rank": 1,
      "four_forces": {
        "push_of_situation": "What about their situation led them to look for a solution?",
        "pull_of_new_solution": "What about the new solution attracted them?",
        "habit_of_present": "What habits prevent trying something new?",
        "anxiety_of_new": "What anxieties about trying/using a new solution?"
      },
      "timeline": {
        "first_thought": "When did they first think about needing a solution?",
        "event_one": "What kicked them into active looking?",
        "event_two": "What triggered deciding mode?"
      },
      "evidence": {
        "interview_mentions": 8,
        "search_volume": 12000,
        "ad_ctr": 0.045,
        "evidence_strength": "HIGH"
      }
    }
  ]
}
```

---

## PainsDiscoveryFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PAINS DISCOVERY FLOW                                    │
│                                                                              │
│  Purpose: Discover and rank Pains for the validated segment                 │
│                                                                              │
│  Input: Validated Segment(s) + Jobs                                         │
│  Output: Ranked Pains with severity scores                                  │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PAIN RESEARCHER AGENT (P1)                                          │   │
│  │                                                                      │   │
│  │  Discover pains through:                                             │   │
│  │  • Pain Interviews ("What frustrates you?")                         │   │
│  │  • Review Mining (What do they complain about?)                     │   │
│  │  • Support Ticket Analysis (What problems arise?)                   │   │
│  │  • Forum Mining (What questions/complaints?)                        │   │
│  │                                                                      │   │
│  │  Categorize pains:                                                   │   │
│  │  • Undesired outcomes (what they're trying to avoid)               │   │
│  │  • Obstacles (what prevents them from getting job done)            │   │
│  │  • Risks (what could go wrong)                                      │   │
│  │                                                                      │   │
│  │  Output: Pain Inventory                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PAIN RANKING AGENT (P2)                                             │   │
│  │                                                                      │   │
│  │  Rank pains by severity through:                                     │   │
│  │  • Interview ranking ("Which is most painful?")                     │   │
│  │  • Pain-focused Ad Tests (which pain messaging gets clicks?)        │   │
│  │  • A/B Landing Pages (which pain angle converts?)                   │   │
│  │  • Severity Survey (rate pain severity 1-5)                         │   │
│  │                                                                      │   │
│  │  Output: Ranked Pain List with severity scores                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## GainsDiscoveryFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      GAINS DISCOVERY FLOW                                    │
│                                                                              │
│  Purpose: Discover and rank Gains for the validated segment                 │
│                                                                              │
│  Input: Validated Segment(s) + Jobs                                         │
│  Output: Ranked Gains with importance scores                                │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  GAIN RESEARCHER AGENT (G1)                                          │   │
│  │                                                                      │   │
│  │  Discover gains through:                                             │   │
│  │  • Gain Interviews ("What would delight you?")                      │   │
│  │  • Review Mining (What do they praise in competitors?)              │   │
│  │  • Feature Request Analysis (What do they ask for?)                 │   │
│  │  • Success Story Analysis (What outcomes do they celebrate?)        │   │
│  │                                                                      │   │
│  │  Categorize gains:                                                   │   │
│  │  • Required gains (must-have outcomes)                              │   │
│  │  • Expected gains (standard expectations)                           │   │
│  │  • Desired gains (would be nice)                                    │   │
│  │  • Unexpected gains (delighters)                                    │   │
│  │                                                                      │   │
│  │  Output: Gain Inventory                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  GAIN RANKING AGENT (G2)                                             │   │
│  │                                                                      │   │
│  │  Rank gains by importance through:                                   │   │
│  │  • Interview ranking ("Which matters most?")                        │   │
│  │  • Conjoint Analysis (trade-off preferences)                        │   │
│  │  • Feature Voting (which features = which gains?)                   │   │
│  │  • A/B Landing Pages (which gain angle converts?)                   │   │
│  │                                                                      │   │
│  │  Output: Ranked Gain List with importance scores                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ValueMapDesignFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VALUE MAP DESIGN FLOW                                   │
│                                                                              │
│  Purpose: Design the left side of VPC based on ranked pains and gains       │
│                                                                              │
│  Input: Ranked Jobs, Pains, Gains                                           │
│  Output: Value Map (Products, Pain Relievers, Gain Creators)                │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  SOLUTION DESIGNER AGENT (V1)                                        │   │
│  │                                                                      │   │
│  │  Design Products/Services that address top jobs:                     │   │
│  │  • Map each major job to a product/service/feature                  │   │
│  │  • Prioritize based on job importance                               │   │
│  │  • Consider technical feasibility                                   │   │
│  │                                                                      │   │
│  │  Output: Products/Services List                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PAIN RELIEVER DESIGNER AGENT (V2)                                   │   │
│  │                                                                      │   │
│  │  Design Pain Relievers for top pains:                                │   │
│  │  • Map each severe pain to a reliever                               │   │
│  │  • Describe HOW the product relieves each pain                      │   │
│  │  • Prioritize by pain severity                                      │   │
│  │                                                                      │   │
│  │  Output: Pain Relievers mapped to Pains                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  GAIN CREATOR DESIGNER AGENT (V3)                                    │   │
│  │                                                                      │   │
│  │  Design Gain Creators for top gains:                                 │   │
│  │  • Map each important gain to a creator                             │   │
│  │  • Describe HOW the product creates each gain                       │   │
│  │  • Prioritize by gain importance                                    │   │
│  │                                                                      │   │
│  │  Output: Gain Creators mapped to Gains                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## WillingnessToPayFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WILLINGNESS TO PAY FLOW                                   │
│                                                                              │
│  Purpose: Test whether customers will actually pay for the value prop       │
│                                                                              │
│  Input: Value Map + Customer Segment                                        │
│  Output: WTP Evidence (price sensitivity, conversion rates)                 │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PRICING EXPERIMENT AGENT (W1)                                       │   │
│  │                                                                      │   │
│  │  Design WTP experiments:                                             │   │
│  │  • Van Westendorp Survey (price sensitivity)                        │   │
│  │  • Pricing Page A/B Test (which price converts?)                    │   │
│  │  • Conjoint with Price (trade-off vs price)                         │   │
│  │                                                                      │   │
│  │  Output: Price Sensitivity Analysis                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PAYMENT TEST AGENT (W2)                                             │   │
│  │                                                                      │   │
│  │  Run actual payment tests:                                           │   │
│  │  • Pre-order Page (will they pay deposit?)                          │   │
│  │  • Crowdfunding Test (will they back?)                              │   │
│  │  • Pilot Program (will they pay for beta?)                          │   │
│  │  • Letter of Intent (B2B commitment)                                │   │
│  │                                                                      │   │
│  │  Output: Payment Conversion Data                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  HITL: approve_pricing_test (if real money involved)                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## FitAssessmentFlow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FIT ASSESSMENT FLOW                                     │
│                                                                              │
│  Purpose: Assess Problem-Solution Fit and decide next iteration             │
│                                                                              │
│  Input: Complete VPC (Customer Profile + Value Map)                         │
│  Output: Fit Score + Iteration Decision                                     │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  FIT ANALYST AGENT (F1)                                              │   │
│  │                                                                      │   │
│  │  Assess fit between Customer Profile and Value Map:                  │   │
│  │  • Do Pain Relievers address the top pains?                         │   │
│  │  • Do Gain Creators deliver the top gains?                          │   │
│  │  • Are the top jobs served by products/services?                    │   │
│  │  • Is there willingness to pay at viable price point?               │   │
│  │                                                                      │   │
│  │  Output: Fit Score (0-100) + Gap Analysis                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ITERATION ROUTER AGENT (F2)                                         │   │
│  │                                                                      │   │
│  │  Decide next step based on fit score and gaps:                       │   │
│  │                                                                      │   │
│  │  IF fit_score >= 70 AND wtp_validated:                              │   │
│  │      → EXIT to Phase 2 (Desirability Testing)                       │   │
│  │                                                                      │   │
│  │  IF fit_score < 70:                                                  │   │
│  │      Identify biggest gap:                                           │   │
│  │      • Wrong segment? → Loop to SegmentDiscoveryFlow                │   │
│  │      • Wrong jobs? → Loop to JobsDiscoveryFlow                      │   │
│  │      • Missing pains? → Loop to PainsDiscoveryFlow                  │   │
│  │      • Missing gains? → Loop to GainsDiscoveryFlow                  │   │
│  │      • Bad value map? → Loop to ValueMapDesignFlow                  │   │
│  │      • WTP issue? → Loop to WillingnessToPayFlow                    │   │
│  │                                                                      │   │
│  │  Output: Next Flow to invoke + specific focus                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  HITL: approve_vpc_completion (when fit >= 70)                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1 Agent Summary

| ID | Agent Name | Founder | Flow | Role |
|----|------------|---------|------|------|
| E1 | Experiment Designer | Sage | All Discovery | Design experiment mix |
| D1 | Customer Interview | Sage | Segment | Conduct discovery interviews |
| D2 | Observation | Pulse | Segment | Observe behavior (indirect) |
| D3 | CTA Test | Pulse | Segment | Run CTA experiments |
| D4 | Evidence Triangulation | Guardian | Segment | Synthesize multi-source evidence |
| J1 | JTBD Researcher | Sage | Jobs | Discover jobs-to-be-done |
| J2 | Job Ranking | Sage | Jobs | Rank jobs by importance |
| P1 | Pain Researcher | Sage | Pains | Discover customer pains |
| P2 | Pain Ranking | Sage | Pains | Rank pains by severity |
| G1 | Gain Researcher | Sage | Gains | Discover customer gains |
| G2 | Gain Ranking | Sage | Gains | Rank gains by importance |
| V1 | Solution Designer | Forge | Value Map | Design products/services |
| V2 | Pain Reliever Designer | Forge | Value Map | Design pain relievers |
| V3 | Gain Creator Designer | Forge | Value Map | Design gain creators |
| W1 | Pricing Experiment | Ledger | WTP | Design pricing experiments |
| W2 | Payment Test | Ledger | WTP | Run payment tests |
| F1 | Fit Analyst | Compass | Fit Assessment | Score problem-solution fit |
| F2 | Iteration Router | Compass | Fit Assessment | Decide next iteration |

**Total Phase 1 Agents: 18**

---

## Phase 1 HITL Checkpoints

| Checkpoint | Flow | Purpose |
|------------|------|---------|
| `approve_experiment_plan` | All Discovery | Approve experiment mix before running |
| `approve_pricing_test` | WTP | Approve tests involving real money |
| `approve_vpc_completion` | Fit Assessment | Confirm VPC ready for Phase 2 |

---

## VPC Output Schema (Phase 1 Final Artifact)

```json
{
  "vpc_id": "uuid",
  "brief_id": "uuid",
  "created_at": "timestamp",
  "iteration": 3,
  "fit_score": 78,

  "customer_profile": {
    "segment": {
      "segment_id": "uuid",
      "name": "Early-stage SaaS founders",
      "description": "...",
      "evidence_strength": "HIGH",
      "validation_status": "VALIDATED"
    },
    "jobs": [
      {
        "job_id": "uuid",
        "statement": "When launching a new product, I want to validate demand quickly, so I can avoid wasting months building something nobody wants",
        "type": "functional",
        "importance_rank": 1,
        "importance_score": 4.8
      }
    ],
    "pains": [
      {
        "pain_id": "uuid",
        "description": "Spending months building before talking to customers",
        "category": "obstacle",
        "severity_rank": 1,
        "severity_score": 4.9
      }
    ],
    "gains": [
      {
        "gain_id": "uuid",
        "description": "Confidence that customers will pay before building",
        "category": "desired",
        "importance_rank": 1,
        "importance_score": 4.7
      }
    ]
  },

  "value_map": {
    "products_services": [
      {
        "id": "uuid",
        "name": "AI Validation Engine",
        "description": "...",
        "addresses_jobs": ["job_id_1", "job_id_2"]
      }
    ],
    "pain_relievers": [
      {
        "id": "uuid",
        "description": "Runs validation experiments in days, not months",
        "addresses_pain": "pain_id_1",
        "effectiveness_score": 4.5
      }
    ],
    "gain_creators": [
      {
        "id": "uuid",
        "description": "Produces evidence of customer demand before building",
        "creates_gain": "gain_id_1",
        "effectiveness_score": 4.6
      }
    ]
  },

  "fit_analysis": {
    "fit_score": 78,
    "jobs_addressed_pct": 85,
    "pains_addressed_pct": 75,
    "gains_addressed_pct": 70,
    "wtp_validated": true,
    "gaps": [
      {
        "type": "pain",
        "item": "Fear of competitor copying idea",
        "status": "NOT_ADDRESSED"
      }
    ],
    "strengths": [
      "Strong job fit",
      "Top pain well addressed"
    ]
  },

  "wtp_evidence": {
    "tested_price_points": ["$29", "$49", "$99"],
    "optimal_price": "$49",
    "conversion_at_optimal": 0.034,
    "pre_orders_collected": 23,
    "evidence_strength": "MEDIUM"
  },

  "iteration_history": [
    {
      "iteration": 1,
      "fit_score": 45,
      "pivot_type": "segment",
      "lesson_learned": "B2C segment not viable, pivoted to B2B"
    }
  ],

  "ready_for_phase_2": true
}
```

---

## Summary

| Phase | Flows | Agents | HITL | Output |
|-------|-------|--------|------|--------|
| **Phase 0: Onboarding** | 1 | 4 | 1 | Founder's Brief |
| **Phase 1: VPC Discovery** | 7 | 18 | 3 | Validated VPC |
| **Total** | **8** | **22** | **4** | |

These two phases create the foundation for all subsequent validation work. The Founder's Brief captures intent; the Validated VPC captures customer reality.

---

## VPD Framework Compliance

This specification has been validated against Alex Osterwalder's Value Proposition Design framework (Strategyzer).

### Framework Alignment Checklist

| VPD Element | Status | Implementation |
|-------------|--------|----------------|
| **Value Proposition Canvas Structure** | ✅ | Customer Profile (Jobs, Pains, Gains) + Value Map (Products, Pain Relievers, Gain Creators) |
| **Jobs Categorization** | ✅ | Functional, Emotional, Social + Supporting (Buyer, Co-creator, Transferrer) |
| **Pains Categorization** | ✅ | Undesired Outcomes, Obstacles, Risks |
| **Gains Categorization** | ✅ | Required, Expected, Desired, Unexpected |
| **Right Side First** | ✅ | Phase 1 starts with Customer Profile before Value Map |
| **Problem-Solution Fit Definition** | ✅ | Fit score ≥70% with WTP evidence |

### Testing Business Ideas Alignment

| Element | Status | Implementation |
|---------|--------|----------------|
| **Assumptions Mapping** | ✅ | E1 agent uses 2x2 matrix (importance × evidence) |
| **Test Card Framework** | ✅ | 4-step schema (Hypothesis, Test, Metric, Criteria) |
| **Learning Card Framework** | ✅ | 4-step schema (Hypothesis, Observation, Learnings, Actions) |
| **44 Experiment Library** | ✅ | D3 agent uses Strategyzer naming conventions |
| **Evidence Strength Hierarchy** | ✅ | Paid (5) > High-CTA (4) > Medium-CTA (3) > Low-CTA (2) > Stated (1) |
| **SAY vs DO Principle** | ✅ | D4 agent triangulates behavioral vs stated evidence |

### Interview Methodology Alignment

| Element | Status | Implementation |
|---------|--------|----------------|
| **Strategyzer 8 Ground Rules** | ✅ | D1 agent backstory + explicit rules |
| **The Mom Test Rules** | ✅ | D1 agent: past behavior, no hypotheticals, no pitching |
| **Trigger Questions** | ✅ | Jobs, Pains, Gains questions from Strategyzer library |
| **Problem vs Solution Interview** | ✅ | Problem first, solution only after validation |

### JTBD Methodology Alignment

| Element | Status | Implementation |
|---------|--------|----------------|
| **Job Story Format** | ✅ | "When [situation], I want to [motivation], so I can [outcome]" |
| **Timeline Technique** | ✅ | First Thought → Event One → Event Two → Purchase |
| **Four Forces Model** | ✅ | Push/Pull toward change vs Habit/Anxiety resistance |
| **Supporting Jobs** | ✅ | Buyer, Co-creator, Transferrer job categories |

### Key VPD Principles Embedded

1. **"Start with the customer, not the solution"**
   - Phase 0 captures Founder hypotheses WITHOUT validating them
   - Phase 1 discovers actual customer reality

2. **"What customers SAY ≠ what they DO"**
   - D1 agent asks about past behavior, not future intentions
   - D3 agent runs CTA experiments for behavioral evidence
   - D4 agent compares SAY vs DO sources

3. **"Focus on the most important jobs, pains, and gains"**
   - All discovery flows include ranking agents (J2, P2, G2)
   - Only top-ranked items flow to Value Map design

4. **"Great value propositions address a few pains really well"**
   - V2 Pain Reliever Designer prioritizes by pain severity
   - F1 Fit Analyst measures coverage percentage

5. **"Evidence trumps opinion"**
   - Test Cards require success criteria SET IN ADVANCE
   - Learning Cards capture what actually happened
   - Experiments progress from cheap/fast to expensive/reliable

### Sources

- Osterwalder, A., Pigneur, Y., et al. (2014). *Value Proposition Design*. Wiley.
- Bland, D. J., Osterwalder, A. (2019). *Testing Business Ideas*. Wiley.
- Fitzpatrick, R. (2013). *The Mom Test*. CreateSpace.
- Moesta, B., Spiek, C. *Jobs-to-be-Done Framework*. Re-Wired Group.
- Strategyzer Experiment Library: https://www.strategyzer.com/training/experiment-library

---

**Document Version**: 1.1.0
**Last Updated**: 2026-01-05
**VPD Compliance Review**: Complete
