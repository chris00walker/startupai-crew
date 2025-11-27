# Governance Crew Implementation

## Overview

The Governance Crew handles quality assurance, compliance, flywheel learning, and privacy protection. Owned by Guardian (CGoO).

**Status:** Implemented (Phase 2A-2D complete)

## Agents (3)

### 1. QA Auditor
Quality review with cross-validation learning context.

**Tools:**
- `LearningRetrievalTool` - Retrieves past learnings for context
- `GuardianReviewTool` - Auto-QA for creatives (landing pages, ads)
- `MethodologyCheckTool` - VPC/BMC validation
- `FlywheelInsightsTool` - Industry/stage pattern retrieval

### 2. Compliance Monitor
Process compliance and privacy protection.

**Tools:**
- `AnonymizerTool` - PII anonymization
- `MethodologyCheckTool` - VPC/BMC structure validation
- `PrivacyGuardTool` - PII detection, GDPR/CCPA/HIPAA compliance

### 3. Accountability Tracker
Flywheel learning capture and outcome tracking.

**Tools:**
- `LearningCaptureTool` - Captures anonymized learnings
- `LearningRetrievalTool` - Retrieves past learnings
- `AnonymizerTool` - Strips PII before storage
- `FlywheelInsightsTool` - Industry/stage patterns
- `OutcomeTrackerTool` - Prediction/outcome tracking
- `PrivacyGuardTool` - Privacy validation before storage

## Tasks

| Task | Description | Agent |
|------|-------------|-------|
| `quality_review` | Framework compliance, logical consistency | qa_auditor |
| `final_audit` | Final validation before completion | qa_auditor |
| `track_progress` | Progress tracking and accountability | accountability_tracker |
| `review_creatives` | Auto-QA landing pages and ads | qa_auditor |
| `validate_methodology` | VPC/BMC structure validation | compliance_monitor |
| `retrieve_similar_validations` | Cross-validation context retrieval | qa_auditor |
| `track_predictions` | Record predictions at decision points | accountability_tracker |
| `record_outcomes` | Capture actual outcomes for feedback | accountability_tracker |
| `check_privacy` | Privacy validation before Flywheel storage | compliance_monitor |
| `validate_cross_validation_sharing` | Privacy boundaries between validations | compliance_monitor |

## Output

**QA Report** containing:
- Pass/Fail/Conditional status
- Framework compliance score
- Logical consistency score
- Completeness score
- Actionable feedback

**Flywheel Learnings** containing:
- Anonymized patterns from validation
- Outcome predictions and actuals
- Industry/stage context

## Implementation Files

```
src/startupai/crews/governance/
├── config/
│   ├── agents.yaml           # 3 agent definitions
│   └── tasks.yaml            # 10 task definitions
└── governance_crew.py        # Crew with 8 tools wired
```

## Test Coverage

```
tests/integration/
├── test_hitl_workflow.py     # 32 tests (GuardianReview, Methodology)
├── test_flywheel_workflow.py # 38 tests (Flywheel learning)
└── test_privacy_guard.py     # 40 tests (PrivacyGuard)
```

## Phases Delivered

- **Phase 2A:** GuardianReviewTool, MethodologyCheckTool, HITL creative workflow
- **Phase 2C:** FlywheelInsightsTool, OutcomeTrackerTool, cross-validation learning
- **Phase 2D:** PrivacyGuardTool, compliance checks, privacy boundaries

---
**Spec**: `docs/master-architecture/03-validation-spec.md`
**Last Updated**: 2025-11-26
