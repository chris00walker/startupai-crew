# Database Schema Audit Report

**Repository**: `/home/chris/projects/app.startupai.site`
**Date**: 2026-01-06
**Auditor**: Sub-Agent 1 (Backend Developer)

---

## Executive Summary

- **Total Tables Found**: 23 tables across 35 migration files
- **Drizzle Schema Files**: 10 TypeScript schema definitions
- **Schema-Migration Alignment**: PARTIAL - Several tables missing from Drizzle schemas

### Critical Findings

1. **Missing Drizzle Schemas**: 10+ tables exist in migrations but have NO Drizzle TypeScript definitions
2. **Onboarding Tables**: `onboarding_sessions` and `entrepreneur_briefs` exist but not in Drizzle
3. **Flywheel System**: 4 tables (`learnings`, `patterns`, `outcomes`, `domain_expertise`) missing from Drizzle
4. **Approval System**: 3 approval-related tables missing from Drizzle
5. **PHANTOM Tables**: `value_proposition_canvas`, `business_model_canvas`, `crewai_validation_states`, `learning_cards` have Drizzle schemas but NO migrations

---

## Tables Inventory

| # | Table Name | Migration File | Drizzle Schema | Status |
|---|------------|----------------|----------------|--------|
| 1 | `user_profiles` | 00001_initial_schema.sql | users.ts | SYNCED |
| 2 | `projects` | 00001_initial_schema.sql | projects.ts | SYNCED |
| 3 | `hypotheses` | 00001_initial_schema.sql | hypotheses.ts | SYNCED |
| 4 | `evidence` | 00001_initial_schema.sql | evidence.ts | SYNCED |
| 5 | `experiments` | 00001_initial_schema.sql | experiments.ts | PARTIAL |
| 6 | `reports` | 00001_initial_schema.sql | reports.ts | PARTIAL |
| 7 | `gate_policies` | 00001_initial_schema.sql | MISSING | ORPHANED |
| 8 | `override_requests` | 00001_initial_schema.sql | MISSING | ORPHANED |
| 9 | `audit_log` | 00001_initial_schema.sql | MISSING | ORPHANED |
| 10 | `trial_usage_counters` | 00007_trial_usage_counters.sql | usage-quota.ts | SYNCED |
| 11 | `onboarding_sessions` | 00009_onboarding_schema.sql | MISSING | ORPHANED |
| 12 | `entrepreneur_briefs` | 00009_onboarding_schema.sql | MISSING | ORPHANED |
| 13 | `consultant_profiles` | 00011_consultant_profiles.sql | MISSING | ORPHANED |
| 14 | `consultant_onboarding_sessions` | 00012 | MISSING | ORPHANED |
| 15 | `assistant_conversations` | 00013 | MISSING | ORPHANED |
| 16 | `learnings` | 20251126000001_flywheel_learning.sql | MISSING | ORPHANED |
| 17 | `patterns` | 20251126000001_flywheel_learning.sql | MISSING | ORPHANED |
| 18 | `outcomes` | 20251126000001_flywheel_learning.sql | MISSING | ORPHANED |
| 19 | `domain_expertise` | 20251126000001_flywheel_learning.sql | MISSING | ORPHANED |
| 20 | `approval_requests` | 20251126000002_approval_requests.sql | MISSING | ORPHANED |
| 21 | `approval_preferences` | 20251126000002_approval_requests.sql | MISSING | ORPHANED |
| 22 | `approval_history` | 20251126000002_approval_requests.sql | MISSING | ORPHANED |
| 23 | `public_activity_log` | 20251130000001 | public-activity-log.ts | SYNCED |

### PHANTOM Tables (Drizzle exists, NO migration)

| Table | Drizzle File | Columns | Notes |
|-------|--------------|---------|-------|
| `value_proposition_canvas` | value-proposition-canvas.ts | 67+ | Core VPC feature |
| `business_model_canvas` | business-model-canvas.ts | 15+ | Core BMC feature |
| `crewai_validation_states` | crewai-validation-states.ts | 67 | Full validation state |
| `learning_cards` | experiments.ts | 9 | Strategyzer learning cards |

---

## Key Table Details

### `entrepreneur_briefs` (29 columns)

**Created in**: `00009_onboarding_schema.sql`
**Drizzle Schema**: MISSING

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| session_id | VARCHAR(255) | FK to onboarding_sessions |
| user_id | UUID | FK to auth.users |
| customer_segments | JSONB | Stage 2 data |
| primary_customer_segment | JSONB | |
| problem_description | TEXT | Stage 3 data |
| problem_pain_level | INTEGER | 1-10 |
| solution_description | TEXT | Stage 4 data |
| unique_value_proposition | TEXT | |
| competitors | JSONB | Stage 5 data |
| budget_range | VARCHAR(100) | Stage 6 data |
| three_month_goals | JSONB | Stage 7 data |
| completeness_score | INTEGER | 0-100 |
| overall_quality_score | INTEGER | 0-100 |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### `approval_requests` (22 columns)

**Created in**: `20251126000002_approval_requests.sql`
**Drizzle Schema**: MISSING

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| execution_id | TEXT | CrewAI execution ID |
| task_id | TEXT | CrewAI task ID |
| user_id | UUID | FK to auth.users |
| approval_type | TEXT | segment_pivot, spend_increase, etc. |
| owner_role | TEXT | compass, ledger, pulse, etc. |
| title | TEXT | |
| description | TEXT | |
| task_output | JSONB | AI analysis |
| options | JSONB | Available choices |
| status | TEXT | pending, approved, rejected |
| decision | TEXT | Chosen option |
| human_feedback | TEXT | User reasoning |
| decided_at | TIMESTAMPTZ | |
| expires_at | TIMESTAMPTZ | 48 hours default |

---

## Special Focus Answers

### Does `entrepreneur_briefs` table exist?
**YES** - Created in `00009_onboarding_schema.sql` with 29 columns.
**Issue**: No Drizzle schema for type-safe queries.

### Does `founders_briefs` table exist?
**NO** - This is specified in 05-spec but not created.

### What tables relate to VPC?
1. `value_proposition_canvas` - PHANTOM (schema only)
2. `entrepreneur_briefs` - stores customer segments, problem/solution
3. `crewai_validation_states` - PHANTOM (would store VPC state)

### What tables store CrewAI data?
1. `crewai_validation_states` - PHANTOM
2. `approval_requests` - EXISTS (execution_id, kickoff_id)
3. `public_activity_log` - EXISTS (kickoff_id)
4. `reports` - EXISTS (stores report content)

---

## Recommendations

### Priority 1: Create Missing Drizzle Schemas

- `entrepreneur_briefs` (29 columns)
- `approval_requests` (22 columns)
- `onboarding_sessions` (20 columns)
- Flywheel tables (4 tables)

### Priority 2: Create Migrations for Phantom Tables

- `value_proposition_canvas`
- `business_model_canvas`
- `crewai_validation_states`
- `learning_cards`

### Priority 3: Fix Schema Mismatches

- `experiments` - Drizzle has extra columns not in DB
- `reports` - Column name/type mismatches
