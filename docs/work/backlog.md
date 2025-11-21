# StartupAI Validation Backlog

This is not a feature list. It's a queue of **hypotheses to validate** using lean startup methodology: Build → Measure → Learn.

## How to Use This Document

1. **Pick a hypothesis** based on what you need to learn next
2. **Build the minimum** required to test it
3. **Measure the outcome** with real users
4. **Learn and decide**: Pivot or persevere
5. **Update this document** with learnings

---

## Priority 0: Flows Architecture Rebuild

> **CURRENT FOCUS**: Rebuild from 6-agent workflow to 8-crew/18-agent Flows architecture

### Hypothesis: Multi-Crew System Enables Scale

> **If** we structure validation as 8 specialized crews with 18 agents using CrewAI Flows,
> **Then** we can deliver higher quality analysis with clear accountability and extensibility.

**Build**:
- Phase 1: Service Crew, Analysis Crew, Governance Crew (QA)
- Phase 2: Build Crew, Growth Crew, Synthesis Crew
- Phase 3: Finance Crew, Enhanced Governance Crew

**Measure**:
- Output quality vs current 6-agent system
- Time to complete validation cycle
- Ability to extend with new crews/agents

**Learn**:
- Does crew specialization improve output?
- Is the Service/Commercial model effective?
- Where are the bottlenecks?

**Minimum Build** (Phase 1):
```
[ ] state_schemas.py - ValidationState, ClientBrief, CustomerProfile
[ ] Service Crew - 3 agents (intake, brief capture)
[ ] Analysis Crew - 2 agents (customer research, competitor analysis)
[ ] Governance Crew - 1 agent (QA validation)
[ ] Phase 1 Flow - orchestrate with @listen/@router
```

**Status**: IN PROGRESS - See `in-progress.md` for detailed task tracking

---

### Hypothesis: Tools Improve Analysis Quality

> **If** we add web search, analytics, and report tools to agents,
> **Then** analysis quality will significantly improve beyond pure LLM reasoning.

**Build**:
- `tools/web_search.py` - market research capability
- `tools/analytics.py` - data processing
- `tools/report_generator.py` - structured outputs

**Measure**:
- Quality score comparison (with/without tools)
- Factual accuracy
- Token efficiency

**Learn**:
- Which tools provide most value?
- Is real-time data necessary or is LLM knowledge sufficient?

**Status**: NOT STARTED - See `docs/tools/README.md` for specifications

---

### Hypothesis: HITL Approvals Prevent Bad Outcomes

> **If** we require human approval for high-risk actions (spend, campaigns, gates),
> **Then** users will trust the system with more autonomous operation.

**Build**:
- 6 approval checkpoint types per `reference/approval-workflows.md`
- Webhook notification system
- Resume API for continuing flows

**Measure**:
- Approval latency
- Override rate (how often users change AI recommendations)
- Trust scores

**Learn**:
- Which approvals are always accepted (can be automated)?
- What information do users need to approve confidently?

**Status**: NOT STARTED - Requires Phase 1 completion

---

## Priority 1: Core Value Delivery

### Hypothesis: Users Complete Analysis

> **If** we provide an end-to-end flow from onboarding to analysis results display,
> **Then** users will complete the full analysis and find value in the output.

**Build**:
- Poll CrewAI status from product app
- Store results in Supabase when complete
- Display results in dashboard

**Measure**:
- Completion rate: % of users who view results
- Time to completion: How long do they wait?
- Return rate: Do they come back?

**Learn**:
- Is the analysis output valuable?
- Is the wait time acceptable?
- What do users do with the results?

**Minimum Build**:
```
[ ] API route to poll CrewAI /status
[ ] Background job or webhook handler
[ ] Store in entrepreneur_briefs table
[ ] Basic results display page
```

**Status**: NOT STARTED - This is the critical blocker

---

### Hypothesis: Quality Output Drives Referrals

> **If** the analysis quality matches Fortune 500 consulting,
> **Then** users will refer other founders.

**Build**:
- Complete the E2E flow first (above hypothesis)
- Add NPS survey after results delivery
- Track referral source

**Measure**:
- NPS score
- Referral rate
- Organic signup source

**Learn**:
- Is "Fortune 500 quality" the right positioning?
- What specific outputs are most valued?
- What's missing from the analysis?

**Status**: BLOCKED by E2E flow

---

## Priority 2: User Acquisition

### Hypothesis: Transparency Increases Trust

> **If** we show real-time agent activity on the marketing site,
> **Then** visitors will trust the AI and convert to signup.

**Build**:
- Activity feed API in crew repo
- Display component on marketing site
- Show agent names, current tasks, recent completions

**Measure**:
- Conversion rate: visitors → signups
- Time on page: marketing site
- A/B test: with activity feed vs without

**Learn**:
- Does transparency drive conversion?
- Is real-time important, or is "recent activity" enough?
- Which agent activities are most compelling?

**Minimum Build**:
```
[ ] GET /activity endpoint in CrewAI
[ ] Serverless function on marketing site
[ ] Activity feed component
[ ] A/B test framework
```

**Status**: NOT STARTED

---

### Hypothesis: Public Metrics Build Credibility

> **If** we display aggregate metrics (analyses completed, satisfaction scores),
> **Then** visitors will trust the platform.

**Build**:
- Metrics API endpoint
- Public metrics component
- Auto-updating counters

**Measure**:
- Conversion rate impact
- Credibility perception (survey)

**Learn**:
- Do metrics matter to our audience?
- Which metrics are most compelling?
- Is there a threshold where metrics become meaningful?

**Status**: NOT STARTED - Requires completed analyses to have data

---

## Priority 3: User Retention

### Hypothesis: Iterative Analysis Increases Retention

> **If** users can re-run analysis after making changes,
> **Then** they will continue using the platform.

**Build**:
- Edit entrepreneur brief
- Re-run analysis button
- Version history of analyses

**Measure**:
- Re-run rate
- Retention at 30/60/90 days
- Feature usage

**Learn**:
- Do users want to iterate?
- What triggers a re-run?
- How often do they pivot?

**Status**: NOT STARTED - Requires E2E flow first

---

### Hypothesis: Evidence Collection Proves Value

> **If** users can upload and tag validation evidence,
> **Then** they will perceive ongoing value and continue using the platform.

**Build**:
- Evidence upload UI
- Tagging system
- Link evidence to hypotheses

**Measure**:
- Evidence upload rate
- Retention correlation
- Feature engagement

**Learn**:
- Do users actually collect evidence?
- Is manual upload too much friction?
- What types of evidence do they collect?

**Status**: Schema exists, UI missing

---

## Priority 4: Monetization

### Hypothesis: Tiered Pricing Captures Value

> **If** we offer trial → paid tiers with clear value differences,
> **Then** users will upgrade when they hit tier limits.

**Build**:
- Tier limits enforcement
- Upgrade prompts
- Payment integration

**Measure**:
- Trial → paid conversion
- Revenue per user
- Churn rate by tier

**Learn**:
- What limits trigger upgrades?
- Is the pricing right?
- Which tier is most popular?

**Status**: Pricing defined, enforcement not built

---

## Deprioritized (Revisit Later)

### Real-time Streaming

> Users want to watch analysis happen step-by-step.

**Why deprioritized**: Unclear if this is actually wanted. Validate core value first.

### Advanced Market Data APIs

> Bloomberg, Crunchbase, etc. for competitive intelligence.

**Why deprioritized**: Start with web search tool, add expensive APIs only if needed.

---

## Learnings Log

Document what you learn from each validation:

| Date | Hypothesis | Outcome | Learning | Decision |
|------|------------|---------|----------|----------|
| | | | | |

---

## Decision Framework

When choosing what to validate next, ask:

1. **What's the riskiest assumption?** Start there.
2. **What blocks other work?** Unblock it.
3. **What can we learn fastest?** Minimize build time.
4. **What has the biggest impact if true?** Maximize learning value.

Currently, **Priority 1: E2E Analysis Flow** is the answer to all four questions:
- Riskiest: Will users find value in the output?
- Blocking: All other hypotheses require completed analyses
- Fastest: Core infrastructure already exists
- Biggest impact: Validates entire product thesis

---

## Last Updated
2025-11-21
