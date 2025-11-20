# StartupAI Validation Backlog

This is not a feature list. It's a queue of **hypotheses to validate** using lean startup methodology: Build → Measure → Learn.

## How to Use This Document

1. **Pick a hypothesis** based on what you need to learn next
2. **Build the minimum** required to test it
3. **Measure the outcome** with real users
4. **Learn and decide**: Pivot or persevere
5. **Update this document** with learnings

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

### Multi-crew System

> Different workflows for different use cases.

**Why deprioritized**: Need to prove single workflow works first.

### Custom Tools

> Web search, market data APIs for better analysis.

**Why deprioritized**: Pure LLM analysis may be sufficient. Validate quality first.

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
2025-11-20
