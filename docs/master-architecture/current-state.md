# StartupAI Current State - Honest Assessment

This document provides an unvarnished view of what works, what's broken, and what doesn't exist across the three services.

## Status Summary

| Service | Overall Status | Completion |
|---------|---------------|------------|
| AI Founders Core (startupai-crew) | Core functional, tools limited | 85% core, 15% tools |
| Marketing Site (startupai.site) | Functional, static | 90% |
| Product App (app.startupai.site) | Partial, migration in progress | 65-70% |

---

## AI Founders Core (`startupai-crew`)

### What Works
- 6-agent workflow executes successfully
- LLM-based reasoning produces quality output
- CrewAI AMP deployment is live and accessible
- REST API (kickoff, status) responds correctly
- GitHub auto-deploy configured

**Deployment Details**:
- UUID: `b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b`
- Base URL: `https://startupai-b4d5c1dd-27e2-4163-b9fb-a18ca06ca-4f4192a6.crewai.com`

### What's Limited
- **Pure LLM-based**: No external tools (web search, data retrieval)
- **Token usage**: ~100K tokens per run (expensive)
- **No streaming**: Users wait without progress updates
- **No automated storage**: Results stay in CrewAI, not Supabase

### What Doesn't Exist
- Activity feed API for marketing site
- Webhook notifications
- Real-time progress events
- Automated result storage to Supabase

### Configuration Status
| Item | Status |
|------|--------|
| `config/agents.yaml` | Complete (6 agents) |
| `config/tasks.yaml` | Complete (6 tasks) |
| Environment vars | Set in CrewAI dashboard |
| Authentication | Bearer token working |

---

## Marketing Site (`startupai.site`)

### What Works
- Static export builds successfully
- Authentication flow to product app works
- Waitlist form (Formspree) collecting leads
- Navigation and content pages render
- SEO metadata in place

**Deployment Details**:
- Platform: Netlify
- Type: Static export (`next export`)

### What's Limited
- **No dynamic content**: Cannot show real-time agent activity
- **Aspirational docs**: Service contracts describe non-existent APIs
- **Plan parameter passing**: Works but untested end-to-end

### What Doesn't Exist
- Real-time activity feed display
- Public metrics dashboard
- Agent work transparency (the core value prop)

### Content Status
| Page | Status | Notes |
|------|--------|-------|
| Home | Complete | Hero, features, CTA |
| About | Complete | Team, mission |
| Pricing | Complete | Plan comparison |
| Beta | Complete | Waitlist signup |
| Contact | Complete | Contact form |

### Documentation Issues
- `docs/service-contracts/` describes APIs that don't exist
- `docs/specs/crewai-integration.md` has aspirational code examples
- References to non-existent Activity Feed API

---

## Product App (`app.startupai.site`)

### What Works
- Supabase authentication (GitHub OAuth)
- Database schema (12 migrations deployed)
- Onboarding chat with Vercel AI SDK
- Basic page structure (20 pages)
- Component library (50+ Shadcn components)

**Deployment Details**:
- Platform: Netlify (considering Vercel migration)
- Type: Server-side rendering

### What's Partial
- **Onboarding flow**: 7 stages implemented, quality varies
- **CrewAI integration**: API route exists, end-to-end untested
- **Dashboard**: Basic structure, missing analysis display
- **Evidence collection**: Schema exists, UI incomplete

### What Doesn't Exist
- Analysis results display (after CrewAI completes)
- Evidence management UI
- Gate scores visualization
- Export functionality
- User settings page

### Technical Debt
- **Router migration**: Mix of App Router and Pages Router
- **Type errors**: Some unresolved TypeScript issues
- **Missing tests**: Coverage < 20%
- **Dead references**: Points to non-existent marketing site docs

### Database Status
| Table | Schema | Data | UI |
|-------|--------|------|-----|
| users | Done | Working | Partial |
| projects | Done | Working | Partial |
| hypotheses | Done | Working | Missing |
| evidence | Done | Empty | Missing |
| onboarding_sessions | Done | Working | Working |
| entrepreneur_briefs | Done | Empty | Missing |
| gate_scores | Done | Empty | Missing |

---

## Cross-Service Integration

### Working Integrations
| From | To | Status |
|------|-----|--------|
| Marketing → Supabase Auth | Product callback | Working |
| Product → CrewAI API | Kickoff request | Implemented, untested E2E |
| Marketing → Product | Plan parameter | Working |

### Broken/Missing Integrations
| From | To | Status | Issue |
|------|-----|--------|-------|
| CrewAI → Supabase | Results storage | Missing | Results stay in CrewAI |
| Marketing ← CrewAI | Activity feed | Missing | API doesn't exist |
| Product ← CrewAI | Status polling | Implemented | No UI to display |

### Environment Variable Sync
| Variable | Marketing | Product | Crew |
|----------|-----------|---------|------|
| Supabase URL | Set | Set | N/A |
| Supabase Anon Key | Set | Set | N/A |
| Supabase Service Key | N/A | Set | N/A |
| OpenAI Key | N/A | Set | Set (dashboard) |
| CrewAI Bearer | N/A | Set | N/A |

---

## Critical Blockers

### 1. No End-to-End Analysis Flow
**Issue**: User completes onboarding → CrewAI runs → Results stored... where?

**Current state**: Results stay in CrewAI AMP, not in Supabase. No UI to retrieve and display them.

**Required**:
- API route to poll CrewAI status
- Background job or webhook to retrieve results
- Store results in `entrepreneur_briefs` or new table
- UI to display analysis results

### 2. Marketing Site Cannot Show Agent Activity
**Issue**: Core value proposition is transparency, but no transparency mechanism exists.

**Current state**: Marketing site is static, cannot fetch real-time data.

**Options**:
- Build activity feed API in crew
- Use serverless function on marketing site
- Embed from product app (iframe or microfrontend)

### 3. Documentation Mismatch
**Issue**: Docs describe features that don't exist, causing confusion.

**Required**:
- Archive aspirational docs
- Document only what's implemented
- Use validation backlog for hypotheses

---

## Recommended Next Steps

1. **Complete the E2E flow**: User → Onboarding → CrewAI → Results Display
2. **Archive aspirational docs**: Move to `docs/archive/`
3. **Decide on transparency mechanism**: How will marketing show agent work?
4. **Increase test coverage**: Product app needs E2E tests
5. **Resolve router migration**: Finish App Router migration in product app

---

## Last Updated
2025-11-20

This document should be updated whenever significant changes occur to any service.
