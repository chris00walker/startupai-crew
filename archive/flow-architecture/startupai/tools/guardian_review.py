"""
Guardian Review Tool for StartupAI.

Automated QA for creative artifacts (landing pages, ad creatives)
before they go to human review. This reduces human review burden
by catching obvious issues automatically.

The Guardian can:
- Auto-approve safe creatives that pass all checks
- Flag issues that require human attention
- Provide specific feedback for revision

This implements the first line of defense in the HITL workflow.
"""

import re
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from crewai.tools import BaseTool
from pydantic import Field, BaseModel


# =======================================================================================
# MODELS
# =======================================================================================

class ReviewSeverity(str, Enum):
    """Severity levels for review issues."""
    BLOCKER = "blocker"        # Cannot deploy - must fix
    WARNING = "warning"        # Should fix before human review
    SUGGESTION = "suggestion"  # Nice to have improvement


class ReviewCategory(str, Enum):
    """Categories of review checks."""
    COMPLIANCE = "compliance"        # Legal/regulatory issues
    BRAND = "brand"                  # Brand guideline violations
    CLARITY = "clarity"              # Messaging clarity
    ACCESSIBILITY = "accessibility"  # A11y issues
    CONVERSION = "conversion"        # Conversion optimization
    SECURITY = "security"            # Security concerns
    TECHNICAL = "technical"          # Technical issues


class ReviewIssue(BaseModel):
    """A single issue found during review."""
    severity: ReviewSeverity
    category: ReviewCategory
    message: str
    location: Optional[str] = None  # Where in the artifact
    suggestion: Optional[str] = None  # How to fix


class ReviewDecision(str, Enum):
    """Guardian's decision on the artifact."""
    AUTO_APPROVED = "auto_approved"          # Safe to deploy
    NEEDS_HUMAN_REVIEW = "needs_human_review"  # Escalate to human
    REJECTED = "rejected"                    # Cannot deploy


class GuardianReviewResult(BaseModel):
    """Result from Guardian review."""
    decision: ReviewDecision
    artifact_type: str
    artifact_id: str

    # Issue counts
    blocker_count: int = 0
    warning_count: int = 0
    suggestion_count: int = 0

    # Detailed issues
    issues: List[ReviewIssue] = []

    # Summary
    summary: str = ""
    requires_human_review: bool = False
    review_reason: Optional[str] = None

    # Metadata
    reviewed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    review_time_ms: int = 0


# =======================================================================================
# GUARDIAN REVIEW TOOL
# =======================================================================================

class GuardianReviewTool(BaseTool):
    """
    Automated QA tool for creative artifacts.

    The Guardian reviews landing pages and ad creatives for:
    - Compliance issues (misleading claims, missing disclaimers)
    - Brand consistency (tone, messaging)
    - Accessibility (alt text, contrast, screen reader)
    - Conversion best practices (CTA clarity, value prop visibility)
    - Security concerns (unsafe URLs, suspicious scripts)

    Artifacts that pass all checks can be auto-approved.
    Those with issues are flagged for human review.
    """

    name: str = "guardian_review"
    description: str = """
    Review creative artifacts (landing pages, ads) for quality and compliance.

    Input should be a JSON object containing:
    - artifact_type: "landing_page" or "ad_creative"
    - artifact_id: Unique identifier for the artifact
    - content: The artifact content to review
      - For landing_page: HTML code
      - For ad_creative: JSON with headline, body, image_url, cta
    - context: Optional context about the business/campaign

    Returns:
    - decision: "auto_approved", "needs_human_review", or "rejected"
    - issues: List of issues found, if any
    - summary: Human-readable summary of the review
    """

    # Configuration
    strict_mode: bool = Field(
        default=False,
        description="If True, any warning escalates to human review"
    )
    auto_approve_threshold: int = Field(
        default=0,
        description="Max warnings allowed for auto-approval (blockers always escalate)"
    )

    # Compliance patterns to check
    _compliance_patterns: Dict[str, str] = {
        r'\b(guaranteed|100%|always|never fail)\b': "Absolute claims may be misleading",
        r'\b(best|#1|leading|top)\b': "Superlative claims may need substantiation",
        r'\b(free)\b(?!.*terms)': "Free offers should include terms",
        r'\b(limited time|act now|hurry)\b': "Urgency language may need time limits",
    }

    # Brand/tone patterns
    _tone_patterns: Dict[str, str] = {
        r'[A-Z]{5,}': "Excessive caps may appear aggressive",
        r'!{2,}': "Multiple exclamation marks reduce professionalism",
        r'\$+\d': "Price claims should be verified",
    }

    def _run(self, input_data: str) -> str:
        """
        Review a creative artifact.

        Args:
            input_data: JSON string with artifact details

        Returns:
            Formatted review result
        """
        try:
            start_time = datetime.now()

            # Parse input
            try:
                data = json.loads(input_data)
            except json.JSONDecodeError:
                return self._format_error("Invalid JSON input")

            artifact_type = data.get("artifact_type", "unknown")
            artifact_id = data.get("artifact_id", "unknown")
            content = data.get("content", "")
            context = data.get("context", {})

            # Route to appropriate reviewer
            if artifact_type == "landing_page":
                result = self._review_landing_page(artifact_id, content, context)
            elif artifact_type == "ad_creative":
                result = self._review_ad_creative(artifact_id, content, context)
            else:
                return self._format_error(f"Unknown artifact type: {artifact_type}")

            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            result.review_time_ms = elapsed_ms

            return self._format_output(result)

        except Exception as e:
            return self._format_error(f"Review failed: {str(e)}")

    async def _arun(self, input_data: str) -> str:
        """Async version - delegates to sync."""
        return self._run(input_data)

    def _review_landing_page(
        self,
        artifact_id: str,
        html_content: str,
        context: Dict[str, Any]
    ) -> GuardianReviewResult:
        """Review a landing page for quality and compliance."""
        issues: List[ReviewIssue] = []

        # Extract text content from HTML for analysis
        text_content = self._extract_text_from_html(html_content)

        # 1. Compliance checks
        issues.extend(self._check_compliance(text_content))

        # 2. Accessibility checks
        issues.extend(self._check_accessibility(html_content))

        # 3. Conversion checks
        issues.extend(self._check_conversion_elements(html_content))

        # 4. Security checks
        issues.extend(self._check_security(html_content))

        # 5. Tone/brand checks
        issues.extend(self._check_tone(text_content))

        # Make decision
        result = self._make_decision(
            artifact_type="landing_page",
            artifact_id=artifact_id,
            issues=issues
        )

        return result

    def _review_ad_creative(
        self,
        artifact_id: str,
        creative: Dict[str, Any],
        context: Dict[str, Any]
    ) -> GuardianReviewResult:
        """Review an ad creative for quality and compliance."""
        issues: List[ReviewIssue] = []

        headline = creative.get("headline", "")
        body = creative.get("body", "")
        cta = creative.get("cta", "")
        image_url = creative.get("image_url", "")

        # Combine text for compliance checks
        full_text = f"{headline} {body} {cta}"

        # 1. Compliance checks
        issues.extend(self._check_compliance(full_text))

        # 2. Character limits (platform-specific)
        if len(headline) > 40:
            issues.append(ReviewIssue(
                severity=ReviewSeverity.WARNING,
                category=ReviewCategory.TECHNICAL,
                message=f"Headline too long ({len(headline)} chars, max 40)",
                location="headline",
                suggestion="Shorten headline to fit platform limits"
            ))

        if len(body) > 125:
            issues.append(ReviewIssue(
                severity=ReviewSeverity.WARNING,
                category=ReviewCategory.TECHNICAL,
                message=f"Body too long ({len(body)} chars, max 125)",
                location="body",
                suggestion="Condense body text"
            ))

        # 3. CTA clarity
        if not cta or len(cta) < 3:
            issues.append(ReviewIssue(
                severity=ReviewSeverity.WARNING,
                category=ReviewCategory.CONVERSION,
                message="CTA is missing or too short",
                location="cta",
                suggestion="Add a clear call-to-action (e.g., 'Learn More', 'Get Started')"
            ))

        # 4. Image URL check
        if image_url and not image_url.startswith("https://"):
            issues.append(ReviewIssue(
                severity=ReviewSeverity.BLOCKER,
                category=ReviewCategory.SECURITY,
                message="Image URL must use HTTPS",
                location="image_url",
                suggestion="Use secure HTTPS URL for images"
            ))

        # 5. Tone checks
        issues.extend(self._check_tone(full_text))

        # Make decision
        result = self._make_decision(
            artifact_type="ad_creative",
            artifact_id=artifact_id,
            issues=issues
        )

        return result

    def _check_compliance(self, text: str) -> List[ReviewIssue]:
        """Check text for compliance issues."""
        issues = []

        for pattern, message in self._compliance_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(ReviewIssue(
                    severity=ReviewSeverity.WARNING,
                    category=ReviewCategory.COMPLIANCE,
                    message=message,
                    suggestion="Review claim for accuracy or add disclaimers"
                ))

        return issues

    def _check_accessibility(self, html: str) -> List[ReviewIssue]:
        """Check HTML for accessibility issues."""
        issues = []

        # Check for images without alt text
        img_pattern = r'<img[^>]*(?<!alt=")[^>]*>'
        if re.search(img_pattern, html, re.IGNORECASE):
            # More precise check
            for match in re.finditer(r'<img[^>]*>', html, re.IGNORECASE):
                if 'alt=' not in match.group().lower():
                    issues.append(ReviewIssue(
                        severity=ReviewSeverity.BLOCKER,
                        category=ReviewCategory.ACCESSIBILITY,
                        message="Image missing alt text",
                        location="img tag",
                        suggestion="Add descriptive alt attribute to all images"
                    ))
                    break  # Only report once

        # Check for form inputs without labels
        if '<input' in html.lower() and '<label' not in html.lower():
            if 'aria-label' not in html.lower() and 'placeholder' not in html.lower():
                issues.append(ReviewIssue(
                    severity=ReviewSeverity.WARNING,
                    category=ReviewCategory.ACCESSIBILITY,
                    message="Form inputs may lack labels",
                    suggestion="Add <label> elements or aria-label attributes"
                ))

        # Check for lang attribute
        if '<html' in html.lower() and 'lang=' not in html.lower():
            issues.append(ReviewIssue(
                severity=ReviewSeverity.WARNING,
                category=ReviewCategory.ACCESSIBILITY,
                message="HTML missing lang attribute",
                suggestion="Add lang='en' (or appropriate language) to <html> tag"
            ))

        return issues

    def _check_conversion_elements(self, html: str) -> List[ReviewIssue]:
        """Check landing page for conversion best practices."""
        issues = []

        # Check for CTA button
        if '<button' not in html.lower() and 'type="submit"' not in html.lower():
            issues.append(ReviewIssue(
                severity=ReviewSeverity.WARNING,
                category=ReviewCategory.CONVERSION,
                message="No clear CTA button found",
                suggestion="Add a prominent call-to-action button"
            ))

        # Check for headline (h1)
        if '<h1' not in html.lower():
            issues.append(ReviewIssue(
                severity=ReviewSeverity.SUGGESTION,
                category=ReviewCategory.CONVERSION,
                message="No H1 headline found",
                suggestion="Add a clear H1 headline for better SEO and clarity"
            ))

        # Check for email capture
        if 'type="email"' not in html.lower() and 'email' not in html.lower():
            issues.append(ReviewIssue(
                severity=ReviewSeverity.SUGGESTION,
                category=ReviewCategory.CONVERSION,
                message="No email capture field found",
                suggestion="Consider adding email signup for lead capture"
            ))

        return issues

    def _check_security(self, html: str) -> List[ReviewIssue]:
        """Check for security issues."""
        issues = []

        # Check for http:// links (should be https)
        if re.search(r'(src|href)\s*=\s*["\']http://', html, re.IGNORECASE):
            issues.append(ReviewIssue(
                severity=ReviewSeverity.BLOCKER,
                category=ReviewCategory.SECURITY,
                message="Non-HTTPS URLs detected",
                suggestion="Change all http:// URLs to https://"
            ))

        # Check for inline event handlers with external URLs
        if re.search(r'on\w+\s*=\s*["\'][^"\']*https?://', html, re.IGNORECASE):
            issues.append(ReviewIssue(
                severity=ReviewSeverity.WARNING,
                category=ReviewCategory.SECURITY,
                message="Inline event handler with external URL",
                suggestion="Move external calls to script files"
            ))

        # Check for javascript: URLs
        if 'javascript:' in html.lower():
            issues.append(ReviewIssue(
                severity=ReviewSeverity.WARNING,
                category=ReviewCategory.SECURITY,
                message="javascript: URL detected",
                suggestion="Use event handlers instead of javascript: URLs"
            ))

        return issues

    def _check_tone(self, text: str) -> List[ReviewIssue]:
        """Check text for tone/brand issues."""
        issues = []

        for pattern, message in self._tone_patterns.items():
            if re.search(pattern, text):
                issues.append(ReviewIssue(
                    severity=ReviewSeverity.SUGGESTION,
                    category=ReviewCategory.BRAND,
                    message=message,
                ))

        return issues

    def _extract_text_from_html(self, html: str) -> str:
        """Extract visible text content from HTML."""
        # Remove script and style tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Clean up whitespace
        text = ' '.join(text.split())
        return text

    def _make_decision(
        self,
        artifact_type: str,
        artifact_id: str,
        issues: List[ReviewIssue]
    ) -> GuardianReviewResult:
        """Make a review decision based on issues found."""
        blocker_count = sum(1 for i in issues if i.severity == ReviewSeverity.BLOCKER)
        warning_count = sum(1 for i in issues if i.severity == ReviewSeverity.WARNING)
        suggestion_count = sum(1 for i in issues if i.severity == ReviewSeverity.SUGGESTION)

        # Decision logic
        if blocker_count > 0:
            decision = ReviewDecision.REJECTED
            summary = f"REJECTED: {blocker_count} blocking issue(s) must be fixed"
            requires_human = True
            reason = "Blocking issues require fixes before approval"
        elif warning_count > self.auto_approve_threshold or self.strict_mode:
            decision = ReviewDecision.NEEDS_HUMAN_REVIEW
            summary = f"NEEDS REVIEW: {warning_count} warning(s) require human evaluation"
            requires_human = True
            reason = f"{warning_count} warnings exceed auto-approval threshold"
        else:
            decision = ReviewDecision.AUTO_APPROVED
            if suggestion_count > 0:
                summary = f"AUTO-APPROVED with {suggestion_count} suggestion(s)"
            else:
                summary = "AUTO-APPROVED: All checks passed"
            requires_human = False
            reason = None

        return GuardianReviewResult(
            decision=decision,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            blocker_count=blocker_count,
            warning_count=warning_count,
            suggestion_count=suggestion_count,
            issues=issues,
            summary=summary,
            requires_human_review=requires_human,
            review_reason=reason,
        )

    def _format_output(self, result: GuardianReviewResult) -> str:
        """Format review result for agent consumption."""
        lines = [
            "## Guardian Review Complete",
            "",
            f"**Decision:** {result.decision.value.upper()}",
            f"**Summary:** {result.summary}",
            f"**Review Time:** {result.review_time_ms}ms",
            "",
            f"- Blockers: {result.blocker_count}",
            f"- Warnings: {result.warning_count}",
            f"- Suggestions: {result.suggestion_count}",
            "",
        ]

        if result.issues:
            lines.append("### Issues Found")
            lines.append("")

            # Group by severity
            for severity in [ReviewSeverity.BLOCKER, ReviewSeverity.WARNING, ReviewSeverity.SUGGESTION]:
                severity_issues = [i for i in result.issues if i.severity == severity]
                if severity_issues:
                    icon = "🔴" if severity == ReviewSeverity.BLOCKER else "🟡" if severity == ReviewSeverity.WARNING else "🔵"
                    lines.append(f"#### {icon} {severity.value.title()}s")
                    for issue in severity_issues:
                        loc = f" ({issue.location})" if issue.location else ""
                        lines.append(f"- **[{issue.category.value}]** {issue.message}{loc}")
                        if issue.suggestion:
                            lines.append(f"  - 💡 {issue.suggestion}")
                    lines.append("")
        else:
            lines.append("### No Issues Found")
            lines.append("")
            lines.append("The artifact passed all quality checks.")

        if result.requires_human_review:
            lines.append("---")
            lines.append(f"**⚠️ Human Review Required:** {result.review_reason}")

        return "\n".join(lines)

    def _format_error(self, message: str) -> str:
        """Format error message."""
        return f"## Guardian Review Failed\n\n❌ {message}"

    def review_with_result(
        self,
        artifact_type: str,
        artifact_id: str,
        content: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> GuardianReviewResult:
        """
        Review an artifact and return structured result.

        Use this method when you need programmatic access to review results.
        """
        input_data = json.dumps({
            "artifact_type": artifact_type,
            "artifact_id": artifact_id,
            "content": content,
            "context": context or {}
        })

        # Run review (this returns formatted string, we need to re-run for result)
        self._run(input_data)

        # Re-run to get actual result
        if artifact_type == "landing_page":
            return self._review_landing_page(artifact_id, content, context or {})
        elif artifact_type == "ad_creative":
            return self._review_ad_creative(artifact_id, content, context or {})
        else:
            raise ValueError(f"Unknown artifact type: {artifact_type}")


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def review_landing_page(html: str, artifact_id: str = "unknown") -> str:
    """
    Convenience function to review a landing page.

    Args:
        html: Landing page HTML code
        artifact_id: Identifier for the page

    Returns:
        Formatted review result
    """
    tool = GuardianReviewTool()
    return tool._run(json.dumps({
        "artifact_type": "landing_page",
        "artifact_id": artifact_id,
        "content": html
    }))


def review_ad_creative(
    headline: str,
    body: str,
    cta: str,
    image_url: str = "",
    artifact_id: str = "unknown"
) -> str:
    """
    Convenience function to review an ad creative.

    Args:
        headline: Ad headline
        body: Ad body text
        cta: Call-to-action text
        image_url: URL of ad image
        artifact_id: Identifier for the ad

    Returns:
        Formatted review result
    """
    tool = GuardianReviewTool()
    return tool._run(json.dumps({
        "artifact_type": "ad_creative",
        "artifact_id": artifact_id,
        "content": {
            "headline": headline,
            "body": body,
            "cta": cta,
            "image_url": image_url
        }
    }))
