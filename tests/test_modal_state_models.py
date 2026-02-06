"""
Tests for Modal State Models (src/state/models.py).

Tests Pydantic model validation, serialization, and field constraints.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from src.state.models import (
    # Enums
    ValidationSignal,
    PivotRecommendation,
    JobType,
    PainSeverity,
    GainRelevance,
    ValidationStatus,
    EvidenceType,
    AssumptionCategory,
    # Founder's Brief models
    TheIdea,
    ProblemHypothesis,
    CustomerHypothesis,
    SolutionHypothesis,
    Assumption,
    SuccessCriteria,
    FounderContext,
    QAStatus,
    InterviewMetadata,
    FoundersBrief,
    # VPC models
    CustomerJob,
    CustomerPain,
    CustomerGain,
    CustomerProfile,
    ProductService,
    PainReliever,
    GainCreator,
    ValueMap,
    FitAssessment,
    # Evidence models
    Experiment,
    DesirabilityEvidence,
    FeasibilityEvidence,
    ViabilityEvidence,
    # State models
    HITLCheckpoint,
    PhaseState,
    ValidationRunState,
)


# =============================================================================
# Enum Tests
# =============================================================================

class TestValidationSignalEnum:
    """Tests for ValidationSignal enum values."""

    def test_desirability_signals(self):
        """Test desirability signal values."""
        assert ValidationSignal.NO_INTEREST.value == "no_interest"
        assert ValidationSignal.MILD_INTEREST.value == "mild_interest"
        assert ValidationSignal.STRONG_COMMITMENT.value == "strong_commitment"

    def test_feasibility_signals(self):
        """Test feasibility signal values."""
        assert ValidationSignal.GREEN.value == "green"
        assert ValidationSignal.ORANGE_CONSTRAINED.value == "orange_constrained"
        assert ValidationSignal.RED_IMPOSSIBLE.value == "red_impossible"

    def test_viability_signals(self):
        """Test viability signal values."""
        assert ValidationSignal.PROFITABLE.value == "profitable"
        assert ValidationSignal.MARGINAL.value == "marginal"
        assert ValidationSignal.UNDERWATER.value == "underwater"


class TestPivotRecommendationEnum:
    """Tests for PivotRecommendation enum values."""

    def test_pivot_types(self):
        """Test all pivot type values."""
        assert PivotRecommendation.NO_PIVOT.value == "no_pivot"
        assert PivotRecommendation.SEGMENT_PIVOT.value == "segment_pivot"
        assert PivotRecommendation.VALUE_PIVOT.value == "value_pivot"
        assert PivotRecommendation.FEATURE_PIVOT.value == "feature_pivot"
        assert PivotRecommendation.STRATEGIC_PIVOT.value == "strategic_pivot"
        assert PivotRecommendation.KILL.value == "kill"


class TestEvidenceTypeEnum:
    """Tests for EvidenceType (SAY vs DO) enum."""

    def test_do_evidence_types(self):
        """Test DO evidence types (stronger)."""
        assert EvidenceType.SKIN_IN_GAME.value == "skin_in_game"
        assert EvidenceType.BEHAVIOR.value == "behavior"
        assert EvidenceType.CTA_CLICKS.value == "cta_clicks"

    def test_say_evidence_types(self):
        """Test SAY evidence types (weaker)."""
        assert EvidenceType.VERBAL_COMMITMENT.value == "verbal_commitment"
        assert EvidenceType.SURVEY_RESPONSE.value == "survey_response"
        assert EvidenceType.INTERVIEW_STATEMENT.value == "interview_statement"


# =============================================================================
# Founder's Brief Tests
# =============================================================================

class TestTheIdea:
    """Tests for TheIdea model."""

    def test_minimal_creation(self):
        """Test creating with required fields only."""
        idea = TheIdea(
            one_liner="AI-powered supply chain optimizer",
            description="A platform that uses ML to optimize logistics.",
        )
        assert idea.one_liner == "AI-powered supply chain optimizer"
        assert idea.inspiration == ""
        assert idea.unique_insight == ""

    def test_full_creation(self):
        """Test creating with all fields."""
        idea = TheIdea(
            one_liner="AI supply chain",
            description="Full description here",
            inspiration="Saw inefficiencies in my previous job",
            unique_insight="ML can reduce costs by 30%",
        )
        assert idea.unique_insight == "ML can reduce costs by 30%"


class TestAssumption:
    """Tests for Assumption model."""

    def test_assumption_creation(self):
        """Test creating an assumption."""
        assumption = Assumption(
            assumption="Customers will pay $100/month",
            category=AssumptionCategory.BUSINESS_MODEL,
            risk_level="high",
            how_to_test="Price sensitivity survey",
        )
        assert assumption.category == AssumptionCategory.BUSINESS_MODEL
        assert assumption.testable is True
        assert assumption.tested is False
        assert assumption.validated is None

    def test_risk_level_validation(self):
        """Test risk level must be high/medium/low."""
        with pytest.raises(ValueError):
            Assumption(
                assumption="Test",
                category=AssumptionCategory.PROBLEM,
                risk_level="critical",  # Invalid
            )


class TestFoundersBrief:
    """Tests for FoundersBrief model."""

    @pytest.fixture
    def minimal_brief(self):
        """Create a minimal valid Founder's Brief."""
        return FoundersBrief(
            the_idea=TheIdea(
                one_liner="Test product",
                description="A test product description",
            ),
            problem_hypothesis=ProblemHypothesis(
                problem_statement="People waste time",
                who_has_this_problem="Office workers",
            ),
            customer_hypothesis=CustomerHypothesis(
                primary_segment="Enterprise",
                segment_description="Large companies",
            ),
            solution_hypothesis=SolutionHypothesis(
                proposed_solution="Automation tool",
            ),
        )

    def test_minimal_creation(self, minimal_brief):
        """Test creating with minimal required fields."""
        assert minimal_brief.the_idea.one_liner == "Test product"
        assert minimal_brief.version == 1
        assert minimal_brief.key_assumptions == []

    def test_legacy_accessors(self, minimal_brief):
        """Test backward compatibility accessors."""
        assert minimal_brief.concept == "A test product description"
        assert minimal_brief.one_liner == "Test product"
        assert minimal_brief.concept_legitimacy == "pending"
        assert minimal_brief.intent_verification == "pending"

    def test_serialization(self, minimal_brief):
        """Test JSON serialization."""
        data = minimal_brief.model_dump(mode="json")
        assert data["the_idea"]["one_liner"] == "Test product"
        assert data["version"] == 1

    def test_deserialization(self, minimal_brief):
        """Test JSON deserialization."""
        data = minimal_brief.model_dump(mode="json")
        restored = FoundersBrief(**data)
        assert restored.the_idea.one_liner == minimal_brief.the_idea.one_liner


# =============================================================================
# VPC Model Tests
# =============================================================================

class TestCustomerProfile:
    """Tests for CustomerProfile model."""

    def test_empty_profile(self):
        """Test creating an empty profile."""
        profile = CustomerProfile(
            segment_name="SMB Owners",
            segment_description="Small business owners",
        )
        assert profile.jobs == []
        assert profile.pains == []
        assert profile.gains == []

    def test_profile_with_jobs(self):
        """Test profile with customer jobs."""
        job = CustomerJob(
            id="job_001",
            job_statement="When managing inventory, I want to forecast demand",
            job_type=JobType.FUNCTIONAL,
            priority=8,
        )
        profile = CustomerProfile(
            segment_name="Retailers",
            segment_description="Retail store owners",
            jobs=[job],
        )
        assert len(profile.jobs) == 1
        assert profile.jobs[0].job_type == JobType.FUNCTIONAL


class TestFitAssessment:
    """Tests for FitAssessment model."""

    def test_passing_fit(self):
        """Test fit score >= 70 is gate_ready."""
        fit = FitAssessment(
            fit_score=75,
            fit_status="strong",
            profile_completeness=0.9,
            value_map_coverage=0.85,
            evidence_strength="strong",
            gate_ready=True,
        )
        assert fit.fit_score >= 70
        assert fit.gate_ready is True

    def test_failing_fit(self):
        """Test fit score < 70 is not gate_ready."""
        fit = FitAssessment(
            fit_score=55,
            fit_status="weak",
            profile_completeness=0.6,
            value_map_coverage=0.5,
            evidence_strength="weak",
            gate_ready=False,
            blockers=["Insufficient pain validation", "No DO evidence"],
        )
        assert fit.fit_score < 70
        assert fit.gate_ready is False
        assert len(fit.blockers) == 2


# =============================================================================
# Evidence Model Tests
# =============================================================================

class TestDesirabilityEvidence:
    """Tests for DesirabilityEvidence model."""

    def test_problem_resonance_calculation(self):
        """Test problem_resonance field range."""
        evidence = DesirabilityEvidence(
            ad_impressions=1000,
            ad_clicks=150,
            ad_signups=30,
            problem_resonance=0.65,
            zombie_ratio=0.20,
        )
        assert 0 <= evidence.problem_resonance <= 1
        assert 0 <= evidence.zombie_ratio <= 1

    def test_signal_derivation_strong(self):
        """Test STRONG_COMMITMENT signal criteria."""
        evidence = DesirabilityEvidence(
            problem_resonance=0.45,  # >= 0.3
            zombie_ratio=0.25,  # < 0.7
            signal=ValidationSignal.STRONG_COMMITMENT,
        )
        assert evidence.signal == ValidationSignal.STRONG_COMMITMENT

    def test_signal_derivation_mild(self):
        """Test MILD_INTEREST signal criteria (high zombie)."""
        evidence = DesirabilityEvidence(
            problem_resonance=0.35,  # >= 0.3
            zombie_ratio=0.75,  # >= 0.7
            signal=ValidationSignal.MILD_INTEREST,
        )
        assert evidence.signal == ValidationSignal.MILD_INTEREST

    def test_signal_derivation_none(self):
        """Test NO_INTEREST signal criteria (low resonance)."""
        evidence = DesirabilityEvidence(
            problem_resonance=0.15,  # < 0.3
            zombie_ratio=0.40,
            signal=ValidationSignal.NO_INTEREST,
        )
        assert evidence.signal == ValidationSignal.NO_INTEREST


class TestFeasibilityEvidence:
    """Tests for FeasibilityEvidence model."""

    def test_green_signal(self):
        """Test GREEN feasibility."""
        evidence = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=False,
            signal=ValidationSignal.GREEN,
        )
        assert evidence.signal == ValidationSignal.GREEN

    def test_orange_signal(self):
        """Test ORANGE_CONSTRAINED feasibility."""
        evidence = FeasibilityEvidence(
            core_features_feasible=True,
            downgrade_required=True,
            downgrade_features=["Real-time sync", "AI recommendations"],
            signal=ValidationSignal.ORANGE_CONSTRAINED,
        )
        assert evidence.signal == ValidationSignal.ORANGE_CONSTRAINED
        assert len(evidence.downgrade_features) == 2

    def test_red_signal(self):
        """Test RED_IMPOSSIBLE feasibility."""
        evidence = FeasibilityEvidence(
            core_features_feasible=False,
            constraints=["No API available", "Patent blocked"],
            signal=ValidationSignal.RED_IMPOSSIBLE,
        )
        assert evidence.signal == ValidationSignal.RED_IMPOSSIBLE


class TestViabilityEvidence:
    """Tests for ViabilityEvidence model."""

    def test_profitable_ltv_cac(self):
        """Test PROFITABLE with LTV:CAC >= 3."""
        evidence = ViabilityEvidence(
            cac=100,
            ltv=400,
            ltv_cac_ratio=4.0,
            signal=ValidationSignal.PROFITABLE,
        )
        assert evidence.ltv_cac_ratio >= 3.0
        assert evidence.signal == ValidationSignal.PROFITABLE

    def test_marginal_ltv_cac(self):
        """Test MARGINAL with 1 <= LTV:CAC < 3."""
        evidence = ViabilityEvidence(
            cac=100,
            ltv=200,
            ltv_cac_ratio=2.0,
            signal=ValidationSignal.MARGINAL,
        )
        assert 1.0 <= evidence.ltv_cac_ratio < 3.0
        assert evidence.signal == ValidationSignal.MARGINAL

    def test_underwater_ltv_cac(self):
        """Test UNDERWATER with LTV:CAC < 1."""
        evidence = ViabilityEvidence(
            cac=100,
            ltv=50,
            ltv_cac_ratio=0.5,
            signal=ValidationSignal.UNDERWATER,
        )
        assert evidence.ltv_cac_ratio < 1.0
        assert evidence.signal == ValidationSignal.UNDERWATER


# =============================================================================
# State Model Tests
# =============================================================================

class TestValidationRunState:
    """Tests for ValidationRunState model."""

    @pytest.fixture
    def minimal_state(self):
        """Create a minimal validation run state."""
        return ValidationRunState(
            run_id=uuid4(),
            project_id=uuid4(),
            user_id=uuid4(),
            entrepreneur_input="AI-powered inventory management for SMBs",
        )

    def test_minimal_creation(self, minimal_state):
        """Test creating with minimal fields."""
        assert minimal_state.current_phase == 0
        assert minimal_state.status == "pending"
        assert minimal_state.founders_brief is None

    def test_serialization_roundtrip(self, minimal_state):
        """Test JSON serialization and deserialization."""
        data = minimal_state.model_dump(mode="json")
        restored = ValidationRunState(**data)
        assert restored.run_id == minimal_state.run_id
        assert restored.entrepreneur_input == minimal_state.entrepreneur_input

    def test_phase_progression(self, minimal_state):
        """Test state through phase progression."""
        # Phase 0
        minimal_state.current_phase = 0
        minimal_state.status = "running"
        assert minimal_state.current_phase == 0

        # Phase 1
        minimal_state.current_phase = 1
        assert minimal_state.current_phase == 1

        # Continue through all phases
        for phase in range(2, 5):
            minimal_state.current_phase = phase
            assert minimal_state.current_phase == phase

    def test_hitl_state(self, minimal_state):
        """Test HITL checkpoint state."""
        minimal_state.hitl_state = "approve_founders_brief"
        minimal_state.status = "paused"
        assert minimal_state.hitl_state == "approve_founders_brief"


class TestHITLCheckpoint:
    """Tests for HITLCheckpoint model."""

    def test_checkpoint_creation(self):
        """Test creating a HITL checkpoint."""
        checkpoint = HITLCheckpoint(
            checkpoint_name="approve_discovery_output",
            phase=1,
            title="VPC Discovery Complete",
            description="Review the VPC fit score before proceeding.",
            context={"fit_score": 78},
            options=[
                {"id": "approve", "label": "Approve"},
                {"id": "iterate", "label": "Iterate"},
            ],
            recommended_option="approve",
        )
        assert checkpoint.checkpoint_name == "approve_discovery_output"
        assert checkpoint.decision is None  # Not yet decided

    def test_checkpoint_decision(self):
        """Test recording a decision."""
        checkpoint = HITLCheckpoint(
            checkpoint_name="approve_desirability_gate",
            phase=2,
            title="Desirability Gate",
            description="Approve desirability validation.",
            decision="approved",
            feedback="Looks good, proceed.",
            decided_at=datetime.utcnow(),
        )
        assert checkpoint.decision == "approved"
        assert checkpoint.feedback == "Looks good, proceed."
