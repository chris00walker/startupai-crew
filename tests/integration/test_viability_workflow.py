"""
Tests for Phase 2B: HITL Viability Approval Workflow.

Tests the viability approval tool, flow nodes, and resume handler
for unit economics decisions.
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from startupai.tools.viability_approval import (
    ViabilityApprovalTool,
    ViabilityApprovalResult,
    ViabilityStatus,
    PivotRecommendation,
    analyze_viability,
    format_viability_for_dashboard,
)
from startupai.webhooks.resume_handler import (
    ResumeHandler,
    ApprovalType,
    ViabilityChoice,
)


# ===========================================================================
# VIABILITY APPROVAL TOOL TESTS
# ===========================================================================

class TestViabilityApprovalTool:
    """Tests for the ViabilityApprovalTool."""

    def test_analyze_profitable_economics(self):
        """Test analysis of healthy unit economics."""
        tool = ViabilityApprovalTool()

        result = tool._run(json.dumps({
            "cac": 100.0,
            "ltv": 500.0,
            "gross_margin": 0.70,
            "tam": 1000000000,
        }))

        assert "Viability Analysis Complete" in result
        assert "PROFITABLE" in result
        assert "LTV/CAC Ratio:** 5.00" in result

    def test_analyze_underwater_economics(self):
        """Test analysis of underwater unit economics (CAC > LTV)."""
        tool = ViabilityApprovalTool()

        result = tool._run(json.dumps({
            "cac": 200.0,
            "ltv": 100.0,
            "gross_margin": 0.50,
        }))

        assert "UNDERWATER" in result
        assert "HUMAN DECISION REQUIRED" in result
        assert "Pivot Options" in result

    def test_analyze_marginal_economics(self):
        """Test analysis of marginal unit economics."""
        tool = ViabilityApprovalTool()

        result = tool._run(json.dumps({
            "cac": 100.0,
            "ltv": 150.0,  # LTV/CAC = 1.5 (marginal)
            "gross_margin": 0.55,
        }))

        assert "MARGINAL" in result
        assert "LTV/CAC Ratio:** 1.50" in result

    def test_analyze_zombie_market(self):
        """Test detection of zombie market (profitable but tiny TAM)."""
        tool = ViabilityApprovalTool()

        result = tool._run(json.dumps({
            "cac": 50.0,
            "ltv": 300.0,  # LTV/CAC = 6 (profitable)
            "gross_margin": 0.60,
            "tam": 5000000,  # Small TAM < 10M
        }))

        assert "ZOMBIE" in result or "PROFITABLE" in result

    def test_analyze_with_result_method(self):
        """Test the analyze_with_result convenience method."""
        tool = ViabilityApprovalTool()

        result = tool.analyze_with_result(
            cac=150.0,
            ltv=100.0,
            gross_margin=0.45,
            context={"business_type": "saas"}
        )

        assert isinstance(result, ViabilityApprovalResult)
        assert result.status == ViabilityStatus.UNDERWATER
        assert result.needs_human_decision is True
        assert len(result.pivot_options) > 0

    def test_pivot_options_generated(self):
        """Test that pivot options are generated for underwater economics."""
        tool = ViabilityApprovalTool()

        result = tool.analyze_with_result(
            cac=200.0,
            ltv=80.0,
            gross_margin=0.40,
        )

        # Should have price and cost pivot options
        pivot_types = [opt.pivot_type for opt in result.pivot_options]
        assert PivotRecommendation.PRICE_PIVOT in pivot_types
        assert PivotRecommendation.COST_PIVOT in pivot_types

    def test_recommended_pivot_selection(self):
        """Test that a recommended pivot is selected for underwater economics."""
        result = analyze_viability(
            cac=180.0,
            ltv=90.0,
            gross_margin=0.50,
            context={"conversion_rate": 0.02}  # Low conversion suggests cost pivot
        )

        assert result.recommended_pivot is not None
        assert result.recommended_pivot in [
            PivotRecommendation.PRICE_PIVOT,
            PivotRecommendation.COST_PIVOT,
        ]

    def test_format_for_dashboard(self):
        """Test formatting viability result for dashboard display."""
        result = analyze_viability(
            cac=100.0,
            ltv=80.0,
            gross_margin=0.55,
        )

        dashboard_data = format_viability_for_dashboard(result)

        assert "status" in dashboard_data
        assert "needs_decision" in dashboard_data
        assert "metrics" in dashboard_data
        assert "pivot_options" in dashboard_data
        assert "summary" in dashboard_data
        assert dashboard_data["metrics"]["cac"] == 100.0
        assert dashboard_data["metrics"]["ltv"] == 80.0

    def test_invalid_json_input(self):
        """Test handling of invalid JSON input."""
        tool = ViabilityApprovalTool()

        result = tool._run("not valid json")

        assert "Error" in result

    def test_confidence_score_calculation(self):
        """Test that confidence score is calculated reasonably."""
        # With TAM and context
        result1 = analyze_viability(
            cac=100.0,
            ltv=300.0,
            gross_margin=0.60,
            tam=500000000,
            context={"business_type": "saas"}
        )

        # Without TAM or context
        result2 = analyze_viability(
            cac=100.0,
            ltv=300.0,
            gross_margin=0.60,
        )

        # More data should give higher confidence
        assert result1.confidence_score >= result2.confidence_score


# ===========================================================================
# RESUME HANDLER VIABILITY TESTS
# ===========================================================================

class TestResumeHandlerViability:
    """Tests for viability decision handling in ResumeHandler."""

    def test_handle_price_pivot_decision(self):
        """Test handling a price pivot decision."""
        handler = ResumeHandler()

        payload = {
            "kickoff_id": "test_123",
            "approval_type": "viability_decision",
            "viability_decision": {
                "choice": "price_pivot",
                "rationale": "Strong conversion suggests price elasticity",
                "new_price_target": 149.0,
            }
        }

        result = handler.process(payload)

        assert result["choice"] == "price_pivot"
        assert result["new_price_target"] == 149.0
        assert result["_meta"]["approval_type"] == "viability_decision"

    def test_handle_cost_pivot_decision(self):
        """Test handling a cost pivot decision."""
        handler = ResumeHandler()

        payload = {
            "kickoff_id": "test_123",
            "approval_type": "viability_decision",
            "viability_decision": {
                "choice": "cost_pivot",
                "rationale": "Need to reduce CAC significantly",
                "cost_reduction_target": 0.35,
                "features_to_cut": ["premium_support", "advanced_analytics"],
            }
        }

        result = handler.process(payload)

        assert result["choice"] == "cost_pivot"
        assert result["cost_reduction_target"] == 0.35
        assert "premium_support" in result["features_to_cut"]

    def test_handle_kill_decision(self):
        """Test handling a kill decision."""
        handler = ResumeHandler()

        payload = {
            "kickoff_id": "test_123",
            "approval_type": "viability_decision",
            "viability_decision": {
                "choice": "kill",
                "rationale": "No viable path to profitability",
                "kill_reason": "CAC too high for target market",
            }
        }

        result = handler.process(payload)

        assert result["choice"] == "kill"
        assert result["kill_reason"] == "CAC too high for target market"

    def test_handle_continue_decision(self):
        """Test handling a continue (proceed despite warnings) decision."""
        handler = ResumeHandler()

        payload = {
            "kickoff_id": "test_123",
            "approval_type": "viability_decision",
            "viability_decision": {
                "choice": "continue",
                "rationale": "Early stage, will optimize later",
            }
        }

        result = handler.process(payload)

        assert result["choice"] == "continue"


# ===========================================================================
# VIABILITY FLOW NODE TESTS
# ===========================================================================

class TestViabilityFlowNode:
    """Tests for viability approval flow nodes in InternalValidationFlow."""

    def test_flow_has_viability_approval_methods(self):
        """Test that InternalValidationFlow has viability approval methods."""
        from startupai.flows.internal_validation_flow import InternalValidationFlow

        # Check methods exist
        assert hasattr(InternalValidationFlow, 'pause_for_viability_decision')
        assert hasattr(InternalValidationFlow, '_notify_viability_approval_needed')
        assert hasattr(InternalValidationFlow, '_handle_viability_resume')
        assert hasattr(InternalValidationFlow, '_execute_price_pivot')
        assert hasattr(InternalValidationFlow, '_execute_cost_pivot')
        assert hasattr(InternalValidationFlow, '_execute_kill')

    def test_state_has_viability_fields(self):
        """Test that ValidationState has viability HITL fields."""
        from startupai.flows.state_schemas import StartupValidationState

        state = StartupValidationState()

        # Check fields exist
        assert hasattr(state, 'viability_analysis')
        assert hasattr(state, 'viability_decision')

        # Check defaults
        assert state.viability_analysis is None
        assert state.viability_decision is None

    def test_handle_price_pivot_resume(self):
        """Test the _handle_viability_resume method with price pivot."""
        from startupai.flows.internal_validation_flow import InternalValidationFlow
        from startupai.flows.state_schemas import (
            StartupValidationState,
            ViabilityEvidence,
            Phase,
        )

        # Create flow with viability evidence
        flow = InternalValidationFlow(
            entrepreneur_input="Test business idea",
            project_id="test_project",
        )

        # Set up viability evidence (underwater)
        flow.state.viability_evidence = ViabilityEvidence(
            cac=200.0,
            ltv=100.0,
            ltv_cac_ratio=0.5,
            gross_margin=0.50,
        )
        flow.state.human_input_required = True
        flow.state.pivot_history = []

        # Simulate price pivot decision
        price_pivot_decision = {
            "choice": "price_pivot",
            "rationale": "Test price increase",
            "new_price_target": 200.0,
        }

        flow._handle_viability_resume(price_pivot_decision)

        # Verify state updated
        assert flow.state.human_input_required is False
        assert flow.state.viability_decision == price_pivot_decision

    def test_handle_cost_pivot_resume(self):
        """Test the _handle_viability_resume method with cost pivot."""
        from startupai.flows.internal_validation_flow import InternalValidationFlow
        from startupai.flows.state_schemas import ViabilityEvidence

        flow = InternalValidationFlow(
            entrepreneur_input="Test business idea",
            project_id="test_project",
        )

        flow.state.viability_evidence = ViabilityEvidence(
            cac=200.0,
            ltv=150.0,
            ltv_cac_ratio=0.75,
            gross_margin=0.50,
        )
        flow.state.human_input_required = True
        flow.state.pivot_history = []

        cost_pivot_decision = {
            "choice": "cost_pivot",
            "rationale": "Reduce CAC",
            "cost_reduction_target": 0.4,
            "features_to_cut": ["feature1"],
        }

        flow._handle_viability_resume(cost_pivot_decision)

        assert flow.state.human_input_required is False
        # CAC should be reduced
        assert flow.state.viability_evidence.cac == 120.0  # 200 * 0.6

    def test_handle_kill_resume(self):
        """Test the _handle_viability_resume method with kill decision."""
        from startupai.flows.internal_validation_flow import InternalValidationFlow
        from startupai.flows.state_schemas import Phase

        flow = InternalValidationFlow(
            entrepreneur_input="Test business idea",
            project_id="test_project",
        )

        flow.state.human_input_required = True
        flow.state.pivot_history = []

        kill_decision = {
            "choice": "kill",
            "rationale": "No viable path",
            "kill_reason": "Market too small",
        }

        flow._handle_viability_resume(kill_decision)

        assert flow.state.phase == Phase.KILLED
        assert "Project terminated" in flow.state.final_recommendation


# ===========================================================================
# FINANCE CREW TOOL WIRING TESTS
# ===========================================================================

class TestFinanceCrewViabilityTools:
    """Tests for Finance Crew viability tool wiring."""

    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY required for crew instantiation"
    )
    def test_finance_crew_has_viability_tool(self):
        """Test that Finance Crew has viability approval tool."""
        from startupai.crews.finance.finance_crew import FinanceCrew

        crew = FinanceCrew()

        assert hasattr(crew, '_viability_approval_tool')
        assert isinstance(crew._viability_approval_tool, ViabilityApprovalTool)

    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY required for crew instantiation"
    )
    def test_unit_economics_analyst_has_viability_tool(self):
        """Test that unit_economics_analyst agent has viability tool."""
        from startupai.crews.finance.finance_crew import FinanceCrew

        crew = FinanceCrew()
        agent = crew.unit_economics_analyst()

        tool_names = [t.name for t in agent.tools]
        assert "viability_approval" in tool_names


# ===========================================================================
# INTEGRATION TESTS
# ===========================================================================

class TestViabilityIntegration:
    """Integration tests for the full viability HITL workflow."""

    def test_viability_analysis_to_decision_flow(self):
        """Test the flow from viability analysis to human decision."""
        # Step 1: Analyze unit economics
        viability_result = analyze_viability(
            cac=180.0,
            ltv=90.0,
            gross_margin=0.45,
            context={"segment": "SMB SaaS"}
        )

        assert viability_result.status == ViabilityStatus.UNDERWATER
        assert viability_result.needs_human_decision is True

        # Step 2: Format for dashboard
        dashboard_data = format_viability_for_dashboard(viability_result)

        assert dashboard_data["needs_decision"] is True
        assert len(dashboard_data["pivot_options"]) >= 2

        # Step 3: Simulate human decision
        decision_payload = {
            "kickoff_id": "integration_test",
            "approval_type": "viability_decision",
            "viability_decision": {
                "choice": viability_result.recommended_pivot.value if viability_result.recommended_pivot else "cost_pivot",
                "rationale": "Following AI recommendation",
                "cost_reduction_target": 0.30,
            }
        }

        # Step 4: Process the decision
        handler = ResumeHandler()
        result = handler.process(decision_payload)

        assert result["_meta"]["approval_type"] == "viability_decision"
        assert "choice" in result

    def test_profitable_economics_no_decision_needed(self):
        """Test that profitable economics don't require human decision."""
        result = analyze_viability(
            cac=80.0,
            ltv=400.0,  # LTV/CAC = 5
            gross_margin=0.70,
        )

        assert result.status == ViabilityStatus.PROFITABLE
        assert result.needs_human_decision is False
        assert len(result.pivot_options) == 0
