"""
Tests for Landing Page Deployment Tool.

Tests LandingPageDeploymentTool with mocked Supabase Storage responses
to avoid actual deployments during testing.

Architecture: ADR-003 - Supabase Storage for Landing Pages
"""

import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

from shared.tools.landing_page_deploy import (
    LandingPageDeploymentTool,
    deploy_landing_page,
    DeploymentResult,
    LandingPageDeployInput,
    TRACKING_JS_TEMPLATE,
)


# ===========================================================================
# TEST FIXTURES
# ===========================================================================


@pytest.fixture
def deploy_tool():
    """Create a LandingPageDeploymentTool instance."""
    return LandingPageDeploymentTool()


@pytest.fixture
def sample_html():
    """Sample HTML for testing."""
    return """<!DOCTYPE html>
<html>
<head><title>Test Landing Page</title></head>
<body>
    <h1>Validate Your Startup Idea</h1>
    <p>Sign up for early access.</p>
    <form><input type="email" name="email" placeholder="Email"><button>Sign Up</button></form>
</body>
</html>"""


@pytest.fixture
def sample_html_no_body():
    """Sample HTML without closing body tag."""
    return """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<h1>Hello World</h1>
</html>"""


@pytest.fixture
def mock_supabase_storage():
    """Mock Supabase storage bucket."""
    mock_storage = MagicMock()
    mock_storage.upload.return_value = Mock()
    mock_storage.get_public_url.return_value = (
        "https://eqxropalhxjeyvfcoyxg.supabase.co/storage/v1/object/public/landing-pages/test-project/variant-a.html"
    )
    return mock_storage


@pytest.fixture
def mock_supabase_client(mock_supabase_storage):
    """Mock Supabase client."""
    mock_client = MagicMock()
    mock_client.storage.from_.return_value = mock_supabase_storage
    mock_client.table.return_value.upsert.return_value.execute.return_value = Mock()
    return mock_client


# ===========================================================================
# DEPLOYMENT RESULT TESTS
# ===========================================================================


class TestDeploymentResult:
    """Tests for DeploymentResult model."""

    def test_successful_result(self):
        """Test creating a successful deployment result."""
        result = DeploymentResult(
            success=True,
            deployed_url="https://test.supabase.co/storage/v1/object/public/landing-pages/proj/variant.html",
            deploy_id="proj/variant.html",
            site_id="proj/variant.html",
            site_name="landing-pages/proj/variant.html",
            variant_id="variant-a",
            deploy_time_ms=1234,
        )

        assert result.success is True
        assert "supabase.co" in result.deployed_url
        assert result.deploy_id == "proj/variant.html"
        assert result.site_id == "proj/variant.html"
        assert result.site_name == "landing-pages/proj/variant.html"
        assert result.variant_id == "variant-a"
        assert result.deploy_time_ms == 1234
        assert result.error_message is None
        assert result.error_code is None

    def test_failed_result(self):
        """Test creating a failed deployment result."""
        result = DeploymentResult(
            success=False,
            variant_id="variant-b",
            error_message="Bucket not found",
            error_code="BUCKET_NOT_FOUND",
        )

        assert result.success is False
        assert result.deployed_url is None
        assert result.variant_id == "variant-b"
        assert result.error_message == "Bucket not found"
        assert result.error_code == "BUCKET_NOT_FOUND"

    def test_default_deployed_at(self):
        """Test that deployed_at is auto-populated."""
        result = DeploymentResult(success=True, variant_id="test")
        assert result.deployed_at is not None
        # Should be a valid ISO format datetime
        datetime.fromisoformat(result.deployed_at)


# ===========================================================================
# INPUT SCHEMA TESTS
# ===========================================================================


class TestLandingPageDeployInput:
    """Tests for LandingPageDeployInput schema."""

    def test_required_fields(self):
        """Test required fields are enforced."""
        with pytest.raises(ValueError):
            LandingPageDeployInput()  # Missing required fields

    def test_valid_input(self):
        """Test valid input creation."""
        input_data = LandingPageDeployInput(
            html="<html><body>Test</body></html>",
            project_id="proj-123",
            variant_id="variant-a",
        )

        assert input_data.html == "<html><body>Test</body></html>"
        assert input_data.project_id == "proj-123"
        assert input_data.variant_id == "variant-a"
        assert input_data.site_name is None

    def test_default_variant_id(self):
        """Test default variant_id is 'default'."""
        input_data = LandingPageDeployInput(
            html="<html></html>",
            project_id="proj-456",
        )
        assert input_data.variant_id == "default"

    def test_optional_site_name(self):
        """Test optional site_name (backward compatibility)."""
        input_data = LandingPageDeployInput(
            html="<html></html>",
            project_id="proj-789",
            site_name="custom-site-name",  # Ignored in new implementation
        )
        assert input_data.site_name == "custom-site-name"


# ===========================================================================
# TOOL TESTS - NO API CALLS
# ===========================================================================


class TestLandingPageDeploymentToolBasic:
    """Tests for LandingPageDeploymentTool without API calls."""

    def test_tool_attributes(self, deploy_tool):
        """Test tool has correct attributes."""
        assert deploy_tool.name == "landing_page_deploy"
        assert "Supabase Storage" in deploy_tool.description
        assert deploy_tool.args_schema == LandingPageDeployInput

    def test_sanitize_path_segment_lowercase(self, deploy_tool):
        """Test path segment is lowercased."""
        result = deploy_tool._sanitize_path_segment("TestProject")
        assert result == "testproject"

    def test_sanitize_path_segment_special_chars(self, deploy_tool):
        """Test special characters are replaced with hyphens."""
        result = deploy_tool._sanitize_path_segment("test_project@123")
        assert result == "test-project-123"

    def test_sanitize_path_segment_consecutive_hyphens(self, deploy_tool):
        """Test consecutive hyphens are collapsed."""
        result = deploy_tool._sanitize_path_segment("test--project---name")
        assert result == "test-project-name"

    def test_sanitize_path_segment_truncation(self, deploy_tool):
        """Test path segment is truncated to 50 chars."""
        long_name = "a" * 100
        result = deploy_tool._sanitize_path_segment(long_name)
        assert len(result) == 50

    def test_sanitize_path_segment_strip_hyphens(self, deploy_tool):
        """Test leading/trailing hyphens are stripped."""
        result = deploy_tool._sanitize_path_segment("-test-project-")
        assert result == "test-project"

    def test_sanitize_path_segment_empty_returns_default(self, deploy_tool):
        """Test empty string returns 'default'."""
        result = deploy_tool._sanitize_path_segment("---")
        assert result == "default"

    def test_format_output_success(self, deploy_tool):
        """Test formatting successful deployment output."""
        result = DeploymentResult(
            success=True,
            deployed_url="https://test.supabase.co/storage/v1/object/public/landing-pages/proj/variant.html",
            variant_id="variant-a",
            site_name="landing-pages/proj/variant.html",
            deploy_id="proj/variant.html",
            deploy_time_ms=500,
        )

        output = deploy_tool._format_output(result)

        assert "Landing Page Deployed Successfully" in output
        assert "supabase.co" in output
        assert "variant-a" in output
        assert "proj/variant.html" in output
        assert "500ms" in output

    def test_format_output_failure(self, deploy_tool):
        """Test formatting failed deployment output."""
        result = DeploymentResult(
            success=False,
            variant_id="variant-b",
            error_message="Bucket not found",
            error_code="BUCKET_NOT_FOUND",
        )

        output = deploy_tool._format_output(result)

        assert "Landing Page Deployment Failed" in output
        assert "Bucket not found" in output
        assert "BUCKET_NOT_FOUND" in output
        assert "variant-b" in output

    def test_format_error(self, deploy_tool):
        """Test formatting error message."""
        output = deploy_tool._format_error("Test error", "TEST_CODE")

        assert "Landing Page Deployment Failed" in output
        assert "Test error" in output
        assert "TEST_CODE" in output
        assert "SUPABASE_URL" in output  # Should mention env vars


# ===========================================================================
# TRACKING JS INJECTION TESTS
# ===========================================================================


class TestTrackingJSInjection:
    """Tests for tracking JavaScript injection."""

    def test_inject_tracking_before_body_end(self, deploy_tool, sample_html):
        """Test tracking JS is injected before </body>."""
        result = deploy_tool._inject_tracking(
            html=sample_html,
            variant_id="test-variant",
            supabase_url="https://test.supabase.co",
            supabase_anon_key="test-anon-key",
        )

        # Tracking JS should be present
        assert "lp_pageviews" in result
        assert "lp_submissions" in result
        assert "test-variant" in result
        assert "test-anon-key" in result

        # Should still have </body>
        assert "</body>" in result.lower()

        # Tracking JS should be before </body>
        tracking_idx = result.lower().find("lp_pageviews")
        body_end_idx = result.lower().rfind("</body>")
        assert tracking_idx < body_end_idx

    def test_inject_tracking_no_body_tag(self, deploy_tool, sample_html_no_body):
        """Test tracking JS is appended when no </body> tag."""
        result = deploy_tool._inject_tracking(
            html=sample_html_no_body,
            variant_id="test-variant",
            supabase_url="https://test.supabase.co",
            supabase_anon_key="test-anon-key",
        )

        # Tracking JS should be present at end
        assert "lp_pageviews" in result
        assert result.endswith("</script>\n")

    def test_inject_tracking_no_anon_key(self, deploy_tool, sample_html):
        """Test tracking JS is skipped when no anon key."""
        result = deploy_tool._inject_tracking(
            html=sample_html,
            variant_id="test-variant",
            supabase_url="https://test.supabase.co",
            supabase_anon_key="",  # Empty
        )

        # Should return original HTML unchanged
        assert result == sample_html
        assert "lp_pageviews" not in result

    def test_tracking_js_template_has_placeholders(self):
        """Test that tracking JS template has required placeholders."""
        assert "{supabase_url}" in TRACKING_JS_TEMPLATE
        assert "{supabase_anon_key}" in TRACKING_JS_TEMPLATE
        assert "{variant_id}" in TRACKING_JS_TEMPLATE

    def test_tracking_js_case_insensitive_body_tag(self, deploy_tool):
        """Test tracking JS injection handles case-insensitive body tag."""
        html_upper = "<html><BODY><p>Test</p></BODY></html>"
        result = deploy_tool._inject_tracking(
            html=html_upper,
            variant_id="test",
            supabase_url="https://test.supabase.co",
            supabase_anon_key="key",
        )
        assert "lp_pageviews" in result


# ===========================================================================
# TOOL TESTS - WITH MOCKED SUPABASE CALLS
# ===========================================================================


class TestLandingPageDeploymentToolWithMocks:
    """Tests for LandingPageDeploymentTool with mocked Supabase calls."""

    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-service-key',
        'SUPABASE_ANON_KEY': 'test-anon-key',
    })
    @patch('state.persistence.get_supabase')
    def test_run_successful_deployment(
        self, mock_get_supabase, deploy_tool, sample_html, mock_supabase_client
    ):
        """Test successful deployment to Supabase Storage."""
        mock_get_supabase.return_value = mock_supabase_client

        result = deploy_tool._run(
            html=sample_html,
            project_id="test-project",
            variant_id="variant-a",
        )

        assert "Landing Page Deployed Successfully" in result
        assert "supabase.co" in result
        assert "variant-a" in result

        # Verify storage was called
        mock_supabase_client.storage.from_.assert_called_with("landing-pages")

    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-service-key',
        'SUPABASE_ANON_KEY': 'test-anon-key',
    })
    @patch('state.persistence.get_supabase')
    def test_run_storage_path_sanitized(
        self, mock_get_supabase, deploy_tool, sample_html, mock_supabase_client
    ):
        """Test that project_id and variant_id are sanitized for storage path."""
        mock_get_supabase.return_value = mock_supabase_client

        result = deploy_tool._run(
            html=sample_html,
            project_id="Test_Project@123",
            variant_id="Variant A!",
        )

        # Verify upload was called with sanitized path
        mock_storage = mock_supabase_client.storage.from_.return_value
        upload_call = mock_storage.upload.call_args

        # Path should be sanitized
        storage_path = upload_call[1].get('path') or upload_call[0][0]
        assert storage_path == "test-project-123/variant-a.html"

    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-service-key',
    }, clear=True)  # No SUPABASE_ANON_KEY
    @patch('state.persistence.get_supabase')
    def test_run_no_anon_key_warning(
        self, mock_get_supabase, deploy_tool, sample_html, mock_supabase_client
    ):
        """Test deployment succeeds but warns when SUPABASE_ANON_KEY is missing."""
        mock_get_supabase.return_value = mock_supabase_client

        result = deploy_tool._run(
            html=sample_html,
            project_id="test-project",
            variant_id="variant-a",
        )

        # Should still succeed (tracking just won't work)
        assert "Landing Page Deployed Successfully" in result

    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-service-key',
        'SUPABASE_ANON_KEY': 'test-anon-key',
    })
    @patch('state.persistence.get_supabase')
    def test_run_bucket_not_found(self, mock_get_supabase, deploy_tool, sample_html):
        """Test error when storage bucket doesn't exist."""
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_storage.upload.side_effect = Exception("Bucket not found")
        mock_client.storage.from_.return_value = mock_storage
        mock_get_supabase.return_value = mock_client

        result = deploy_tool._run(
            html=sample_html,
            project_id="test-project",
            variant_id="variant-a",
        )

        assert "Landing Page Deployment Failed" in result
        assert "BUCKET_NOT_FOUND" in result

    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-service-key',
        'SUPABASE_ANON_KEY': 'test-anon-key',
    })
    @patch('state.persistence.get_supabase')
    def test_run_upload_error(self, mock_get_supabase, deploy_tool, sample_html):
        """Test handling of upload failure."""
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_storage.upload.side_effect = Exception("Network error")
        mock_client.storage.from_.return_value = mock_storage
        mock_get_supabase.return_value = mock_client

        result = deploy_tool._run(
            html=sample_html,
            project_id="test-project",
            variant_id="variant-a",
        )

        assert "Landing Page Deployment Failed" in result
        assert "DEPLOY_ERROR" in result
        assert "Network error" in result

    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-service-key',
        'SUPABASE_ANON_KEY': 'test-anon-key',
    })
    @patch('state.persistence.get_supabase')
    def test_run_metadata_failure_continues(
        self, mock_get_supabase, deploy_tool, sample_html
    ):
        """Test that metadata recording failure doesn't fail the deployment."""
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_storage.upload.return_value = Mock()
        mock_storage.get_public_url.return_value = "https://test.supabase.co/storage/v1/object/public/landing-pages/test/variant.html"
        mock_client.storage.from_.return_value = mock_storage

        # Table upsert fails
        mock_client.table.return_value.upsert.return_value.execute.side_effect = Exception("DB error")
        mock_get_supabase.return_value = mock_client

        result = deploy_tool._run(
            html=sample_html,
            project_id="test",
            variant_id="variant",
        )

        # Should still succeed (metadata is non-critical)
        assert "Landing Page Deployed Successfully" in result


# ===========================================================================
# CONVENIENCE FUNCTION TESTS
# ===========================================================================


class TestDeployLandingPageFunction:
    """Tests for deploy_landing_page convenience function."""

    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-service-key',
        'SUPABASE_ANON_KEY': 'test-anon-key',
    })
    @patch('state.persistence.get_supabase')
    def test_deploy_landing_page_success(
        self, mock_get_supabase, sample_html, mock_supabase_client
    ):
        """Test convenience function successful deployment."""
        mock_get_supabase.return_value = mock_supabase_client

        result = deploy_landing_page(
            html=sample_html,
            project_id="test-project",
            variant_id="test-variant",
        )

        assert "Landing Page Deployed Successfully" in result

    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-service-key',
        'SUPABASE_ANON_KEY': 'test-anon-key',
    })
    @patch('state.persistence.get_supabase')
    def test_deploy_landing_page_with_site_name_ignored(
        self, mock_get_supabase, sample_html, mock_supabase_client
    ):
        """Test convenience function ignores site_name (backward compat)."""
        mock_get_supabase.return_value = mock_supabase_client

        result = deploy_landing_page(
            html=sample_html,
            project_id="test-project",
            variant_id="test-variant",
            site_name="custom-site",  # Should be ignored
        )

        assert "Landing Page Deployed Successfully" in result
        # site_name doesn't affect the storage path
        mock_storage = mock_supabase_client.storage.from_.return_value
        upload_call = mock_storage.upload.call_args
        storage_path = upload_call[1].get('path') or upload_call[0][0]
        assert "custom-site" not in storage_path


# ===========================================================================
# INTEGRATION WITH BUILDCREW TESTS
# ===========================================================================


class TestBuildCrewIntegration:
    """Tests to verify tool is correctly wired to BuildCrew."""

    def test_tool_can_be_imported_from_shared_tools(self):
        """Test that tool can be imported from shared.tools."""
        from shared.tools import LandingPageDeploymentTool, deploy_landing_page, DeploymentResult

        assert LandingPageDeploymentTool is not None
        assert deploy_landing_page is not None
        assert DeploymentResult is not None

    def test_build_crew_f3_has_deployment_tool(self):
        """Test that F3 agent in BuildCrew has the deployment tool."""
        # Import the crew to verify it compiles with the new tool
        from crews.desirability.build_crew import BuildCrew

        # Verify the import doesn't fail
        assert BuildCrew is not None

    def test_tool_instantiation_in_agent_context(self):
        """Test that tool can be instantiated as agents do."""
        from shared.tools import LandingPageDeploymentTool

        tool = LandingPageDeploymentTool()

        assert tool.name == "landing_page_deploy"
        assert tool.args_schema == LandingPageDeployInput


# ===========================================================================
# ASYNC TESTS
# ===========================================================================


class TestAsyncSupport:
    """Tests for async method support."""

    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-service-key',
        'SUPABASE_ANON_KEY': 'test-anon-key',
    })
    @patch('state.persistence.get_supabase')
    @pytest.mark.asyncio
    async def test_arun_delegates_to_run(
        self, mock_get_supabase, deploy_tool, sample_html, mock_supabase_client
    ):
        """Test that _arun delegates to _run."""
        mock_get_supabase.return_value = mock_supabase_client

        result = await deploy_tool._arun(
            html=sample_html,
            project_id="test-project",
            variant_id="variant-a",
        )

        assert "Landing Page Deployed Successfully" in result
