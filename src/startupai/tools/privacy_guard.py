"""
PrivacyGuard Tool - Advanced Privacy Protection for Flywheel Learning.

Provides additional privacy protection beyond basic anonymization:
- Data sensitivity classification
- Leakage detection in LLM outputs
- Compliance policy checking
- Audit trail generation
- Cross-validation privacy boundaries

Works with AnonymizerTool to ensure safe knowledge sharing.
"""

import json
import re
import hashlib
from typing import Dict, List, Optional, Any, Set, ClassVar
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from startupai.tools.anonymizer import anonymize_text, EMAIL_PATTERN, PHONE_PATTERN, URL_PATTERN


# =======================================================================================
# ENUMS AND MODELS
# =======================================================================================

class SensitivityLevel(str, Enum):
    """Data sensitivity classification levels."""
    PUBLIC = "public"           # Can be shared freely
    INTERNAL = "internal"       # Internal use only
    CONFIDENTIAL = "confidential"  # Business sensitive
    RESTRICTED = "restricted"   # Highly sensitive, PII


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    GENERAL = "general"


class PrivacyViolation(BaseModel):
    """A detected privacy violation."""
    violation_type: str
    severity: SensitivityLevel
    description: str
    location: Optional[str] = None
    recommendation: str


class PrivacyAuditRecord(BaseModel):
    """Audit record for privacy-related operations."""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    operation: str
    data_classification: SensitivityLevel
    validation_id: Optional[str] = None
    violations_found: int = 0
    action_taken: str
    checksum: Optional[str] = None  # For data integrity verification


class PrivacyCheckResult(BaseModel):
    """Result of a privacy check operation."""
    is_safe: bool
    sensitivity_level: SensitivityLevel
    violations: List[PrivacyViolation] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    audit_record: Optional[PrivacyAuditRecord] = None
    sanitized_content: Optional[str] = None


# =======================================================================================
# PRIVACY GUARD TOOL
# =======================================================================================

class PrivacyGuardTool(BaseTool):
    """
    Advanced privacy protection tool for the Flywheel learning system.

    Provides:
    1. Data sensitivity classification
    2. Privacy violation detection
    3. Compliance policy checking
    4. Audit trail generation
    5. Safe content sanitization
    """

    name: str = "privacy_guard"
    description: str = """Check content for privacy violations and classify sensitivity.

    Input: JSON with action and content:
    {
        "action": "check" | "classify" | "sanitize" | "audit",
        "content": "text or data to check",
        "context": {
            "validation_id": "optional validation ID",
            "source": "where the data came from",
            "intended_use": "how the data will be used"
        },
        "compliance": ["gdpr", "ccpa"]  // optional frameworks to check
    }

    Returns privacy assessment with violations and recommendations."""

    # Sensitive data patterns
    SENSITIVE_PATTERNS: ClassVar[Dict[str, re.Pattern]] = {
        "email": EMAIL_PATTERN,
        "phone": PHONE_PATTERN,
        "url": URL_PATTERN,
        "api_key": re.compile(r'\b(sk-[a-zA-Z0-9]{20,}|api[_-]?key[_-]?[=:]\s*["\']?[a-zA-Z0-9]{20,})', re.IGNORECASE),
        "password": re.compile(r'(password|passwd|pwd)[_\s]*[=:]\s*["\']?[^\s"\']{4,}', re.IGNORECASE),
        "secret": re.compile(r'(secret|token|credential)[_\s]*[=:]\s*["\']?[a-zA-Z0-9]{10,}', re.IGNORECASE),
        "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        "credit_card": re.compile(r'\b(?:\d[ -]*?){13,19}\b'),
        "ip_address": re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
        "date_of_birth": re.compile(r'\b(dob|date.?of.?birth|born)[:\s]+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', re.IGNORECASE),
    }

    # High-risk keywords that might indicate sensitive content
    HIGH_RISK_KEYWORDS: ClassVar[Set[str]] = {
        "social security", "ssn", "passport", "driver license",
        "bank account", "routing number", "credit card",
        "medical record", "health information", "diagnosis",
        "salary", "compensation", "financial statement",
        "private key", "api key", "password", "secret",
    }

    # Business-sensitive keywords
    BUSINESS_SENSITIVE: ClassVar[Set[str]] = {
        "revenue", "profit", "loss", "valuation", "funding",
        "customer list", "pricing strategy", "trade secret",
        "acquisition", "merger", "lawsuit", "litigation",
    }

    def _run(self, input_data: str) -> str:
        """
        Process privacy guard request.

        Args:
            input_data: JSON string with action and content

        Returns:
            Privacy check results
        """
        try:
            data = json.loads(input_data) if isinstance(input_data, str) else input_data
        except json.JSONDecodeError:
            return "Error: Invalid JSON input"

        action = data.get("action", "check")
        content = data.get("content", "")
        context = data.get("context", {})
        compliance = data.get("compliance", ["general"])

        if action == "check":
            result = self.check_privacy(content, context, compliance)
            return self._format_check_result(result)
        elif action == "classify":
            level = self.classify_sensitivity(content)
            return f"Sensitivity Level: {level.value.upper()}\n\nClassification based on content analysis."
        elif action == "sanitize":
            result = self.sanitize_content(content, context)
            return result.sanitized_content or content
        elif action == "audit":
            record = self.create_audit_record(content, context)
            return self._format_audit_record(record)
        else:
            return f"Unknown action: {action}"

    def check_privacy(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        compliance_frameworks: Optional[List[str]] = None,
    ) -> PrivacyCheckResult:
        """
        Comprehensive privacy check on content.

        Args:
            content: The content to check
            context: Optional context about the data
            compliance_frameworks: Frameworks to check against

        Returns:
            PrivacyCheckResult with violations and recommendations
        """
        violations = []
        recommendations = []

        # Check for sensitive patterns
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            matches = pattern.findall(content)
            if matches:
                violations.append(PrivacyViolation(
                    violation_type=f"pii_{pattern_name}",
                    severity=SensitivityLevel.RESTRICTED,
                    description=f"Found {len(matches)} instance(s) of {pattern_name.replace('_', ' ')}",
                    recommendation=f"Remove or anonymize {pattern_name.replace('_', ' ')} before storage",
                ))

        # Check for high-risk keywords
        content_lower = content.lower()
        found_high_risk = [kw for kw in self.HIGH_RISK_KEYWORDS if kw in content_lower]
        if found_high_risk:
            violations.append(PrivacyViolation(
                violation_type="high_risk_content",
                severity=SensitivityLevel.CONFIDENTIAL,
                description=f"High-risk keywords detected: {', '.join(found_high_risk[:5])}",
                recommendation="Review content for actual sensitive data presence",
            ))

        # Check for business-sensitive content
        found_business = [kw for kw in self.BUSINESS_SENSITIVE if kw in content_lower]
        if found_business:
            violations.append(PrivacyViolation(
                violation_type="business_sensitive",
                severity=SensitivityLevel.CONFIDENTIAL,
                description=f"Business-sensitive terms detected: {', '.join(found_business[:5])}",
                recommendation="Ensure business data is abstracted before cross-validation sharing",
            ))

        # Compliance-specific checks
        if compliance_frameworks:
            for framework in compliance_frameworks:
                framework_violations = self._check_compliance(content, framework)
                violations.extend(framework_violations)

        # Generate recommendations
        if violations:
            recommendations.append("Run content through AnonymizerTool before storage")
            recommendations.append("Abstract business-specific details to general patterns")
            if any(v.severity == SensitivityLevel.RESTRICTED for v in violations):
                recommendations.append("CRITICAL: Content contains PII - do not store without sanitization")

        # Determine overall sensitivity
        if any(v.severity == SensitivityLevel.RESTRICTED for v in violations):
            sensitivity = SensitivityLevel.RESTRICTED
        elif any(v.severity == SensitivityLevel.CONFIDENTIAL for v in violations):
            sensitivity = SensitivityLevel.CONFIDENTIAL
        elif violations:
            sensitivity = SensitivityLevel.INTERNAL
        else:
            sensitivity = SensitivityLevel.PUBLIC

        # Create audit record
        audit_record = PrivacyAuditRecord(
            operation="privacy_check",
            data_classification=sensitivity,
            validation_id=context.get("validation_id") if context else None,
            violations_found=len(violations),
            action_taken="check_completed",
            checksum=self._compute_checksum(content),
        )

        return PrivacyCheckResult(
            is_safe=len(violations) == 0,
            sensitivity_level=sensitivity,
            violations=violations,
            recommendations=recommendations,
            audit_record=audit_record,
        )

    def classify_sensitivity(self, content: str) -> SensitivityLevel:
        """
        Classify the sensitivity level of content.

        Args:
            content: The content to classify

        Returns:
            SensitivityLevel classification
        """
        # Check for restricted (PII) patterns
        for pattern_name in ["email", "phone", "ssn", "credit_card", "api_key", "password"]:
            if self.SENSITIVE_PATTERNS[pattern_name].search(content):
                return SensitivityLevel.RESTRICTED

        content_lower = content.lower()

        # Check for high-risk keywords
        if any(kw in content_lower for kw in self.HIGH_RISK_KEYWORDS):
            return SensitivityLevel.CONFIDENTIAL

        # Check for business-sensitive content
        if any(kw in content_lower for kw in self.BUSINESS_SENSITIVE):
            return SensitivityLevel.CONFIDENTIAL

        # Check for internal indicators
        internal_indicators = ["internal", "draft", "confidential", "proprietary"]
        if any(ind in content_lower for ind in internal_indicators):
            return SensitivityLevel.INTERNAL

        return SensitivityLevel.PUBLIC

    def sanitize_content(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PrivacyCheckResult:
        """
        Sanitize content by removing/replacing sensitive data.

        Args:
            content: The content to sanitize
            context: Optional context for better sanitization

        Returns:
            PrivacyCheckResult with sanitized_content
        """
        # First do a privacy check
        check_result = self.check_privacy(content, context)

        # Apply anonymization
        sanitized = anonymize_text(content, preserve_structure=True)

        # Additional sanitization for detected patterns
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            placeholder = f"[{pattern_name.upper()}]"
            sanitized = pattern.sub(placeholder, sanitized)

        # Update result with sanitized content
        check_result.sanitized_content = sanitized
        check_result.audit_record.action_taken = "content_sanitized"

        return check_result

    def create_audit_record(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PrivacyAuditRecord:
        """
        Create an audit record for privacy operations.

        Args:
            content: The content being processed
            context: Operation context

        Returns:
            PrivacyAuditRecord for compliance tracking
        """
        sensitivity = self.classify_sensitivity(content)

        return PrivacyAuditRecord(
            operation="audit_created",
            data_classification=sensitivity,
            validation_id=context.get("validation_id") if context else None,
            violations_found=0,
            action_taken="audit_record_generated",
            checksum=self._compute_checksum(content),
        )

    def validate_cross_validation_sharing(
        self,
        content: str,
        source_validation_id: str,
        target_validation_id: str,
    ) -> PrivacyCheckResult:
        """
        Validate that content can be safely shared across validations.

        This enforces privacy boundaries between different founder validations.

        Args:
            content: Content to be shared
            source_validation_id: Where the content came from
            target_validation_id: Where it's being shared to

        Returns:
            PrivacyCheckResult indicating if sharing is safe
        """
        # Run standard privacy check
        result = self.check_privacy(content, {
            "validation_id": source_validation_id,
            "intended_use": f"cross_validation_sharing_to_{target_validation_id}",
        })

        # Add cross-validation specific checks
        if not result.is_safe:
            result.recommendations.append(
                "Content must be fully anonymized before cross-validation sharing"
            )
            result.recommendations.append(
                "Use abstract_business_context() to remove founder-specific details"
            )

        # Even if safe, add reminder about abstraction
        if result.is_safe:
            result.recommendations.append(
                "Ensure patterns are abstracted to industry-level insights"
            )

        return result

    def _check_compliance(
        self,
        content: str,
        framework: str,
    ) -> List[PrivacyViolation]:
        """Check content against specific compliance framework."""
        violations = []

        if framework.lower() == "gdpr":
            # GDPR specific checks
            if EMAIL_PATTERN.search(content) or PHONE_PATTERN.search(content):
                violations.append(PrivacyViolation(
                    violation_type="gdpr_personal_data",
                    severity=SensitivityLevel.RESTRICTED,
                    description="GDPR: Personal data detected (email/phone)",
                    recommendation="Obtain consent or anonymize before processing",
                ))

        elif framework.lower() == "ccpa":
            # CCPA specific checks
            pii_patterns = ["email", "phone", "ssn", "ip_address"]
            for pattern_name in pii_patterns:
                if self.SENSITIVE_PATTERNS[pattern_name].search(content):
                    violations.append(PrivacyViolation(
                        violation_type="ccpa_personal_information",
                        severity=SensitivityLevel.RESTRICTED,
                        description=f"CCPA: Personal information detected ({pattern_name})",
                        recommendation="Provide opt-out mechanism or anonymize",
                    ))
                    break

        elif framework.lower() == "hipaa":
            # HIPAA specific checks
            hipaa_terms = ["patient", "diagnosis", "treatment", "medical record", "health"]
            content_lower = content.lower()
            if any(term in content_lower for term in hipaa_terms):
                violations.append(PrivacyViolation(
                    violation_type="hipaa_phi_indicator",
                    severity=SensitivityLevel.RESTRICTED,
                    description="HIPAA: Potential PHI indicators detected",
                    recommendation="Ensure proper de-identification per HIPAA Safe Harbor",
                ))

        return violations

    def _compute_checksum(self, content: str) -> str:
        """Compute SHA-256 checksum for data integrity."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _format_check_result(self, result: PrivacyCheckResult) -> str:
        """Format privacy check result for display."""
        lines = [
            "## Privacy Check Result\n",
            f"**Status:** {'SAFE' if result.is_safe else 'VIOLATIONS DETECTED'}",
            f"**Sensitivity Level:** {result.sensitivity_level.value.upper()}",
            "",
        ]

        if result.violations:
            lines.append("### Violations Found")
            for v in result.violations:
                lines.append(f"- **{v.violation_type}** ({v.severity.value})")
                lines.append(f"  - {v.description}")
                lines.append(f"  - Recommendation: {v.recommendation}")
            lines.append("")

        if result.recommendations:
            lines.append("### Recommendations")
            for r in result.recommendations:
                lines.append(f"- {r}")

        return "\n".join(lines)

    def _format_audit_record(self, record: PrivacyAuditRecord) -> str:
        """Format audit record for display."""
        return f"""## Privacy Audit Record

**Timestamp:** {record.timestamp}
**Operation:** {record.operation}
**Classification:** {record.data_classification.value.upper()}
**Validation ID:** {record.validation_id or 'N/A'}
**Violations Found:** {record.violations_found}
**Action Taken:** {record.action_taken}
**Data Checksum:** {record.checksum or 'N/A'}
"""


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def check_privacy(
    content: str,
    compliance: Optional[List[str]] = None,
) -> PrivacyCheckResult:
    """
    Quick privacy check on content.

    Args:
        content: Content to check
        compliance: Optional compliance frameworks to check

    Returns:
        PrivacyCheckResult
    """
    tool = PrivacyGuardTool()
    return tool.check_privacy(content, compliance_frameworks=compliance)


def is_safe_for_storage(content: str) -> bool:
    """
    Quick check if content is safe for Flywheel storage.

    Args:
        content: Content to check

    Returns:
        True if safe, False if contains sensitive data
    """
    tool = PrivacyGuardTool()
    result = tool.check_privacy(content)
    return result.is_safe


def sanitize_for_flywheel(content: str) -> str:
    """
    Sanitize content for safe Flywheel storage.

    Args:
        content: Content to sanitize

    Returns:
        Sanitized content
    """
    tool = PrivacyGuardTool()
    result = tool.sanitize_content(content)
    return result.sanitized_content or content


def classify_sensitivity(content: str) -> str:
    """
    Classify content sensitivity level.

    Args:
        content: Content to classify

    Returns:
        Sensitivity level string
    """
    tool = PrivacyGuardTool()
    return tool.classify_sensitivity(content).value
