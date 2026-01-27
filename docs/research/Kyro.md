# StartupAI Research Fellow - Kyro Gibling

Focus: Three bounded research problems for mathematical calibration and decision theory

## Contents
1. Desirability Signal + Optimal Stopping
2. Fit Score as a Calibrated Decision Rule
3. Policy Bandit Calibration & Nonstationarity
4. Definition of Done (All Problems)
5. Working Agreement
6. SQL Query Appendix

---

# 1) Desirability Signal + Optimal Stopping

## Problem Statement
The system decides whether to pivot or proceed based on a small set of ad and landing‑page metrics. Today, it makes a single decision from raw rates without accounting for how much data was collected. We need a principled way to decide when there is enough evidence and what decision minimizes regret.

## Why It Matters
A bad call here wastes budget or sends founders down the wrong path. If the system pivots too early, it kills promising ideas; if it proceeds too early, it wastes engineering and money. Calibrated stopping can materially reduce false pivots and improve trust.

## Current State (with file references)
- Metrics & thresholds are defined in YAML and used verbatim:
  - `src/crews/desirability/config/growth_tasks.yaml`
- Decision logic is deterministic, with hard thresholds:
  - `src/modal_app/phases/phase_2.py`
- Status: AdPlatformTool (Meta/Google) is stubbed; integration work in progress.
- Experiment data handling has three distinct paths:
  - Real API data (no LLM):
    - `AnalyticsTool` (Netlify) performs live HTTP calls
    - `src/shared/tools/analytics_privacy.py`
  - Ad platform integrations are currently stubbed (even with tokens):
    - `AdPlatformTool` returns placeholder responses for Meta/Google
    - `src/shared/tools/analytics_privacy.py`
    - Note: implementation is in progress and expected soon
  - Placeholder outputs when tokens are not configured (no LLM):
    - Returns a clear “Configuration Required” response with zeroed metrics
    - `src/shared/tools/analytics_privacy.py`
  - Structured output tools for experiment design (LLM for templates, not metrics):
    - `TestCardTool`, `LearningCardTool` produce experiment plans and learning cards
    - `src/shared/tools/llm_tools.py`
- Landing page tracking (real events when deployed):
  - JS writes to `lp_pageviews` and `lp_submissions`
  - `src/shared/tools/landing_page_deploy.py`
- Fallback behavior: if GrowthCrew output is missing/unparseable, it uses hardcoded low‑signal defaults:
  - `src/crews/desirability/__init__.py`

## The Mathematical Challenge (formal but accessible)
You observe counts of impressions (I), clicks (C), signups (S). Current rules use:
```
p_res = (C + S) / I
p_zom = (C - S) / C
```
and compare to fixed thresholds.

The challenge: decide when to stop collecting data and which action (proceed, value pivot, segment pivot) minimizes expected regret. This is a sequential decision problem with uncertainty and budget cost.

## Available Data (for calibration)
- Phase 2 metrics stored in `validation_runs.phase_state` and `hitl_requests.context` (Supabase).
- Landing‑page events in `lp_pageviews` and `lp_submissions` (Supabase), if tracking is deployed.
- Ad metrics from external APIs if configured.
- HITL decisions in `hitl_requests` (approved / iterate / override_proceed / segment_* / custom_segment / rejected).

What’s missing:
- A consistent record of raw counts (I/C/S) per run and time.
- A sample size field in Phase 2 outputs.

## Data Integrity Note
- Tool‑sourced metrics are only guaranteed for Netlify analytics today.
- Ad platform metrics are currently placeholder/stubbed until the Meta/Google SDK integrations land.
- LLM agents can still synthesize metrics in their outputs if tools are not invoked; treat those as unverified.

## Suggested Approach (week-by-week)
Week 1:
- Map all paths by which metrics are created (API vs LP tables vs fallback).
- Query production data (if access available) to see distributions of impressions/clicks/signups and how often HITL overrides happen.
- Identify minimum viable metrics to trust.

Week 2:
- Build a Bayesian model (beta-binomial) for p_res and p_zom.
- Define a simple stopping rule (e.g., posterior probability of exceeding threshold).
- Draft decision rule with asymmetric costs.

Week 3:
- Simulate decision quality under different stopping rules.
- Compare false pivot vs false proceed tradeoffs.

Week 4:
- Propose integration: replace hard thresholds with posterior probabilities + stopping rule.
- Provide pseudocode + calibration checklist.

## Success Criteria
- A formal decision rule that uses uncertainty (not just point estimates).
- A recommended stopping condition (e.g., “Stop when P(p_res ≥ 0.3) ≥ 0.9 or budget exhausted”).
- Pseudocode + parameter defaults that can be implemented with existing metrics.

## First Steps (week 1)
Read:
- `src/crews/desirability/config/growth_tasks.yaml`
- `src/modal_app/phases/phase_2.py`
- `src/crews/desirability/__init__.py`
- `src/shared/tools/landing_page_deploy.py`
- `src/shared/tools/analytics_privacy.py`

If production access exists, pull:
- `validation_runs.phase_state`
- `hitl_requests.context`
- `lp_pageviews`, `lp_submissions`

---

# 2) Fit Score as a Calibrated Decision Rule

## Problem Statement
The system computes a “fit score” in Phase 1 from a set of LLM‑generated inputs (jobs/pains/gains/WTP). This score decides whether the startup proceeds to costly validation. The current formula is a fixed weighted sum with hard thresholds. We need a calibrated score that correlates with real outcomes.

## Why It Matters
Fit gating is the earliest major fork. If the score is too strict, founders churn; if too lenient, the system wastes time and money downstream. A calibrated decision rule improves trust and allocates resources better.

## Current State (with file references)
- Fit score formula and thresholds are defined in YAML:
  - `src/crews/discovery/config/fit_assessment_tasks.yaml`
- Crew that executes it:
  - `src/crews/discovery/fit_assessment_crew.py`
- Gate enforcement in Phase 1:
  - `src/modal_app/phases/phase_1.py`
- Fit score used later in synthesis (Phase 4):
  - `src/modal_app/phases/phase_4.py`

Known inconsistency:
- HITL options include “segment_pivot” but `/hitl/approve` does not accept that decision.
  - Options in `src/modal_app/phases/phase_1.py`
  - Allowed decisions in `src/modal_app/app.py`

## The Mathematical Challenge (formal but accessible)
Let E = {J, P, G, W} be evidence scores for Jobs, Pains, Gains, WTP. We need a calibrated estimator f(E) that outputs a probability of true fit, and a decision rule:
```
a* = argmin_a  E[L(a, F) | E]
```
where a is proceed / iterate / pivot and F is latent “true fit.”

## Available Data (for calibration)
- Fit scores and related metrics stored in `validation_runs.phase_state` after Phase 1.
- HITL decisions in `hitl_requests` (approved / iterate / rejected).
- Final decisions in Phase 4 (`final_decision` in phase state).

What’s missing:
- Ground‑truth labels tied directly to Phase 1 decisions (e.g., later success/failure).
- Explicit storage of fit routing decision (SEGMENT_PIVOT vs ITERATE_*).

## Suggested Approach (week-by-week)
Week 1:
- Extract sample of Phase 1 runs and their fit scores + HITL decisions.
- Quantify how often humans override (approve when score low, or iterate when high).

Week 2:
- Model P(proceed success | fit score) using a simple calibration curve.
- Propose a Bayesian or logistic calibration (monotonic).

Week 3:
- Derive decision thresholds that minimize expected regret (cost of false proceed vs false pivot).
- Simulate outcomes under different thresholds.

Week 4:
- Propose updated scoring rule + thresholds with supporting plots/pseudocode.

## Success Criteria
- A monotonic calibrated model mapping fit_score → probability of eventual success.
- A revised decision rule (e.g., proceed if P(success) ≥ 0.8).
- Clear evidence that thresholds improve decision quality on historical data.

## First Steps (week 1)
Read:
- `src/crews/discovery/config/fit_assessment_tasks.yaml`
- `src/crews/discovery/fit_assessment_crew.py`
- `src/modal_app/phases/phase_1.py`

If production access exists, query:
- `validation_runs.phase_state` (fit_score)
- `hitl_requests` (decisions)
- Final outcomes in `phase_state`

---

# 3) Policy Bandit Calibration & Nonstationarity

## Problem Statement
A policy bandit was designed to choose between experiment configuration policies (e.g., YAML baseline vs retrieval‑augmented). The database schema exists, but current runtime code does not appear to use it. We need to confirm usage and propose a policy that adapts to changing conditions.

## Why It Matters
If policy selection is wrong or stale, experiment results degrade and the system learns the wrong thing. If it’s unused, there’s untapped leverage in making experiments adapt based on evidence.

## Current State (with file references)
- Bandit schema and UCB function live in migrations:
  - `db/migrations/004_experiment_outcomes.sql`
- Policy tracking in learnings table:
  - `db/migrations/005_add_policy_version_to_learnings.sql`
- Bandit + resolver implementation exists only in archive:
  - `archive/flow-architecture/startupai/tools/policy_bandit.py`
  - `archive/flow-architecture/startupai/tools/experiment_config_resolver.py`
- No active usage detected in current `src/` code.

## The Mathematical Challenge (formal but accessible)
Select policy a_t that maximizes expected reward r_t (e.g., conversion rate), while rewards drift over time. A contextual or time‑decayed bandit is required:
```
a_t = argmax_a (mu_hat_a(t) + bonus_a(t))
```
but mu_hat_a(t) should discount stale data or adapt to changes.

## Available Data (for calibration)
- `experiment_outcomes` table (if populated in production).
- `learnings` table with policy_version and experiment_id (if connected).

What’s missing:
- Evidence of any writes to `experiment_outcomes` from current runtime.
- Clear reward definitions used consistently across experiment types.

## Suggested Approach (week-by-week)
Week 1:
- Confirm if bandit is in production (search services for writes to `experiment_outcomes`).
- If unused, document why and whether it should be revived.

Week 2:
- Define reward signals and context features (experiment type, channel, audience).
- Propose a baseline UCB/Thompson model with time‑decay.

Week 3:
- Plan offline evaluation (IPS/DR) using historical data.
- Compare static vs decayed policies in simulation.

Week 4:
- Deliver a policy selection spec + integration plan (which services must write outcomes).

## Success Criteria
- A clear answer on whether bandit should be active.
- A formal policy definition + calibration method if it is revived.
- A data pipeline proposal to populate `experiment_outcomes`.

## First Steps (week 1)
Read:
- `db/migrations/004_experiment_outcomes.sql`
- `archive/flow-architecture/startupai/tools/policy_bandit.py`
- `archive/flow-architecture/startupai/tools/experiment_config_resolver.py`

Search current services for any `experiment_outcomes` writes (none in `src/`).

---

# Definition of Done (All Problems)
A problem is complete when you deliver:
- [ ] 1–2 page mathematical specification
- [ ] Pseudocode implementable in Python
- [ ] Calibration requirements (data needed, sample sizes)
- [ ] Recommended parameter defaults
- [ ] Brief risk analysis (what happens if we get this wrong)

---

# Working Agreement
- Weekly sync: 30 min to present progress + get feedback
- Deliverables go in `docs/research/[problem-name]/`
- You own the math; Chris owns implementation priority
- “Good enough to ship” beats “perfect but stalled”

---

# SQL Query Appendix (Supabase)
Note: Code uses `validation_runs.id` as the run identifier and joins to `hitl_requests.run_id`. If your DB uses `validation_runs.run_id` instead, swap joins accordingly. The same queries are available in `docs/research/sql/supabase_queries.sql`.

## Fit Score Distribution
```sql
SELECT
  (phase_state->'fit_assessment'->>'fit_score')::int AS fit_score,
  COUNT(*) AS runs
FROM validation_runs
WHERE phase_state ? 'fit_assessment'
GROUP BY fit_score
ORDER BY fit_score;
```

## Fit Score vs HITL Decision (Phase 1)
```sql
SELECT
  (vr.phase_state->'fit_assessment'->>'fit_score')::int AS fit_score,
  hr.decision,
  COUNT(*) AS decisions
FROM validation_runs vr
JOIN hitl_requests hr ON hr.run_id = vr.id
WHERE hr.checkpoint_name = 'approve_discovery_output'
GROUP BY fit_score, hr.decision
ORDER BY fit_score, hr.decision;
```

## Fit Score vs Final Decision
```sql
SELECT
  (phase_state->'fit_assessment'->>'fit_score')::int AS fit_score,
  (phase_state->>'final_decision') AS final_decision,
  COUNT(*) AS runs
FROM validation_runs
WHERE phase_state ? 'fit_assessment'
GROUP BY fit_score, final_decision
ORDER BY fit_score, final_decision;
```

## Desirability Metrics Distribution
```sql
SELECT
  (phase_state->'desirability_evidence'->>'problem_resonance')::float AS problem_resonance,
  (phase_state->'desirability_evidence'->>'zombie_ratio')::float AS zombie_ratio,
  COUNT(*) AS runs
FROM validation_runs
WHERE phase_state ? 'desirability_evidence'
GROUP BY problem_resonance, zombie_ratio
ORDER BY problem_resonance, zombie_ratio;
```

## Desirability Checkpoint Outcomes
```sql
SELECT
  hr.checkpoint_name,
  hr.decision,
  COUNT(*) AS decisions
FROM hitl_requests hr
WHERE hr.phase = 2
GROUP BY hr.checkpoint_name, hr.decision
ORDER BY hr.checkpoint_name, hr.decision;
```

## Desirability Metrics vs Decision
```sql
SELECT
  (vr.phase_state->'desirability_evidence'->>'problem_resonance')::float AS problem_resonance,
  (vr.phase_state->'desirability_evidence'->>'zombie_ratio')::float AS zombie_ratio,
  hr.decision,
  COUNT(*) AS decisions
FROM validation_runs vr
JOIN hitl_requests hr ON hr.run_id = vr.id
WHERE hr.phase = 2
GROUP BY problem_resonance, zombie_ratio, hr.decision
ORDER BY problem_resonance, zombie_ratio, hr.decision;
```

## Landing Page Conversion by Variant
```sql
SELECT
  lpv.variant_id,
  COUNT(*) AS pageviews,
  COALESCE(ls.submissions, 0) AS submissions,
  COALESCE(ls.submissions, 0)::float / NULLIF(COUNT(*), 0) AS conversion_rate
FROM lp_pageviews lpv
LEFT JOIN (
  SELECT variant_id, COUNT(*) AS submissions
  FROM lp_submissions
  GROUP BY variant_id
) ls ON ls.variant_id = lpv.variant_id
GROUP BY lpv.variant_id, ls.submissions
ORDER BY conversion_rate DESC;
```

## Experiment Outcomes by Policy (Bandit Data)
```sql
SELECT
  experiment_type,
  policy_version,
  COUNT(*) AS n,
  AVG(primary_value) AS avg_reward,
  STDDEV(primary_value) AS sd_reward
FROM experiment_outcomes
WHERE status = 'completed'
GROUP BY experiment_type, policy_version
ORDER BY experiment_type, policy_version;
```

## Check if Bandit Data is Empty
```sql
SELECT COUNT(*) AS total_rows FROM experiment_outcomes;
```
