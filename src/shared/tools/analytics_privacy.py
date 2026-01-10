"""
Analytics and Privacy Tools for StartupAI Validation Engine (Phase C).

Provides:
- AnalyticsTool: Fetch landing page analytics from Netlify API
- AnonymizerTool: Anonymize PII from validation outputs for learning pipeline
- AdPlatformTool: Interface for Meta/Google Ads (MCP wrapper)
- CalendarTool: Schedule interview slots (MCP wrapper)

Target agents: P3, D3, L1, W1, W2, P1, P2, D1
"""

import os
import re
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from crewai.tools import BaseTool
from pydantic import Field, BaseModel


# =======================================================================================
# OUTPUT MODELS
# =======================================================================================


class AnalyticsMetrics(BaseModel):
    """Metrics from landing page analytics."""

    pageviews: int = 0
    visitors: int = 0
    unique_visitors: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    conversion_count: int = 0
    conversion_rate: float = 0.0


class DailyMetric(BaseModel):
    """Single day of analytics data."""

    date: str
    pageviews: int = 0
    visitors: int = 0
    conversions: int = 0


class AnalyticsOutput(BaseModel):
    """Structured output from analytics tool."""

    site_id: str
    site_name: Optional[str] = None
    date_range_start: str
    date_range_end: str
    metrics: AnalyticsMetrics
    daily_data: List[DailyMetric] = []
    source: str = "netlify"
    timestamp: datetime = Field(default_factory=datetime.now)


class AnonymizationResult(BaseModel):
    """Result of anonymizing text."""

    original_length: int
    anonymized_length: int
    entities_found: int
    entity_types: List[str]
    anonymized_text: str
    timestamp: datetime = Field(default_factory=datetime.now)


class AdCampaignData(BaseModel):
    """Ad campaign performance data."""

    campaign_id: str
    campaign_name: str
    platform: str  # "meta" or "google"
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    conversions: int = 0
    ctr: float = 0.0  # Click-through rate
    cpc: float = 0.0  # Cost per click
    cpa: float = 0.0  # Cost per acquisition


class AdPlatformOutput(BaseModel):
    """Structured output from ad platform tool."""

    platform: str
    account_id: str
    date_range_start: str
    date_range_end: str
    campaigns: List[AdCampaignData]
    total_spend: float = 0.0
    total_conversions: int = 0
    avg_cpa: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)


class CalendarSlot(BaseModel):
    """Available interview time slot."""

    start: str  # ISO datetime
    end: str  # ISO datetime
    duration_minutes: int = 30


class CalendarOutput(BaseModel):
    """Structured output from calendar tool."""

    available_slots: List[CalendarSlot]
    timezone: str = "UTC"
    search_range_days: int = 7
    timestamp: datetime = Field(default_factory=datetime.now)


# =======================================================================================
# ANALYTICS TOOL
# =======================================================================================


class AnalyticsTool(BaseTool):
    """
    Fetch landing page analytics from Netlify API.

    Provides pageviews, visitors, bounce rate, and conversion data
    for deployed landing pages.

    Target agents: P3, D3, L1, W1, W2
    """

    name: str = "get_analytics"
    description: str = """
    Fetch analytics data for a deployed landing page.

    Use this tool to:
    - Get pageview and visitor counts for landing pages
    - Calculate conversion rates (signups / visitors)
    - Track bounce rates and session durations
    - Analyze daily trends over a date range

    Input should be a JSON string with:
    {
        "site_id": "netlify-site-id",
        "days": 7  // Optional, defaults to 7 days
    }

    Or just the site_id as a string for default 7-day analytics.

    Returns structured analytics data for validation decisions.
    """

    def _get_netlify_client(self):
        """Get Netlify API access token."""
        token = os.environ.get("NETLIFY_ACCESS_TOKEN")
        if not token:
            raise ValueError("NETLIFY_ACCESS_TOKEN environment variable not set")
        return token

    def _run(self, input_data: str) -> str:
        """
        Fetch analytics from Netlify API.

        Args:
            input_data: JSON with site_id and optional days, or just site_id string

        Returns:
            Formatted analytics data
        """
        try:
            # Parse input
            if input_data.startswith("{"):
                data = json.loads(input_data)
                site_id = data.get("site_id", "")
                days = data.get("days", 7)
            else:
                site_id = input_data.strip()
                days = 7

            if not site_id:
                return "Error: site_id is required"

            # Get token
            token = self._get_netlify_client()

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Fetch from Netlify Analytics API
            analytics = self._fetch_netlify_analytics(token, site_id, start_date, end_date)

            return self._format_output(analytics)

        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except json.JSONDecodeError as e:
            return f"Invalid JSON input: {str(e)}"
        except Exception as e:
            return f"Analytics fetch failed: {str(e)}"

    def _fetch_netlify_analytics(
        self, token: str, site_id: str, start_date: datetime, end_date: datetime
    ) -> AnalyticsOutput:
        """Fetch analytics from Netlify API."""
        try:
            import requests

            headers = {"Authorization": f"Bearer {token}"}

            # Get site info
            site_response = requests.get(
                f"https://api.netlify.com/api/v1/sites/{site_id}",
                headers=headers,
                timeout=10,
            )

            site_name = None
            if site_response.status_code == 200:
                site_data = site_response.json()
                site_name = site_data.get("name", site_id)

            # Get analytics (Netlify Analytics API)
            # Note: Netlify Analytics requires Pro plan
            analytics_url = f"https://api.netlify.com/api/v1/sites/{site_id}/analytics"
            params = {
                "from": int(start_date.timestamp() * 1000),
                "to": int(end_date.timestamp() * 1000),
                "resolution": "day",
            }

            analytics_response = requests.get(
                analytics_url,
                headers=headers,
                params=params,
                timeout=10,
            )

            if analytics_response.status_code == 200:
                raw_data = analytics_response.json()
                return self._parse_netlify_response(
                    site_id, site_name, start_date, end_date, raw_data
                )
            elif analytics_response.status_code == 402:
                # Analytics requires Pro plan - return simulated data with warning
                return self._create_placeholder_analytics(
                    site_id, site_name, start_date, end_date,
                    note="Netlify Analytics requires Pro plan. Using placeholder data."
                )
            else:
                return self._create_placeholder_analytics(
                    site_id, site_name, start_date, end_date,
                    note=f"API returned status {analytics_response.status_code}"
                )

        except ImportError:
            return self._create_placeholder_analytics(
                site_id, None, start_date, end_date,
                note="requests library not available"
            )
        except requests.RequestException as e:
            return self._create_placeholder_analytics(
                site_id, None, start_date, end_date,
                note=f"Request failed: {str(e)}"
            )

    def _parse_netlify_response(
        self,
        site_id: str,
        site_name: Optional[str],
        start_date: datetime,
        end_date: datetime,
        raw_data: Dict[str, Any],
    ) -> AnalyticsOutput:
        """Parse Netlify Analytics API response."""
        # Extract metrics from response
        pageviews = raw_data.get("pageviews", 0)
        visitors = raw_data.get("visitors", 0)
        unique_visitors = raw_data.get("unique_visitors", visitors)
        bounce_rate = raw_data.get("bounce_rate", 0.0)

        # Calculate conversion rate (if form submissions are tracked)
        conversions = raw_data.get("form_submissions", 0)
        conversion_rate = (conversions / visitors * 100) if visitors > 0 else 0.0

        metrics = AnalyticsMetrics(
            pageviews=pageviews,
            visitors=visitors,
            unique_visitors=unique_visitors,
            bounce_rate=bounce_rate,
            conversion_count=conversions,
            conversion_rate=conversion_rate,
        )

        # Parse daily data if available
        daily_data = []
        for day in raw_data.get("data", []):
            daily_data.append(
                DailyMetric(
                    date=day.get("date", ""),
                    pageviews=day.get("pageviews", 0),
                    visitors=day.get("visitors", 0),
                    conversions=day.get("conversions", 0),
                )
            )

        return AnalyticsOutput(
            site_id=site_id,
            site_name=site_name,
            date_range_start=start_date.strftime("%Y-%m-%d"),
            date_range_end=end_date.strftime("%Y-%m-%d"),
            metrics=metrics,
            daily_data=daily_data,
            source="netlify",
        )

    def _create_placeholder_analytics(
        self,
        site_id: str,
        site_name: Optional[str],
        start_date: datetime,
        end_date: datetime,
        note: str = "",
    ) -> AnalyticsOutput:
        """Create placeholder analytics when API is unavailable."""
        return AnalyticsOutput(
            site_id=site_id,
            site_name=site_name or site_id,
            date_range_start=start_date.strftime("%Y-%m-%d"),
            date_range_end=end_date.strftime("%Y-%m-%d"),
            metrics=AnalyticsMetrics(
                pageviews=0,
                visitors=0,
                unique_visitors=0,
                bounce_rate=0.0,
                conversion_count=0,
                conversion_rate=0.0,
            ),
            daily_data=[],
            source=f"placeholder ({note})" if note else "placeholder",
        )

    def _format_output(self, output: AnalyticsOutput) -> str:
        """Format analytics for agent consumption."""
        lines = [
            f"# Landing Page Analytics: {output.site_name or output.site_id}",
            "",
            f"**Site ID:** {output.site_id}",
            f"**Date Range:** {output.date_range_start} to {output.date_range_end}",
            f"**Source:** {output.source}",
            "",
            "## Key Metrics",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Pageviews | {output.metrics.pageviews:,} |",
            f"| Visitors | {output.metrics.visitors:,} |",
            f"| Unique Visitors | {output.metrics.unique_visitors:,} |",
            f"| Bounce Rate | {output.metrics.bounce_rate:.1%} |",
            f"| Conversions | {output.metrics.conversion_count:,} |",
            f"| Conversion Rate | {output.metrics.conversion_rate:.2%} |",
            "",
        ]

        if output.daily_data:
            lines.append("## Daily Trend")
            lines.append("")
            lines.append("| Date | Pageviews | Visitors | Conversions |")
            lines.append("|------|-----------|----------|-------------|")
            for day in output.daily_data:
                lines.append(
                    f"| {day.date} | {day.pageviews:,} | {day.visitors:,} | {day.conversions:,} |"
                )
            lines.append("")

        lines.append(f"*Retrieved at {output.timestamp.isoformat()}*")

        return "\n".join(lines)

    async def _arun(self, input_data: str) -> str:
        """Async version - delegates to sync."""
        return self._run(input_data)


# =======================================================================================
# ANONYMIZER TOOL
# =======================================================================================


class AnonymizerTool(BaseTool):
    """
    Anonymize PII from validation outputs for the learning pipeline.

    Removes or abstracts identifying information while preserving
    business context needed for pattern learning.

    Target: Learning pipeline (all phases)
    """

    name: str = "anonymize_data"
    description: str = """
    Anonymize personally identifiable information (PII) from text.

    Use this tool to:
    - Remove email addresses, phone numbers, and URLs
    - Abstract company and person names
    - Preserve business context (industry, model, segment)
    - Prepare data for the learning flywheel

    Input should be the text to anonymize.

    Returns anonymized text safe for storage in the learning database.
    """

    # PII patterns to detect and anonymize
    patterns: Dict[str, str] = Field(
        default={
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(\+?1?[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "url": r"https?://[^\s<>\"{}|\\^`\[\]]+",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "dollar_amount": r"\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|M|B|k|K))?\b",
        }
    )

    # Replacement tokens
    replacements: Dict[str, str] = Field(
        default={
            "email": "[EMAIL]",
            "phone": "[PHONE]",
            "url": "[URL]",
            "ip_address": "[IP]",
            "ssn": "[SSN]",
            "credit_card": "[CARD]",
            "dollar_amount": "[AMOUNT]",
        }
    )

    def _run(self, text: str) -> str:
        """
        Anonymize PII from text.

        Args:
            text: Text containing potential PII

        Returns:
            Formatted anonymization result
        """
        try:
            original_length = len(text)
            anonymized_text = text
            entities_found = 0
            entity_types_found = set()

            # Apply pattern-based anonymization
            for entity_type, pattern in self.patterns.items():
                matches = re.findall(pattern, anonymized_text, re.IGNORECASE)
                if matches:
                    entities_found += len(matches)
                    entity_types_found.add(entity_type)
                    replacement = self.replacements.get(entity_type, "[REDACTED]")
                    anonymized_text = re.sub(
                        pattern, replacement, anonymized_text, flags=re.IGNORECASE
                    )

            # Try Presidio if available for advanced anonymization
            try:
                anonymized_text, presidio_count, presidio_types = self._presidio_anonymize(
                    anonymized_text
                )
                entities_found += presidio_count
                entity_types_found.update(presidio_types)
            except ImportError:
                pass  # Presidio not installed, continue with regex-only

            result = AnonymizationResult(
                original_length=original_length,
                anonymized_length=len(anonymized_text),
                entities_found=entities_found,
                entity_types=list(entity_types_found),
                anonymized_text=anonymized_text,
            )

            return self._format_output(result)

        except Exception as e:
            return f"Anonymization failed: {str(e)}"

    def _presidio_anonymize(self, text: str) -> tuple[str, int, set]:
        """Use Microsoft Presidio for advanced anonymization if available."""
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine

        analyzer = AnalyzerEngine()
        anonymizer = AnonymizerEngine()

        # Analyze for PII
        results = analyzer.analyze(text=text, language="en")

        if not results:
            return text, 0, set()

        # Anonymize detected entities
        anonymized = anonymizer.anonymize(text=text, analyzer_results=results)

        entity_types = {r.entity_type for r in results}
        return anonymized.text, len(results), entity_types

    def _format_output(self, result: AnonymizationResult) -> str:
        """Format anonymization result for agent consumption."""
        lines = [
            "# Anonymization Result",
            "",
            "## Summary",
            f"- **Original Length:** {result.original_length:,} characters",
            f"- **Anonymized Length:** {result.anonymized_length:,} characters",
            f"- **Entities Found:** {result.entities_found}",
            f"- **Entity Types:** {', '.join(result.entity_types) if result.entity_types else 'None'}",
            "",
            "## Anonymized Text",
            "",
            result.anonymized_text,
            "",
            f"*Anonymized at {result.timestamp.isoformat()}*",
        ]

        return "\n".join(lines)

    async def _arun(self, text: str) -> str:
        """Async version - delegates to sync."""
        return self._run(text)


# =======================================================================================
# AD PLATFORM TOOL
# =======================================================================================


class AdPlatformTool(BaseTool):
    """
    Interface for Meta and Google Ads platforms.

    Fetches campaign performance data for ad experiments.
    Wraps external MCP servers when configured.

    Target agents: P1, P2, P3, D3
    """

    name: str = "get_ad_metrics"
    description: str = """
    Fetch ad campaign performance metrics from Meta or Google Ads.

    Use this tool to:
    - Get impressions, clicks, and conversions for campaigns
    - Calculate CTR, CPC, and CPA metrics
    - Track ad spend and ROI
    - Compare variant performance in ad experiments

    Input should be a JSON string with:
    {
        "platform": "meta" or "google",
        "campaign_id": "campaign-id",  // Optional, omit for all campaigns
        "days": 7  // Optional, defaults to 7 days
    }

    Returns structured ad performance data.
    """

    platform: str = Field(default="meta", description="Ad platform: 'meta' or 'google'")

    def _run(self, input_data: str) -> str:
        """
        Fetch ad metrics from specified platform.

        Args:
            input_data: JSON with platform, campaign_id, and days

        Returns:
            Formatted ad performance data
        """
        try:
            # Parse input
            if input_data.startswith("{"):
                data = json.loads(input_data)
                platform = data.get("platform", self.platform)
                campaign_id = data.get("campaign_id")
                days = data.get("days", 7)
            else:
                platform = self.platform
                campaign_id = input_data.strip() if input_data.strip() else None
                days = 7

            # Check for platform credentials
            if platform == "meta":
                token = os.environ.get("META_ACCESS_TOKEN")
                if not token:
                    return self._create_placeholder_response(
                        platform, "META_ACCESS_TOKEN not configured"
                    )
                return self._fetch_meta_ads(token, campaign_id, days)

            elif platform == "google":
                token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
                if not token:
                    return self._create_placeholder_response(
                        platform, "GOOGLE_ADS_DEVELOPER_TOKEN not configured"
                    )
                return self._fetch_google_ads(token, campaign_id, days)

            else:
                return f"Error: Unknown platform '{platform}'. Use 'meta' or 'google'."

        except json.JSONDecodeError as e:
            return f"Invalid JSON input: {str(e)}"
        except Exception as e:
            return f"Ad metrics fetch failed: {str(e)}"

    def _fetch_meta_ads(
        self, token: str, campaign_id: Optional[str], days: int
    ) -> str:
        """Fetch ads from Meta Marketing API."""
        # Note: Full implementation would use facebook-business SDK
        # For now, return structured placeholder indicating setup needed
        return self._create_placeholder_response(
            "meta",
            "Meta Ads API integration pending. "
            "Configure META_ACCESS_TOKEN and install facebook-business SDK.",
            campaign_id=campaign_id,
        )

    def _fetch_google_ads(
        self, token: str, campaign_id: Optional[str], days: int
    ) -> str:
        """Fetch ads from Google Ads API."""
        # Note: Full implementation would use google-ads SDK
        # For now, return structured placeholder indicating setup needed
        return self._create_placeholder_response(
            "google",
            "Google Ads API integration pending. "
            "Configure GOOGLE_ADS_DEVELOPER_TOKEN and install google-ads SDK.",
            campaign_id=campaign_id,
        )

    def _create_placeholder_response(
        self, platform: str, note: str, campaign_id: Optional[str] = None
    ) -> str:
        """Create placeholder response when API is not configured."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        lines = [
            f"# {platform.title()} Ads Performance",
            "",
            f"**Platform:** {platform}",
            f"**Date Range:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "",
            "## Status",
            "",
            f"⚠️ **Configuration Required:** {note}",
            "",
            "## Setup Instructions",
            "",
        ]

        if platform == "meta":
            lines.extend(
                [
                    "1. Create a Meta Business account and app",
                    "2. Generate an access token with ads_read permission",
                    "3. Set META_ACCESS_TOKEN environment variable",
                    "4. Install: `pip install facebook-business`",
                    "",
                    "**MCP Alternative:** Use meta-ads-mcp server",
                    "```",
                    'uvx meta-ads-mcp --token "$META_ACCESS_TOKEN"',
                    "```",
                ]
            )
        else:  # google
            lines.extend(
                [
                    "1. Create a Google Ads developer account",
                    "2. Generate OAuth credentials and developer token",
                    "3. Set GOOGLE_ADS_DEVELOPER_TOKEN environment variable",
                    "4. Install: `pip install google-ads`",
                    "",
                    "**MCP Alternative:** Use google-ads-mcp server",
                    "```",
                    'uvx google-ads-mcp --token "$GOOGLE_ADS_DEVELOPER_TOKEN"',
                    "```",
                ]
            )

        lines.append("")
        lines.append(f"*Checked at {datetime.now().isoformat()}*")

        return "\n".join(lines)

    async def _arun(self, input_data: str) -> str:
        """Async version - delegates to sync."""
        return self._run(input_data)


# =======================================================================================
# CALENDAR TOOL
# =======================================================================================


class CalendarTool(BaseTool):
    """
    Schedule interview slots using calendar integration.

    Finds available times for customer discovery interviews.
    Wraps Google Calendar MCP when configured.

    Target agent: D1 (Customer Interview Agent)
    """

    name: str = "find_interview_slots"
    description: str = """
    Find available time slots for customer interviews.

    Use this tool to:
    - Check calendar availability for interview scheduling
    - Find open slots in the next N days
    - Suggest times for discovery calls

    Input should be a JSON string with:
    {
        "days_ahead": 7,  // Optional, defaults to 7
        "duration_minutes": 30,  // Optional, defaults to 30
        "timezone": "America/New_York"  // Optional
    }

    Or just a number for days_ahead with defaults.

    Returns list of available interview time slots.
    """

    def _run(self, input_data: str) -> str:
        """
        Find available interview slots.

        Args:
            input_data: JSON with scheduling parameters

        Returns:
            Formatted available slots
        """
        try:
            # Parse input
            if input_data.startswith("{"):
                data = json.loads(input_data)
                days_ahead = data.get("days_ahead", 7)
                duration = data.get("duration_minutes", 30)
                timezone = data.get("timezone", "UTC")
            else:
                days_ahead = int(input_data) if input_data.strip().isdigit() else 7
                duration = 30
                timezone = "UTC"

            # Check for calendar credentials
            creds = os.environ.get("GOOGLE_CALENDAR_CREDENTIALS")
            if not creds:
                return self._create_placeholder_response(days_ahead, duration, timezone)

            # Full implementation would use Google Calendar API
            return self._fetch_calendar_slots(creds, days_ahead, duration, timezone)

        except json.JSONDecodeError as e:
            return f"Invalid JSON input: {str(e)}"
        except Exception as e:
            return f"Calendar fetch failed: {str(e)}"

    def _fetch_calendar_slots(
        self, creds: str, days_ahead: int, duration: int, timezone: str
    ) -> str:
        """Fetch available slots from Google Calendar."""
        # Note: Full implementation would use google-auth and google-api-python-client
        return self._create_placeholder_response(
            days_ahead, duration, timezone,
            note="Google Calendar API integration pending. "
            "Install google-auth and google-api-python-client."
        )

    def _create_placeholder_response(
        self, days_ahead: int, duration: int, timezone: str, note: str = ""
    ) -> str:
        """Create placeholder response with suggested times."""
        # Generate reasonable interview slots
        slots = []
        now = datetime.now()

        for day_offset in range(1, days_ahead + 1):
            day = now + timedelta(days=day_offset)
            # Skip weekends
            if day.weekday() >= 5:
                continue

            # Add morning and afternoon slots
            for hour in [9, 10, 11, 14, 15, 16]:
                slot_start = day.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start + timedelta(minutes=duration)
                slots.append(
                    CalendarSlot(
                        start=slot_start.isoformat(),
                        end=slot_end.isoformat(),
                        duration_minutes=duration,
                    )
                )

        output = CalendarOutput(
            available_slots=slots[:10],  # Limit to 10 slots
            timezone=timezone,
            search_range_days=days_ahead,
        )

        lines = [
            "# Available Interview Slots",
            "",
            f"**Timezone:** {output.timezone}",
            f"**Search Range:** Next {output.search_range_days} days",
            f"**Duration:** {duration} minutes",
            "",
        ]

        if note:
            lines.extend([
                "## Status",
                f"⚠️ {note}",
                "",
                "## Suggested Slots (Placeholder)",
                "",
            ])
        else:
            lines.append("## Available Slots")
            lines.append("")

        lines.append("| Date | Start | End |")
        lines.append("|------|-------|-----|")

        for slot in output.available_slots:
            start = datetime.fromisoformat(slot.start)
            end = datetime.fromisoformat(slot.end)
            lines.append(
                f"| {start.strftime('%Y-%m-%d')} | {start.strftime('%H:%M')} | {end.strftime('%H:%M')} |"
            )

        lines.append("")

        if not note:
            lines.extend([
                "## Setup Instructions",
                "",
                "To enable live calendar integration:",
                "1. Create Google Cloud project with Calendar API",
                "2. Set up OAuth credentials",
                "3. Set GOOGLE_CALENDAR_CREDENTIALS environment variable",
                "",
                "**MCP Alternative:** Use google-calendar-mcp server",
                "```",
                "uvx google-calendar-mcp",
                "```",
                "",
            ])

        lines.append(f"*Generated at {output.timestamp.isoformat()}*")

        return "\n".join(lines)

    async def _arun(self, input_data: str) -> str:
        """Async version - delegates to sync."""
        return self._run(input_data)


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================


def get_analytics(site_id: str, days: int = 7) -> str:
    """
    Convenience function for fetching analytics.

    Args:
        site_id: Netlify site ID
        days: Number of days to fetch

    Returns:
        Formatted analytics data
    """
    tool = AnalyticsTool()
    return tool._run(json.dumps({"site_id": site_id, "days": days}))


def anonymize_data(text: str) -> str:
    """
    Convenience function for anonymizing text.

    Args:
        text: Text to anonymize

    Returns:
        Anonymized text with PII removed
    """
    tool = AnonymizerTool()
    return tool._run(text)


def get_ad_metrics(platform: str, campaign_id: Optional[str] = None, days: int = 7) -> str:
    """
    Convenience function for fetching ad metrics.

    Args:
        platform: 'meta' or 'google'
        campaign_id: Optional specific campaign
        days: Number of days to fetch

    Returns:
        Formatted ad performance data
    """
    tool = AdPlatformTool()
    return tool._run(
        json.dumps({"platform": platform, "campaign_id": campaign_id, "days": days})
    )


def find_interview_slots(days_ahead: int = 7, duration_minutes: int = 30) -> str:
    """
    Convenience function for finding interview slots.

    Args:
        days_ahead: Days to look ahead
        duration_minutes: Interview duration

    Returns:
        Formatted available slots
    """
    tool = CalendarTool()
    return tool._run(
        json.dumps({"days_ahead": days_ahead, "duration_minutes": duration_minutes})
    )
