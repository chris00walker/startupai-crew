---
title: Dogfooding Methodology
status: active
created: 2026-01-12
updated: 2026-01-20
purpose: Testing methodology using StartupAI as its own first customer
---

# Dogfooding Methodology

## The Foundational Principle

> **"If StartupAI can't validate itself, it won't work for anyone else."**

StartupAI must be its own first and most demanding customer. All planning, development, and testing uses real StartupAI accounts exercising the product as real users would.

## Validation-Driven Dogfooding

Dogfooding serves two purposes:
1. **Quality Testing** - Catch bugs and friction before customers do
2. **Assumption Testing** - Collect evidence for our 8 key assumptions

Every dogfooding session should ask: **"What assumption did we just test?"**

See [Product App Validation Docs](../../app.startupai.site/docs/validation/) for:
- [startupai-brief.md](../../app.startupai.site/docs/validation/startupai-brief.md) - StartupAI's own Founder's Brief
- [assumptions.md](../../app.startupai.site/docs/validation/assumptions.md) - 8 key assumptions
- [evidence-tracker.md](../../app.startupai.site/docs/validation/evidence-tracker.md) - Evidence state

## Why Dogfooding

1. **Real Data Testing** - No mock data. VPCs, experiments, and validation results are for StartupAI itself.
2. **User Empathy** - Experiencing the product as users do reveals friction points.
3. **Quality Assurance** - If it breaks for us, it would break for customers.
4. **Continuous Validation** - We validate our own validation methodology.
5. **Evidence Collection** - Every checkpoint tests an assumption.

## Test Accounts

### Founder Account
| Field | Value |
|-------|-------|
| Email | chris00walker@proton.me |
| Password | W7txYdr7bV0Tc30U0bv& |
| Role | Founder |
| Project | StartupAI |
| Purpose | Tests the full founder validation journey (Phase 0-4) |

### Consultant Account
| Field | Value |
|-------|-------|
| Email | chris00walker@gmail.com |
| Password | Test123! |
| Role | Consultant |
| Client | StartupAI |
| Purpose | Tests advisor features and client management |

## Testing Requirements

### Before Any Release
1. **Founder Journey** (chris00walker@proton.me)
   - [ ] Complete Quick Start with StartupAI business description
   - [ ] Approve Phase 1 Brief (approve_brief checkpoint)
   - [ ] Review and approve Phase 1 VPC (approve_discovery_output checkpoint)
   - [ ] View Phase 2 landing page generation
   - [ ] Approve all HITL checkpoints in the path

2. **Consultant Journey** (chris00walker@gmail.com)
   - [ ] View client (StartupAI) validation progress
   - [ ] Access client evidence and reports
   - [ ] Test advisor-specific features

3. **Evidence Quality**
   - [ ] VPC fit score is realistic (not 100% or 0%)
   - [ ] Customer profile reflects real founder pain points
   - [ ] Generated landing pages have real content (no placeholders)

### Phase-by-Phase Testing

| Phase | Founder Actions | Expected Outcomes | Assumption Tested |
|-------|-----------------|-------------------|-------------------|
| 0 - Onboarding | Complete Quick Start | Founder's Brief generated | A2, A3 |
| 1 - VPC Discovery | Approve VPC | Fit score ≥70, real customer insights | A1, A3 |
| 2 - Desirability | View experiments | Landing page deployed, not placeholder | A5 |
| 3 - Feasibility | Review build assessment | Technical feasibility signal | A3 |
| 4 - Viability | Final decision | Clear proceed/pivot recommendation | A3 |

### Evidence Collection at Each Checkpoint

| HITL Checkpoint | Assumption | Evidence to Record |
|-----------------|------------|-------------------|
| `approve_brief` | A1, A3 | Did user approve? What was edited? |
| `approve_discovery_output` | A1, A3 | Did user approve? Fit score accepted? |
| `approve_landing_page` | A1, A5 | Landing page resonance, edits made |
| `approve_experiment_design` | A1 | Experiment approved without changes? |
| `approve_feasibility` | A1, A3 | Technical assessment accepted? |
| `approve_viability` | A1 | Final recommendation trusted? |

**After each dogfooding session**, update:
- [evidence-tracker.md](../../app.startupai.site/docs/validation/evidence-tracker.md)
- Sample size (n) for relevant assumptions
- Qualitative notes on friction or trust signals

## Integration with Development

### Workflow
```
1. Write code
2. Test with Founder account (chris00walker@proton.me)
3. If broken → fix wherever the issue is (frontend, backend, database)
4. Test with Consultant account (chris00walker@gmail.com) if relevant
5. Only then → consider code review / PR
```

### Debug Strategy
When something breaks during dogfooding:
- **Frontend issue** → Fix in app.startupai.site
- **Backend issue** → Fix in startupai-crew
- **Data issue** → Fix in Supabase (migrations, RLS, data)
- **Integration issue** → Trace the full path, fix at the source

## What We're Building For

StartupAI is:
- **Business Idea**: AI-powered startup validation platform
- **Problem**: Founders waste months building products nobody wants
- **Customer**: Pre-seed/seed founders who need structured validation
- **Solution**: 6 AI Founders running Fortune 500 validation methodology

When testing, use this exact context. The VPC, customer profile, and experiments should reflect this reality.

## Cross-References

- Backend memory: `startupai-crew/CLAUDE.md` → Dogfooding Methodology section
- Frontend memory: `app.startupai.site/CLAUDE.md` → Dogfooding Methodology section
- Testing docs: `startupai-crew/docs/testing/testing.md`
- Master architecture: `startupai-crew/docs/master-architecture/`
- **Validation docs**: `app.startupai.site/docs/validation/` → Self-validation methodology
  - `startupai-brief.md` - StartupAI's own Founder's Brief
  - `assumptions.md` - 8 key assumptions with test cards
  - `evidence-tracker.md` - Evidence state and log
  - `roadmap.md` - Validation-driven feature roadmap

---

**Last Updated**: 2026-01-20
**Maintainer**: Chris Walker
