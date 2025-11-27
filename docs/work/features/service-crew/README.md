# Service Crew Implementation

## Overview

The Service Crew handles customer intake and brief capture. Owned by Sage (CSO).

## Agents

1. **Customer Service Agent** - Lead qualification, routing
2. **Founder Onboarding Agent** - Structured interviews for founders
3. **Consultant Onboarding Agent** - Multi-client context for agencies

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
│   ├── agents.yaml
│   └── tasks.yaml
└── service_crew.py
```

## Status

**Implemented** - Phase 1A complete

---
**Spec**: `docs/master-architecture/03-validation-spec.md`
**Last Updated**: 2025-11-26
