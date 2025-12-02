# ============================================
# StartupAI Crew - Developer Makefile
# ============================================

.PHONY: help dev test seed simulate lint clean

# Default target
help:
	@echo "StartupAI Crew - Developer Commands"
	@echo ""
	@echo "Setup & Development:"
	@echo "  make dev        - Install dependencies and run local flow"
	@echo "  make sync       - Sync dependencies with uv"
	@echo ""
	@echo "Testing:"
	@echo "  make test       - Run all tests"
	@echo "  make test-v     - Run tests with verbose output"
	@echo "  make test-cov   - Run tests with coverage report"
	@echo "  make test-flows - Run flow routing tests only"
	@echo "  make test-persistence - Run persistence layer tests"
	@echo "  make smoke      - Quick smoke test (fastest tests)"
	@echo ""
	@echo "Benchmarks (requires OpenAI API key):"
	@echo "  make benchmark  - CrewAI quality benchmark (3 iterations)"
	@echo "  make benchmark-full - Extended benchmark (5 iterations)"
	@echo ""
	@echo "Developer Tools:"
	@echo "  make seed       - Create demo project (in-memory)"
	@echo "  make seed-db    - Create demo project (Supabase)"
	@echo "  make simulate   - Run flow simulation with mock data"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy     - Push to CrewAI AMP"
	@echo "  make status     - Check deployment status"
	@echo "  make logs       - View deployment logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      - Remove build artifacts"

# ============================================
# Setup & Development
# ============================================

dev: sync
	crewai run

sync:
	uv sync

# ============================================
# Testing
# ============================================

test:
	uv run python -m pytest tests/ -v --tb=short

test-v:
	uv run python -m pytest tests/ -v --tb=long

test-cov:
	uv run python -m pytest tests/ -v --cov=startupai --cov-report=html --cov-report=term-missing

# Targeted test commands
test-flows:
	uv run python -m pytest tests/test_flow_routing.py tests/test_routing_logic.py -v --tb=short

test-persistence:
	uv run python -m pytest tests/test_persistence_repository.py -v --tb=short

test-schemas:
	uv run python -m pytest tests/test_state_schemas.py -v --tb=short

# Quick smoke test (fastest tests only)
smoke:
	uv run python -m pytest tests/test_state_schemas.py tests/test_routing_logic.py -v --tb=short

# ============================================
# Quality Benchmarks (CrewAI - uses OpenAI API)
# ============================================

benchmark:
	@echo "Running CrewAI quality benchmarks (3 iterations)..."
	crewai test -n 3 -m gpt-4o

benchmark-full:
	@echo "Running CrewAI quality benchmarks (5 iterations)..."
	crewai test -n 5 -m gpt-4o

# ============================================
# Developer Tools
# ============================================

seed:
	uv run python scripts/seed_demo_project.py

seed-db:
	uv run python scripts/seed_demo_project.py --supabase

simulate:
	uv run python scripts/simulate_flow.py

# ============================================
# Deployment (CrewAI AMP)
# ============================================

DEPLOY_UUID := b4d5c1dd-27e2-4163-b9fb-a18ca06ca13b

deploy:
	crewai deploy push --uuid $(DEPLOY_UUID)

status:
	crewai deploy status --uuid $(DEPLOY_UUID)

logs:
	crewai deploy logs --uuid $(DEPLOY_UUID)

# ============================================
# Cleanup
# ============================================

clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
