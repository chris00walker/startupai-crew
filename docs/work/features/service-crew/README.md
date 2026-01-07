# Service Crew Implementation

> **ARCHIVED (2026-01-07)**: This documents the original 8-crew architecture. The project has migrated to a 3-Crew architecture. Service Crew functionality is now part of **Crew 1 (Intake)** in `src/intake_crew/`. See [02-organization.md](../../../master-architecture/02-organization.md) for current architecture.

## Overview (Historical)

The Service Crew handled customer intake and brief capture. Owned by Sage (CSO).

**Status:** Archived - Migrated to Crew 1

## Agents (3)

### 1. Customer Service Agent
Initial lead qualification and routing.

**Responsibilities:**
- Assess inquiry type (founder vs consultant)
- Route to appropriate onboarding agent
- Capture basic context

### 2. Founder Onboarding Agent
Structured interviews for individual founders.

**Responsibilities:**
- Conduct guided interview
- Extract business hypothesis
- Identify key assumptions
- Define validation goals

### 3. Consultant Onboarding Agent
Multi-client context for agencies and consultants.

**Responsibilities:**
- Handle multi-client workflows
- Aggregate client briefs
- Support portfolio management context

## Tasks

| Task | Description | Agent |
|------|-------------|-------|
| `qualify_lead` | Initial lead assessment | customer_service |
| `route_to_onboarding` | Direct to founder/consultant path | customer_service |
| `conduct_founder_interview` | Structured founder interview | founder_onboarding |
| `conduct_consultant_interview` | Multi-client interview | consultant_onboarding |
| `generate_client_brief` | Compile brief from interview | founder_onboarding / consultant_onboarding |

## Output

**Client Brief** containing:
- Business idea/hypothesis
- Target customer description
- Problem being solved
- Current stage
- Key assumptions
- Validation goals

## Implementation Files

```
src/startupai/crews/service/
├── config/
│   ├── agents.yaml           # 3 agent definitions
│   └── tasks.yaml            # 5 task definitions
└── service_crew.py           # Crew orchestration
```

## Test Coverage

```
tests/integration/
└── test_service_crew.py      # End-to-end onboarding tests
```

## Phase Delivered

- **Phase 1A:** Full intake workflow with founder/consultant paths

---
**Spec**: `docs/master-architecture/03-methodology.md`
**Last Updated**: 2026-01-07 (archived)
