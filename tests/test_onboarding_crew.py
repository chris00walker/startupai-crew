"""
Tests for Founder's Brief Schema (Pydantic models).

Tests the output schema validation for FoundersBrief and related models.
The onboarding crew was removed in favor of Quick Start pass-through +
Phase 1 Stage A BriefGenerationCrew. These schema tests remain valid
because the Pydantic models are still used across the codebase.
"""

import pytest

from src.state.models import (
    FoundersBrief,
    TheIdea,
    ProblemHypothesis,
    CustomerHypothesis,
    SolutionHypothesis,
    QAStatus,
)


# =============================================================================
# Output Schema Tests
# =============================================================================

class TestFoundersBriefSchema:
    """Tests for Founder's Brief output schema."""

    def test_founders_brief_required_fields(self):
        """Test FoundersBrief requires core fields."""
        with pytest.raises(Exception):  # Pydantic validation error
            FoundersBrief()  # Missing required fields

    def test_founders_brief_minimal(self, minimal_founders_brief):
        """Test creating minimal valid Founder's Brief."""
        assert minimal_founders_brief.the_idea.one_liner == "AI-powered supply chain optimizer"
        assert minimal_founders_brief.version == 1

    def test_founders_brief_serialization(self, minimal_founders_brief):
        """Test JSON serialization roundtrip."""
        data = minimal_founders_brief.model_dump(mode="json")
        restored = FoundersBrief(**data)
        assert restored.the_idea.one_liner == minimal_founders_brief.the_idea.one_liner

    def test_qa_status_defaults(self, minimal_founders_brief):
        """Test QA status has correct defaults."""
        assert minimal_founders_brief.qa_status.legitimacy_check == "pending"
        assert minimal_founders_brief.qa_status.intent_verification == "pending"
        assert minimal_founders_brief.qa_status.overall_status == "pending"

    def test_validation_status_markers(self, minimal_founders_brief):
        """Test hypotheses are marked as NOT VALIDATED."""
        assert "NOT VALIDATED" in minimal_founders_brief.problem_hypothesis.validation_status
        assert "NOT VALIDATED" in minimal_founders_brief.customer_hypothesis.validation_status
        assert "NOT VALIDATED" in minimal_founders_brief.solution_hypothesis.validation_status
