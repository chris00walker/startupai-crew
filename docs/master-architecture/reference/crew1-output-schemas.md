---
purpose: Pydantic output schema definitions for Crew 1 (Intake)
status: active
created: 2026-01-06
schema_location: src/intake_crew/schemas.py
---

# Crew 1 Output Schemas

This document defines the Pydantic output schemas for all 6 tasks in Crew 1 (Intake). These schemas enforce structured outputs and enable reliable crew-to-crew data transfer.

## Schema Overview

| Task | Schema | Description |
|------|--------|-------------|
| 1. parse_founder_input | `FounderBrief` | Structured entrepreneur brief |
| 2. research_customer_problem | `CustomerResearchOutput` | JTBD customer profiles |
| 3. create_value_proposition_canvas | `ValuePropositionCanvas` | Complete VPC with fit analysis |
| 4. qa_gate_intake | `QAGateOutput` | Quality assessment before HITL |
| 5. approve_intake_to_validation | `HumanApprovalInput` | Human decision capture |
| 6. trigger_validation_crew | `CrewInvocationResult` | Crew 2 invocation result |

---

## Enumerations

### RiskLevel
```python
class RiskLevel(str, Enum):
    CRITICAL = "critical"   # Must be true or business fails
    HIGH = "high"           # Significant impact if wrong
    MEDIUM = "medium"       # Important but recoverable
    LOW = "low"             # Nice to validate
```

### PainSeverity
```python
class PainSeverity(str, Enum):
    EXTREME = "extreme"     # Constant, unbearable frustration
    HIGH = "high"           # Frequent, significant pain
    MODERATE = "moderate"   # Occasional, manageable
    LOW = "low"             # Minor inconvenience
```

### GainImportance
```python
class GainImportance(str, Enum):
    ESSENTIAL = "essential"     # Must-have for solution adoption
    EXPECTED = "expected"       # Standard expectation
    DESIRED = "desired"         # Would be nice to have
    UNEXPECTED = "unexpected"   # Delighter if present
```

### JobType
```python
class JobType(str, Enum):
    FUNCTIONAL = "functional"   # What task they want done
    EMOTIONAL = "emotional"     # How they want to feel
    SOCIAL = "social"           # How they want to be perceived
```

### QAStatus
```python
class QAStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"  # Pass with required changes
```

### ApprovalDecision
```python
class ApprovalDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
```

---

## Task 1: FounderBrief

**Purpose**: Structured entrepreneur brief from raw founder input.

```python
class Hypothesis(BaseModel):
    statement: str          # Clear, testable hypothesis
    risk_level: RiskLevel   # Criticality ranking
    validation_method: Optional[str]  # How to test

class FounderBrief(BaseModel):
    business_idea: str          # min 20 chars
    problem_statement: str      # min 20 chars
    proposed_solution: str      # min 20 chars
    target_customers: List[str] # min 1 item
    key_hypotheses: List[Hypothesis]  # min 1 item
    success_metrics: List[str]  # min 1 item
    parsed_at: str              # ISO timestamp (auto)
```

**Validation Rules**:
- `business_idea`, `problem_statement`, `proposed_solution` must be at least 20 characters
- At least 1 target customer segment
- At least 1 testable hypothesis with risk level
- At least 1 success metric

---

## Task 2: CustomerResearchOutput

**Purpose**: Customer research using Jobs-to-be-Done methodology.

```python
class CustomerJob(BaseModel):
    job_type: JobType           # functional/emotional/social
    description: str            # min 10 chars
    frequency: Optional[str]    # How often
    importance: int             # 1-10 scale

class CustomerPain(BaseModel):
    description: str            # min 10 chars
    severity: PainSeverity      # extreme/high/moderate/low
    frequency: Optional[str]
    current_workaround: Optional[str]

class CustomerGain(BaseModel):
    description: str            # min 10 chars
    importance: GainImportance  # essential/expected/desired/unexpected
    current_satisfaction: Optional[int]  # 1-10

class CustomerSegmentProfile(BaseModel):
    segment_name: str           # min 3 chars
    segment_description: str    # min 20 chars
    jobs_to_be_done: List[CustomerJob]    # min 1
    pains: List[CustomerPain]             # min 1
    gains: List[CustomerGain]             # min 1
    research_sources: List[str]           # URLs/names

class CustomerResearchOutput(BaseModel):
    customer_segments: List[CustomerSegmentProfile]  # min 1
    research_summary: str       # min 50 chars
    researched_at: str          # ISO timestamp (auto)
```

**Validation Rules**:
- At least 1 customer segment
- Each segment must have jobs, pains, and gains
- Job importance must be 1-10
- Research summary must be at least 50 characters

---

## Task 3: ValuePropositionCanvas

**Purpose**: Complete Value Proposition Canvas with fit analysis.

```python
class PainReliever(BaseModel):
    pain_addressed: str         # Which pain
    reliever_description: str   # min 10 chars
    relief_strength: Literal["complete", "partial", "minimal"]

class GainCreator(BaseModel):
    gain_addressed: str         # Which gain
    creator_description: str    # min 10 chars
    creation_strength: Literal["strong", "moderate", "weak"]

class ValueMap(BaseModel):
    products_services: List[str]          # min 1
    pain_relievers: List[PainReliever]    # min 1
    gain_creators: List[GainCreator]      # min 1

class FitAnalysis(BaseModel):
    covered_jobs: List[str]     # Jobs addressed
    covered_pains: List[str]    # Pains with relievers
    covered_gains: List[str]    # Gains with creators
    gaps: List[str]             # Unaddressed needs
    fit_score: float            # 0.0-1.0

class ValuePropositionCanvas(BaseModel):
    primary_segment: str        # Which segment
    customer_jobs: List[str]    # min 1
    customer_pains: List[str]   # min 1
    customer_gains: List[str]   # min 1
    value_map: ValueMap
    fit_analysis: FitAnalysis
    value_proposition_statement: str  # min 20 chars
    canvas_created_at: str      # ISO timestamp (auto)
```

**Validation Rules**:
- `fit_score` must be between 0.0 and 1.0
- `value_proposition_statement` must be at least 20 characters
- All lists must have at least 1 item

---

## Task 4: QAGateOutput

**Purpose**: Quality assessment of all intake outputs before HITL.

```python
class ReviewSection(BaseModel):
    status: QAStatus            # pass/fail/conditional
    issues: List[str]           # Problems found
    suggestions: List[str]      # Improvements

class QAGateOutput(BaseModel):
    overall_status: QAStatus
    brief_review: ReviewSection
    customer_research_review: ReviewSection
    vpc_review: ReviewSection
    recommendations: List[str]
    blocking_issues: List[str]  # Must-fix before proceeding
    completeness_score: float   # 0.0-1.0
    quality_score: float        # 0.0-1.0
    methodology_compliance_score: float  # 0.0-1.0
    ready_for_human_review: bool
    reviewed_at: str            # ISO timestamp (auto)
```

**Validation Rules**:
- All scores must be between 0.0 and 1.0
- `ready_for_human_review` determines if HITL can proceed

---

## Task 5: HumanApprovalInput

**Purpose**: Human approval decision for intake phase (HITL).

```python
class HumanApprovalInput(BaseModel):
    decision: ApprovalDecision  # approved/rejected/needs_revision
    comments: Optional[str]     # Human feedback
    specific_feedback: List[str]  # Items to address
    approved_by: Optional[str]  # Identifier
    approved_at: str            # ISO timestamp (auto)
```

**Validation Rules**:
- `decision` is required
- `specific_feedback` captures actionable items if revision needed

---

## Task 6: CrewInvocationResult

**Purpose**: Result of invoking Crew 2 (Validation Engine).

```python
class CrewInvocationResult(BaseModel):
    success: bool
    crew_name: str = "Validation Crew"
    kickoff_id: Optional[str]   # Crew 2 execution ID
    data_sent: Dict[str, bool]  # What was included
    error_message: Optional[str]
    retry_count: int = 0
    invoked_at: str             # ISO timestamp (auto)
```

**Validation Rules**:
- `success` indicates if Crew 2 was successfully invoked
- `kickoff_id` is populated on success for tracking
- `error_message` is populated on failure

---

## Usage in crew.py

```python
from intake_crew.schemas import (
    FounderBrief,
    CustomerResearchOutput,
    ValuePropositionCanvas,
    QAGateOutput,
    HumanApprovalInput,
    CrewInvocationResult,
)

@task
def parse_founder_input(self) -> Task:
    return Task(
        config=self.tasks_config["parse_founder_input"],
        output_pydantic=FounderBrief,  # Enforces schema
        markdown=False,
    )
```

---

## Data Flow

```
Task 1 (FounderBrief)
    ↓
Task 2 (CustomerResearchOutput) ← depends on Task 1
    ↓
Task 3 (ValuePropositionCanvas) ← depends on Tasks 1, 2
    ↓
Task 4 (QAGateOutput) ← depends on Tasks 1, 3
    ↓
Task 5 (HumanApprovalInput) ← HITL, depends on Task 4
    ↓
Task 6 (CrewInvocationResult) ← depends on Task 5
    ↓
[Crew 2: Validation Engine]
```

---

## Related Files

| File | Purpose |
|------|---------|
| `src/intake_crew/schemas.py` | Schema definitions |
| `src/intake_crew/crew.py` | Schema wiring via `output_pydantic` |
| `src/intake_crew/config/tasks.yaml` | Task descriptions with schema alignment |
| `tests/test_intake_schemas.py` | Unit tests (28 tests) |
