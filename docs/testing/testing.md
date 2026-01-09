# Testing Guide

This document covers the testing strategy for the StartupAI CrewAI backend (Modal deployment).

## Testing Philosophy

We use a **two-tier testing approach**:

| Tier | Tool | Cost | When | Purpose |
|------|------|------|------|---------|
| **1. CI Tests** | pytest | Free | Every PR | Unit/integration testing |
| **2. Modal Testing** | Modal CLI | Modal credits | Pre-release | Live deployment testing |

```
┌─────────────────────────────────────────────────────────────────┐
│                     TESTING PIPELINE                            │
├───────────────────┬────────────────────┬───────────────────────┤
│  PR/Push          │  Pre-Release       │  Post-Deploy          │
│  (GitHub Actions) │  (Manual CLI)      │  (Modal Dashboard)    │
├───────────────────┼────────────────────┼───────────────────────┤
│  pytest           │  modal run         │  Logs (debugging)     │
│  (free, fast)     │  (live testing)    │  Metrics (analytics)  │
│  524 tests        │                    │                       │
└───────────────────┴────────────────────┴───────────────────────┘
```

## Running Tests

### pytest (Unit & Integration)

```bash
# Run all tests with coverage
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_modal_state_models.py

# Run with verbose output
uv run pytest tests/ -v

# Run only integration tests
uv run pytest tests/integration/

# Run specific test class
uv run pytest tests/test_desirability_crews.py::TestPhase2Flow
```

### Modal Testing (Live)

```bash
# Test locally with hot reload
modal serve src/modal_app/app.py

# Deploy to Modal
modal deploy src/modal_app/app.py

# Run specific function
modal run src/modal_app/app.py::kickoff --input '{"entrepreneur_input": "..."}'
```

## Test Structure

```
tests/
├── conftest.py                       # Shared fixtures
├── test_crew_input_context.py        # Context propagation tests
├── test_desirability_crews.py        # Phase 2 crew structure & routing
├── test_e2e_validation_scenarios.py  # Full validation flow scenarios
├── test_feasibility_crews.py         # Phase 3 crew structure & routing
├── test_hitl_contracts.py            # HITL checkpoint contracts
├── test_hitl_state_transitions.py    # HITL state machine tests
├── test_innovation_physics_routing.py # Signal-based routing tests
├── test_modal_api_integration.py     # Modal API tests
├── test_modal_state_models.py        # Pydantic state model tests
├── test_onboarding_crew.py           # Phase 0 crew tests
├── test_pivot_workflow.py            # Pivot context propagation
├── test_signal_routing_comprehensive.py # All signal routing paths
├── test_viability_crews.py           # Phase 4 crew structure & routing
├── test_vpc_discovery_crews.py       # Phase 1 crew tests
├── test_yaml_template_validation.py  # YAML config validation
└── integration/
    └── test_modal_e2e.py             # End-to-end Modal tests
```

## Test Categories

### Phase Tests
Each phase has dedicated tests for its crews:
- `test_onboarding_crew.py` - Phase 0: Founder's Brief capture
- `test_vpc_discovery_crews.py` - Phase 1: VPC Discovery
- `test_desirability_crews.py` - Phase 2: Desirability validation
- `test_feasibility_crews.py` - Phase 3: Feasibility validation
- `test_viability_crews.py` - Phase 4: Viability & Decision

### Signal Routing Tests
- `test_signal_routing_comprehensive.py` - All signal → checkpoint routing
- `test_innovation_physics_routing.py` - Innovation Physics formula tests

### HITL Tests
- `test_hitl_contracts.py` - HITL checkpoint structure validation
- `test_hitl_state_transitions.py` - State machine transitions

### Context Tests
- `test_crew_input_context.py` - Crew input validation
- `test_pivot_workflow.py` - Pivot context preservation

### E2E Tests
- `test_e2e_validation_scenarios.py` - Full flow scenarios
- `tests/integration/test_modal_e2e.py` - Modal deployment E2E

## Fixtures

### State Fixtures (conftest.py)

| Fixture | Description |
|---------|-------------|
| `sample_entrepreneur_input` | Sample business idea text |
| `mock_founders_brief` | Mock FoundersBrief Pydantic model |
| `mock_customer_profile` | Mock CustomerProfile model |
| `mock_value_map` | Mock value proposition map |
| `mock_fit_assessment` | Mock FitAssessment with fit_score |
| `mock_desirability_evidence` | Mock DesirabilityEvidence (strong_commitment) |
| `mock_feasibility_evidence` | Mock FeasibilityEvidence (green signal) |
| `mock_viability_evidence` | Mock ViabilityEvidence (profitable signal) |

### Minimal Fixtures

| Fixture | Description |
|---------|-------------|
| `minimal_founders_brief` | Minimal valid FoundersBrief for testing |

## Mock Patching Guidelines

**Critical**: When patching functions imported by phase modules, patch at the **usage location**, not the definition location.

### Correct Patching

```python
# Phase modules import at top-level:
# from src.state import update_progress
# from src.crews.desirability import run_build_crew

# CORRECT: Patch where imported/used
@patch("src.modal_app.phases.phase_2.update_progress")
@patch("src.modal_app.phases.phase_2.generate_alternative_segments")
@patch("src.crews.desirability.run_build_crew")
def test_phase_2_execution(mock_build, mock_alts, mock_progress):
    pass
```

### Incorrect Patching

```python
# WRONG: Patching at definition doesn't work after import
@patch("src.state.update_progress")  # Won't work - already imported
@patch("src.modal_app.helpers.segment_alternatives.generate_alternative_segments")  # Won't work
def test_phase_2_execution(mock_alts, mock_progress):
    pass
```

### Phase-Specific Patch Paths

| Phase | update_progress path |
|-------|---------------------|
| Phase 0 | `src.modal_app.phases.phase_0.update_progress` |
| Phase 1 | `src.modal_app.phases.phase_1.update_progress` |
| Phase 2 | `src.modal_app.phases.phase_2.update_progress` |
| Phase 3 | `src.modal_app.phases.phase_3.update_progress` |
| Phase 4 | `src.modal_app.phases.phase_4.update_progress` |

## Expected Values

### HITL Recommended Values by Phase

| Phase | Signal | hitl_recommended |
|-------|--------|------------------|
| Phase 0 | - | `"approve"` |
| Phase 1 | fit_score ≥ 70 | `"approve"` |
| Phase 1 | fit_score < 70 | `"iterate"` |
| Phase 2 | strong_commitment | `"approved"` |
| Phase 2 | no_interest | `"segment_1"` or `"custom_segment"` |
| Phase 2 | mild_interest | `"approved"` |
| Phase 3 | green | `"approve"` |
| Phase 3 | orange_constrained | `"feature_pivot"` |
| Phase 3 | red_impossible | `"kill"` |
| Phase 4 | profitable | `"proceed"` |
| Phase 4 | marginal | `"price_pivot"` |
| Phase 4 | underwater | `"price_pivot"` |

## Coverage

Coverage is configured in `pytest.ini`:

```ini
addopts = -v --tb=short --cov=src --cov-report=term-missing
```

View coverage report after running tests:
```bash
uv run pytest tests/ --cov-report=html
open htmlcov/index.html
```

## CI/CD Pipeline

GitHub Actions runs on every PR and push to main:

| Job | Trigger | Description |
|-----|---------|-------------|
| `pytest` | PR + push | Unit/integration tests with coverage |
| `lint` | PR + push | Code quality checks |

No secrets required - pytest runs without API keys (all crews mocked).

## Writing New Tests

### Unit Test Example

```python
import pytest
from src.state.models import ValidationSignal

def test_signal_values():
    """Test that signals have expected values."""
    assert ValidationSignal.STRONG_COMMITMENT.value == "strong_commitment"
    assert ValidationSignal.NO_INTEREST.value == "no_interest"
```

### Phase Test Example

```python
import pytest
from unittest.mock import patch, MagicMock

def test_phase_2_strong_commitment_recommends_approve(minimal_founders_brief):
    """Test that STRONG_COMMITMENT signal recommends approved."""
    mock_desirability = MagicMock()
    mock_desirability.model_dump.return_value = {
        "problem_resonance": 0.45,
        "zombie_ratio": 0.30,
    }

    with patch("src.modal_app.phases.phase_2.update_progress"), \
         patch("src.crews.desirability.run_build_crew") as mock_build, \
         patch("src.crews.desirability.run_growth_crew") as mock_growth, \
         patch("src.crews.desirability.run_governance_crew"):

        mock_build.return_value = {}
        mock_growth.return_value = mock_desirability

        from src.modal_app.phases.phase_2 import execute

        result = execute(
            run_id="test-run",
            state={
                "founders_brief": minimal_founders_brief.model_dump(),
                "customer_profile": {"pains": []},
                "value_map": {},
            },
        )

        assert result["hitl_recommended"] == "approved"
```

## Troubleshooting

### "KeyError: 'SUPABASE_KEY'"

This means `update_progress` wasn't mocked at the correct location. Use:
```python
@patch("src.modal_app.phases.phase_X.update_progress")  # Replace X with phase number
```

### "No module named 'src'"

```bash
# Install in development mode
uv sync
```

### Test isolation issues

If tests pass individually but fail when run together:
1. Check for `importlib.reload()` calls that defeat patches
2. Ensure mocks are at usage location, not definition location
3. Add fixtures to reset module state between tests

---
**Last Updated**: 2026-01-09
**Test Count**: 524 tests (3 skipped)
**Coverage**: ~53%
