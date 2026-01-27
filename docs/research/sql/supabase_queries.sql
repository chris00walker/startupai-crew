-- StartupAI Research Fellow: Supabase Query Pack
-- Purpose: Pull distributions and decision outcomes for calibration
-- Notes:
-- - Code uses validation_runs.id as run_id; if your DB uses validation_runs.run_id,
--   swap joins accordingly.

-- =========================================
-- Fit Score Distribution
-- =========================================
SELECT
  (phase_state->'fit_assessment'->>'fit_score')::int AS fit_score,
  COUNT(*) AS runs
FROM validation_runs
WHERE phase_state ? 'fit_assessment'
GROUP BY fit_score
ORDER BY fit_score;

-- =========================================
-- Fit Score vs HITL Decision (Phase 1)
-- =========================================
SELECT
  (vr.phase_state->'fit_assessment'->>'fit_score')::int AS fit_score,
  hr.decision,
  COUNT(*) AS decisions
FROM validation_runs vr
JOIN hitl_requests hr ON hr.run_id = vr.id
WHERE hr.checkpoint_name = 'approve_discovery_output'
GROUP BY fit_score, hr.decision
ORDER BY fit_score, hr.decision;

-- =========================================
-- Fit Score vs Final Decision
-- =========================================
SELECT
  (phase_state->'fit_assessment'->>'fit_score')::int AS fit_score,
  (phase_state->>'final_decision') AS final_decision,
  COUNT(*) AS runs
FROM validation_runs
WHERE phase_state ? 'fit_assessment'
GROUP BY fit_score, final_decision
ORDER BY fit_score, final_decision;

-- =========================================
-- Desirability Metrics Distribution
-- =========================================
SELECT
  (phase_state->'desirability_evidence'->>'problem_resonance')::float AS problem_resonance,
  (phase_state->'desirability_evidence'->>'zombie_ratio')::float AS zombie_ratio,
  COUNT(*) AS runs
FROM validation_runs
WHERE phase_state ? 'desirability_evidence'
GROUP BY problem_resonance, zombie_ratio
ORDER BY problem_resonance, zombie_ratio;

-- =========================================
-- Desirability Checkpoint Outcomes
-- =========================================
SELECT
  hr.checkpoint_name,
  hr.decision,
  COUNT(*) AS decisions
FROM hitl_requests hr
WHERE hr.phase = 2
GROUP BY hr.checkpoint_name, hr.decision
ORDER BY hr.checkpoint_name, hr.decision;

-- =========================================
-- Desirability Metrics vs Decision
-- =========================================
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

-- =========================================
-- Landing Page Conversion by Variant
-- =========================================
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

-- =========================================
-- Experiment Outcomes by Policy (Bandit Data)
-- =========================================
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

-- =========================================
-- Check if Bandit Data is Empty
-- =========================================
SELECT COUNT(*) AS total_rows FROM experiment_outcomes;
