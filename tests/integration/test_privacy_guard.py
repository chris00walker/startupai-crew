"""
Tests for PrivacyGuard Tool.

Tests cover:
1. PII detection (emails, phones, SSNs, credit cards)
2. Credential detection (API keys, passwords)
3. Business sensitivity classification
4. Compliance framework checks (GDPR, CCPA, HIPAA)
5. Content sanitization
6. Cross-validation privacy boundaries
"""

import pytest
import json

from startupai.tools.privacy_guard import (
    PrivacyGuardTool,
    SensitivityLevel,
    ComplianceFramework,
    PrivacyViolation,
    PrivacyAuditRecord,
    PrivacyCheckResult,
    check_privacy,
    is_safe_for_storage,
    sanitize_for_flywheel,
    classify_sensitivity,
)


# =======================================================================================
# PRIVACY GUARD TOOL TESTS
# =======================================================================================

class TestPrivacyGuardTool:
    """Tests for PrivacyGuardTool."""

    def test_tool_creation(self):
        """Test tool can be instantiated."""
        tool = PrivacyGuardTool()
        assert tool.name == "privacy_guard"
        assert "privacy" in tool.description.lower()

    def test_detect_email(self):
        """Test email detection."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy("Contact john@example.com for details")

        assert not result.is_safe
        assert result.sensitivity_level == SensitivityLevel.RESTRICTED
        assert any("email" in v.violation_type for v in result.violations)

    def test_detect_phone(self):
        """Test phone number detection."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy("Call me at 555-123-4567")

        assert not result.is_safe
        assert any("phone" in v.violation_type for v in result.violations)

    def test_detect_ssn(self):
        """Test SSN detection."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy("SSN: 123-45-6789")

        assert not result.is_safe
        assert result.sensitivity_level == SensitivityLevel.RESTRICTED
        assert any("ssn" in v.violation_type for v in result.violations)

    def test_detect_credit_card(self):
        """Test credit card detection."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy("Card: 4111-1111-1111-1111")

        assert not result.is_safe
        assert any("credit_card" in v.violation_type for v in result.violations)

    def test_detect_api_key(self):
        """Test API key detection."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy("Use api_key=sk-abc123def456ghi789jkl012")

        assert not result.is_safe
        assert any("api_key" in v.violation_type for v in result.violations)

    def test_detect_password(self):
        """Test password detection."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy("password=mysecretpass123")

        assert not result.is_safe
        assert any("password" in v.violation_type for v in result.violations)

    def test_safe_content(self):
        """Test that clean content passes."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy("This is a general learning about SaaS pricing strategies.")

        assert result.is_safe
        assert result.sensitivity_level == SensitivityLevel.PUBLIC

    def test_high_risk_keywords(self):
        """Test high-risk keyword detection."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy("The social security number was verified")

        assert not result.is_safe
        assert any("high_risk" in v.violation_type for v in result.violations)

    def test_business_sensitive_keywords(self):
        """Test business-sensitive keyword detection."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy("Our revenue last quarter was $5M with 40% profit margin")

        assert not result.is_safe
        assert result.sensitivity_level in [SensitivityLevel.CONFIDENTIAL, SensitivityLevel.RESTRICTED]
        assert any("business_sensitive" in v.violation_type for v in result.violations)


# =======================================================================================
# SENSITIVITY CLASSIFICATION TESTS
# =======================================================================================

class TestSensitivityClassification:
    """Tests for sensitivity classification."""

    def test_classify_restricted(self):
        """Test restricted classification for PII."""
        tool = PrivacyGuardTool()
        level = tool.classify_sensitivity("Email: test@example.com")
        assert level == SensitivityLevel.RESTRICTED

    def test_classify_confidential(self):
        """Test confidential classification for business data."""
        tool = PrivacyGuardTool()
        level = tool.classify_sensitivity("Our valuation is $10M")
        assert level == SensitivityLevel.CONFIDENTIAL

    def test_classify_internal(self):
        """Test internal classification."""
        tool = PrivacyGuardTool()
        level = tool.classify_sensitivity("This is an internal draft document")
        assert level == SensitivityLevel.INTERNAL

    def test_classify_public(self):
        """Test public classification."""
        tool = PrivacyGuardTool()
        level = tool.classify_sensitivity("SaaS companies typically target 3x LTV/CAC ratio")
        assert level == SensitivityLevel.PUBLIC


# =======================================================================================
# COMPLIANCE FRAMEWORK TESTS
# =======================================================================================

class TestComplianceChecks:
    """Tests for compliance framework checks."""

    def test_gdpr_email_violation(self):
        """Test GDPR violation for email."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy(
            "Contact user@example.com",
            compliance_frameworks=["gdpr"]
        )

        assert not result.is_safe
        assert any("gdpr" in v.violation_type.lower() for v in result.violations)

    def test_ccpa_pii_violation(self):
        """Test CCPA violation for PII."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy(
            "User IP: 192.168.1.1",
            compliance_frameworks=["ccpa"]
        )

        assert not result.is_safe
        assert any("ccpa" in v.violation_type.lower() for v in result.violations)

    def test_hipaa_phi_indicators(self):
        """Test HIPAA PHI indicator detection."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy(
            "Patient diagnosis shows treatment plan",
            compliance_frameworks=["hipaa"]
        )

        assert not result.is_safe
        assert any("hipaa" in v.violation_type.lower() for v in result.violations)


# =======================================================================================
# SANITIZATION TESTS
# =======================================================================================

class TestContentSanitization:
    """Tests for content sanitization."""

    def test_sanitize_email(self):
        """Test email sanitization."""
        tool = PrivacyGuardTool()
        result = tool.sanitize_content("Contact john@example.com for help")

        assert result.sanitized_content is not None
        assert "john@example.com" not in result.sanitized_content
        assert "[EMAIL]" in result.sanitized_content

    def test_sanitize_phone(self):
        """Test phone sanitization."""
        tool = PrivacyGuardTool()
        result = tool.sanitize_content("Call 555-123-4567")

        assert result.sanitized_content is not None
        assert "555-123-4567" not in result.sanitized_content
        assert "[PHONE]" in result.sanitized_content

    def test_sanitize_multiple_pii(self):
        """Test sanitization of multiple PII types."""
        tool = PrivacyGuardTool()
        content = "Email: john@test.com, Phone: 555-999-8888, SSN: 123-45-6789"
        result = tool.sanitize_content(content)

        assert result.sanitized_content is not None
        assert "john@test.com" not in result.sanitized_content
        assert "555-999-8888" not in result.sanitized_content
        assert "123-45-6789" not in result.sanitized_content

    def test_sanitize_preserves_structure(self):
        """Test that sanitization preserves content structure."""
        tool = PrivacyGuardTool()
        content = "Customer john@test.com reported issue on 2024-01-15"
        result = tool.sanitize_content(content)

        assert result.sanitized_content is not None
        assert "Customer" in result.sanitized_content
        assert "reported issue" in result.sanitized_content


# =======================================================================================
# AUDIT RECORD TESTS
# =======================================================================================

class TestAuditRecords:
    """Tests for audit record generation."""

    def test_audit_record_creation(self):
        """Test audit record is created."""
        tool = PrivacyGuardTool()
        record = tool.create_audit_record(
            "Test content",
            {"validation_id": "val_123"}
        )

        assert record.timestamp is not None
        assert record.operation == "audit_created"
        assert record.validation_id == "val_123"
        assert record.checksum is not None

    def test_audit_record_in_check_result(self):
        """Test audit record included in check result."""
        tool = PrivacyGuardTool()
        result = tool.check_privacy("Test content")

        assert result.audit_record is not None
        assert result.audit_record.operation == "privacy_check"
        assert result.audit_record.checksum is not None

    def test_checksum_consistency(self):
        """Test checksum is consistent for same content."""
        tool = PrivacyGuardTool()
        content = "Consistent test content"

        record1 = tool.create_audit_record(content, {})
        record2 = tool.create_audit_record(content, {})

        assert record1.checksum == record2.checksum

    def test_checksum_changes_with_content(self):
        """Test checksum changes with different content."""
        tool = PrivacyGuardTool()

        record1 = tool.create_audit_record("Content A", {})
        record2 = tool.create_audit_record("Content B", {})

        assert record1.checksum != record2.checksum


# =======================================================================================
# CROSS-VALIDATION PRIVACY TESTS
# =======================================================================================

class TestCrossValidationPrivacy:
    """Tests for cross-validation privacy boundaries."""

    def test_cross_validation_with_pii_fails(self):
        """Test cross-validation sharing fails with PII."""
        tool = PrivacyGuardTool()
        result = tool.validate_cross_validation_sharing(
            content="Customer john@test.com had great feedback",
            source_validation_id="val_001",
            target_validation_id="val_002",
        )

        assert not result.is_safe
        assert len(result.violations) > 0

    def test_cross_validation_clean_content_passes(self):
        """Test cross-validation sharing passes with clean content."""
        tool = PrivacyGuardTool()
        result = tool.validate_cross_validation_sharing(
            content="B2B SaaS companies typically see 3-5% monthly churn in early stages",
            source_validation_id="val_001",
            target_validation_id="val_002",
        )

        assert result.is_safe
        assert len(result.recommendations) > 0  # Should still have abstraction reminder

    def test_cross_validation_recommendations(self):
        """Test cross-validation provides useful recommendations."""
        tool = PrivacyGuardTool()
        result = tool.validate_cross_validation_sharing(
            content="Our company Acme Corp found that pricing at $99/mo worked best",
            source_validation_id="val_001",
            target_validation_id="val_002",
        )

        # May or may not be safe depending on detection
        assert len(result.recommendations) > 0


# =======================================================================================
# TOOL RUN METHOD TESTS
# =======================================================================================

class TestToolRunMethod:
    """Tests for the _run method interface."""

    def test_run_check_action(self):
        """Test check action via _run."""
        tool = PrivacyGuardTool()
        result = tool._run(json.dumps({
            "action": "check",
            "content": "Contact test@example.com",
        }))

        assert "Privacy Check Result" in result
        assert "VIOLATIONS DETECTED" in result

    def test_run_classify_action(self):
        """Test classify action via _run."""
        tool = PrivacyGuardTool()
        result = tool._run(json.dumps({
            "action": "classify",
            "content": "Public information about SaaS",
        }))

        assert "Sensitivity Level" in result
        assert "PUBLIC" in result

    def test_run_sanitize_action(self):
        """Test sanitize action via _run."""
        tool = PrivacyGuardTool()
        result = tool._run(json.dumps({
            "action": "sanitize",
            "content": "Email: john@test.com",
        }))

        assert "john@test.com" not in result
        assert "[EMAIL]" in result

    def test_run_audit_action(self):
        """Test audit action via _run."""
        tool = PrivacyGuardTool()
        result = tool._run(json.dumps({
            "action": "audit",
            "content": "Test content",
            "context": {"validation_id": "val_test"},
        }))

        assert "Privacy Audit Record" in result
        assert "val_test" in result

    def test_run_invalid_json(self):
        """Test handling of invalid JSON."""
        tool = PrivacyGuardTool()
        result = tool._run("not valid json")

        assert "Error" in result

    def test_run_unknown_action(self):
        """Test handling of unknown action."""
        tool = PrivacyGuardTool()
        result = tool._run(json.dumps({
            "action": "unknown",
        }))

        assert "Unknown action" in result


# =======================================================================================
# CONVENIENCE FUNCTION TESTS
# =======================================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_check_privacy_function(self):
        """Test check_privacy convenience function."""
        result = check_privacy("Test content with email@test.com")

        assert isinstance(result, PrivacyCheckResult)
        assert not result.is_safe

    def test_is_safe_for_storage_true(self):
        """Test is_safe_for_storage returns True for clean content."""
        is_safe = is_safe_for_storage("General SaaS pricing patterns")
        assert is_safe is True

    def test_is_safe_for_storage_false(self):
        """Test is_safe_for_storage returns False for PII."""
        is_safe = is_safe_for_storage("User email: test@example.com")
        assert is_safe is False

    def test_sanitize_for_flywheel(self):
        """Test sanitize_for_flywheel convenience function."""
        sanitized = sanitize_for_flywheel("Contact john@test.com for details")

        assert "john@test.com" not in sanitized
        assert "[EMAIL]" in sanitized

    def test_classify_sensitivity_function(self):
        """Test classify_sensitivity convenience function."""
        level = classify_sensitivity("Our revenue was $5M")
        assert level == "confidential"


# =======================================================================================
# TOOLS EXPORT TESTS
# =======================================================================================

class TestToolsExport:
    """Tests for tools module exports."""

    def test_privacy_guard_exported(self):
        """Test PrivacyGuard exports from tools module."""
        from startupai.tools import (
            PrivacyGuardTool,
            SensitivityLevel,
            ComplianceFramework,
            PrivacyViolation,
            PrivacyAuditRecord,
            PrivacyCheckResult,
            check_privacy,
            is_safe_for_storage,
            sanitize_for_flywheel,
            classify_sensitivity,
        )

        # Verify all imports work
        assert PrivacyGuardTool is not None
        assert SensitivityLevel.RESTRICTED is not None
        assert ComplianceFramework.GDPR is not None
        assert callable(check_privacy)
        assert callable(is_safe_for_storage)
        assert callable(sanitize_for_flywheel)
        assert callable(classify_sensitivity)
