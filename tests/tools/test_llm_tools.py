"""
Tests for LLM-Based Tools (Phase D).

Tests CanvasBuilderTool, TestCardTool, and LearningCardTool.
These tools generate structured outputs using LLM prompts.
"""

import json
import pytest

from shared.tools.llm_tools import (
    CanvasBuilderTool,
    TestCardTool,
    LearningCardTool,
    build_canvas_element,
    design_test_card,
    capture_learning,
    CanvasBuilderOutput,
    TestCardOutput,
    LearningCardOutput,
    CanvasElement,
    TestCard,
    LearningCard,
    CanvasElementType,
    ExperimentType,
    EvidenceType,
    SignalStrength,
)


# ===========================================================================
# TEST FIXTURES
# ===========================================================================


@pytest.fixture
def canvas_builder_tool():
    """Create a CanvasBuilderTool instance."""
    return CanvasBuilderTool()


@pytest.fixture
def test_card_tool():
    """Create a TestCardTool instance."""
    return TestCardTool()


@pytest.fixture
def learning_card_tool():
    """Create a LearningCardTool instance."""
    return LearningCardTool()


@pytest.fixture
def sample_customer_profile():
    """Sample customer profile for testing."""
    return {
        "customer_jobs": [
            "Manage team schedules efficiently",
            "Track project progress",
            "Communicate with remote team members",
        ],
        "customer_pains": [
            "Too many meetings waste time",
            "Hard to get accurate project status",
            "Communication gets lost across tools",
        ],
        "customer_gains": [
            "Save 5 hours per week on admin tasks",
            "Real-time visibility into project health",
            "Single source of truth for team",
        ],
        "business_context": "B2B SaaS for remote team management",
    }


# ===========================================================================
# CANVAS BUILDER TOOL TESTS
# ===========================================================================


class TestCanvasBuilderTool:
    """Tests for CanvasBuilderTool."""

    def test_tool_has_correct_name(self, canvas_builder_tool):
        """Tool should have correct name."""
        assert canvas_builder_tool.name == "build_canvas_element"

    def test_tool_has_description(self, canvas_builder_tool):
        """Tool should have a description."""
        assert len(canvas_builder_tool.description) > 50
        assert "canvas" in canvas_builder_tool.description.lower()

    def test_builds_product_service_elements(self, canvas_builder_tool, sample_customer_profile):
        """Tool should build product/service elements."""
        input_data = json.dumps({
            "element_type": "product_service",
            **sample_customer_profile,
        })
        result = canvas_builder_tool._run(input_data)

        assert "# Canvas Elements" in result
        assert "Product Service" in result or "product_service" in result.lower()
        assert "Priority" in result
        assert "Assumptions" in result

    def test_builds_pain_reliever_elements(self, canvas_builder_tool, sample_customer_profile):
        """Tool should build pain reliever elements."""
        input_data = json.dumps({
            "element_type": "pain_reliever",
            **sample_customer_profile,
        })
        result = canvas_builder_tool._run(input_data)

        assert "# Canvas Elements" in result
        assert "Pain Reliever" in result or "pain_reliever" in result.lower()

    def test_builds_gain_creator_elements(self, canvas_builder_tool, sample_customer_profile):
        """Tool should build gain creator elements."""
        input_data = json.dumps({
            "element_type": "gain_creator",
            **sample_customer_profile,
        })
        result = canvas_builder_tool._run(input_data)

        assert "# Canvas Elements" in result
        assert "Gain Creator" in result or "gain_creator" in result.lower()

    def test_accepts_string_input(self, canvas_builder_tool):
        """Tool should accept simple string context."""
        result = canvas_builder_tool._run("A mobile app for pet owners")

        assert "# Canvas Elements" in result
        # Should create placeholder when no specific jobs/pains/gains provided
        assert "Placeholder" in result or "element" in result.lower()

    def test_includes_assumptions(self, canvas_builder_tool, sample_customer_profile):
        """Tool should include assumptions to test."""
        input_data = json.dumps({
            "element_type": "product_service",
            **sample_customer_profile,
        })
        result = canvas_builder_tool._run(input_data)

        assert "Assumptions to Test" in result or "Assumptions" in result

    def test_includes_evidence_needed(self, canvas_builder_tool, sample_customer_profile):
        """Tool should include evidence needed."""
        input_data = json.dumps({
            "element_type": "product_service",
            **sample_customer_profile,
        })
        result = canvas_builder_tool._run(input_data)

        assert "Evidence Needed" in result or "Evidence" in result

    def test_handles_empty_inputs(self, canvas_builder_tool):
        """Tool should handle empty inputs gracefully."""
        input_data = json.dumps({
            "element_type": "product_service",
            "customer_jobs": [],
            "customer_pains": [],
            "customer_gains": [],
        })
        result = canvas_builder_tool._run(input_data)

        assert "# Canvas Elements" in result
        # Should create placeholder
        assert "Placeholder" in result or "Total Elements" in result


# ===========================================================================
# TEST CARD TOOL TESTS
# ===========================================================================


class TestTestCardTool:
    """Tests for TestCardTool."""

    def test_tool_has_correct_name(self, test_card_tool):
        """Tool should have correct name."""
        assert test_card_tool.name == "design_test_card"

    def test_tool_has_description(self, test_card_tool):
        """Tool should have a description."""
        assert len(test_card_tool.description) > 50
        assert "test" in test_card_tool.description.lower()

    def test_generates_test_cards_for_assumptions(self, test_card_tool):
        """Tool should generate test cards for assumptions."""
        input_data = json.dumps({
            "assumptions": [
                "Customers spend 5+ hours on admin tasks weekly",
                "Customers will pay $50/month for time savings",
            ],
            "experiment_type": "interview",
            "time_budget": "2 weeks",
        })
        result = test_card_tool._run(input_data)

        assert "# Test Cards" in result
        assert "Hypothesis" in result
        assert "We believe that" in result

    def test_includes_success_criteria(self, test_card_tool):
        """Tool should include success criteria."""
        input_data = json.dumps({
            "assumptions": ["Users prefer mobile apps"],
            "experiment_type": "survey",
        })
        result = test_card_tool._run(input_data)

        assert "Success Criteria" in result

    def test_includes_metric(self, test_card_tool):
        """Tool should include measurement metric."""
        input_data = json.dumps({
            "assumptions": ["Users will sign up"],
            "experiment_type": "landing_page",
        })
        result = test_card_tool._run(input_data)

        assert "Metric" in result

    def test_supports_different_experiment_types(self, test_card_tool):
        """Tool should support different experiment types."""
        for exp_type in ["interview", "survey", "landing_page", "ad_campaign", "prototype"]:
            input_data = json.dumps({
                "assumptions": ["Test assumption"],
                "experiment_type": exp_type,
            })
            result = test_card_tool._run(input_data)

            assert exp_type in result or "Test Cards" in result

    def test_accepts_simple_assumption_string(self, test_card_tool):
        """Tool should accept simple assumption string."""
        result = test_card_tool._run("Users want faster checkout")

        assert "# Test Cards" in result
        assert "We believe that" in result

    def test_requires_assumptions(self, test_card_tool):
        """Tool should require assumptions."""
        input_data = json.dumps({
            "experiment_type": "interview",
        })
        result = test_card_tool._run(input_data)

        assert "error" in result.lower() or "No assumptions" in result

    def test_includes_time_box(self, test_card_tool):
        """Tool should include time box."""
        input_data = json.dumps({
            "assumptions": ["Test assumption"],
            "time_budget": "1 week",
        })
        result = test_card_tool._run(input_data)

        assert "Time Box" in result or "1 week" in result


# ===========================================================================
# LEARNING CARD TOOL TESTS
# ===========================================================================


class TestLearningCardTool:
    """Tests for LearningCardTool."""

    def test_tool_has_correct_name(self, learning_card_tool):
        """Tool should have correct name."""
        assert learning_card_tool.name == "capture_learning"

    def test_tool_has_description(self, learning_card_tool):
        """Tool should have a description."""
        assert len(learning_card_tool.description) > 50
        assert "learning" in learning_card_tool.description.lower()

    def test_generates_learning_card(self, learning_card_tool):
        """Tool should generate learning card from experiment results."""
        input_data = json.dumps({
            "hypothesis": "Customers spend 5+ hours on admin tasks weekly",
            "observation": "4 out of 5 interviewees confirmed spending 6+ hours on admin",
            "signal_strength": "strong",
            "sample_size": 5,
        })
        result = learning_card_tool._run(input_data)

        assert "# Learning Card" in result
        assert "Hypothesis Tested" in result
        assert "We Observed" in result

    def test_includes_insight(self, learning_card_tool):
        """Tool should include insight."""
        input_data = json.dumps({
            "hypothesis": "Test hypothesis",
            "observation": "Test observation",
        })
        result = learning_card_tool._run(input_data)

        assert "Learned" in result

    def test_includes_decision(self, learning_card_tool):
        """Tool should include decision."""
        input_data = json.dumps({
            "hypothesis": "Test hypothesis",
            "observation": "Test observation",
        })
        result = learning_card_tool._run(input_data)

        assert "Therefore We Will" in result

    def test_strong_signal_recommendation(self, learning_card_tool):
        """Strong signal should recommend proceeding."""
        input_data = json.dumps({
            "hypothesis": "Test hypothesis",
            "observation": "Strong confirmation",
            "signal_strength": "strong",
        })
        result = learning_card_tool._run(input_data)

        assert "STRONG" in result
        assert "Proceed" in result or "confidence" in result.lower()

    def test_weak_signal_recommendation(self, learning_card_tool):
        """Weak signal should recommend pivoting."""
        input_data = json.dumps({
            "hypothesis": "Test hypothesis",
            "observation": "Poor results",
            "signal_strength": "weak",
        })
        result = learning_card_tool._run(input_data)

        assert "WEAK" in result
        assert "Pivot" in result or "alternative" in result.lower()

    def test_includes_sample_size(self, learning_card_tool):
        """Tool should include sample size in output."""
        input_data = json.dumps({
            "hypothesis": "Test hypothesis",
            "observation": "Test observation",
            "sample_size": 25,
        })
        result = learning_card_tool._run(input_data)

        assert "Sample Size" in result or "25" in result

    def test_includes_quotes(self, learning_card_tool):
        """Tool should include supporting quotes."""
        input_data = json.dumps({
            "hypothesis": "Test hypothesis",
            "observation": "Test observation",
            "quotes": ["I spend way too much time on admin", "This would save me hours"],
        })
        result = learning_card_tool._run(input_data)

        assert "Supporting Evidence" in result or "too much time" in result

    def test_requires_hypothesis_and_observation(self, learning_card_tool):
        """Tool should require hypothesis and observation."""
        # Missing observation
        result = learning_card_tool._run(json.dumps({"hypothesis": "Test"}))
        assert "error" in result.lower() or "required" in result.lower()

        # Missing hypothesis
        result = learning_card_tool._run(json.dumps({"observation": "Test"}))
        assert "error" in result.lower() or "required" in result.lower()

    def test_requires_json_input(self, learning_card_tool):
        """Tool should require JSON input."""
        result = learning_card_tool._run("just a string")
        assert "error" in result.lower() or "JSON" in result


# ===========================================================================
# CONVENIENCE FUNCTION TESTS
# ===========================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_build_canvas_element_function(self):
        """build_canvas_element() convenience function should work."""
        result = build_canvas_element(
            element_type="product_service",
            customer_jobs=["Manage team schedules"],
            business_context="B2B SaaS",
        )
        assert "# Canvas Elements" in result

    def test_design_test_card_function(self):
        """design_test_card() convenience function should work."""
        result = design_test_card(
            assumptions=["Users want feature X"],
            experiment_type="survey",
            time_budget="1 week",
        )
        assert "# Test Cards" in result

    def test_capture_learning_function(self):
        """capture_learning() convenience function should work."""
        result = capture_learning(
            hypothesis="Test hypothesis",
            observation="Test observation",
            signal_strength="moderate",
        )
        assert "# Learning Card" in result


# ===========================================================================
# PYDANTIC MODEL TESTS
# ===========================================================================


class TestPydanticModels:
    """Tests for Pydantic output models."""

    def test_canvas_element_model(self):
        """CanvasElement model should be valid."""
        element = CanvasElement(
            element_type=CanvasElementType.PRODUCT_SERVICE,
            name="Test Product",
            description="A test product description",
            target_job="Help users do X",
            priority=1,
            assumptions=["Assumption 1", "Assumption 2"],
            evidence_needed=["Evidence 1"],
        )
        assert element.element_type == CanvasElementType.PRODUCT_SERVICE
        assert element.priority == 1
        assert len(element.assumptions) == 2

    def test_canvas_builder_output_model(self):
        """CanvasBuilderOutput model should be valid."""
        output = CanvasBuilderOutput(
            element_type=CanvasElementType.PAIN_RELIEVER,
            elements=[
                CanvasElement(
                    element_type=CanvasElementType.PAIN_RELIEVER,
                    name="Pain Fix",
                    description="Fixes the pain",
                    priority=1,
                )
            ],
            total_elements=1,
        )
        assert output.element_type == CanvasElementType.PAIN_RELIEVER
        assert output.total_elements == 1
        assert output.timestamp is not None

    def test_test_card_model(self):
        """TestCard model should be valid."""
        card = TestCard(
            hypothesis="We believe that X",
            test_description="To verify, we will do Y",
            metric="Measure Z",
            success_criteria="Right if Z > 50%",
            experiment_type=ExperimentType.INTERVIEW,
            evidence_type=EvidenceType.SAY,
            time_box="1 week",
            priority=1,
        )
        assert card.experiment_type == ExperimentType.INTERVIEW
        assert card.evidence_type == EvidenceType.SAY

    def test_test_card_output_model(self):
        """TestCardOutput model should be valid."""
        output = TestCardOutput(
            test_cards=[
                TestCard(
                    hypothesis="Test",
                    test_description="Test",
                    metric="Test",
                    success_criteria="Test",
                    experiment_type=ExperimentType.SURVEY,
                    evidence_type=EvidenceType.SAY,
                    time_box="1 week",
                    priority=1,
                )
            ],
            total_cards=1,
        )
        assert output.total_cards == 1
        assert output.timestamp is not None

    def test_learning_card_model(self):
        """LearningCard model should be valid."""
        card = LearningCard(
            hypothesis_tested="We believed X",
            observation="We observed Y",
            insight="We learned Z",
            decision="We will do A",
            signal_strength=SignalStrength.STRONG,
            evidence_type=EvidenceType.DO,
            sample_size=10,
            confidence_level=0.95,
        )
        assert card.signal_strength == SignalStrength.STRONG
        assert card.confidence_level == 0.95

    def test_learning_card_output_model(self):
        """LearningCardOutput model should be valid."""
        output = LearningCardOutput(
            learning_cards=[
                LearningCard(
                    hypothesis_tested="Test",
                    observation="Test",
                    insight="Test",
                    decision="Test",
                    signal_strength=SignalStrength.MODERATE,
                    evidence_type=EvidenceType.SAY,
                )
            ],
            total_learnings=1,
            validated_hypotheses=0,
            invalidated_hypotheses=0,
            inconclusive=1,
        )
        assert output.total_learnings == 1
        assert output.inconclusive == 1


# ===========================================================================
# ENUM TESTS
# ===========================================================================


class TestEnums:
    """Tests for enum values."""

    def test_canvas_element_type_values(self):
        """CanvasElementType should have expected values."""
        assert CanvasElementType.PRODUCT_SERVICE.value == "product_service"
        assert CanvasElementType.PAIN_RELIEVER.value == "pain_reliever"
        assert CanvasElementType.GAIN_CREATOR.value == "gain_creator"

    def test_experiment_type_values(self):
        """ExperimentType should have expected values."""
        assert ExperimentType.INTERVIEW.value == "interview"
        assert ExperimentType.LANDING_PAGE.value == "landing_page"
        assert ExperimentType.AD_CAMPAIGN.value == "ad_campaign"

    def test_evidence_type_values(self):
        """EvidenceType should have expected values."""
        assert EvidenceType.SAY.value == "say"
        assert EvidenceType.DO.value == "do"
        assert EvidenceType.DO_DIRECT.value == "do_direct"

    def test_signal_strength_values(self):
        """SignalStrength should have expected values."""
        assert SignalStrength.STRONG.value == "strong"
        assert SignalStrength.WEAK.value == "weak"
        assert SignalStrength.INCONCLUSIVE.value == "inconclusive"


# ===========================================================================
# IMPORT TESTS
# ===========================================================================


class TestImports:
    """Tests to verify imports work correctly."""

    def test_can_import_from_shared_tools(self):
        """Should be able to import from shared.tools."""
        from shared.tools import (
            CanvasBuilderTool,
            TestCardTool,
            LearningCardTool,
        )

        assert CanvasBuilderTool is not None
        assert TestCardTool is not None
        assert LearningCardTool is not None

    def test_can_import_convenience_functions(self):
        """Should be able to import convenience functions."""
        from shared.tools import (
            build_canvas_element,
            design_test_card,
            capture_learning,
        )

        assert callable(build_canvas_element)
        assert callable(design_test_card)
        assert callable(capture_learning)

    def test_can_import_output_models(self):
        """Should be able to import output models."""
        from shared.tools import (
            CanvasBuilderOutput,
            TestCardOutput,
            LearningCardOutput,
        )

        assert CanvasBuilderOutput is not None
        assert TestCardOutput is not None
        assert LearningCardOutput is not None

    def test_can_import_enums(self):
        """Should be able to import enums."""
        from shared.tools import (
            CanvasElementType,
            ExperimentType,
            EvidenceType,
            SignalStrength,
        )

        assert CanvasElementType is not None
        assert ExperimentType is not None
        assert EvidenceType is not None
        assert SignalStrength is not None
