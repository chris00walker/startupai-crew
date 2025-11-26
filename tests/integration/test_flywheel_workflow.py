"""
Tests for Phase 2C: Flywheel Learning System.

Tests cover:
1. FlywheelInsightsTool - Industry/stage pattern retrieval
2. OutcomeTrackerTool - Prediction tracking and outcome recording
3. Cross-validation context retrieval
4. Governance Crew integration
"""

import pytest
import json
from unittest.mock import Mock, patch

from startupai.tools.flywheel_insights import (
    FlywheelInsightsTool,
    OutcomeTrackerTool,
    StartupStage,
    IndustryVertical,
    PredictionType,
    ValidationContext,
    PatternLearning,
    OutcomePrediction,
    FlywheelInsight,
    get_flywheel_insights,
    capture_flywheel_pattern,
    track_prediction,
    record_prediction_outcome,
)


# =======================================================================================
# FLYWHEEL INSIGHTS TOOL TESTS
# =======================================================================================

class TestFlywheelInsightsTool:
    """Tests for FlywheelInsightsTool."""

    def test_tool_creation(self):
        """Test tool can be instantiated."""
        tool = FlywheelInsightsTool()
        assert tool.name == "flywheel_insights"
        assert "Flywheel" in tool.description

    def test_get_insights_saas_b2b(self):
        """Test getting insights for SaaS B2B industry."""
        tool = FlywheelInsightsTool()
        result = tool._run(json.dumps({
            "action": "get_insights",
            "context": {
                "industry": "saas_b2b",
                "stage": "problem_validated",
                "phase": "desirability",
            },
            "query": "Testing B2B SaaS landing page",
        }))

        assert "Industry Patterns" in result
        assert "saas" in result.lower() or "SaaS" in result
        assert "CAC" in result
        assert "LTV" in result

    def test_get_insights_marketplace(self):
        """Test getting insights for marketplace industry."""
        tool = FlywheelInsightsTool()
        result = tool._run(json.dumps({
            "action": "get_insights",
            "context": {
                "industry": "marketplace",
                "stage": "ideation",
            },
        }))

        assert "Industry Patterns" in result
        assert "chicken" in result.lower() or "supply" in result.lower()

    def test_get_insights_with_stage_guidance(self):
        """Test stage-specific guidance is included."""
        tool = FlywheelInsightsTool()
        result = tool._run(json.dumps({
            "action": "get_insights",
            "context": {
                "industry": "saas_b2c",
                "stage": "ideation",
            },
        }))

        assert "Stage Guidance" in result
        assert "Problem validation" in result or "Don't build" in result

    def test_get_insights_for_context_programmatic(self):
        """Test programmatic access returns structured dict."""
        tool = FlywheelInsightsTool()
        result = tool.get_insights_for_context(
            industry="saas_b2b",
            stage="solution_validated",
            current_situation="Testing pricing",
            phase="viability",
        )

        assert isinstance(result, dict)
        assert "industry_patterns" in result
        assert "stage_guidance" in result
        assert "recommendations" in result
        assert result["industry_patterns"].get("typical_ltv_cac") == (3, 7)

    def test_capture_pattern(self):
        """Test capturing a new pattern."""
        tool = FlywheelInsightsTool()
        result = tool._run(json.dumps({
            "action": "capture_pattern",
            "title": "High churn in B2B SaaS",
            "description": "When customer support response > 24h, churn doubles",
            "context": {
                "industry": "saas_b2b",
                "stage": "pmf",
            },
            "tags": ["churn", "support", "retention"],
            "confidence": 0.85,
        }))

        assert "Pattern captured" in result
        assert "High churn" in result or "churn" in result.lower()

    def test_capture_pattern_requires_title(self):
        """Test that pattern capture requires title."""
        tool = FlywheelInsightsTool()
        result = tool._run(json.dumps({
            "action": "capture_pattern",
            "description": "Some description",
        }))

        assert "Error" in result
        assert "title" in result.lower()

    def test_track_prediction(self):
        """Test tracking a prediction."""
        tool = FlywheelInsightsTool()
        result = tool._run(json.dumps({
            "action": "track_prediction",
            "validation_id": "val_123",
            "prediction_type": "gate_decision",
            "phase": "desirability",
            "predicted_outcome": "proceed",
            "confidence": 0.8,
            "reasoning": "Strong customer resonance signals",
        }))

        assert "Prediction tracked" in result
        assert "gate_decision" in result

    def test_record_outcome(self):
        """Test recording actual outcome."""
        tool = FlywheelInsightsTool()
        result = tool._run(json.dumps({
            "action": "record_outcome",
            "prediction_id": "pred_456",
            "actual_outcome": "proceeded_successfully",
            "variance_notes": "Slightly better than expected",
        }))

        assert "Outcome recorded" in result
        assert "pred_456" in result

    def test_get_stage_guidance(self):
        """Test getting detailed stage guidance."""
        tool = FlywheelInsightsTool()
        result = tool._run(json.dumps({
            "action": "get_guidance",
            "stage": "problem_validated",
        }))

        assert "Problem Validated" in result
        assert "Solution-problem fit" in result
        assert "Success Criteria" in result

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON input."""
        tool = FlywheelInsightsTool()
        result = tool._run("not valid json")

        assert "Error" in result

    def test_unknown_action(self):
        """Test handling of unknown action."""
        tool = FlywheelInsightsTool()
        result = tool._run(json.dumps({
            "action": "unknown_action",
        }))

        assert "Unknown action" in result

    def test_industry_patterns_completeness(self):
        """Test that all expected industry patterns exist."""
        tool = FlywheelInsightsTool()

        assert "saas_b2b" in tool.INDUSTRY_PATTERNS
        assert "saas_b2c" in tool.INDUSTRY_PATTERNS
        assert "marketplace" in tool.INDUSTRY_PATTERNS
        assert "ecommerce" in tool.INDUSTRY_PATTERNS

        # Check pattern structure
        saas_pattern = tool.INDUSTRY_PATTERNS["saas_b2b"]
        assert "typical_cac_range" in saas_pattern
        assert "typical_ltv_cac" in saas_pattern
        assert "common_pivots" in saas_pattern
        assert "warning_signs" in saas_pattern

    def test_stage_guidance_completeness(self):
        """Test that all expected stage guidance exists."""
        tool = FlywheelInsightsTool()

        assert "ideation" in tool.STAGE_GUIDANCE
        assert "problem_validated" in tool.STAGE_GUIDANCE
        assert "solution_validated" in tool.STAGE_GUIDANCE

        # Check guidance structure
        ideation = tool.STAGE_GUIDANCE["ideation"]
        assert "focus" in ideation
        assert "key_questions" in ideation
        assert "common_mistakes" in ideation
        assert "success_criteria" in ideation


# =======================================================================================
# OUTCOME TRACKER TOOL TESTS
# =======================================================================================

class TestOutcomeTrackerTool:
    """Tests for OutcomeTrackerTool."""

    def test_tool_creation(self):
        """Test tool can be instantiated."""
        tool = OutcomeTrackerTool()
        assert tool.name == "outcome_tracker"
        assert "prediction" in tool.description.lower()

    def test_make_prediction_programmatic(self):
        """Test programmatic prediction creation."""
        tool = OutcomeTrackerTool()
        prediction = tool.make_prediction(
            validation_id="val_789",
            prediction_type="pivot_success",
            predicted_outcome="successful_pivot",
            confidence=0.7,
            reasoning="Market segment more receptive",
            context={"industry": "saas_b2b"},
        )

        assert prediction["id"] is not None
        assert prediction["validation_id"] == "val_789"
        assert prediction["prediction_type"] == "pivot_success"
        assert prediction["confidence"] == 0.7
        assert prediction["actual_outcome"] is None

    def test_record_outcome_programmatic(self):
        """Test programmatic outcome recording."""
        tool = OutcomeTrackerTool()
        result = tool.record_outcome(
            prediction_id="pred_123",
            actual_outcome="pivot_successful",
            notes="Conversion improved 3x after pivot",
        )

        assert result["prediction_id"] == "pred_123"
        assert result["actual_outcome"] == "pivot_successful"
        assert result["learning_captured"] is True

    def test_make_prediction_via_run(self):
        """Test prediction via _run method."""
        tool = OutcomeTrackerTool()
        result = tool._run(json.dumps({
            "action": "predict",
            "validation_id": "val_test",
            "prediction_type": "desirability_outcome",
            "predicted_outcome": "high_conversion",
            "confidence": 0.6,
            "reasoning": "Strong pain point identified",
        }))

        assert "Prediction Recorded" in result
        assert "desirability_outcome" in result
        assert "60%" in result

    def test_record_outcome_via_run(self):
        """Test outcome recording via _run method."""
        tool = OutcomeTrackerTool()
        result = tool._run(json.dumps({
            "action": "record_outcome",
            "prediction_id": "pred_test",
            "actual_outcome": "moderate_conversion",
            "notes": "Below expectation due to seasonality",
        }))

        assert "Outcome Recorded" in result
        assert "moderate_conversion" in result

    def test_get_accuracy_metrics(self):
        """Test accuracy metrics retrieval."""
        tool = OutcomeTrackerTool()
        result = tool._run(json.dumps({
            "action": "get_accuracy",
            "prediction_type": "gate_decision",
            "time_range": "30d",
        }))

        assert "Accuracy Metrics" in result
        assert "gate_decision" in result
        assert "%" in result

    def test_invalid_action(self):
        """Test handling of invalid action."""
        tool = OutcomeTrackerTool()
        result = tool._run(json.dumps({
            "action": "invalid",
        }))

        assert "Unknown action" in result


# =======================================================================================
# MODEL TESTS
# =======================================================================================

class TestFlywheelModels:
    """Tests for Flywheel data models."""

    def test_validation_context_creation(self):
        """Test ValidationContext model."""
        context = ValidationContext(
            industry=IndustryVertical.SAAS_B2B,
            stage=StartupStage.PROBLEM_VALIDATED,
            target_segment="SMB",
            business_model="subscription",
            ltv_cac_ratio=4.5,
            pivot_count=1,
        )

        assert context.industry == IndustryVertical.SAAS_B2B
        assert context.stage == StartupStage.PROBLEM_VALIDATED
        assert context.ltv_cac_ratio == 4.5
        assert context.pivot_count == 1

    def test_pattern_learning_creation(self):
        """Test PatternLearning model."""
        context = ValidationContext(industry=IndustryVertical.MARKETPLACE)
        pattern = PatternLearning(
            title="Supply-side acquisition first",
            description="Marketplaces should build supply before demand",
            context=context,
            tags=["marketplace", "chicken-egg"],
            confidence_score=0.9,
            when_to_apply="Early marketplace validation",
            expected_outcome="Easier demand acquisition with supply ready",
        )

        assert pattern.id is not None
        assert pattern.learning_type == "pattern"
        assert pattern.confidence_score == 0.9
        assert "marketplace" in pattern.tags

    def test_outcome_prediction_creation(self):
        """Test OutcomePrediction model."""
        prediction = OutcomePrediction(
            prediction_type=PredictionType.GATE_DECISION,
            validation_id="val_123",
            phase="desirability",
            context=ValidationContext(),
            predicted_outcome="proceed",
            confidence=0.75,
            reasoning="Evidence supports market need",
        )

        assert prediction.prediction_type == PredictionType.GATE_DECISION
        assert prediction.predicted_outcome == "proceed"
        assert prediction.actual_outcome is None
        assert prediction.was_correct is None

    def test_flywheel_insight_creation(self):
        """Test FlywheelInsight model."""
        insight = FlywheelInsight(
            insight_type="pattern_cluster",
            title="B2B SaaS pricing patterns",
            description="Value-based pricing outperforms cost-plus",
            supporting_evidence=["pattern_1", "pattern_2"],
            confidence=0.85,
            applicable_contexts=["saas_b2b", "solution_validated"],
        )

        assert insight.insight_type == "pattern_cluster"
        assert len(insight.supporting_evidence) == 2
        assert insight.confidence == 0.85


# =======================================================================================
# ENUM TESTS
# =======================================================================================

class TestFlywheelEnums:
    """Tests for Flywheel enums."""

    def test_startup_stage_values(self):
        """Test StartupStage enum values."""
        assert StartupStage.IDEATION.value == "ideation"
        assert StartupStage.PROBLEM_VALIDATED.value == "problem_validated"
        assert StartupStage.SOLUTION_VALIDATED.value == "solution_validated"
        assert StartupStage.PRODUCT_MARKET_FIT.value == "pmf"
        assert StartupStage.SCALING.value == "scaling"

    def test_industry_vertical_values(self):
        """Test IndustryVertical enum values."""
        assert IndustryVertical.SAAS_B2B.value == "saas_b2b"
        assert IndustryVertical.SAAS_B2C.value == "saas_b2c"
        assert IndustryVertical.MARKETPLACE.value == "marketplace"
        assert IndustryVertical.ECOMMERCE.value == "ecommerce"
        assert IndustryVertical.FINTECH.value == "fintech"
        assert IndustryVertical.AI_ML.value == "ai_ml"

    def test_prediction_type_values(self):
        """Test PredictionType enum values."""
        assert PredictionType.DESIRABILITY_OUTCOME.value == "desirability_outcome"
        assert PredictionType.FEASIBILITY_OUTCOME.value == "feasibility_outcome"
        assert PredictionType.VIABILITY_OUTCOME.value == "viability_outcome"
        assert PredictionType.PIVOT_SUCCESS.value == "pivot_success"
        assert PredictionType.GATE_DECISION.value == "gate_decision"


# =======================================================================================
# CONVENIENCE FUNCTION TESTS
# =======================================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_flywheel_insights(self):
        """Test get_flywheel_insights convenience function."""
        result = get_flywheel_insights(
            industry="saas_b2b",
            stage="ideation",
            situation="Testing new SaaS idea",
            phase="desirability",
        )

        assert "Flywheel Insights" in result
        assert "Industry Patterns" in result

    def test_capture_flywheel_pattern(self):
        """Test capture_flywheel_pattern convenience function."""
        result = capture_flywheel_pattern(
            title="Test pattern",
            description="Testing pattern capture",
            industry="marketplace",
            stage="problem_validated",
            tags=["test"],
        )

        assert "Pattern captured" in result

    def test_track_prediction(self):
        """Test track_prediction convenience function."""
        result = track_prediction(
            validation_id="val_conv",
            prediction_type="gate_decision",
            predicted_outcome="proceed",
            confidence=0.8,
            reasoning="Strong signals",
        )

        assert "Prediction Recorded" in result

    def test_record_prediction_outcome(self):
        """Test record_prediction_outcome convenience function."""
        result = record_prediction_outcome(
            prediction_id="pred_conv",
            actual_outcome="proceeded_successfully",
            notes="Met expectations",
        )

        assert "Outcome Recorded" in result


# =======================================================================================
# GOVERNANCE CREW INTEGRATION TESTS
# =======================================================================================

import os

# Check for OPENAI_API_KEY availability
HAS_OPENAI_KEY = bool(os.environ.get("OPENAI_API_KEY"))
SKIP_REASON = "OPENAI_API_KEY required for CrewAI agent instantiation"


class TestGovernanceCrewIntegration:
    """Tests for Governance Crew integration with Flywheel tools."""

    @pytest.mark.skipif(not HAS_OPENAI_KEY, reason=SKIP_REASON)
    def test_governance_crew_has_flywheel_tools(self):
        """Test Governance Crew has Flywheel tools wired."""
        from startupai.crews.governance.governance_crew import GovernanceCrew

        crew = GovernanceCrew()

        # Check tools exist
        assert hasattr(crew, '_flywheel_insights_tool')
        assert hasattr(crew, '_outcome_tracker_tool')
        assert isinstance(crew._flywheel_insights_tool, FlywheelInsightsTool)
        assert isinstance(crew._outcome_tracker_tool, OutcomeTrackerTool)

    @pytest.mark.skipif(not HAS_OPENAI_KEY, reason=SKIP_REASON)
    def test_qa_auditor_has_flywheel_insights(self):
        """Test qa_auditor agent has FlywheelInsightsTool."""
        from startupai.crews.governance.governance_crew import GovernanceCrew

        crew = GovernanceCrew()
        agent = crew.qa_auditor()

        tool_names = [t.name for t in agent.tools]
        assert "flywheel_insights" in tool_names

    @pytest.mark.skipif(not HAS_OPENAI_KEY, reason=SKIP_REASON)
    def test_accountability_tracker_has_outcome_tracker(self):
        """Test accountability_tracker agent has OutcomeTrackerTool."""
        from startupai.crews.governance.governance_crew import GovernanceCrew

        crew = GovernanceCrew()
        agent = crew.accountability_tracker()

        tool_names = [t.name for t in agent.tools]
        assert "outcome_tracker" in tool_names
        assert "flywheel_insights" in tool_names

    @pytest.mark.skipif(not HAS_OPENAI_KEY, reason=SKIP_REASON)
    def test_flywheel_tasks_exist(self):
        """Test Flywheel-related tasks are defined."""
        from startupai.crews.governance.governance_crew import GovernanceCrew

        crew = GovernanceCrew()

        # Check task methods exist
        assert hasattr(crew, 'retrieve_similar_validations')
        assert hasattr(crew, 'track_predictions')
        assert hasattr(crew, 'record_outcomes')

        # Verify they return Task objects
        task = crew.retrieve_similar_validations()
        assert task is not None

    def test_governance_crew_flywheel_imports(self):
        """Test that Governance Crew can import Flywheel tools (no API key needed)."""
        # This test verifies the import path works without instantiating the crew
        from startupai.crews.governance.governance_crew import (
            GovernanceCrew,
            FlywheelInsightsTool,
            OutcomeTrackerTool,
        )

        # Verify tools can be instantiated independently
        flywheel_tool = FlywheelInsightsTool()
        outcome_tool = OutcomeTrackerTool()

        assert flywheel_tool.name == "flywheel_insights"
        assert outcome_tool.name == "outcome_tracker"


# =======================================================================================
# TOOLS EXPORT TESTS
# =======================================================================================

class TestToolsExport:
    """Tests for tools module exports."""

    def test_flywheel_tools_exported(self):
        """Test Flywheel tools are exported from tools module."""
        from startupai.tools import (
            FlywheelInsightsTool,
            OutcomeTrackerTool,
            StartupStage,
            IndustryVertical,
            PredictionType,
            ValidationContext,
            PatternLearning,
            OutcomePrediction,
            FlywheelInsight,
            get_flywheel_insights,
            capture_flywheel_pattern,
            track_prediction,
            record_prediction_outcome,
        )

        # Verify all imports work
        assert FlywheelInsightsTool is not None
        assert OutcomeTrackerTool is not None
        assert StartupStage.IDEATION is not None
        assert IndustryVertical.SAAS_B2B is not None
        assert PredictionType.GATE_DECISION is not None
        assert ValidationContext is not None
        assert PatternLearning is not None
        assert OutcomePrediction is not None
        assert FlywheelInsight is not None
        assert callable(get_flywheel_insights)
        assert callable(capture_flywheel_pattern)
        assert callable(track_prediction)
        assert callable(record_prediction_outcome)
