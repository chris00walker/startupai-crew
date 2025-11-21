---
purpose: "Private technical source of truth for active work"
status: "active"
last_reviewed: "2025-11-21"
---

# In Progress

## Phase 1: Service Side + Desirability Validation

The following items are actively being worked on. See `phases.md` for complete criteria.

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| State schemas (`state_schemas.py`) | Not Started | @ai-platform | ValidationState, ClientBrief, CustomerProfile, CompetitorReport |
| Service Crew (3 agents) | Not Started | @ai-platform | Customer Service, Founder Onboarding, Consultant Onboarding |
| Analysis Crew (2 agents) | Not Started | @ai-platform | Customer Researcher, Competitor Analyst |
| Governance Crew Phase 1 | Not Started | @ai-platform | QA Agent only |
| Phase 1 Flow orchestration | Not Started | @ai-platform | Wire crews with @listen and @router |
| Test with StartupAI context | Blocked | @ai-platform | Requires crews to be built |

### Immediate Next Step

**Create state schemas** - This unblocks all crew development.

```python
# src/startupai/flows/state_schemas.py
class ValidationState(BaseModel):
    id: str
    brief: ClientBrief
    customer_profiles: List[CustomerProfile] = []
    competitor_analysis: CompetitorReport = None
    qa_status: str = "pending"
```

### What This Unblocks (Downstream)

Completing Phase 1 unblocks:
- **Product App**: Results display UI, AI visibility in dashboards
- **Marketing Site**: Activity Feed API, Trust Metrics API, validation cycles

---

## Documentation / Infrastructure

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Docs reorganization | Complete | @ai-platform | See done.md |
| Work tracking sync | In Progress | @ai-platform | This update |

---

## How to Use This Document

1. **Pick an item** from the table above
2. **Update status** when you start work
3. **Move to done.md** when complete
4. **Update phases.md** checkboxes to match

---
**Last Updated**: 2025-11-21
