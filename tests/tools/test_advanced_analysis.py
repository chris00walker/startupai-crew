"""
Tests for Advanced Analysis Tools (Phase B).

Tests TranscriptionTool, InsightExtractorTool, BehaviorPatternTool, and ABTestTool.
Uses mocking to avoid actual API calls.
"""

import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

from shared.tools.advanced_analysis import (
    TranscriptionTool,
    InsightExtractorTool,
    BehaviorPatternTool,
    ABTestTool,
    transcribe_audio,
    extract_insights,
    identify_patterns,
    run_ab_test,
    TranscriptionOutput,
    InsightExtractionOutput,
    BehaviorPatternOutput,
    ABTestResult,
)


# ===========================================================================
# TEST FIXTURES
# ===========================================================================


@pytest.fixture
def mock_openai_transcription_response():
    """Mock OpenAI Whisper transcription response."""
    mock_response = MagicMock()
    mock_response.text = "This is a test transcript from the interview."
    mock_response.duration = 120.5
    mock_response.language = "english"
    return mock_response


@pytest.fixture
def mock_openai_insight_response():
    """Mock OpenAI insight extraction response."""
    return json.dumps({
        "key_themes": ["customer pain", "workflow inefficiency", "tool fragmentation"],
        "pain_points": ["slow manual processes", "too many tools to manage"],
        "opportunities": ["automation potential", "single dashboard solution"],
        "notable_quotes": ["I spend 3 hours a day on manual data entry"],
        "behavioral_insights": ["switching between 5+ tools daily"],
    })


@pytest.fixture
def mock_openai_pattern_response():
    """Mock OpenAI pattern identification response."""
    return json.dumps({
        "patterns": [
            {
                "pattern_name": "Tool Overload",
                "description": "Users frequently switch between multiple tools",
                "frequency": "common",
                "evidence": ["5+ tool switches daily", "context switching complaints"],
                "implications": ["productivity loss", "integration opportunity"],
            }
        ],
        "say_vs_do_discrepancies": ["Say they want simple, but use complex solutions"],
        "behavioral_signals": ["high engagement on automation content"],
        "recommendations": ["Focus on single-dashboard value prop"],
    })


@pytest.fixture
def transcription_tool():
    """Create a TranscriptionTool instance."""
    return TranscriptionTool()


@pytest.fixture
def insight_tool():
    """Create an InsightExtractorTool instance."""
    return InsightExtractorTool()


@pytest.fixture
def pattern_tool():
    """Create a BehaviorPatternTool instance."""
    return BehaviorPatternTool()


@pytest.fixture
def ab_test_tool():
    """Create an ABTestTool instance."""
    return ABTestTool()


# ===========================================================================
# TRANSCRIPTION TOOL TESTS
# ===========================================================================


class TestTranscriptionTool:
    """Tests for TranscriptionTool."""

    def test_tool_has_correct_name(self, transcription_tool):
        """Tool should have correct name."""
        assert transcription_tool.name == "transcribe_audio"

    def test_tool_has_description(self, transcription_tool):
        """Tool should have a description."""
        assert len(transcription_tool.description) > 50
        assert "transcribe" in transcription_tool.description.lower()

    def test_text_input_formatting(self, transcription_tool):
        """Tool should format pre-transcribed text input."""
        text = """This is a multi-line transcript from a customer interview.
        The customer mentioned several pain points about their current workflow.
        They specifically complained about manual data entry taking too long."""

        result = transcription_tool._run(text)

        assert "# Interview Transcript" in result
        assert "text_input" in result
        assert "multi-line transcript" in result

    def test_short_text_input(self, transcription_tool):
        """Tool should handle short text input."""
        result = transcription_tool._run("Short interview notes")

        assert "# Interview Transcript" in result
        assert "Short interview notes" in result

    @patch("shared.tools.advanced_analysis.TranscriptionTool._get_openai_client")
    def test_file_transcription(
        self, mock_get_client, transcription_tool, mock_openai_transcription_response
    ):
        """Tool should transcribe audio files."""
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value = (
            mock_openai_transcription_response
        )
        mock_get_client.return_value = mock_client

        # Mock file existence
        with patch("os.path.isfile", return_value=True):
            with patch("builtins.open", mock_open(read_data=b"audio data")):
                result = transcription_tool._run("/path/to/interview.mp3")

        assert "# Interview Transcript" in result
        assert "test transcript from the interview" in result

    def test_missing_api_key(self, transcription_tool):
        """Tool should handle missing API key gracefully."""
        with patch.dict("os.environ", {}, clear=True):
            result = transcription_tool._run("Test input that would need transcription")

        # Should either work as text input or show error
        assert "Transcript" in result or "error" in result.lower()


# ===========================================================================
# INSIGHT EXTRACTOR TOOL TESTS
# ===========================================================================


class TestInsightExtractorTool:
    """Tests for InsightExtractorTool."""

    def test_tool_has_correct_name(self, insight_tool):
        """Tool should have correct name."""
        assert insight_tool.name == "extract_insights"

    def test_tool_has_description(self, insight_tool):
        """Tool should have a description."""
        assert len(insight_tool.description) > 50
        assert "insight" in insight_tool.description.lower()

    @patch("shared.tools.advanced_analysis.InsightExtractorTool._get_openai_client")
    def test_extracts_themes_and_pain_points(
        self, mock_get_client, insight_tool, mock_openai_insight_response
    ):
        """Tool should extract themes and pain points."""
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = mock_openai_insight_response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = insight_tool._run("Customer interview transcript about workflow issues")

        assert "# Extracted Insights" in result
        assert "Key Themes" in result
        assert "Pain Points" in result
        assert "Opportunities" in result

    @patch("shared.tools.advanced_analysis.InsightExtractorTool._get_openai_client")
    def test_handles_api_error(self, mock_get_client, insight_tool):
        """Tool should handle API errors gracefully."""
        mock_get_client.side_effect = Exception("API error")

        result = insight_tool._run("Test text")

        assert "error" in result.lower() or "failed" in result.lower()

    @patch("shared.tools.advanced_analysis.InsightExtractorTool._get_openai_client")
    def test_handles_invalid_json_response(self, mock_get_client, insight_tool):
        """Tool should handle invalid JSON from API."""
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Not valid JSON"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = insight_tool._run("Test text")

        assert "failed" in result.lower() or "error" in result.lower()


# ===========================================================================
# BEHAVIOR PATTERN TOOL TESTS
# ===========================================================================


class TestBehaviorPatternTool:
    """Tests for BehaviorPatternTool."""

    def test_tool_has_correct_name(self, pattern_tool):
        """Tool should have correct name."""
        assert pattern_tool.name == "identify_patterns"

    def test_tool_has_description(self, pattern_tool):
        """Tool should have a description."""
        assert len(pattern_tool.description) > 50
        assert "pattern" in pattern_tool.description.lower()

    @patch("shared.tools.advanced_analysis.BehaviorPatternTool._get_openai_client")
    def test_identifies_patterns(
        self, mock_get_client, pattern_tool, mock_openai_pattern_response
    ):
        """Tool should identify behavioral patterns."""
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = mock_openai_pattern_response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = pattern_tool._run("Evidence about user tool switching behavior")

        assert "# Behavioral Pattern Analysis" in result
        assert "Identified Patterns" in result
        assert "SAY vs DO Discrepancies" in result

    @patch("shared.tools.advanced_analysis.BehaviorPatternTool._get_openai_client")
    def test_handles_topic_in_input(
        self, mock_get_client, pattern_tool, mock_openai_pattern_response
    ):
        """Tool should handle topic passed via pipe separator."""
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = mock_openai_pattern_response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = pattern_tool._run("tool usage | Evidence about user behavior")

        assert "tool usage" in result

    @patch("shared.tools.advanced_analysis.BehaviorPatternTool._get_openai_client")
    def test_handles_api_error(self, mock_get_client, pattern_tool):
        """Tool should handle API errors gracefully."""
        mock_get_client.side_effect = Exception("API error")

        result = pattern_tool._run("Test evidence")

        assert "error" in result.lower() or "failed" in result.lower()


# ===========================================================================
# A/B TEST TOOL TESTS
# ===========================================================================


class TestABTestTool:
    """Tests for ABTestTool."""

    def test_tool_has_correct_name(self, ab_test_tool):
        """Tool should have correct name."""
        assert ab_test_tool.name == "run_ab_test"

    def test_tool_has_description(self, ab_test_tool):
        """Tool should have a description."""
        assert len(ab_test_tool.description) > 50
        assert "a/b" in ab_test_tool.description.lower()

    def test_calculates_conversion_rates(self, ab_test_tool):
        """Tool should calculate correct conversion rates."""
        test_data = json.dumps({
            "test_name": "Button Color Test",
            "variant_a": {"name": "Blue", "conversions": 50, "total": 500},
            "variant_b": {"name": "Green", "conversions": 75, "total": 500},
        })

        result = ab_test_tool._run(test_data)

        assert "# A/B Test Results" in result
        assert "Button Color Test" in result
        assert "10.00%" in result  # 50/500
        assert "15.00%" in result  # 75/500

    def test_identifies_significant_winner(self, ab_test_tool):
        """Tool should identify statistically significant winner."""
        # Large sample with clear difference
        test_data = json.dumps({
            "test_name": "Headline Test",
            "variant_a": {"name": "Original", "conversions": 100, "total": 1000},
            "variant_b": {"name": "New", "conversions": 150, "total": 1000},
        })

        result = ab_test_tool._run(test_data)

        assert "Winner" in result or "Significant" in result

    def test_handles_insignificant_results(self, ab_test_tool):
        """Tool should handle non-significant results."""
        # Small sample with small difference
        test_data = json.dumps({
            "test_name": "Minor Test",
            "variant_a": {"name": "A", "conversions": 5, "total": 50},
            "variant_b": {"name": "B", "conversions": 6, "total": 50},
        })

        result = ab_test_tool._run(test_data)

        assert "not statistically significant" in result.lower() or "inconclusive" in result.lower()

    def test_calculates_relative_lift(self, ab_test_tool):
        """Tool should calculate relative lift correctly."""
        test_data = json.dumps({
            "test_name": "Lift Test",
            "variant_a": {"name": "Control", "conversions": 100, "total": 1000},
            "variant_b": {"name": "Treatment", "conversions": 120, "total": 1000},
        })

        result = ab_test_tool._run(test_data)

        # 20% lift: (12% - 10%) / 10% = 20%
        assert "+20" in result or "20.0%" in result

    def test_handles_invalid_json(self, ab_test_tool):
        """Tool should handle invalid JSON input."""
        result = ab_test_tool._run("not valid json")

        assert "Invalid JSON" in result or "error" in result.lower()

    def test_handles_zero_conversions(self, ab_test_tool):
        """Tool should handle zero conversions gracefully."""
        test_data = json.dumps({
            "test_name": "Zero Test",
            "variant_a": {"name": "A", "conversions": 0, "total": 100},
            "variant_b": {"name": "B", "conversions": 5, "total": 100},
        })

        result = ab_test_tool._run(test_data)

        assert "0.00%" in result
        assert "5.00%" in result


# ===========================================================================
# CONVENIENCE FUNCTION TESTS
# ===========================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_transcribe_audio_function(self):
        """transcribe_audio() convenience function should work."""
        result = transcribe_audio("Test interview transcript content goes here")
        assert "# Interview Transcript" in result

    @patch("shared.tools.advanced_analysis.InsightExtractorTool._get_openai_client")
    def test_extract_insights_function(
        self, mock_get_client, mock_openai_insight_response
    ):
        """extract_insights() convenience function should work."""
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = mock_openai_insight_response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = extract_insights("Customer feedback text")
        assert "# Extracted Insights" in result

    @patch("shared.tools.advanced_analysis.BehaviorPatternTool._get_openai_client")
    def test_identify_patterns_function(
        self, mock_get_client, mock_openai_pattern_response
    ):
        """identify_patterns() convenience function should work."""
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = mock_openai_pattern_response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = identify_patterns("Behavioral evidence")
        assert "# Behavioral Pattern Analysis" in result

    def test_run_ab_test_function(self):
        """run_ab_test() convenience function should work."""
        result = run_ab_test(
            test_name="CTA Test",
            variant_a_name="Control",
            variant_a_conversions=50,
            variant_a_total=500,
            variant_b_name="Treatment",
            variant_b_conversions=65,
            variant_b_total=500,
        )
        assert "# A/B Test Results" in result


# ===========================================================================
# PYDANTIC MODEL TESTS
# ===========================================================================


class TestPydanticModels:
    """Tests for Pydantic output models."""

    def test_transcription_output_model(self):
        """TranscriptionOutput model should be valid."""
        output = TranscriptionOutput(
            source_type="audio_file",
            transcript="Test transcript",
            duration_seconds=120.5,
            language="english",
        )
        assert output.source_type == "audio_file"
        assert output.transcript == "Test transcript"
        assert output.timestamp is not None

    def test_insight_extraction_output_model(self):
        """InsightExtractionOutput model should be valid."""
        output = InsightExtractionOutput(
            source_text_preview="Test preview...",
            insights=[],
            key_themes=["theme1", "theme2"],
            pain_points=["pain1"],
            opportunities=["opp1"],
            notable_quotes=["quote1"],
        )
        assert len(output.key_themes) == 2
        assert len(output.pain_points) == 1

    def test_behavior_pattern_output_model(self):
        """BehaviorPatternOutput model should be valid."""
        output = BehaviorPatternOutput(
            topic="user behavior",
            patterns=[],
            say_vs_do_discrepancies=["discrepancy1"],
            behavioral_signals=["signal1", "signal2"],
            recommendations=["rec1"],
        )
        assert output.topic == "user behavior"
        assert len(output.behavioral_signals) == 2

    def test_ab_test_result_model(self):
        """ABTestResult model should be valid."""
        output = ABTestResult(
            test_name="Test",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_conversions=50,
            variant_a_total=500,
            variant_b_conversions=75,
            variant_b_total=500,
            variant_a_rate=0.10,
            variant_b_rate=0.15,
            relative_lift=50.0,
            p_value=0.02,
            is_significant=True,
            confidence_level=0.95,
            winner="B",
            recommendation="Implement B",
        )
        assert output.is_significant is True
        assert output.winner == "B"


# ===========================================================================
# IMPORT TESTS
# ===========================================================================


class TestImports:
    """Tests to verify imports work correctly."""

    def test_can_import_from_shared_tools(self):
        """Should be able to import from shared.tools."""
        from shared.tools import (
            TranscriptionTool,
            InsightExtractorTool,
            BehaviorPatternTool,
            ABTestTool,
        )

        assert TranscriptionTool is not None
        assert InsightExtractorTool is not None
        assert BehaviorPatternTool is not None
        assert ABTestTool is not None

    def test_can_import_convenience_functions(self):
        """Should be able to import convenience functions."""
        from shared.tools import (
            transcribe_audio,
            extract_insights,
            identify_patterns,
            run_ab_test,
        )

        assert callable(transcribe_audio)
        assert callable(extract_insights)
        assert callable(identify_patterns)
        assert callable(run_ab_test)

    def test_can_import_output_models(self):
        """Should be able to import output models."""
        from shared.tools import (
            TranscriptionOutput,
            InsightExtractionOutput,
            BehaviorPatternOutput,
            ABTestResult,
        )

        assert TranscriptionOutput is not None
        assert InsightExtractionOutput is not None
        assert BehaviorPatternOutput is not None
        assert ABTestResult is not None
