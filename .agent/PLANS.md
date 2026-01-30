# ExecPlans

ExecPlans are short, living implementation plans used for complex work.

## When to use
Required for:
- Complex features with multiple moving parts
- Cross-layer integrations (UI/API/DB or service-to-service)
- Significant refactors or migrations

Optional for medium tasks; skip for small fixes and single-file edits.

## Format
Create a new section per plan at the top of this file.

### ExecPlan: <title> (YYYY-MM-DD)
- Objective:
- Non-goals:
- Constraints/assumptions:
- Risks/unknowns:
- Milestones:
  1. ...
  2. ...
- Validation:
  - Commands/tests/manual checks

## Repo Validation Defaults
Use these as a baseline; add or remove based on scope.

- `make test`
- `make smoke` (fast sanity check)
- `make test-flows` (when flow routing changes)
- `make test-persistence` (when persistence layer changes)
- `make test-schemas` (when state schema changes)

## Execution rules
- Treat the plan as the source of truth; update it as decisions change.
- Resolve ambiguities in the plan before coding.
- Implement milestone by milestone without asking for "next steps" between milestones unless blocked or new info changes scope.
- Record changes or discoveries in a short "Log" subsection under the plan.
