# Testing Guide

This document covers the testing strategy for the StartupAI CrewAI backend.

## Testing Philosophy

We use a **three-tier testing approach**:

| Tier | Tool | Cost | When | Purpose |
|------|------|------|------|---------|
| **1. CI Tests** | pytest | Free | Every PR | Unit/integration testing |
| **2. Performance** | `crewai test` | OpenAI API | Pre-release (manual) | GPT-scored evaluation |
| **3. Production** | AMP Traces | Free | Post-deploy | Debugging & analytics |

```
┌─────────────────────────────────────────────────────────────────┐
│                     TESTING PIPELINE                            │
├───────────────────┬────────────────────┬───────────────────────┤
│  PR/Push          │  Pre-Release       │  Post-Deploy          │
│  (GitHub Actions) │  (Manual CLI)      │  (AMP Dashboard)      │
├───────────────────┼────────────────────┼───────────────────────┤
│  pytest           │  crewai test -n 3  │  Traces (debugging)   │
│  (free, fast)     │  (GPT scoring)     │  Metrics (analytics)  │
│                   │                    │  Trigger Crew (manual)│
└───────────────────┴────────────────────┴───────────────────────┘
```

## Running Tests

### pytest (Unit & Integration)

```bash
# Run all tests with coverage
pytest tests/

# Run specific test file
pytest tests/test_state_schemas.py

# Run with verbose output
pytest tests/ -v

# Run only unit tests (fast)
pytest tests/ -m "not integration"
```

### crewai test (Performance)

```bash
# Default: 2 iterations with gpt-4o-mini
crewai test

# Custom iterations and model
crewai test -n 5 -m gpt-4o

# Track metrics over time
python scripts/track_performance.py -n 3 -m gpt-4o-mini --threshold 7.0
```

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures (23 fixtures)
├── test_state_schemas.py          # State model validation
├── test_persistence_repository.py # Repository layer tests
├── test_flow_routing.py           # Gate router unit tests
├── test_routing_logic.py          # Innovation physics routing
├── test_events.py                 # Event system tests
├── test_decision_log.py           # Decision logging tests
├── test_area_improvements.py      # Policy/budget tests
└── integration/
    ├── test_viability_workflow.py # HITL viability approval
    ├── test_build_crew.py         # Landing page pipeline
    ├── test_hitl_workflow.py      # Creative review & HITL
    ├── test_flywheel_workflow.py  # Learning system tests
    └── test_privacy_guard.py      # Privacy/PII detection
```

## Fixtures

### State Fixtures

| Fixture | Description |
|---------|-------------|
| `base_state()` | Minimal IDEATION phase state |
| `desirability_state()` | DESIRABILITY phase with test data |
| `feasibility_state()` | FEASIBILITY phase (chains from desirability) |
| `viability_state()` | VIABILITY phase (chains from feasibility) |
| `validated_state()` | Fully VALIDATED state |

### Signal Combination Fixtures

| Fixture | Signal |
|---------|--------|
| `no_interest_state()` | Desirability: NO_INTEREST |
| `weak_interest_state()` | Desirability: WEAK_INTEREST |
| `red_feasibility_state()` | Feasibility: RED_IMPOSSIBLE |
| `constrained_feasibility_state()` | Feasibility: ORANGE_CONSTRAINED |
| `underwater_viability_state()` | Viability: UNDERWATER |
| `zombie_market_state()` | Viability: ZOMBIE_MARKET |

### Mock Fixtures

| Fixture | Description |
|---------|-------------|
| `mock_repository()` | InMemoryStateRepository |
| `mock_service_crew()` | Mocked Service Crew |
| `mock_all_crews()` | All crews mocked together |
| `mock_supabase()` | Mocked Supabase client |

## Coverage

Coverage is configured in `pytest.ini`:

```ini
addopts = -v --tb=short --cov=src/startupai --cov-report=term-missing --cov-fail-under=50
```

**Current target**: 50% minimum coverage (actual: ~66%)

View coverage report after running tests:
```bash
pytest tests/ --cov-report=html
open htmlcov/index.html
```

## CI/CD Pipeline

GitHub Actions runs on every PR and push to main:

| Job | Trigger | Description |
|-----|---------|-------------|
| `pytest` | PR + push | Unit/integration tests with coverage |
| `lint` | PR + push | Ruff linting (non-blocking) |

No secrets required - pytest runs without API keys.

## AMP Platform Testing

The CrewAI AMP dashboard provides production testing and monitoring:

### Traces (Post-Deployment Debugging)

Access via: **Dashboard → Traces tab**

Traces capture:
- Agent thoughts and reasoning
- Task execution details and outcomes
- Tool usage and outputs
- Token consumption (prompt/completion breakdown)
- Execution times per task
- Cost estimates

**Use cases:**
- Debug failed executions
- Identify slow tasks
- Optimize token usage
- Track cost trends

### Trigger Crew (Manual Integration Testing)

Access via: **Dashboard → Crew details → Trigger Crew**

Use this to:
- Test with custom inputs before announcing changes
- Verify webhook integrations work
- Validate edge cases

### Metrics Tab (Performance Analytics)

Access via: **Dashboard → Metrics tab**

View historical:
- Execution counts
- Success/failure rates
- Average execution times
- Token usage trends

### Pre-Release Checklist

Before major releases:
```bash
# 1. Run local tests
pytest tests/

# 2. Run CrewAI performance evaluation (costs OpenAI API)
crewai test -n 3 -m gpt-4o-mini

# 3. Deploy to AMP
crewai deploy push --uuid 6b1e5c4d-e708-4921-be55-08fcb0d1e94b

# 4. Run post-deploy validation
./scripts/post_deploy_validation.sh

# 5. Monitor Traces for any issues in AMP dashboard
```

### Deep Dive: AMP Observability

For comprehensive production testing using AMP's observability features, see:
- **[AMP Observability Testing Strategy](./amp-observability-testing.md)** - Webhook streaming, trace analysis, alerting
- **Test Scenarios**: `tests/scenarios/test_scenarios.json` - Standard inputs for Trigger Crew

## Performance Metrics

The `scripts/track_performance.py` script:

1. Runs `crewai test` with specified iterations
2. Parses output for scores (0-10 scale) and timing
3. Appends results to `metrics/performance_history.json`
4. Fails if average score drops below threshold

**Default threshold**: 7.0 (can be adjusted with `--threshold`)

### Metrics Format

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "iterations": 3,
  "model": "gpt-4o-mini",
  "average_score": 8.2,
  "average_time": 45.5,
  "task_scores": [
    {"task": "analyze_entrepreneur", "average": 8.5},
    {"task": "generate_vpc", "average": 7.9}
  ]
}
```

## Writing New Tests

### Unit Test Example

```python
import pytest
from startupai.flows.state_schemas import ValidationPhase

def test_validation_phase_progression():
    """Test that phases progress in correct order."""
    phases = list(ValidationPhase)
    assert phases[0] == ValidationPhase.IDEATION
    assert phases[-1] == ValidationPhase.VALIDATED
```

### Integration Test Example

```python
import pytest
from unittest.mock import patch, Mock

@pytest.fixture
def mock_crew():
    with patch("startupai.crews.service.service_crew.ServiceCrew") as mock:
        crew_instance = Mock()
        crew_instance.kickoff.return_value = {"status": "success"}
        mock.return_value = crew_instance
        yield mock

def test_service_crew_execution(mock_crew, base_state):
    """Test service crew produces expected output."""
    # Test implementation
    pass
```

### Testing Gates

```python
def test_desirability_gate_strong_signal(desirability_state):
    """Test gate passes with strong interest signal."""
    flow = create_test_flow(desirability_state)
    result = flow.desirability_gate()
    assert result == "feasibility"
```

## Troubleshooting

### "No module named 'startupai'"

```bash
# Install in development mode
uv sync --all-extras
```

### "OPENAI_API_KEY not set"

```bash
# For local testing, create .env file
echo "OPENAI_API_KEY=sk-..." > .env

# Or use shared secrets
source ~/.secrets/startupai
```

### pytest-asyncio warnings

Ensure `pytest.ini` has:
```ini
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```
