"""
Tests for Analytics and Privacy Tools (Phase C).

Tests AnalyticsTool, AnonymizerTool, AdPlatformTool, and CalendarTool.
Uses mocking to avoid actual API calls.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from shared.tools.analytics_privacy import (
    AnalyticsTool,
    AnonymizerTool,
    AdPlatformTool,
    CalendarTool,
    get_analytics,
    anonymize_data,
    get_ad_metrics,
    find_interview_slots,
    AnalyticsOutput,
    AnonymizationResult,
    AdPlatformOutput,
    CalendarOutput,
)


# ===========================================================================
# TEST FIXTURES
# ===========================================================================


@pytest.fixture
def mock_netlify_analytics_response():
    """Mock Netlify Analytics API response."""
    return {
        "pageviews": 1500,
        "visitors": 300,
        "unique_visitors": 280,
        "bounce_rate": 0.42,
        "form_submissions": 45,
        "data": [
            {"date": "2026-01-08", "pageviews": 500, "visitors": 100, "conversions": 15},
            {"date": "2026-01-09", "pageviews": 520, "visitors": 105, "conversions": 16},
            {"date": "2026-01-10", "pageviews": 480, "visitors": 95, "conversions": 14},
        ],
    }


@pytest.fixture
def analytics_tool():
    """Create an AnalyticsTool instance."""
    return AnalyticsTool()


@pytest.fixture
def anonymizer_tool():
    """Create an AnonymizerTool instance."""
    return AnonymizerTool()


@pytest.fixture
def ad_platform_tool():
    """Create an AdPlatformTool instance."""
    return AdPlatformTool()


@pytest.fixture
def calendar_tool():
    """Create a CalendarTool instance."""
    return CalendarTool()


# ===========================================================================
# ANALYTICS TOOL TESTS
# ===========================================================================


class TestAnalyticsTool:
    """Tests for AnalyticsTool."""

    def test_tool_has_correct_name(self, analytics_tool):
        """Tool should have correct name."""
        assert analytics_tool.name == "get_analytics"

    def test_tool_has_description(self, analytics_tool):
        """Tool should have a description."""
        assert len(analytics_tool.description) > 50
        assert "analytics" in analytics_tool.description.lower()

    def test_missing_site_id(self, analytics_tool):
        """Tool should require site_id."""
        result = analytics_tool._run("{}")
        assert "error" in result.lower() or "required" in result.lower()

    def test_accepts_json_input(self, analytics_tool):
        """Tool should accept JSON input."""
        with patch.dict("os.environ", {"NETLIFY_ACCESS_TOKEN": "test-token"}):
            with patch("requests.get") as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 402  # Pro plan required
                mock_get.return_value = mock_response

                result = analytics_tool._run('{"site_id": "test-site", "days": 7}')

                assert "# Landing Page Analytics" in result
                assert "test-site" in result

    def test_accepts_string_input(self, analytics_tool):
        """Tool should accept simple string site_id."""
        with patch.dict("os.environ", {"NETLIFY_ACCESS_TOKEN": "test-token"}):
            with patch("requests.get") as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 402
                mock_get.return_value = mock_response

                result = analytics_tool._run("my-site-id")

                assert "# Landing Page Analytics" in result
                assert "my-site-id" in result

    def test_handles_missing_token(self, analytics_tool):
        """Tool should handle missing API token."""
        with patch.dict("os.environ", {}, clear=True):
            result = analytics_tool._run("test-site")
            assert "error" in result.lower() or "not set" in result.lower()

    @patch("requests.get")
    def test_parses_analytics_response(self, mock_get, analytics_tool, mock_netlify_analytics_response):
        """Tool should parse analytics response correctly."""
        with patch.dict("os.environ", {"NETLIFY_ACCESS_TOKEN": "test-token"}):
            # Mock site info call
            site_response = MagicMock()
            site_response.status_code = 200
            site_response.json.return_value = {"name": "My Test Site"}

            # Mock analytics call
            analytics_response = MagicMock()
            analytics_response.status_code = 200
            analytics_response.json.return_value = mock_netlify_analytics_response

            mock_get.side_effect = [site_response, analytics_response]

            result = analytics_tool._run("test-site")

            assert "My Test Site" in result
            assert "1,500" in result  # Pageviews
            assert "300" in result  # Visitors
            assert "45" in result  # Conversions

    def test_formats_metrics_table(self, analytics_tool):
        """Tool should format metrics as a table."""
        with patch.dict("os.environ", {"NETLIFY_ACCESS_TOKEN": "test-token"}):
            with patch("requests.get") as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 402
                mock_get.return_value = mock_response

                result = analytics_tool._run("test-site")

                assert "| Metric | Value |" in result
                assert "Pageviews" in result
                assert "Visitors" in result


# ===========================================================================
# ANONYMIZER TOOL TESTS
# ===========================================================================


class TestAnonymizerTool:
    """Tests for AnonymizerTool."""

    def test_tool_has_correct_name(self, anonymizer_tool):
        """Tool should have correct name."""
        assert anonymizer_tool.name == "anonymize_data"

    def test_tool_has_description(self, anonymizer_tool):
        """Tool should have a description."""
        assert len(anonymizer_tool.description) > 50
        assert "anonymize" in anonymizer_tool.description.lower()

    def test_anonymizes_email(self, anonymizer_tool):
        """Tool should anonymize email addresses."""
        text = "Contact John at john.smith@acme.com for details."
        result = anonymizer_tool._run(text)

        assert "[EMAIL]" in result
        assert "john.smith@acme.com" not in result
        assert "Contact John at" in result

    def test_anonymizes_phone(self, anonymizer_tool):
        """Tool should anonymize phone numbers."""
        text = "Call us at 555-123-4567 or (800) 555-1234."
        result = anonymizer_tool._run(text)

        assert "[PHONE]" in result
        assert "555-123-4567" not in result
        assert "555-1234" not in result

    def test_anonymizes_url(self, anonymizer_tool):
        """Tool should anonymize URLs."""
        text = "Visit https://acme-corp.com/secret-page for info."
        result = anonymizer_tool._run(text)

        assert "[URL]" in result
        assert "acme-corp.com" not in result

    def test_anonymizes_dollar_amounts(self, anonymizer_tool):
        """Tool should anonymize dollar amounts."""
        text = "Revenue was $1,234,567 last quarter and ARR is $5.2 million."
        result = anonymizer_tool._run(text)

        assert "[AMOUNT]" in result
        assert "$1,234,567" not in result

    def test_preserves_non_pii_text(self, anonymizer_tool):
        """Tool should preserve text that isn't PII."""
        text = "The B2B SaaS company targets healthcare providers."
        result = anonymizer_tool._run(text)

        assert "B2B SaaS company" in result
        assert "healthcare providers" in result

    def test_reports_entity_counts(self, anonymizer_tool):
        """Tool should report number of entities found."""
        text = "Email: test@example.com, Phone: 555-1234"
        result = anonymizer_tool._run(text)

        assert "Entities Found" in result
        assert "Entity Types" in result

    def test_handles_no_pii(self, anonymizer_tool):
        """Tool should handle text with no PII."""
        text = "This is a normal sentence with no PII."
        result = anonymizer_tool._run(text)

        assert "Entities Found" in result
        assert "0" in result or "None" in result


# ===========================================================================
# AD PLATFORM TOOL TESTS
# ===========================================================================


class TestAdPlatformTool:
    """Tests for AdPlatformTool."""

    def test_tool_has_correct_name(self, ad_platform_tool):
        """Tool should have correct name."""
        assert ad_platform_tool.name == "get_ad_metrics"

    def test_tool_has_description(self, ad_platform_tool):
        """Tool should have a description."""
        assert len(ad_platform_tool.description) > 50
        assert "ad" in ad_platform_tool.description.lower()

    def test_handles_meta_without_token(self, ad_platform_tool):
        """Tool should handle missing Meta token gracefully."""
        with patch.dict("os.environ", {}, clear=True):
            result = ad_platform_tool._run(platform="meta")

            assert "Meta Ads" in result
            assert "Configuration Required" in result
            assert "META_ACCESS_TOKEN" in result

    def test_handles_google_without_token(self, ad_platform_tool):
        """Tool should handle missing Google token gracefully."""
        with patch.dict("os.environ", {}, clear=True):
            result = ad_platform_tool._run(platform="google")

            assert "Google Ads" in result
            assert "Configuration Required" in result
            assert "GOOGLE_ADS_DEVELOPER_TOKEN" in result

    def test_provides_setup_instructions(self, ad_platform_tool):
        """Tool should provide setup instructions when not configured."""
        with patch.dict("os.environ", {}, clear=True):
            result = ad_platform_tool._run(platform="meta")

            assert "Setup Instructions" in result
            assert "MCP Alternative" in result

    def test_handles_unknown_platform(self, ad_platform_tool):
        """Tool should reject unknown platforms."""
        result = ad_platform_tool._run(platform="tiktok")
        assert "Unknown platform" in result or "error" in result.lower()

    def test_accepts_campaign_id(self, ad_platform_tool):
        """Tool should accept campaign_id parameter."""
        with patch.dict("os.environ", {}, clear=True):
            # Default platform is meta
            result = ad_platform_tool._run(campaign_id="campaign-123")

            assert "Meta Ads" in result


# ===========================================================================
# CALENDAR TOOL TESTS
# ===========================================================================


class TestCalendarTool:
    """Tests for CalendarTool."""

    def test_tool_has_correct_name(self, calendar_tool):
        """Tool should have correct name."""
        assert calendar_tool.name == "find_interview_slots"

    def test_tool_has_description(self, calendar_tool):
        """Tool should have a description."""
        assert len(calendar_tool.description) > 50
        assert "interview" in calendar_tool.description.lower()

    def test_returns_available_slots(self, calendar_tool):
        """Tool should return available time slots."""
        result = calendar_tool._run(days_ahead=7)

        assert "# Available Interview Slots" in result
        assert "| Date | Start | End |" in result

    def test_respects_duration_parameter(self, calendar_tool):
        """Tool should respect duration parameter."""
        result = calendar_tool._run(days_ahead=7, duration_minutes=45)

        assert "Duration" in result
        assert "45" in result

    def test_skips_weekends(self, calendar_tool):
        """Tool should only suggest weekday slots."""
        result = calendar_tool._run(days_ahead=14)

        # Count rows in the table - should be less than 14 days * 6 slots
        lines = result.split("\n")
        table_rows = [l for l in lines if l.startswith("|") and "Date" not in l and "---" not in l]

        # Should have some slots but not fill all days
        assert len(table_rows) > 0
        assert len(table_rows) <= 60  # 10 days * 6 slots max

    def test_accepts_days_ahead_parameter(self, calendar_tool):
        """Tool should accept days_ahead parameter."""
        result = calendar_tool._run(days_ahead=5)

        assert "# Available Interview Slots" in result
        assert "5 days" in result

    def test_provides_setup_instructions(self, calendar_tool):
        """Tool should provide setup instructions."""
        result = calendar_tool._run(days_ahead=7)

        assert "Setup Instructions" in result or "MCP Alternative" in result


# ===========================================================================
# CONVENIENCE FUNCTION TESTS
# ===========================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_analytics_function(self):
        """get_analytics() convenience function should work."""
        with patch.dict("os.environ", {"NETLIFY_ACCESS_TOKEN": "test-token"}):
            with patch("requests.get") as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 402
                mock_get.return_value = mock_response

                result = get_analytics("test-site", days=7)
                assert "# Landing Page Analytics" in result

    def test_anonymize_data_function(self):
        """anonymize_data() convenience function should work."""
        result = anonymize_data("Email: test@example.com")
        assert "[EMAIL]" in result

    def test_get_ad_metrics_function(self):
        """get_ad_metrics() convenience function should work."""
        with patch.dict("os.environ", {}, clear=True):
            result = get_ad_metrics("meta", campaign_id="123")
            assert "Meta Ads" in result

    def test_find_interview_slots_function(self):
        """find_interview_slots() convenience function should work."""
        result = find_interview_slots(days_ahead=7, duration_minutes=30)
        assert "# Available Interview Slots" in result


# ===========================================================================
# PYDANTIC MODEL TESTS
# ===========================================================================


class TestPydanticModels:
    """Tests for Pydantic output models."""

    def test_analytics_output_model(self):
        """AnalyticsOutput model should be valid."""
        from shared.tools.analytics_privacy import AnalyticsMetrics

        output = AnalyticsOutput(
            site_id="test-site",
            site_name="Test Site",
            date_range_start="2026-01-01",
            date_range_end="2026-01-10",
            metrics=AnalyticsMetrics(
                pageviews=1000,
                visitors=200,
                conversion_rate=0.15,
            ),
            source="netlify",
        )
        assert output.site_id == "test-site"
        assert output.metrics.pageviews == 1000
        assert output.timestamp is not None

    def test_anonymization_result_model(self):
        """AnonymizationResult model should be valid."""
        output = AnonymizationResult(
            original_length=100,
            anonymized_length=95,
            entities_found=2,
            entity_types=["email", "phone"],
            anonymized_text="Anonymized content here",
        )
        assert output.entities_found == 2
        assert len(output.entity_types) == 2

    def test_ad_platform_output_model(self):
        """AdPlatformOutput model should be valid."""
        from shared.tools.analytics_privacy import AdCampaignData

        output = AdPlatformOutput(
            platform="meta",
            account_id="123456",
            date_range_start="2026-01-01",
            date_range_end="2026-01-10",
            campaigns=[
                AdCampaignData(
                    campaign_id="c1",
                    campaign_name="Test Campaign",
                    platform="meta",
                    impressions=10000,
                    clicks=200,
                    spend=50.0,
                    conversions=10,
                )
            ],
            total_spend=50.0,
            total_conversions=10,
        )
        assert output.platform == "meta"
        assert len(output.campaigns) == 1

    def test_calendar_output_model(self):
        """CalendarOutput model should be valid."""
        from shared.tools.analytics_privacy import CalendarSlot

        output = CalendarOutput(
            available_slots=[
                CalendarSlot(
                    start="2026-01-11T09:00:00",
                    end="2026-01-11T09:30:00",
                    duration_minutes=30,
                )
            ],
            timezone="America/New_York",
            search_range_days=7,
        )
        assert len(output.available_slots) == 1
        assert output.timezone == "America/New_York"


# ===========================================================================
# IMPORT TESTS
# ===========================================================================


class TestImports:
    """Tests to verify imports work correctly."""

    def test_can_import_from_shared_tools(self):
        """Should be able to import from shared.tools."""
        from shared.tools import (
            AnalyticsTool,
            AnonymizerTool,
            AdPlatformTool,
            CalendarTool,
        )

        assert AnalyticsTool is not None
        assert AnonymizerTool is not None
        assert AdPlatformTool is not None
        assert CalendarTool is not None

    def test_can_import_convenience_functions(self):
        """Should be able to import convenience functions."""
        from shared.tools import (
            get_analytics,
            anonymize_data,
            get_ad_metrics,
            find_interview_slots,
        )

        assert callable(get_analytics)
        assert callable(anonymize_data)
        assert callable(get_ad_metrics)
        assert callable(find_interview_slots)

    def test_can_import_output_models(self):
        """Should be able to import output models."""
        from shared.tools import (
            AnalyticsOutput,
            AnonymizationResult,
            AdPlatformOutput,
            CalendarOutput,
        )

        assert AnalyticsOutput is not None
        assert AnonymizationResult is not None
        assert AdPlatformOutput is not None
        assert CalendarOutput is not None
