"""
Integration Tests for HITL (Human-in-the-Loop) Workflow.

Tests the creative review and methodology validation workflow:
1. ResumeHandler - Parse /resume webhook payloads
2. GuardianReviewTool - Auto-QA creatives
3. MethodologyCheckTool - VPC/BMC validation

These tests verify the HITL workflow without requiring
actual API calls or human interaction.
"""

import os
import pytest
import json
from datetime import datetime

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from startupai.webhooks.resume_handler import (
    ResumeHandler,
    ResumePayload,
    CreativeApprovalPayload,
    ViabilityDecisionPayload,
    ApprovalType,
    CreativeStatus,
    ViabilityChoice,
    parse_resume_payload,
)
from startupai.tools.guardian_review import (
    GuardianReviewTool,
    ReviewDecision,
    ReviewSeverity,
    review_landing_page,
)
from startupai.tools.methodology_check import (
    MethodologyCheckTool,
    MethodologyType,
    CheckSeverity,
    check_vpc,
)


# ===========================================================================
# RESUME HANDLER TESTS
# ===========================================================================

class TestResumeHandler:
    """Tests for the resume webhook handler."""

    def test_parse_creative_approval_payload(self):
        """Test parsing a creative approval payload."""
        handler = ResumeHandler()

        payload = {
            "kickoff_id": "kickoff_123",
            "approval_type": "creative_approval",
            "project_id": "proj_456",
            "creative_approval": {
                "variant_id": "benefit-v1",
                "status": "approved",
                "feedback": "Looks great!",
                "approved_by": "user_789"
            }
        }

        result = handler.process(payload)

        assert result["variant_id"] == "benefit-v1"
        assert result["approved"] is True
        assert result["status"] == "approved"
        assert result["_meta"]["kickoff_id"] == "kickoff_123"
        assert result["_meta"]["approval_type"] == "creative_approval"

    def test_parse_viability_decision_payload(self):
        """Test parsing a viability decision payload."""
        handler = ResumeHandler()

        payload = {
            "kickoff_id": "kickoff_123",
            "approval_type": "viability_decision",
            "viability_decision": {
                "choice": "price_pivot",
                "rationale": "Margins too thin",
                "new_price_target": 99.99,
                "decided_by": "user_789"
            }
        }

        result = handler.process(payload)

        assert result["choice"] == "price_pivot"
        assert result["new_price_target"] == 99.99
        assert result["rationale"] == "Margins too thin"

    def test_parse_cost_pivot_decision(self):
        """Test parsing a cost pivot decision."""
        handler = ResumeHandler()

        payload = {
            "kickoff_id": "kickoff_123",
            "approval_type": "viability_decision",
            "viability_decision": {
                "choice": "cost_pivot",
                "cost_reduction_target": 0.3,
                "features_to_cut": ["premium_support", "advanced_analytics"]
            }
        }

        result = handler.process(payload)

        assert result["choice"] == "cost_pivot"
        assert result["cost_reduction_target"] == 0.3
        assert "premium_support" in result["features_to_cut"]

    def test_parse_kill_decision(self):
        """Test parsing a kill decision."""
        handler = ResumeHandler()

        payload = {
            "kickoff_id": "kickoff_123",
            "approval_type": "viability_decision",
            "viability_decision": {
                "choice": "kill",
                "kill_reason": "Market too small"
            }
        }

        result = handler.process(payload)

        assert result["choice"] == "kill"
        assert result["kill_reason"] == "Market too small"

    def test_parse_segment_pivot_payload(self):
        """Test parsing a segment pivot payload."""
        handler = ResumeHandler()

        payload = {
            "kickoff_id": "kickoff_123",
            "approval_type": "segment_pivot",
            "segment_pivot": {
                "approved": True,
                "new_segment": "Enterprise CIOs",
                "feedback": "Switching to enterprise market"
            }
        }

        result = handler.process(payload)

        assert result["approved"] is True
        assert result["new_segment"] == "Enterprise CIOs"

    def test_parse_creative_rejection(self):
        """Test parsing a creative rejection."""
        handler = ResumeHandler()

        payload = {
            "kickoff_id": "kickoff_123",
            "approval_type": "creative_approval",
            "creative_approval": {
                "variant_id": "problem-v1",
                "status": "rejected",
                "feedback": "Claims too aggressive",
                "revision_notes": "Remove superlative language"
            }
        }

        result = handler.process(payload)

        assert result["approved"] is False
        assert result["status"] == "rejected"
        assert "superlative" in result["revision_notes"]

    def test_parse_invalid_json(self):
        """Test error handling for invalid JSON."""
        handler = ResumeHandler()

        with pytest.raises(ValueError, match="Invalid JSON"):
            handler.process("not valid json")

    def test_parse_missing_kickoff_id(self):
        """Test error handling for missing required field."""
        handler = ResumeHandler()

        with pytest.raises(ValueError):
            handler.process({"approval_type": "creative_approval"})

    def test_convenience_function(self):
        """Test the convenience function."""
        result = parse_resume_payload({
            "kickoff_id": "test_123",
            "approval_type": "creative_approval",
            "creative_approval": {
                "variant_id": "v1",
                "status": "approved"
            }
        })

        assert result["variant_id"] == "v1"
        assert result["approved"] is True


# ===========================================================================
# GUARDIAN REVIEW TOOL TESTS
# ===========================================================================

class TestGuardianReviewTool:
    """Tests for the Guardian Review tool."""

    def test_review_valid_landing_page(self):
        """Test review of a valid landing page."""
        tool = GuardianReviewTool()

        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Great Product - Sign Up Today</title>
</head>
<body>
    <h1>Transform Your Workflow</h1>
    <p>Save time and get more done.</p>
    <form action="/signup">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email">
        <button type="submit">Get Started</button>
    </form>
</body>
</html>"""

        result = tool._run(json.dumps({
            "artifact_type": "landing_page",
            "artifact_id": "lp_001",
            "content": html
        }))

        # Should auto-approve or have minimal issues
        assert "Guardian Review Complete" in result
        assert "auto_approved" in result.lower() or "needs review" in result.lower()

    def test_review_landing_page_with_issues(self):
        """Test review of a landing page with issues."""
        tool = GuardianReviewTool()

        html = """<!DOCTYPE html>
<html>
<head>
    <title>BEST PRODUCT EVER!!!</title>
</head>
<body>
    <h1>GUARANTEED 100% SUCCESS!!!</h1>
    <p>The #1 BEST solution ALWAYS works!!</p>
    <img src="http://example.com/image.jpg">
    <a href="javascript:void(0)">Click here</a>
</body>
</html>"""

        result = tool._run(json.dumps({
            "artifact_type": "landing_page",
            "artifact_id": "lp_002",
            "content": html
        }))

        # Should flag compliance and security issues
        assert "Issues Found" in result or "REJECTED" in result or "NEEDS REVIEW" in result

    def test_review_ad_creative(self):
        """Test review of an ad creative."""
        tool = GuardianReviewTool()

        result = tool._run(json.dumps({
            "artifact_type": "ad_creative",
            "artifact_id": "ad_001",
            "content": {
                "headline": "Boost Your Productivity",
                "body": "Join thousands who save 10+ hours weekly with our tool.",
                "cta": "Learn More",
                "image_url": "https://example.com/ad-image.jpg"
            }
        }))

        assert "Guardian Review Complete" in result
        assert "auto_approved" in result.lower() or "needs review" in result.lower()

    def test_review_ad_with_long_headline(self):
        """Test ad with headline exceeding character limit."""
        tool = GuardianReviewTool()

        result = tool._run(json.dumps({
            "artifact_type": "ad_creative",
            "artifact_id": "ad_002",
            "content": {
                "headline": "This Is An Extremely Long Headline That Definitely Exceeds Platform Character Limits",
                "body": "Short body",
                "cta": "Go",
                "image_url": "https://example.com/image.jpg"
            }
        }))

        # Should flag headline length
        assert "headline" in result.lower() or "too long" in result.lower()

    def test_review_ad_with_http_image(self):
        """Test ad with non-HTTPS image URL."""
        tool = GuardianReviewTool()

        result = tool._run(json.dumps({
            "artifact_type": "ad_creative",
            "artifact_id": "ad_003",
            "content": {
                "headline": "Great Product",
                "body": "Try it today",
                "cta": "Sign Up",
                "image_url": "http://insecure.example.com/image.jpg"
            }
        }))

        # Should flag security issue
        assert "HTTPS" in result or "security" in result.lower() or "REJECTED" in result

    def test_auto_approval_threshold(self):
        """Test auto-approval threshold configuration."""
        # Strict mode - any warning requires human review
        strict_tool = GuardianReviewTool(strict_mode=True)

        result = strict_tool.review_with_result(
            artifact_type="landing_page",
            artifact_id="lp_strict",
            content="<html><head><title>Test</title></head><body>Content</body></html>"
        )

        # Missing lang and other attributes should trigger human review in strict mode
        if result.warning_count > 0:
            assert result.requires_human_review is True

    def test_convenience_function_landing_page(self):
        """Test the review_landing_page convenience function."""
        result = review_landing_page(
            html="<html><head><title>Test</title></head><body>Hello</body></html>",
            artifact_id="test_lp"
        )

        assert "Guardian Review Complete" in result


# ===========================================================================
# METHODOLOGY CHECK TOOL TESTS
# ===========================================================================

class TestMethodologyCheckTool:
    """Tests for the Methodology Check tool."""

    def test_validate_complete_vpc(self):
        """Test validation of a complete VPC."""
        tool = MethodologyCheckTool()

        result = tool._run(json.dumps({
            "methodology_type": "vpc",
            "artifact": {
                "customer_profile": {
                    "customer_jobs": [
                        "Track project progress",
                        "Collaborate with team",
                        "Meet deadlines"
                    ],
                    "pains": [
                        "Scattered communication",
                        "Missed deadlines",
                        "No visibility into progress"
                    ],
                    "gains": [
                        "Clear project overview",
                        "Better team alignment",
                        "Faster delivery"
                    ]
                },
                "value_map": {
                    "products_services": ["Project dashboard", "Team chat", "Task manager"],
                    "pain_relievers": [
                        "Centralized communication",
                        "Deadline reminders",
                        "Progress tracking"
                    ],
                    "gain_creators": [
                        "Visual dashboards",
                        "Real-time updates",
                        "Automated workflows"
                    ]
                }
            }
        }))

        assert "Methodology Check Complete" in result
        assert "VPC" in result

    def test_validate_incomplete_vpc(self):
        """Test validation of an incomplete VPC."""
        tool = MethodologyCheckTool()

        result = tool._run(json.dumps({
            "methodology_type": "vpc",
            "artifact": {
                "customer_profile": {
                    "customer_jobs": ["One job"],
                    # Missing pains and gains
                },
                "value_map": {
                    "products_services": ["Product"],
                    # Missing pain relievers and gain creators
                }
            }
        }))

        # Should flag missing components
        assert "Missing" in result or "critical" in result.lower()

    def test_validate_customer_profile(self):
        """Test validation of just a customer profile."""
        tool = MethodologyCheckTool()

        result = tool._run(json.dumps({
            "methodology_type": "customer_profile",
            "artifact": {
                "customer_jobs": ["Job 1", "Job 2"],
                "pains": ["Pain 1"],
                "gains": ["Gain 1", "Gain 2"]
            }
        }))

        assert "Methodology Check Complete" in result
        assert "Customer Profile" in result or "customer_profile" in result.lower()

    def test_validate_bmc(self):
        """Test validation of a Business Model Canvas."""
        tool = MethodologyCheckTool()

        result = tool._run(json.dumps({
            "methodology_type": "bmc",
            "artifact": {
                "customer_segments": ["SMBs", "Enterprises"],
                "value_propositions": ["Save time", "Reduce costs"],
                "channels": ["Direct sales", "Web"],
                "customer_relationships": ["Self-service", "Dedicated support"],
                "revenue_streams": ["Subscription", "Professional services"],
                "key_resources": ["Platform", "Team"],
                "key_activities": ["Development", "Sales"],
                "key_partnerships": ["Cloud providers"],
                "cost_structure": ["Development", "Infrastructure", "Sales"]
            }
        }))

        assert "Methodology Check Complete" in result
        assert "BMC" in result

    def test_validate_incomplete_bmc(self):
        """Test validation of an incomplete BMC."""
        tool = MethodologyCheckTool()

        result = tool._run(json.dumps({
            "methodology_type": "bmc",
            "artifact": {
                "customer_segments": ["SMBs"],
                "value_propositions": ["Value"],
                # Missing most blocks
            }
        }))

        # Should flag missing required blocks
        assert "Missing" in result or "critical" in result.lower()

    def test_validate_assumption_map(self):
        """Test validation of an assumption map."""
        tool = MethodologyCheckTool()

        result = tool._run(json.dumps({
            "methodology_type": "assumption_map",
            "artifact": {
                "assumptions": [
                    {
                        "hypothesis": "Users will pay $50/month",
                        "risk_level": "critical",
                        "priority": 1
                    },
                    {
                        "hypothesis": "Users prefer web over mobile",
                        "risk_level": "important",
                        "priority": 2
                    }
                ]
            }
        }))

        assert "Methodology Check Complete" in result

    def test_unknown_methodology_type(self):
        """Test error handling for unknown methodology type."""
        tool = MethodologyCheckTool()

        result = tool._run(json.dumps({
            "methodology_type": "unknown_type",
            "artifact": {}
        }))

        assert "Failed" in result or "Unknown" in result

    def test_convenience_function_vpc(self):
        """Test the check_vpc convenience function."""
        result = check_vpc(
            customer_profile={
                "customer_jobs": ["Job 1"],
                "pains": ["Pain 1"],
                "gains": ["Gain 1"]
            },
            value_map={
                "products_services": ["Product"],
                "pain_relievers": ["Relief"],
                "gain_creators": ["Creator"]
            }
        )

        assert "Methodology Check Complete" in result


# ===========================================================================
# GOVERNANCE CREW INITIALIZATION TESTS
# ===========================================================================

class TestGovernanceCrewHITL:
    """Tests for Governance Crew HITL tool wiring."""

    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY required for crew instantiation"
    )
    def test_governance_crew_has_hitl_tools(self):
        """Test that Governance Crew has HITL tools wired."""
        from startupai.crews.governance.governance_crew import GovernanceCrew

        crew = GovernanceCrew()

        # Check tools are instantiated
        assert hasattr(crew, '_guardian_review_tool')
        assert hasattr(crew, '_methodology_check_tool')

        # Check types
        assert isinstance(crew._guardian_review_tool, GuardianReviewTool)
        assert isinstance(crew._methodology_check_tool, MethodologyCheckTool)

    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY required for crew instantiation"
    )
    def test_qa_auditor_has_review_tool(self):
        """Test that qa_auditor agent has review tool."""
        from startupai.crews.governance.governance_crew import GovernanceCrew

        crew = GovernanceCrew()
        agent = crew.qa_auditor()

        tool_names = [t.name for t in agent.tools]
        assert "guardian_review" in tool_names
        assert "methodology_check" in tool_names


# ===========================================================================
# INTEGRATION TESTS
# ===========================================================================

class TestHITLIntegration:
    """Integration tests for the full HITL workflow."""

    def test_creative_review_to_approval_flow(self):
        """Test the flow from creative review to approval."""
        # Step 1: Generate and review a landing page
        review_tool = GuardianReviewTool()
        review_result = review_tool.review_with_result(
            artifact_type="landing_page",
            artifact_id="integration_test_lp",
            content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Integration Test LP</title>
</head>
<body>
    <h1>Test Product</h1>
    <button>Sign Up</button>
</body>
</html>"""
        )

        # Step 2: Based on review, simulate approval or human review
        if review_result.decision == ReviewDecision.AUTO_APPROVED:
            # Auto-approved, can proceed
            approval_payload = {
                "kickoff_id": "integration_test",
                "approval_type": "creative_approval",
                "creative_approval": {
                    "variant_id": "integration_test_lp",
                    "status": "approved",
                    "feedback": "Auto-approved by Guardian"
                }
            }
        else:
            # Needs human review, simulate human approval
            approval_payload = {
                "kickoff_id": "integration_test",
                "approval_type": "creative_approval",
                "creative_approval": {
                    "variant_id": "integration_test_lp",
                    "status": "approved",
                    "feedback": "Manually reviewed and approved"
                }
            }

        # Step 3: Process the approval
        handler = ResumeHandler()
        result = handler.process(approval_payload)

        assert result["approved"] is True
        assert result["variant_id"] == "integration_test_lp"

    def test_methodology_validation_to_pivot_decision(self):
        """Test methodology validation leading to pivot decision."""
        # Step 1: Validate a VPC
        methodology_tool = MethodologyCheckTool()
        validation_result = methodology_tool._run(json.dumps({
            "methodology_type": "vpc",
            "artifact": {
                "customer_profile": {
                    "customer_jobs": ["Manage projects"],
                    "pains": ["Too many tools"],
                    "gains": ["Single source of truth"]
                },
                "value_map": {
                    "products_services": ["Unified platform"],
                    "pain_relievers": ["All-in-one solution"],
                    "gain_creators": ["Central dashboard"]
                }
            }
        }))

        # Should pass basic validation
        assert "Methodology Check Complete" in validation_result

        # Step 2: Based on validation, simulate a segment pivot decision
        pivot_payload = {
            "kickoff_id": "methodology_test",
            "approval_type": "segment_pivot",
            "segment_pivot": {
                "approved": True,
                "new_segment": "Project Managers at SMBs",
                "feedback": "Narrowing focus based on validation results"
            }
        }

        handler = ResumeHandler()
        result = handler.process(pivot_payload)

        assert result["approved"] is True
        assert result["new_segment"] == "Project Managers at SMBs"


# ===========================================================================
# CREATIVE APPROVAL FLOW NODE TESTS
# ===========================================================================

class TestCreativeApprovalFlowNode:
    """Tests for the creative approval flow node in FounderValidationFlow."""

    def test_flow_has_creative_approval_methods(self):
        """Test that FounderValidationFlow has creative approval methods."""
        from startupai.flows._founder_validation_flow import FounderValidationFlow

        # Check methods exist
        assert hasattr(FounderValidationFlow, 'review_creatives_for_deployment')
        assert hasattr(FounderValidationFlow, 'creative_approval_gate')
        assert hasattr(FounderValidationFlow, 'pause_for_creative_approval')
        assert hasattr(FounderValidationFlow, 'proceed_with_approved_creatives')
        assert hasattr(FounderValidationFlow, 'handle_rejected_creatives')
        assert hasattr(FounderValidationFlow, '_handle_creative_resume')

    def test_state_has_creative_fields(self):
        """Test that ValidationState has creative review fields."""
        from startupai.flows.state_schemas import StartupValidationState

        state = StartupValidationState()

        # Check fields exist with default values
        assert hasattr(state, 'landing_pages')
        assert hasattr(state, 'creative_review_results')
        assert hasattr(state, 'creatives_needing_human_review')
        assert hasattr(state, 'auto_approved_creatives')

        # Check default values
        assert state.landing_pages == []
        assert state.creative_review_results == []
        assert state.creatives_needing_human_review == []
        assert state.auto_approved_creatives == []

    def test_handle_creative_resume(self):
        """Test the _handle_creative_resume method."""
        from startupai.flows._founder_validation_flow import FounderValidationFlow
        from startupai.flows.state_schemas import StartupValidationState

        # Create a flow with initial state
        flow = FounderValidationFlow(
            entrepreneur_input="Test business idea",
            project_id="test_project",
            user_id="test_user",
        )

        # Initialize state fields
        flow.state.creatives_needing_human_review = [
            {"artifact_id": "lp_1", "issues": [], "summary": "Test"},
            {"artifact_id": "lp_2", "issues": [], "summary": "Test"},
        ]
        flow.state.auto_approved_creatives = []
        flow.state.human_input_required = True
        flow.state.guardian_last_issues = []

        # Simulate approval
        approval_payload = {
            "approved_artifact_ids": ["lp_1", "lp_2"],
            "rejected_artifact_ids": [],
            "feedback": ""
        }

        flow._handle_creative_resume(approval_payload)

        # Verify state updated
        assert flow.state.human_input_required is False
        assert "lp_1" in flow.state.auto_approved_creatives
        assert "lp_2" in flow.state.auto_approved_creatives

    def test_handle_creative_resume_with_rejection(self):
        """Test handling creative rejection with feedback."""
        from startupai.flows._founder_validation_flow import FounderValidationFlow

        flow = FounderValidationFlow(
            entrepreneur_input="Test business idea",
            project_id="test_project",
        )

        flow.state.creatives_needing_human_review = [
            {"artifact_id": "lp_1", "issues": [], "summary": "Test"},
        ]
        flow.state.auto_approved_creatives = []
        flow.state.human_input_required = True
        flow.state.guardian_last_issues = []

        # Simulate rejection with feedback
        rejection_payload = {
            "approved_artifact_ids": [],
            "rejected_artifact_ids": ["lp_1"],
            "feedback": "Please fix the headline"
        }

        flow._handle_creative_resume(rejection_payload)

        # Verify feedback captured
        assert "Creative feedback: Please fix the headline" in flow.state.guardian_last_issues
