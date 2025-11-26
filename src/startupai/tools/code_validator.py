"""
Code Validation Tools for StartupAI.

Validates generated code (HTML, CSS, JavaScript) for:
- Syntax errors
- Accessibility compliance (WCAG 2.1 AA basics)
- Security vulnerabilities
- Best practices

These tools ensure generated landing pages are production-ready
before deployment to validation experiments.
"""

import re
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from html.parser import HTMLParser, HTMLParseError

from crewai.tools import BaseTool
from pydantic import Field, BaseModel


# =======================================================================================
# MODELS
# =======================================================================================

class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    ERROR = "error"        # Must fix before deployment
    WARNING = "warning"    # Should fix, but can deploy
    INFO = "info"          # Suggestion for improvement


class ValidationCategory(str, Enum):
    """Categories of validation checks."""
    SYNTAX = "syntax"
    ACCESSIBILITY = "accessibility"
    SECURITY = "security"
    SEO = "seo"
    PERFORMANCE = "performance"
    BEST_PRACTICE = "best_practice"


class ValidationIssue(BaseModel):
    """A single validation issue found in the code."""
    severity: ValidationSeverity
    category: ValidationCategory
    message: str
    line: Optional[int] = None
    suggestion: Optional[str] = None


class ValidationResult(BaseModel):
    """Result of code validation."""
    is_valid: bool
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    issues: List[ValidationIssue] = []
    validated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Summary for quick decisions
    deployment_ready: bool = False
    summary: str = ""


# =======================================================================================
# HTML PARSER FOR VALIDATION
# =======================================================================================

class HTMLValidationParser(HTMLParser):
    """Custom HTML parser that tracks structure and accessibility."""

    def __init__(self):
        super().__init__()
        self.issues: List[ValidationIssue] = []
        self.has_doctype = False
        self.has_html_lang = False
        self.has_title = False
        self.has_meta_viewport = False
        self.has_meta_charset = False
        self.in_title = False
        self.title_content = ""
        self.images_without_alt: List[int] = []
        self.buttons_without_text: List[int] = []
        self.forms_without_labels: List[int] = []
        self.current_form_has_label = False
        self.in_form = False
        self.in_button = False
        self.button_has_text = False
        self.line_number = 1
        self.links: List[str] = []
        self.scripts: List[Dict[str, Any]] = []
        self.inline_styles_count = 0

    def handle_decl(self, decl: str):
        if decl.lower().startswith('doctype'):
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        attrs_dict = dict(attrs)

        if tag == 'html':
            if 'lang' in attrs_dict:
                self.has_html_lang = True
            else:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.ACCESSIBILITY,
                    message="<html> tag missing 'lang' attribute",
                    line=self.getpos()[0],
                    suggestion="Add lang attribute, e.g., <html lang=\"en\">"
                ))

        elif tag == 'title':
            self.in_title = True

        elif tag == 'meta':
            name = attrs_dict.get('name', '').lower()
            if 'charset' in attrs_dict:
                self.has_meta_charset = True
            elif name == 'viewport' or 'viewport' in attrs_dict.get('content', ''):
                self.has_meta_viewport = True

        elif tag == 'img':
            if 'alt' not in attrs_dict:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.ACCESSIBILITY,
                    message="Image missing 'alt' attribute",
                    line=self.getpos()[0],
                    suggestion="Add alt=\"description\" to describe the image"
                ))

        elif tag == 'a':
            href = attrs_dict.get('href', '')
            self.links.append(href)
            if href.startswith('javascript:'):
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.SECURITY,
                    message="javascript: URL in link href",
                    line=self.getpos()[0],
                    suggestion="Use event handlers instead of javascript: URLs"
                ))

        elif tag == 'form':
            self.in_form = True
            self.current_form_has_label = False
            if 'action' not in attrs_dict:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.BEST_PRACTICE,
                    message="Form missing 'action' attribute",
                    line=self.getpos()[0],
                    suggestion="Add action attribute or handle with JavaScript"
                ))

        elif tag == 'label':
            self.current_form_has_label = True

        elif tag == 'input':
            input_type = attrs_dict.get('type', 'text')
            if input_type not in ['hidden', 'submit', 'button', 'reset']:
                # Check if there's a label (simplified check)
                if not self.current_form_has_label and 'aria-label' not in attrs_dict:
                    if 'placeholder' not in attrs_dict:
                        self.issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category=ValidationCategory.ACCESSIBILITY,
                            message=f"Input field missing label or aria-label",
                            line=self.getpos()[0],
                            suggestion="Add a <label> element or aria-label attribute"
                        ))

        elif tag == 'button':
            self.in_button = True
            self.button_has_text = False
            if 'aria-label' in attrs_dict:
                self.button_has_text = True

        elif tag == 'script':
            src = attrs_dict.get('src', '')
            self.scripts.append({
                'src': src,
                'inline': not bool(src),
                'line': self.getpos()[0]
            })

        # Check for inline styles
        if 'style' in attrs_dict:
            self.inline_styles_count += 1

    def handle_endtag(self, tag: str):
        if tag == 'title':
            self.in_title = False
            if self.title_content.strip():
                self.has_title = True
            else:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.SEO,
                    message="Empty <title> tag",
                    suggestion="Add a descriptive page title"
                ))

        elif tag == 'form':
            self.in_form = False

        elif tag == 'button':
            if not self.button_has_text:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.ACCESSIBILITY,
                    message="Button may be missing accessible text",
                    suggestion="Ensure button has visible text or aria-label"
                ))
            self.in_button = False

    def handle_data(self, data: str):
        if self.in_title:
            self.title_content += data
        if self.in_button and data.strip():
            self.button_has_text = True


# =======================================================================================
# CODE VALIDATOR TOOL
# =======================================================================================

class CodeValidatorTool(BaseTool):
    """
    Validate generated code for syntax, accessibility, and security.

    Use this tool to check landing page HTML before deployment.
    Returns validation results with issues categorized by severity.
    """

    name: str = "code_validator"
    description: str = """
    Validate HTML code for syntax errors, accessibility issues, and security vulnerabilities.

    Input should be either:
    - Raw HTML string to validate
    - JSON object with 'html' key containing the HTML to validate

    Returns a validation report with:
    - is_valid: boolean indicating if code is error-free
    - deployment_ready: boolean indicating if code can be deployed
    - issues: list of problems found, categorized by severity
    - summary: human-readable summary of validation results
    """

    # Configuration
    strict_mode: bool = Field(default=False, description="Treat warnings as errors")
    check_accessibility: bool = Field(default=True, description="Run accessibility checks")
    check_security: bool = Field(default=True, description="Run security checks")
    check_seo: bool = Field(default=True, description="Run SEO checks")

    def _run(self, input_data: str) -> str:
        """
        Validate the provided HTML code.

        Args:
            input_data: HTML string or JSON with 'html' key

        Returns:
            Formatted validation report
        """
        try:
            # Parse input
            html_code = self._extract_html(input_data)
            if not html_code:
                return self._format_error("No HTML code provided")

            # Run validation
            result = self._validate_html(html_code)

            return self._format_output(result)

        except Exception as e:
            return self._format_error(f"Validation failed: {str(e)}")

    async def _arun(self, input_data: str) -> str:
        """Async version - delegates to sync."""
        return self._run(input_data)

    def _extract_html(self, input_data: str) -> Optional[str]:
        """Extract HTML from input (raw string or JSON)."""
        # Try parsing as JSON first
        try:
            data = json.loads(input_data)
            if isinstance(data, dict):
                return data.get('html', data.get('code', ''))
        except json.JSONDecodeError:
            pass

        # Assume raw HTML if starts with < or whitespace + <
        stripped = input_data.strip()
        if stripped.startswith('<') or stripped.startswith('<!'):
            return input_data

        return None

    def _validate_html(self, html: str) -> ValidationResult:
        """Run all validation checks on HTML."""
        issues: List[ValidationIssue] = []

        # 1. Syntax validation using HTML parser
        parser = HTMLValidationParser()
        try:
            parser.feed(html)
            issues.extend(parser.issues)
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.SYNTAX,
                message=f"HTML parsing error: {str(e)}",
                suggestion="Check for unclosed tags or invalid HTML syntax"
            ))

        # 2. Structure checks
        if not parser.has_doctype:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.BEST_PRACTICE,
                message="Missing DOCTYPE declaration",
                suggestion="Add <!DOCTYPE html> at the start of the document"
            ))

        if not parser.has_meta_charset:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.BEST_PRACTICE,
                message="Missing charset meta tag",
                suggestion="Add <meta charset=\"UTF-8\"> in <head>"
            ))

        if not parser.has_meta_viewport:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.ACCESSIBILITY,
                message="Missing viewport meta tag",
                suggestion="Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"
            ))

        if not parser.has_title:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.SEO,
                message="Missing or empty <title> tag",
                suggestion="Add a descriptive title for the page"
            ))

        # 3. Security checks
        if self.check_security:
            issues.extend(self._check_security(html, parser))

        # 4. Performance checks
        if parser.inline_styles_count > 5:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.PERFORMANCE,
                message=f"Found {parser.inline_styles_count} inline styles",
                suggestion="Consider moving styles to CSS classes for better maintainability"
            ))

        # 5. Check for common XSS patterns
        xss_patterns = [
            (r'on\w+\s*=\s*["\'][^"\']*\$\{', "Template literal in event handler"),
            (r'<script>[^<]*\$\{', "Template literal in inline script"),
            (r'eval\s*\(', "Use of eval()"),
            (r'document\.write\s*\(', "Use of document.write()"),
        ]

        for pattern, message in xss_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.SECURITY,
                    message=f"Potential security issue: {message}",
                    suggestion="Review for XSS vulnerabilities"
                ))

        # Calculate counts
        error_count = sum(1 for i in issues if i.severity == ValidationSeverity.ERROR)
        warning_count = sum(1 for i in issues if i.severity == ValidationSeverity.WARNING)
        info_count = sum(1 for i in issues if i.severity == ValidationSeverity.INFO)

        # Determine validity
        is_valid = error_count == 0
        deployment_ready = error_count == 0 and (not self.strict_mode or warning_count == 0)

        # Generate summary
        if deployment_ready:
            if warning_count == 0 and info_count == 0:
                summary = "✅ Code is valid and ready for deployment"
            else:
                summary = f"✅ Code is deployable with {warning_count} warning(s) and {info_count} suggestion(s)"
        else:
            summary = f"❌ Code has {error_count} error(s) that must be fixed before deployment"

        return ValidationResult(
            is_valid=is_valid,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            issues=issues,
            deployment_ready=deployment_ready,
            summary=summary
        )

    def _check_security(self, html: str, parser: HTMLValidationParser) -> List[ValidationIssue]:
        """Run security-specific checks."""
        issues = []

        # Check for inline scripts
        inline_scripts = [s for s in parser.scripts if s['inline']]
        if inline_scripts:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.SECURITY,
                message=f"Found {len(inline_scripts)} inline script(s)",
                suggestion="Consider using external scripts with CSP headers"
            ))

        # Check for http:// links (should be https://)
        http_pattern = r'(src|href)\s*=\s*["\']http://'
        if re.search(http_pattern, html, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.SECURITY,
                message="Found non-HTTPS URLs in src or href attributes",
                suggestion="Use HTTPS for all external resources"
            ))

        return issues

    def _format_output(self, result: ValidationResult) -> str:
        """Format validation result for agent consumption."""
        lines = [
            "## Code Validation Report",
            "",
            f"**Status:** {result.summary}",
            f"**Deployment Ready:** {'Yes' if result.deployment_ready else 'No'}",
            "",
            f"- Errors: {result.error_count}",
            f"- Warnings: {result.warning_count}",
            f"- Suggestions: {result.info_count}",
            "",
        ]

        if result.issues:
            lines.append("### Issues Found")
            lines.append("")

            # Group by severity
            for severity in [ValidationSeverity.ERROR, ValidationSeverity.WARNING, ValidationSeverity.INFO]:
                severity_issues = [i for i in result.issues if i.severity == severity]
                if severity_issues:
                    icon = "🔴" if severity == ValidationSeverity.ERROR else "🟡" if severity == ValidationSeverity.WARNING else "🔵"
                    lines.append(f"#### {icon} {severity.value.title()}s")
                    for issue in severity_issues:
                        line_info = f" (line {issue.line})" if issue.line else ""
                        lines.append(f"- **[{issue.category.value}]** {issue.message}{line_info}")
                        if issue.suggestion:
                            lines.append(f"  - 💡 {issue.suggestion}")
                    lines.append("")
        else:
            lines.append("### No Issues Found")
            lines.append("")
            lines.append("The code passed all validation checks.")

        return "\n".join(lines)

    def _format_error(self, message: str) -> str:
        """Format error message."""
        return f"## Code Validation Failed\n\n❌ {message}"

    def validate_with_result(self, html: str) -> ValidationResult:
        """
        Validate HTML and return structured result.

        Use this method when you need programmatic access to validation results.
        """
        return self._validate_html(html)


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def validate_html(html: str, strict: bool = False) -> str:
    """
    Convenience function to validate HTML code.

    Args:
        html: HTML string to validate
        strict: If True, treat warnings as errors

    Returns:
        Formatted validation report
    """
    tool = CodeValidatorTool(strict_mode=strict)
    return tool._run(html)


def is_deployment_ready(html: str) -> bool:
    """
    Quick check if HTML is ready for deployment.

    Args:
        html: HTML string to validate

    Returns:
        True if code has no errors
    """
    tool = CodeValidatorTool()
    result = tool.validate_with_result(html)
    return result.deployment_ready
