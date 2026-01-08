"""
E2E Integration Tests for Modal Architecture

Tests the full Phase 0→4 validation flow with mocked crews.
Verifies state passing between phases and HITL checkpoint generation.

Test coverage:
- Complete validation flow (happy path)
- State propagation between phases
- HITL checkpoint structure validation
- Phase signal generation
- Error handling at each phase
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Any

from src.state.models import (
    FoundersBrief,
    TheIdea,
    ProblemHypothesis,
    CustomerHypothesis,
    SolutionHypothesis,
    SuccessCriteria,
    QAStatus,
    CustomerProfile,
    CustomerJob,
    CustomerPain,
    CustomerGain,
    ValueMap,
    FitAssessment,
    DesirabilityEvidence,
    FeasibilityEvidence,
    ViabilityEvidence,
    ValidationSignal,
    JobType,
    PainSeverity,
    GainRelevance,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_entrepreneur_input() -> str:
    """Sample entrepreneur input for testing."""
    return """
    I'm building an AI-powered B2B SaaS platform that helps small businesses
    automate their customer support using intelligent chatbots. Target customers
    are SMBs with 10-100 employees who currently use email or basic helpdesk
    software. Pricing will be $99/month for basic tier, $299/month for pro tier.
    """


@pytest.fixture
def mock_founders_brief() -> FoundersBrief:
    """Mock Founder's Brief from Phase 0."""
    return FoundersBrief(
        the_idea=TheIdea(
            one_liner="AI-powered customer support automation for SMBs",
            description="Intelligent chatbot platform that learns from interactions",
            inspiration="Frustrated with slow support experiences",
            unique_insight="AI can handle 80% of support queries instantly",
        ),
        problem_hypothesis=ProblemHypothesis(
            problem_statement="SMBs struggle with scaling customer support",
            who_has_this_problem="SMBs with 10-100 employees",
            frequency="Daily",
            current_alternatives="Email, Basic helpdesk software, Phone support",
            why_alternatives_fail="Too slow, expensive to scale, inconsistent quality",
        ),
        customer_hypothesis=CustomerHypothesis(
            primary_segment="SMBs with 10-100 employees",
            segment_description="Growing businesses overwhelmed by support volume",
            characteristics=["Tech-savvy", "Growth-focused", "Budget-conscious"],
            where_to_find_them="LinkedIn, SaaS communities",
        ),
        solution_hypothesis=SolutionHypothesis(
            proposed_solution="AI-powered chatbot platform",
            key_features=["AI chatbot", "Knowledge base", "Human handoff"],
            differentiation="Learns from past tickets for instant answers",
        ),
        success_criteria=SuccessCriteria(
            minimum_viable_signal="10 signups with 50% activation",
            deal_breakers=["No customers willing to pay", "Tech impossible"],
            target_metrics={"cac": "<$500", "nps": ">50"},
        ),
        qa_status=QAStatus(
            legitimacy_check="pass",
            legitimacy_notes="Business concept is legitimate and addressable",
            intent_verification="pass",
            intent_notes="Entrepreneur intent clearly captured",
            overall_status="approved",
        ),
    )


@pytest.fixture
def mock_customer_profile() -> CustomerProfile:
    """Mock Customer Profile from Phase 1."""
    return CustomerProfile(
        segment_name="Tech-savvy SMB Owners",
        segment_description="Growing businesses overwhelmed by support volume",
        jobs=[
            CustomerJob(
                id="job-1",
                job_statement="Provide timely customer support",
                job_type=JobType.FUNCTIONAL,
                priority=9,
            ),
            CustomerJob(
                id="job-2",
                job_statement="Reduce support costs",
                job_type=JobType.FUNCTIONAL,
                priority=8,
            ),
        ],
        pains=[
            CustomerPain(
                id="pain-1",
                pain_statement="Support tickets pile up during peak hours",
                severity=PainSeverity.SEVERE,
                priority=8,
            ),
            CustomerPain(
                id="pain-2",
                pain_statement="Hiring support staff is expensive",
                severity=PainSeverity.MODERATE,
                priority=7,
            ),
        ],
        gains=[
            CustomerGain(
                id="gain-1",
                gain_statement="Faster response times improve customer satisfaction",
                relevance=GainRelevance.ESSENTIAL,
                priority=9,
            ),
            CustomerGain(
                id="gain-2",
                gain_statement="Lower operational costs",
                relevance=GainRelevance.ESSENTIAL,
                priority=8,
            ),
        ],
    )


@pytest.fixture
def mock_value_map() -> dict[str, Any]:
    """Mock Value Map from Phase 1 (as dict for compatibility)."""
    return {
        "products_services": ["AI Chatbot Platform", "Knowledge Base Builder"],
        "pain_relievers": [
            "24/7 automated responses reduce ticket backlog",
            "AI learns from past tickets for instant answers",
        ],
        "gain_creators": [
            "90% reduction in first-response time",
            "50% cost savings vs hiring additional staff",
        ],
    }


@pytest.fixture
def mock_fit_assessment() -> dict[str, Any]:
    """Mock Fit Assessment from Phase 1 (as dict for compatibility)."""
    return {
        "fit_score": 78,
        "fit_status": "strong",
        "profile_completeness": 0.85,
        "value_map_coverage": 0.80,
        "evidence_strength": "strong",
        "experiments_run": 3,
        "experiments_passed": 2,
        "gate_ready": True,
        "blockers": [],
    }


@pytest.fixture
def mock_wtp_results() -> dict[str, Any]:
    """Mock WTP results from Phase 1."""
    return {
        "target_price": 199.0,
        "willingness_to_pay": 249.0,
        "price_sensitivity": 0.3,
        "optimal_price_range": {"min": 149, "max": 299},
    }


@pytest.fixture
def mock_desirability_evidence() -> DesirabilityEvidence:
    """Mock Desirability Evidence from Phase 2."""
    return DesirabilityEvidence(
        problem_resonance=0.72,
        zombie_ratio=0.25,
        conversion_rate=0.045,
        ad_impressions=10000,
        ad_clicks=450,
        ad_signups=45,
        ad_spend=500.0,
        signal=ValidationSignal.STRONG_COMMITMENT,
    )


@pytest.fixture
def mock_feasibility_evidence() -> FeasibilityEvidence:
    """Mock Feasibility Evidence from Phase 3."""
    return FeasibilityEvidence(
        core_features_feasible=True,
        downgrade_required=False,
        downgrade_features=[],
        api_costs_monthly=150.0,
        infra_costs_monthly=200.0,
        constraints=["Rate limits on OpenAI API"],
        signal=ValidationSignal.GREEN,
    )


@pytest.fixture
def mock_viability_evidence() -> ViabilityEvidence:
    """Mock Viability Evidence from Phase 4."""
    return ViabilityEvidence(
        cac=250.0,
        ltv=1500.0,
        ltv_cac_ratio=6.0,
        gross_margin=0.75,
        payback_months=4,
        tam_usd=5_000_000_000,
        sam_usd=500_000_000,
        som_usd=50_000_000,
        signal=ValidationSignal.PROFITABLE,
    )


# =============================================================================
# Phase Execution Tests
# =============================================================================


class TestPhase0Execution:
    """Test Phase 0: Onboarding execution."""

    def test_phase_0_returns_hitl_checkpoint(
        self, sample_entrepreneur_input, mock_founders_brief
    ):
        """Phase 0 should return approve_founders_brief HITL checkpoint."""
        from src.modal_app.phases import phase_0

        with patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            with patch("src.modal_app.phases.phase_0.update_progress"):
                mock_crew.return_value = mock_founders_brief

                result = phase_0.execute(
                    run_id="test-run-001",
                    state={"entrepreneur_input": sample_entrepreneur_input},
                )

        assert result["hitl_checkpoint"] == "approve_founders_brief"
        assert "hitl_options" in result
        assert len(result["hitl_options"]) >= 2
        assert result["hitl_recommended"] == "approve"
        assert "founders_brief" in result["state"]

    def test_phase_0_propagates_founders_brief_to_state(
        self, sample_entrepreneur_input, mock_founders_brief
    ):
        """Phase 0 should add founders_brief to output state."""
        from src.modal_app.phases import phase_0

        with patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            with patch("src.modal_app.phases.phase_0.update_progress"):
                mock_crew.return_value = mock_founders_brief

                result = phase_0.execute(
                    run_id="test-run-001",
                    state={"entrepreneur_input": sample_entrepreneur_input},
                )

        brief = result["state"]["founders_brief"]
        assert brief["the_idea"]["one_liner"] == mock_founders_brief.the_idea.one_liner


class TestPhase1Execution:
    """Test Phase 1: VPC Discovery execution."""

    def test_phase_1_returns_hitl_checkpoint(
        self, mock_founders_brief, mock_customer_profile, mock_value_map, mock_fit_assessment, mock_wtp_results
    ):
        """Phase 1 should return approve_vpc_completion HITL checkpoint."""
        from src.modal_app.phases import phase_1

        with patch("src.crews.discovery.run_discovery_crew") as mock_discovery:
            with patch("src.crews.discovery.run_customer_profile_crew") as mock_profile:
                with patch("src.crews.discovery.run_value_design_crew") as mock_value:
                    with patch("src.crews.discovery.run_wtp_crew") as mock_wtp:
                        with patch("src.crews.discovery.run_fit_assessment_crew") as mock_fit:
                            with patch("src.modal_app.phases.phase_1.update_progress"):
                                mock_discovery.return_value = {"segments": ["SMB"]}
                                mock_profile.return_value = mock_customer_profile
                                mock_value.return_value = mock_value_map
                                mock_wtp.return_value = mock_wtp_results
                                mock_fit.return_value = mock_fit_assessment

                                result = phase_1.execute(
                                    run_id="test-run-001",
                                    state={"founders_brief": mock_founders_brief.model_dump()},
                                )

        assert result["hitl_checkpoint"] == "approve_vpc_completion"
        assert "customer_profile" in result["state"]
        assert "value_map" in result["state"]
        assert "fit_assessment" in result["state"]

    def test_phase_1_fit_score_affects_recommendation(
        self, mock_founders_brief, mock_customer_profile, mock_value_map, mock_wtp_results
    ):
        """Phase 1 should recommend 'iterate' if fit score < 70."""
        from src.modal_app.phases import phase_1

        # Create low-fit assessment (as dict to avoid Pydantic validation)
        low_fit = {
            "fit_score": 55,
            "fit_status": "weak",
            "profile_completeness": 0.5,
            "value_map_coverage": 0.5,
            "evidence_strength": "weak",
            "experiments_run": 1,
            "experiments_passed": 0,
            "gate_ready": False,
            "blockers": ["Low fit score"],
        }

        with patch("src.crews.discovery.run_discovery_crew") as mock_discovery:
            with patch("src.crews.discovery.run_customer_profile_crew") as mock_profile:
                with patch("src.crews.discovery.run_value_design_crew") as mock_value:
                    with patch("src.crews.discovery.run_wtp_crew") as mock_wtp:
                        with patch("src.crews.discovery.run_fit_assessment_crew") as mock_fit:
                            with patch("src.modal_app.phases.phase_1.update_progress"):
                                mock_discovery.return_value = {"segments": ["SMB"]}
                                mock_profile.return_value = mock_customer_profile
                                mock_value.return_value = mock_value_map
                                mock_wtp.return_value = mock_wtp_results
                                mock_fit.return_value = low_fit

                                result = phase_1.execute(
                                    run_id="test-run-001",
                                    state={"founders_brief": mock_founders_brief.model_dump()},
                                )

        assert result["hitl_recommended"] == "iterate"


class TestPhase2Execution:
    """Test Phase 2: Desirability execution."""

    def test_phase_2_returns_hitl_checkpoint(
        self, mock_founders_brief, mock_customer_profile, mock_value_map, mock_desirability_evidence
    ):
        """Phase 2 should return approve_desirability_gate HITL checkpoint."""
        from src.modal_app.phases import phase_2

        with patch("src.crews.desirability.run_build_crew") as mock_build:
            with patch("src.crews.desirability.run_growth_crew") as mock_growth:
                with patch("src.crews.desirability.run_governance_crew") as mock_gov:
                    with patch("src.modal_app.phases.phase_2.update_progress"):
                        mock_build.return_value = {"landing_pages": {}}
                        mock_growth.return_value = mock_desirability_evidence
                        mock_gov.return_value = {"audit": "passed"}

                        result = phase_2.execute(
                            run_id="test-run-001",
                            state={
                                "founders_brief": mock_founders_brief.model_dump(),
                                "customer_profile": mock_customer_profile.model_dump(),
                                "value_map": mock_value_map,
                            },
                        )

        assert result["hitl_checkpoint"] == "approve_desirability_gate"
        assert "desirability_evidence" in result["state"]
        assert result["state"]["desirability_signal"] == "strong_commitment"

    def test_phase_2_low_resonance_triggers_segment_pivot(
        self, mock_founders_brief, mock_customer_profile, mock_value_map
    ):
        """Phase 2 should recommend segment_pivot if problem_resonance < 0.3."""
        from src.modal_app.phases import phase_2

        low_resonance = DesirabilityEvidence(
            problem_resonance=0.15,
            zombie_ratio=0.8,
            conversion_rate=0.01,
            ad_impressions=10000,
            ad_clicks=100,
            ad_signups=10,
            ad_spend=500.0,
            signal=ValidationSignal.NO_INTEREST,
        )

        with patch("src.crews.desirability.run_build_crew") as mock_build:
            with patch("src.crews.desirability.run_growth_crew") as mock_growth:
                with patch("src.crews.desirability.run_governance_crew") as mock_gov:
                    with patch("src.modal_app.phases.phase_2.update_progress"):
                        mock_build.return_value = {"landing_pages": {}}
                        mock_growth.return_value = low_resonance
                        mock_gov.return_value = {"audit": "passed"}

                        result = phase_2.execute(
                            run_id="test-run-001",
                            state={
                                "founders_brief": mock_founders_brief.model_dump(),
                                "customer_profile": mock_customer_profile.model_dump(),
                                "value_map": mock_value_map,
                            },
                        )

        assert result["hitl_recommended"] == "segment_pivot"
        assert result["state"]["desirability_signal"] == "no_interest"


class TestPhase3Execution:
    """Test Phase 3: Feasibility execution."""

    def test_phase_3_returns_hitl_checkpoint(
        self, mock_customer_profile, mock_value_map, mock_feasibility_evidence
    ):
        """Phase 3 should return approve_feasibility_gate HITL checkpoint."""
        from src.modal_app.phases import phase_3

        with patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build:
            with patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_gov:
                with patch("src.modal_app.phases.phase_3.update_progress"):
                    mock_build.return_value = mock_feasibility_evidence
                    mock_gov.return_value = {"audit": "passed"}

                    result = phase_3.execute(
                        run_id="test-run-001",
                        state={
                            "customer_profile": mock_customer_profile.model_dump(),
                            "value_map": mock_value_map,
                        },
                    )

        assert result["hitl_checkpoint"] == "approve_feasibility_gate"
        assert "feasibility_evidence" in result["state"]
        assert result["state"]["feasibility_signal"] == "green"

    def test_phase_3_red_signal_recommends_kill(
        self, mock_customer_profile, mock_value_map
    ):
        """Phase 3 should recommend kill if signal is red_impossible."""
        from src.modal_app.phases import phase_3

        red_feasibility = FeasibilityEvidence(
            core_features_feasible=False,
            downgrade_required=False,
            downgrade_features=[],
            api_costs_monthly=0,
            infra_costs_monthly=0,
            constraints=["No viable technical approach"],
            signal=ValidationSignal.RED_IMPOSSIBLE,
        )

        with patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build:
            with patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_gov:
                with patch("src.modal_app.phases.phase_3.update_progress"):
                    mock_build.return_value = red_feasibility
                    mock_gov.return_value = {"audit": "passed"}

                    result = phase_3.execute(
                        run_id="test-run-001",
                        state={
                            "customer_profile": mock_customer_profile.model_dump(),
                            "value_map": mock_value_map,
                        },
                    )

        assert result["hitl_recommended"] == "kill"
        assert result["state"]["feasibility_signal"] == "red_impossible"


class TestPhase4Execution:
    """Test Phase 4: Viability execution."""

    def test_phase_4_returns_final_decision_checkpoint(
        self,
        mock_founders_brief,
        mock_customer_profile,
        mock_value_map,
        mock_wtp_results,
        mock_desirability_evidence,
        mock_feasibility_evidence,
        mock_viability_evidence,
    ):
        """Phase 4 should return request_human_decision HITL checkpoint."""
        from src.modal_app.phases import phase_4

        with patch("src.crews.viability.run_finance_crew") as mock_finance:
            with patch("src.crews.viability.run_synthesis_crew") as mock_synthesis:
                with patch("src.crews.viability.run_viability_governance_crew") as mock_gov:
                    with patch("src.modal_app.phases.phase_4.update_progress"):
                        mock_finance.return_value = mock_viability_evidence
                        mock_synthesis.return_value = {"learnings": {}, "recommendation": "proceed"}
                        mock_gov.return_value = {"audit": "passed"}

                        result = phase_4.execute(
                            run_id="test-run-001",
                            state={
                                "founders_brief": mock_founders_brief.model_dump(),
                                "customer_profile": mock_customer_profile.model_dump(),
                                "value_map": mock_value_map,
                                "wtp_results": mock_wtp_results,
                                "desirability_evidence": mock_desirability_evidence.model_dump(),
                                "feasibility_evidence": mock_feasibility_evidence.model_dump(),
                                "fit_assessment": {"fit_score": 78},
                            },
                        )

        assert result["hitl_checkpoint"] == "request_human_decision"
        assert "viability_evidence" in result["state"]
        assert result["state"]["viability_signal"] == "profitable"
        assert result["hitl_recommended"] == "proceed"

    def test_phase_4_underwater_recommends_price_pivot(
        self,
        mock_founders_brief,
        mock_customer_profile,
        mock_value_map,
        mock_wtp_results,
        mock_desirability_evidence,
        mock_feasibility_evidence,
    ):
        """Phase 4 should recommend price_pivot if LTV:CAC ratio < 1."""
        from src.modal_app.phases import phase_4

        underwater = ViabilityEvidence(
            cac=1000.0,
            ltv=500.0,
            ltv_cac_ratio=0.5,
            gross_margin=0.3,
            payback_months=24,
            tam_usd=1_000_000_000,
            sam_usd=100_000_000,
            som_usd=10_000_000,
            signal=ValidationSignal.UNDERWATER,
        )

        with patch("src.crews.viability.run_finance_crew") as mock_finance:
            with patch("src.crews.viability.run_synthesis_crew") as mock_synthesis:
                with patch("src.crews.viability.run_viability_governance_crew") as mock_gov:
                    with patch("src.modal_app.phases.phase_4.update_progress"):
                        mock_finance.return_value = underwater
                        mock_synthesis.return_value = {"learnings": {}}
                        mock_gov.return_value = {"audit": "passed"}

                        result = phase_4.execute(
                            run_id="test-run-001",
                            state={
                                "founders_brief": mock_founders_brief.model_dump(),
                                "customer_profile": mock_customer_profile.model_dump(),
                                "value_map": mock_value_map,
                                "wtp_results": mock_wtp_results,
                                "desirability_evidence": mock_desirability_evidence.model_dump(),
                                "feasibility_evidence": mock_feasibility_evidence.model_dump(),
                                "fit_assessment": {"fit_score": 78},
                            },
                        )

        assert result["hitl_recommended"] == "price_pivot"
        assert result["state"]["viability_signal"] == "underwater"


# =============================================================================
# Full E2E Flow Test
# =============================================================================


class TestFullValidationFlow:
    """Test complete Phase 0→4 validation flow."""

    def test_complete_happy_path_flow(
        self,
        sample_entrepreneur_input,
        mock_founders_brief,
        mock_customer_profile,
        mock_value_map,
        mock_fit_assessment,
        mock_wtp_results,
        mock_desirability_evidence,
        mock_feasibility_evidence,
        mock_viability_evidence,
    ):
        """Test complete validation flow from Phase 0 to Phase 4."""
        from src.modal_app.phases import phase_0, phase_1, phase_2, phase_3, phase_4

        run_id = "e2e-test-run-001"
        state = {"entrepreneur_input": sample_entrepreneur_input}

        # Phase 0: Onboarding
        with patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            with patch("src.modal_app.phases.phase_0.update_progress"):
                mock_crew.return_value = mock_founders_brief
                result_0 = phase_0.execute(run_id=run_id, state=state)

        assert result_0["hitl_checkpoint"] == "approve_founders_brief"
        state = result_0["state"]

        # Phase 1: VPC Discovery
        with patch("src.crews.discovery.run_discovery_crew") as mock_discovery:
            with patch("src.crews.discovery.run_customer_profile_crew") as mock_profile:
                with patch("src.crews.discovery.run_value_design_crew") as mock_value:
                    with patch("src.crews.discovery.run_wtp_crew") as mock_wtp:
                        with patch("src.crews.discovery.run_fit_assessment_crew") as mock_fit:
                            with patch("src.modal_app.phases.phase_1.update_progress"):
                                mock_discovery.return_value = {"segments": ["SMB"]}
                                mock_profile.return_value = mock_customer_profile
                                mock_value.return_value = mock_value_map
                                mock_wtp.return_value = mock_wtp_results
                                mock_fit.return_value = mock_fit_assessment
                                result_1 = phase_1.execute(run_id=run_id, state=state)

        assert result_1["hitl_checkpoint"] == "approve_vpc_completion"
        assert result_1["hitl_context"]["fit_score"] >= 70
        state = result_1["state"]

        # Phase 2: Desirability
        with patch("src.crews.desirability.run_build_crew") as mock_build:
            with patch("src.crews.desirability.run_growth_crew") as mock_growth:
                with patch("src.crews.desirability.run_governance_crew") as mock_gov:
                    with patch("src.modal_app.phases.phase_2.update_progress"):
                        mock_build.return_value = {"landing_pages": {}}
                        mock_growth.return_value = mock_desirability_evidence
                        mock_gov.return_value = {"audit": "passed"}
                        result_2 = phase_2.execute(run_id=run_id, state=state)

        assert result_2["hitl_checkpoint"] == "approve_desirability_gate"
        assert result_2["state"]["desirability_signal"] == "strong_commitment"
        state = result_2["state"]

        # Phase 3: Feasibility
        with patch("src.crews.feasibility.run_feasibility_build_crew") as mock_build:
            with patch("src.crews.feasibility.run_feasibility_governance_crew") as mock_gov:
                with patch("src.modal_app.phases.phase_3.update_progress"):
                    mock_build.return_value = mock_feasibility_evidence
                    mock_gov.return_value = {"audit": "passed"}
                    result_3 = phase_3.execute(run_id=run_id, state=state)

        assert result_3["hitl_checkpoint"] == "approve_feasibility_gate"
        assert result_3["state"]["feasibility_signal"] == "green"
        state = result_3["state"]

        # Phase 4: Viability
        with patch("src.crews.viability.run_finance_crew") as mock_finance:
            with patch("src.crews.viability.run_synthesis_crew") as mock_synthesis:
                with patch("src.crews.viability.run_viability_governance_crew") as mock_gov:
                    with patch("src.modal_app.phases.phase_4.update_progress"):
                        mock_finance.return_value = mock_viability_evidence
                        mock_synthesis.return_value = {"learnings": {}, "recommendation": "proceed"}
                        mock_gov.return_value = {"audit": "passed"}
                        result_4 = phase_4.execute(run_id=run_id, state=state)

        # Final assertions
        assert result_4["hitl_checkpoint"] == "request_human_decision"
        assert result_4["state"]["viability_signal"] == "profitable"
        assert result_4["hitl_recommended"] == "proceed"
        assert result_4["hitl_context"]["unit_economics"]["ltv_cac_ratio"] >= 3.0

    def test_state_accumulates_across_phases(
        self,
        sample_entrepreneur_input,
        mock_founders_brief,
        mock_customer_profile,
        mock_value_map,
        mock_fit_assessment,
        mock_wtp_results,
    ):
        """Verify state accumulates required data as it passes through phases."""
        from src.modal_app.phases import phase_0, phase_1

        run_id = "e2e-state-test"
        state = {"entrepreneur_input": sample_entrepreneur_input}

        # Phase 0
        with patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            with patch("src.modal_app.phases.phase_0.update_progress"):
                mock_crew.return_value = mock_founders_brief
                result_0 = phase_0.execute(run_id=run_id, state=state)

        state_after_0 = result_0["state"]
        assert "entrepreneur_input" in state_after_0
        assert "founders_brief" in state_after_0

        # Phase 1
        with patch("src.crews.discovery.run_discovery_crew") as mock_discovery:
            with patch("src.crews.discovery.run_customer_profile_crew") as mock_profile:
                with patch("src.crews.discovery.run_value_design_crew") as mock_value:
                    with patch("src.crews.discovery.run_wtp_crew") as mock_wtp:
                        with patch("src.crews.discovery.run_fit_assessment_crew") as mock_fit:
                            with patch("src.modal_app.phases.phase_1.update_progress"):
                                mock_discovery.return_value = {"segments": ["SMB"]}
                                mock_profile.return_value = mock_customer_profile
                                mock_value.return_value = mock_value_map
                                mock_wtp.return_value = mock_wtp_results
                                mock_fit.return_value = mock_fit_assessment
                                result_1 = phase_1.execute(run_id=run_id, state=state_after_0)

        state_after_1 = result_1["state"]
        # Should still have Phase 0 data
        assert "entrepreneur_input" in state_after_0
        assert "founders_brief" in state_after_1
        # Plus Phase 1 data
        assert "customer_profile" in state_after_1
        assert "value_map" in state_after_1
        assert "wtp_results" in state_after_1
        assert "fit_assessment" in state_after_1


# =============================================================================
# HITL Checkpoint Structure Tests
# =============================================================================


class TestHITLCheckpointStructure:
    """Test HITL checkpoint response structure."""

    def test_hitl_checkpoint_has_required_fields(
        self, sample_entrepreneur_input, mock_founders_brief
    ):
        """All HITL checkpoints should have required fields."""
        from src.modal_app.phases import phase_0

        with patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            with patch("src.modal_app.phases.phase_0.update_progress"):
                mock_crew.return_value = mock_founders_brief
                result = phase_0.execute(
                    run_id="test-hitl-structure",
                    state={"entrepreneur_input": sample_entrepreneur_input},
                )

        # Required HITL fields
        assert "hitl_checkpoint" in result
        assert "hitl_title" in result
        assert "hitl_description" in result
        assert "hitl_context" in result
        assert "hitl_options" in result
        assert "hitl_recommended" in result
        assert "state" in result

    def test_hitl_options_have_required_fields(
        self, sample_entrepreneur_input, mock_founders_brief
    ):
        """Each HITL option should have id, label, and description."""
        from src.modal_app.phases import phase_0

        with patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            with patch("src.modal_app.phases.phase_0.update_progress"):
                mock_crew.return_value = mock_founders_brief
                result = phase_0.execute(
                    run_id="test-hitl-options",
                    state={"entrepreneur_input": sample_entrepreneur_input},
                )

        for option in result["hitl_options"]:
            assert "id" in option
            assert "label" in option
            assert "description" in option

    def test_hitl_recommended_is_valid_option(
        self, sample_entrepreneur_input, mock_founders_brief
    ):
        """hitl_recommended should be one of the option IDs."""
        from src.modal_app.phases import phase_0

        with patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            with patch("src.modal_app.phases.phase_0.update_progress"):
                mock_crew.return_value = mock_founders_brief
                result = phase_0.execute(
                    run_id="test-hitl-recommendation",
                    state={"entrepreneur_input": sample_entrepreneur_input},
                )

        option_ids = [opt["id"] for opt in result["hitl_options"]]
        assert result["hitl_recommended"] in option_ids


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestPhaseErrorHandling:
    """Test error handling in phase execution."""

    def test_phase_0_propagates_crew_errors(self, sample_entrepreneur_input):
        """Phase 0 should propagate crew execution errors."""
        from src.modal_app.phases import phase_0

        with patch("src.crews.onboarding.run_onboarding_crew") as mock_crew:
            with patch("src.modal_app.phases.phase_0.update_progress"):
                mock_crew.side_effect = Exception("Crew execution failed")

                with pytest.raises(Exception, match="Crew execution failed"):
                    phase_0.execute(
                        run_id="test-error",
                        state={"entrepreneur_input": sample_entrepreneur_input},
                    )

    def test_phase_1_propagates_discovery_crew_errors(self, mock_founders_brief):
        """Phase 1 should propagate discovery crew errors."""
        from src.modal_app.phases import phase_1

        with patch("src.crews.discovery.run_discovery_crew") as mock_discovery:
            with patch("src.modal_app.phases.phase_1.update_progress"):
                mock_discovery.side_effect = Exception("Discovery failed")

                with pytest.raises(Exception, match="Discovery failed"):
                    phase_1.execute(
                        run_id="test-error",
                        state={"founders_brief": mock_founders_brief.model_dump()},
                    )
