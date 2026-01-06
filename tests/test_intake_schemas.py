"""
Unit tests for StartupAI Intake Crew Pydantic schemas.

Tests validate that output schemas enforce structure correctly and
catch invalid data as expected.
"""

import pytest
from pydantic import ValidationError

from intake_crew.schemas import (
    # Enums
    RiskLevel,
    PainSeverity,
    GainImportance,
    JobType,
    QAStatus,
    ApprovalDecision,
    # Task 1
    Hypothesis,
    FounderBrief,
    # Task 2
    CustomerJob,
    CustomerPain,
    CustomerGain,
    CustomerSegmentProfile,
    CustomerResearchOutput,
    # Task 3
    PainReliever,
    GainCreator,
    ValueMap,
    FitAnalysis,
    ValuePropositionCanvas,
    # Task 4
    ReviewSection,
    QAGateOutput,
    # Task 5
    HumanApprovalInput,
    # Task 6
    CrewInvocationResult,
)


# =======================================================================================
# TASK 1: FOUNDER BRIEF TESTS
# =======================================================================================


class TestFounderBrief:
    """Tests for FounderBrief (Task 1 output)."""

    def test_valid_founder_brief(self):
        """Valid brief should pass validation."""
        brief = FounderBrief(
            business_idea="An AI-powered platform for startup validation that automates customer research",
            problem_statement="Founders waste weeks doing manual customer research and validation",
            proposed_solution="Automated AI crews that perform customer research and run validation experiments",
            target_customers=["Early-stage founders", "Innovation consultants"],
            key_hypotheses=[
                Hypothesis(
                    statement="Founders need faster validation cycles",
                    risk_level=RiskLevel.CRITICAL,
                    validation_method="Survey + landing page signup rate",
                ),
                Hypothesis(
                    statement="AI can produce quality customer research",
                    risk_level=RiskLevel.HIGH,
                ),
            ],
            success_metrics=["Signup rate > 10%", "NPS > 50"],
        )
        assert brief.business_idea is not None
        assert len(brief.key_hypotheses) == 2
        assert brief.key_hypotheses[0].risk_level == RiskLevel.CRITICAL

    def test_founder_brief_missing_hypotheses(self):
        """Empty hypotheses should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            FounderBrief(
                business_idea="An AI platform for startup validation",
                problem_statement="Founders waste weeks on validation",
                proposed_solution="Automated AI validation crews",
                target_customers=["Founders"],
                key_hypotheses=[],  # Empty - should fail
                success_metrics=["Signup rate"],
            )
        assert "key_hypotheses" in str(exc_info.value)

    def test_founder_brief_short_business_idea(self):
        """Business idea too short should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            FounderBrief(
                business_idea="Short",  # Too short (< 20 chars)
                problem_statement="A detailed problem statement here",
                proposed_solution="A detailed solution statement here",
                target_customers=["Founders"],
                key_hypotheses=[
                    Hypothesis(statement="Test", risk_level=RiskLevel.LOW)
                ],
                success_metrics=["Metric"],
            )
        assert "business_idea" in str(exc_info.value)

    def test_founder_brief_empty_target_customers(self):
        """Empty target customers should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            FounderBrief(
                business_idea="An AI platform for startup validation",
                problem_statement="Founders waste weeks on validation",
                proposed_solution="Automated AI validation crews",
                target_customers=[],  # Empty - should fail
                key_hypotheses=[
                    Hypothesis(statement="Test", risk_level=RiskLevel.LOW)
                ],
                success_metrics=["Metric"],
            )
        assert "target_customers" in str(exc_info.value)


class TestHypothesis:
    """Tests for Hypothesis model."""

    def test_valid_hypothesis(self):
        """Valid hypothesis should pass."""
        hyp = Hypothesis(
            statement="Customers will pay $50/month for validation",
            risk_level=RiskLevel.CRITICAL,
            validation_method="Pricing page A/B test",
        )
        assert hyp.risk_level == RiskLevel.CRITICAL

    def test_hypothesis_optional_validation_method(self):
        """Validation method is optional."""
        hyp = Hypothesis(
            statement="Customers need faster validation",
            risk_level=RiskLevel.HIGH,
        )
        assert hyp.validation_method is None

    def test_hypothesis_invalid_risk_level(self):
        """Invalid risk level should fail."""
        with pytest.raises(ValidationError):
            Hypothesis(
                statement="Test hypothesis",
                risk_level="invalid",  # Not a valid enum value
            )


# =======================================================================================
# TASK 2: CUSTOMER RESEARCH OUTPUT TESTS
# =======================================================================================


class TestCustomerResearchOutput:
    """Tests for CustomerResearchOutput (Task 2 output)."""

    def test_valid_customer_research_output(self):
        """Valid research output should pass."""
        output = CustomerResearchOutput(
            customer_segments=[
                CustomerSegmentProfile(
                    segment_name="Early-stage Founders",
                    segment_description="First-time founders at pre-seed to seed stage building B2B SaaS",
                    jobs_to_be_done=[
                        CustomerJob(
                            job_type=JobType.FUNCTIONAL,
                            description="Validate product-market fit before running out of runway",
                            importance=9,
                        ),
                        CustomerJob(
                            job_type=JobType.EMOTIONAL,
                            description="Feel confident about the direction of their startup",
                            importance=8,
                        ),
                    ],
                    pains=[
                        CustomerPain(
                            description="Spending weeks on manual customer interviews",
                            severity=PainSeverity.HIGH,
                            current_workaround="Hire expensive consultants",
                        ),
                    ],
                    gains=[
                        CustomerGain(
                            description="Get validated insights in days instead of weeks",
                            importance=GainImportance.ESSENTIAL,
                        ),
                    ],
                    research_sources=["Indie Hackers forum", "YC Startup School"],
                )
            ],
            research_summary="Early-stage founders are desperate for faster validation cycles and are currently underserved by expensive consulting options.",
        )
        assert len(output.customer_segments) == 1
        assert output.customer_segments[0].segment_name == "Early-stage Founders"

    def test_customer_research_empty_segments(self):
        """Empty segments should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            CustomerResearchOutput(
                customer_segments=[],  # Empty - should fail
                research_summary="This is a research summary with enough characters.",
            )
        assert "customer_segments" in str(exc_info.value)

    def test_customer_research_short_summary(self):
        """Summary too short should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            CustomerResearchOutput(
                customer_segments=[
                    CustomerSegmentProfile(
                        segment_name="Founders",
                        segment_description="Early-stage startup founders",
                        jobs_to_be_done=[
                            CustomerJob(
                                job_type=JobType.FUNCTIONAL,
                                description="Validate PMF quickly",
                                importance=9,
                            )
                        ],
                        pains=[
                            CustomerPain(
                                description="Manual validation is slow",
                                severity=PainSeverity.HIGH,
                            )
                        ],
                        gains=[
                            CustomerGain(
                                description="Fast, reliable validation",
                                importance=GainImportance.ESSENTIAL,
                            )
                        ],
                    )
                ],
                research_summary="Too short",  # < 50 chars
            )
        assert "research_summary" in str(exc_info.value)


class TestCustomerJob:
    """Tests for CustomerJob model."""

    def test_valid_customer_job(self):
        """Valid job should pass."""
        job = CustomerJob(
            job_type=JobType.SOCIAL,
            description="Be seen as a savvy, data-driven founder",
            frequency="When pitching to investors",
            importance=7,
        )
        assert job.job_type == JobType.SOCIAL
        assert job.importance == 7

    def test_customer_job_importance_range(self):
        """Importance outside 1-10 should fail."""
        with pytest.raises(ValidationError):
            CustomerJob(
                job_type=JobType.FUNCTIONAL,
                description="Test job description here",
                importance=11,  # > 10
            )


# =======================================================================================
# TASK 3: VALUE PROPOSITION CANVAS TESTS
# =======================================================================================


class TestValuePropositionCanvas:
    """Tests for ValuePropositionCanvas (Task 3 output)."""

    def test_valid_vpc(self):
        """Valid VPC should pass validation."""
        vpc = ValuePropositionCanvas(
            primary_segment="Early-stage Founders",
            customer_jobs=["Validate PMF", "Reduce time to market"],
            customer_pains=["Manual research is slow", "Expensive consultants"],
            customer_gains=["Fast validation", "Confident decisions"],
            value_map=ValueMap(
                products_services=["AI Validation Crews", "Customer Research Tool"],
                pain_relievers=[
                    PainReliever(
                        pain_addressed="Manual research is slow",
                        reliever_description="Automated AI crews perform research in hours",
                        relief_strength="complete",
                    ),
                ],
                gain_creators=[
                    GainCreator(
                        gain_addressed="Fast validation",
                        creator_description="Run validation experiments automatically",
                        creation_strength="strong",
                    ),
                ],
            ),
            fit_analysis=FitAnalysis(
                covered_jobs=["Validate PMF"],
                covered_pains=["Manual research is slow"],
                covered_gains=["Fast validation"],
                gaps=["Reduce time to market not directly addressed"],
                fit_score=0.75,
            ),
            value_proposition_statement="For early-stage founders who need fast validation, StartupAI provides automated AI crews that deliver validated insights in hours unlike expensive consultants.",
        )
        assert vpc.primary_segment == "Early-stage Founders"
        assert vpc.fit_analysis.fit_score == 0.75
        assert len(vpc.fit_analysis.gaps) == 1

    def test_vpc_fit_score_range(self):
        """Fit score outside 0-1 should fail."""
        with pytest.raises(ValidationError):
            FitAnalysis(
                covered_jobs=["Job"],
                covered_pains=["Pain"],
                covered_gains=["Gain"],
                gaps=[],
                fit_score=1.5,  # > 1.0
            )

    def test_vpc_short_value_proposition(self):
        """Short value proposition should fail."""
        with pytest.raises(ValidationError):
            ValuePropositionCanvas(
                primary_segment="Founders",
                customer_jobs=["Job"],
                customer_pains=["Pain"],
                customer_gains=["Gain"],
                value_map=ValueMap(
                    products_services=["Product"],
                    pain_relievers=[
                        PainReliever(
                            pain_addressed="Pain",
                            reliever_description="Relieves pain effectively",
                        )
                    ],
                    gain_creators=[
                        GainCreator(
                            gain_addressed="Gain",
                            creator_description="Creates gain effectively",
                        )
                    ],
                ),
                fit_analysis=FitAnalysis(fit_score=0.8),
                value_proposition_statement="Short",  # < 20 chars
            )


# =======================================================================================
# TASK 4: QA GATE OUTPUT TESTS
# =======================================================================================


class TestQAGateOutput:
    """Tests for QAGateOutput (Task 4 output)."""

    def test_valid_qa_gate_output(self):
        """Valid QA output should pass."""
        qa = QAGateOutput(
            overall_status=QAStatus.PASS,
            brief_review=ReviewSection(
                status=QAStatus.PASS,
                issues=[],
                suggestions=["Consider adding more hypotheses"],
            ),
            customer_research_review=ReviewSection(
                status=QAStatus.PASS,
                issues=[],
            ),
            vpc_review=ReviewSection(
                status=QAStatus.CONDITIONAL,
                issues=["Fit score could be higher"],
            ),
            recommendations=["Run additional customer interviews"],
            blocking_issues=[],
            completeness_score=0.9,
            quality_score=0.85,
            methodology_compliance_score=0.95,
            ready_for_human_review=True,
        )
        assert qa.overall_status == QAStatus.PASS
        assert qa.ready_for_human_review is True

    def test_qa_gate_score_range(self):
        """Scores outside 0-1 should fail."""
        with pytest.raises(ValidationError):
            QAGateOutput(
                overall_status=QAStatus.PASS,
                brief_review=ReviewSection(status=QAStatus.PASS),
                customer_research_review=ReviewSection(status=QAStatus.PASS),
                vpc_review=ReviewSection(status=QAStatus.PASS),
                completeness_score=1.5,  # > 1.0
                quality_score=0.8,
                methodology_compliance_score=0.9,
                ready_for_human_review=True,
            )


# =======================================================================================
# TASK 5: HUMAN APPROVAL INPUT TESTS
# =======================================================================================


class TestHumanApprovalInput:
    """Tests for HumanApprovalInput (Task 5 output)."""

    def test_valid_approval(self):
        """Valid approval should pass."""
        approval = HumanApprovalInput(
            decision=ApprovalDecision.APPROVED,
            comments="Looks good to proceed!",
            approved_by="founder@startup.com",
        )
        assert approval.decision == ApprovalDecision.APPROVED

    def test_approval_needs_revision(self):
        """Needs revision with feedback should pass."""
        approval = HumanApprovalInput(
            decision=ApprovalDecision.NEEDS_REVISION,
            comments="Need more customer evidence",
            specific_feedback=[
                "Add more customer interview quotes",
                "Verify pricing assumptions",
            ],
        )
        assert approval.decision == ApprovalDecision.NEEDS_REVISION
        assert len(approval.specific_feedback) == 2

    def test_approval_rejected(self):
        """Rejected approval should pass."""
        approval = HumanApprovalInput(
            decision=ApprovalDecision.REJECTED,
            comments="Business idea is not viable",
        )
        assert approval.decision == ApprovalDecision.REJECTED


# =======================================================================================
# TASK 6: CREW INVOCATION RESULT TESTS
# =======================================================================================


class TestCrewInvocationResult:
    """Tests for CrewInvocationResult (Task 6 output)."""

    def test_successful_invocation(self):
        """Successful invocation should pass."""
        result = CrewInvocationResult(
            success=True,
            kickoff_id="abc123-def456",
            data_sent={
                "entrepreneur_brief": True,
                "customer_profile": True,
                "value_proposition_canvas": True,
                "qa_report": True,
                "human_approval": True,
            },
        )
        assert result.success is True
        assert result.kickoff_id == "abc123-def456"

    def test_failed_invocation(self):
        """Failed invocation should pass."""
        result = CrewInvocationResult(
            success=False,
            error_message="Crew 2 endpoint unavailable",
            retry_count=3,
        )
        assert result.success is False
        assert result.error_message == "Crew 2 endpoint unavailable"


# =======================================================================================
# ENUM TESTS
# =======================================================================================


class TestEnums:
    """Tests for enum values."""

    def test_risk_levels(self):
        """All risk levels should be valid."""
        assert RiskLevel.CRITICAL.value == "critical"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.LOW.value == "low"

    def test_pain_severity(self):
        """All pain severities should be valid."""
        assert PainSeverity.EXTREME.value == "extreme"
        assert PainSeverity.HIGH.value == "high"
        assert PainSeverity.MODERATE.value == "moderate"
        assert PainSeverity.LOW.value == "low"

    def test_gain_importance(self):
        """All gain importances should be valid."""
        assert GainImportance.ESSENTIAL.value == "essential"
        assert GainImportance.EXPECTED.value == "expected"
        assert GainImportance.DESIRED.value == "desired"
        assert GainImportance.UNEXPECTED.value == "unexpected"

    def test_job_types(self):
        """All job types should be valid."""
        assert JobType.FUNCTIONAL.value == "functional"
        assert JobType.EMOTIONAL.value == "emotional"
        assert JobType.SOCIAL.value == "social"

    def test_qa_status(self):
        """All QA statuses should be valid."""
        assert QAStatus.PASS.value == "pass"
        assert QAStatus.FAIL.value == "fail"
        assert QAStatus.CONDITIONAL.value == "conditional"

    def test_approval_decision(self):
        """All approval decisions should be valid."""
        assert ApprovalDecision.APPROVED.value == "approved"
        assert ApprovalDecision.REJECTED.value == "rejected"
        assert ApprovalDecision.NEEDS_REVISION.value == "needs_revision"
