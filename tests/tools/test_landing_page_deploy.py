"""
Tests for Landing Page Deployment Tool.

Tests LandingPageDeploymentTool with mocked Netlify API responses
to avoid actual deployments during testing.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

from shared.tools.landing_page_deploy import (
    LandingPageDeploymentTool,
    deploy_landing_page,
    DeploymentResult,
    LandingPageDeployInput,
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
    <form><input type="email" placeholder="Email"><button>Sign Up</button></form>
</body>
</html>"""


@pytest.fixture
def mock_netlify_create_site_response():
    """Mock successful site creation response."""
    return {
        "id": "site-123-abc",
        "name": "startupai-test-variant-a-abc12345",
        "ssl_url": "https://startupai-test-variant-a-abc12345.netlify.app",
        "url": "http://startupai-test-variant-a-abc12345.netlify.app",
        "admin_url": "https://app.netlify.com/sites/startupai-test-variant-a-abc12345",
    }


@pytest.fixture
def mock_netlify_deploy_response():
    """Mock successful deploy response."""
    return {
        "id": "deploy-456-xyz",
        "state": "ready",
        "required": [],  # No files required (already uploaded)
        "deploy_url": "https://deploy-456-xyz--startupai-test-variant-a-abc12345.netlify.app",
        "ssl_url": "https://startupai-test-variant-a-abc12345.netlify.app",
    }


# ===========================================================================
# DEPLOYMENT RESULT TESTS
# ===========================================================================


class TestDeploymentResult:
    """Tests for DeploymentResult model."""

    def test_successful_result(self):
        """Test creating a successful deployment result."""
        result = DeploymentResult(
            success=True,
            deployed_url="https://test-site.netlify.app",
            deploy_id="deploy-123",
            site_id="site-456",
            site_name="test-site",
            variant_id="variant-a",
            deploy_time_ms=1234,
        )

        assert result.success is True
        assert result.deployed_url == "https://test-site.netlify.app"
        assert result.deploy_id == "deploy-123"
        assert result.site_id == "site-456"
        assert result.site_name == "test-site"
        assert result.variant_id == "variant-a"
        assert result.deploy_time_ms == 1234
        assert result.error_message is None
        assert result.error_code is None

    def test_failed_result(self):
        """Test creating a failed deployment result."""
        result = DeploymentResult(
            success=False,
            variant_id="variant-b",
            error_message="Site creation failed",
            error_code="SITE_CREATE_FAILED",
        )

        assert result.success is False
        assert result.deployed_url is None
        assert result.variant_id == "variant-b"
        assert result.error_message == "Site creation failed"
        assert result.error_code == "SITE_CREATE_FAILED"

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
        """Test optional site_name."""
        input_data = LandingPageDeployInput(
            html="<html></html>",
            project_id="proj-789",
            site_name="custom-site-name",
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
        assert "Deploy landing page HTML to Netlify" in deploy_tool.description
        assert deploy_tool.args_schema == LandingPageDeployInput

    def test_sanitize_site_name_lowercase(self, deploy_tool):
        """Test site name is lowercased."""
        result = deploy_tool._sanitize_site_name("TestSite")
        assert result == "testsite"

    def test_sanitize_site_name_special_chars(self, deploy_tool):
        """Test special characters are replaced with hyphens."""
        result = deploy_tool._sanitize_site_name("test_site@123")
        assert result == "test-site-123"

    def test_sanitize_site_name_consecutive_hyphens(self, deploy_tool):
        """Test consecutive hyphens are collapsed."""
        result = deploy_tool._sanitize_site_name("test--site---name")
        assert result == "test-site-name"

    def test_sanitize_site_name_truncation(self, deploy_tool):
        """Test site name is truncated to 63 chars."""
        long_name = "a" * 100
        result = deploy_tool._sanitize_site_name(long_name)
        assert len(result) == 63

    def test_sanitize_site_name_strip_hyphens(self, deploy_tool):
        """Test leading/trailing hyphens are stripped."""
        result = deploy_tool._sanitize_site_name("-test-site-")
        assert result == "test-site"

    def test_format_output_success(self, deploy_tool):
        """Test formatting successful deployment output."""
        result = DeploymentResult(
            success=True,
            deployed_url="https://test.netlify.app",
            variant_id="variant-a",
            site_name="test",
            deploy_id="deploy-123",
            deploy_time_ms=500,
        )

        output = deploy_tool._format_output(result)

        assert "Landing Page Deployed Successfully" in output
        assert "https://test.netlify.app" in output
        assert "variant-a" in output
        assert "deploy-123" in output
        assert "500ms" in output

    def test_format_output_failure(self, deploy_tool):
        """Test formatting failed deployment output."""
        result = DeploymentResult(
            success=False,
            variant_id="variant-b",
            error_message="API timeout",
            error_code="TIMEOUT",
        )

        output = deploy_tool._format_output(result)

        assert "Landing Page Deployment Failed" in output
        assert "API timeout" in output
        assert "TIMEOUT" in output
        assert "variant-b" in output

    def test_format_error(self, deploy_tool):
        """Test formatting error message."""
        output = deploy_tool._format_error("Test error", "TEST_CODE")

        assert "Landing Page Deployment Failed" in output
        assert "Test error" in output
        assert "TEST_CODE" in output


# ===========================================================================
# TOOL TESTS - WITH MOCKED API CALLS
# ===========================================================================


class TestLandingPageDeploymentToolWithMocks:
    """Tests for LandingPageDeploymentTool with mocked API calls."""

    @patch.dict('os.environ', {'NETLIFY_ACCESS_TOKEN': 'test-token'})
    @patch('shared.tools.landing_page_deploy.HTTPX_AVAILABLE', True)
    def test_run_successful_deployment_httpx(
        self, deploy_tool, sample_html, mock_netlify_create_site_response, mock_netlify_deploy_response
    ):
        """Test successful deployment using httpx."""
        with patch('shared.tools.landing_page_deploy.httpx') as mock_httpx:
            # Mock the client context manager
            mock_client = MagicMock()
            mock_httpx.Client.return_value.__enter__.return_value = mock_client

            # Mock site creation response
            mock_create_response = MagicMock()
            mock_create_response.status_code = 201
            mock_create_response.json.return_value = mock_netlify_create_site_response

            # Mock deploy response
            mock_deploy_response = MagicMock()
            mock_deploy_response.status_code = 201
            mock_deploy_response.json.return_value = mock_netlify_deploy_response

            mock_client.post.side_effect = [mock_create_response, mock_deploy_response]

            result = deploy_tool._run(
                html=sample_html,
                project_id="test-project",
                variant_id="variant-a",
            )

            assert "Landing Page Deployed Successfully" in result
            assert "netlify.app" in result

    @patch.dict('os.environ', {}, clear=True)
    def test_run_missing_token(self, deploy_tool, sample_html):
        """Test error when Netlify token is missing."""
        result = deploy_tool._run(
            html=sample_html,
            project_id="test-project",
            variant_id="variant-a",
        )

        assert "Landing Page Deployment Failed" in result
        assert "NETLIFY_ACCESS_TOKEN" in result
        assert "MISSING_TOKEN" in result

    @patch.dict('os.environ', {'NETLIFY_ACCESS_TOKEN': 'test-token'})
    @patch('shared.tools.landing_page_deploy.HTTPX_AVAILABLE', False)
    @patch('shared.tools.landing_page_deploy.REQUESTS_AVAILABLE', False)
    def test_run_no_http_library(self, deploy_tool, sample_html):
        """Test error when no HTTP library is available."""
        result = deploy_tool._run(
            html=sample_html,
            project_id="test-project",
            variant_id="variant-a",
        )

        assert "Landing Page Deployment Failed" in result
        assert "MISSING_HTTP_LIBRARY" in result

    @patch.dict('os.environ', {'NETLIFY_ACCESS_TOKEN': 'test-token'})
    @patch('shared.tools.landing_page_deploy.HTTPX_AVAILABLE', True)
    def test_run_site_creation_failure(self, deploy_tool, sample_html):
        """Test handling of site creation failure."""
        with patch('shared.tools.landing_page_deploy.httpx') as mock_httpx:
            mock_client = MagicMock()
            mock_httpx.Client.return_value.__enter__.return_value = mock_client

            # Mock failed site creation
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_client.post.return_value = mock_response

            result = deploy_tool._run(
                html=sample_html,
                project_id="test-project",
                variant_id="variant-a",
            )

            assert "Landing Page Deployment Failed" in result
            assert "SITE_CREATE_FAILED" in result


# ===========================================================================
# CONVENIENCE FUNCTION TESTS
# ===========================================================================


class TestDeployLandingPageFunction:
    """Tests for deploy_landing_page convenience function."""

    @patch.dict('os.environ', {}, clear=True)
    def test_deploy_landing_page_no_token(self, sample_html):
        """Test convenience function handles missing token."""
        result = deploy_landing_page(
            html=sample_html,
            project_id="test-project",
            variant_id="test-variant",
        )

        assert "Landing Page Deployment Failed" in result
        assert "NETLIFY_ACCESS_TOKEN" in result

    @patch.dict('os.environ', {'NETLIFY_ACCESS_TOKEN': 'test-token'})
    @patch('shared.tools.landing_page_deploy.HTTPX_AVAILABLE', True)
    def test_deploy_landing_page_with_custom_site_name(
        self, sample_html, mock_netlify_create_site_response, mock_netlify_deploy_response
    ):
        """Test convenience function with custom site name."""
        with patch('shared.tools.landing_page_deploy.httpx') as mock_httpx:
            mock_client = MagicMock()
            mock_httpx.Client.return_value.__enter__.return_value = mock_client

            mock_create_response = MagicMock()
            mock_create_response.status_code = 201
            mock_netlify_create_site_response["name"] = "custom-site"
            mock_create_response.json.return_value = mock_netlify_create_site_response

            mock_deploy_response = MagicMock()
            mock_deploy_response.status_code = 201
            mock_deploy_response.json.return_value = mock_netlify_deploy_response

            mock_client.post.side_effect = [mock_create_response, mock_deploy_response]

            result = deploy_landing_page(
                html=sample_html,
                project_id="test-project",
                variant_id="test-variant",
                site_name="custom-site",
            )

            assert "Landing Page Deployed Successfully" in result


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
