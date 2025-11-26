"""
Integration Tests for Build Crew.

Tests the landing page pipeline:
1. LandingPageGeneratorTool - Generate landing page variants
2. CodeValidatorTool - Validate HTML code
3. LandingPageDeploymentTool - Deploy to Netlify (mocked)

These tests verify the tools work together correctly without
making actual API calls to external services.
"""

import os
import pytest
import json
from unittest.mock import Mock, patch, MagicMock

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from startupai.tools.landing_page import (
    LandingPageGeneratorTool,
    LandingPageVariant,
    LandingPageStyle,
)
from startupai.tools.code_validator import (
    CodeValidatorTool,
    ValidationSeverity,
)
from startupai.tools.landing_page_deploy import (
    LandingPageDeploymentTool,
    DeploymentResult,
)


# ===========================================================================
# LANDING PAGE GENERATOR TESTS
# ===========================================================================

class TestLandingPageGeneratorTool:
    """Tests for the landing page generation tool."""

    def test_generate_with_minimal_input(self):
        """Test generation with just a business idea string."""
        tool = LandingPageGeneratorTool()
        result = tool._run("AI-powered task manager for busy professionals")

        assert "Landing Page Generation Complete" in result
        assert "Generated 2 variants" in result
        assert "benefit-v1" in result
        assert "problem-v1" in result

    def test_generate_with_json_input(self):
        """Test generation with structured JSON input."""
        tool = LandingPageGeneratorTool()
        input_data = json.dumps({
            "business_idea": "Smart calendar that predicts your schedule",
            "target_segment": "Remote workers",
            "value_proposition": "Never miss another meeting with AI scheduling",
            "key_benefits": [
                "Automatic conflict resolution",
                "Smart meeting suggestions",
                "Time zone management"
            ],
            "cta_text": "Get Early Access"
        })

        result = tool._run(input_data)

        assert "Landing Page Generation Complete" in result
        assert "Never miss another meeting" in result or "Remote workers" in result
        assert "Get Early Access" in result

    def test_generate_produces_valid_html(self):
        """Test that generated HTML is valid."""
        tool = LandingPageGeneratorTool()
        input_data = json.dumps({
            "business_idea": "Test Business",
            "value_proposition": "Test Value",
        })

        result = tool._run(input_data)

        # Check for essential HTML elements (output may be truncated)
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "<head>" in result
        assert "<body" in result
        # HTML might be truncated with ... so we just check it starts properly

    def test_generate_multiple_variants(self):
        """Test generating 3 variants."""
        tool = LandingPageGeneratorTool(num_variants=3)
        input_data = json.dumps({
            "business_idea": "Project management for small teams",
            "value_proposition": "Simple project tracking"
        })

        result = tool._run(input_data)

        assert "benefit-v1" in result
        assert "problem-v1" in result
        assert "minimal-v1" in result


# ===========================================================================
# CODE VALIDATOR TESTS
# ===========================================================================

class TestCodeValidatorTool:
    """Tests for the code validation tool."""

    def test_validate_valid_html(self):
        """Test validation of well-formed HTML."""
        tool = CodeValidatorTool()
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
</head>
<body>
    <h1>Hello World</h1>
    <button>Click me</button>
</body>
</html>"""

        result = tool._run(html)

        # Check for deployment ready (with markdown formatting)
        assert "Deployment Ready:** Yes" in result or "Errors: 0" in result

    def test_validate_missing_doctype(self):
        """Test detection of missing DOCTYPE."""
        tool = CodeValidatorTool()
        html = """<html>
<head><title>Test</title></head>
<body><p>Content</p></body>
</html>"""

        result = tool._run(html)

        assert "DOCTYPE" in result or "doctype" in result

    def test_validate_missing_title(self):
        """Test detection of missing title."""
        tool = CodeValidatorTool()
        html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"></head>
<body><p>Content</p></body>
</html>"""

        result = tool._run(html)

        assert "title" in result.lower()

    def test_validate_missing_lang(self):
        """Test detection of missing lang attribute."""
        tool = CodeValidatorTool()
        html = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><p>Content</p></body>
</html>"""

        result = tool._run(html)

        assert "lang" in result.lower()

    def test_validate_image_without_alt(self):
        """Test detection of images without alt text."""
        tool = CodeValidatorTool()
        html = """<!DOCTYPE html>
<html lang="en">
<head><title>Test</title></head>
<body><img src="test.jpg"></body>
</html>"""

        result = tool._run(html)

        assert "alt" in result.lower()

    def test_validate_generated_landing_page(self):
        """Test validation of actual generated landing page."""
        generator = LandingPageGeneratorTool()
        validator = CodeValidatorTool()

        # Generate a landing page
        gen_result = generator._run(json.dumps({
            "business_idea": "Test product",
            "value_proposition": "Great value"
        }))

        # Extract HTML from generation result
        # The HTML is between ```html and ```
        html_start = gen_result.find("```html")
        if html_start > -1:
            html_start += 7  # Skip ```html
            html_end = gen_result.find("```", html_start)
            html = gen_result[html_start:html_end].strip()

            # Validate it
            val_result = validator._run(html)

            # Generated HTML should be deployment ready
            assert "Error" not in val_result or "Errors: 0" in val_result


# ===========================================================================
# LANDING PAGE DEPLOYMENT TESTS (MOCKED)
# ===========================================================================

class TestLandingPageDeploymentTool:
    """Tests for the landing page deployment tool (with mocked API)."""

    def test_deploy_missing_token(self):
        """Test error handling when NETLIFY_ACCESS_TOKEN is missing."""
        tool = LandingPageDeploymentTool()

        with patch.dict('os.environ', {}, clear=True):
            result = tool._run(json.dumps({
                "html": "<html></html>",
                "project_id": "test",
                "variant_id": "v1"
            }))

        assert "NETLIFY_ACCESS_TOKEN" in result
        assert "Failed" in result

    def test_deploy_missing_html(self):
        """Test error handling when HTML is missing."""
        tool = LandingPageDeploymentTool()

        result = tool._run(json.dumps({
            "project_id": "test",
            "variant_id": "v1"
        }))

        assert "Missing" in result or "Failed" in result

    def test_deploy_invalid_json(self):
        """Test error handling for invalid JSON input."""
        tool = LandingPageDeploymentTool()

        result = tool._run("not valid json")

        assert "Invalid" in result or "Failed" in result

    @patch.dict('os.environ', {'NETLIFY_ACCESS_TOKEN': 'test_token'})
    @patch('startupai.tools.landing_page_deploy.HTTPX_AVAILABLE', True)
    def test_deploy_success_with_httpx(self):
        """Test successful deployment with httpx (mocked)."""
        tool = LandingPageDeploymentTool()

        # Mock httpx client
        with patch('httpx.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client

            # Mock site creation response
            mock_site_response = MagicMock()
            mock_site_response.status_code = 201
            mock_site_response.json.return_value = {
                "id": "site_123",
                "name": "startupai-test-v1"
            }

            # Mock deploy creation response
            mock_deploy_response = MagicMock()
            mock_deploy_response.status_code = 200
            mock_deploy_response.json.return_value = {
                "id": "deploy_456",
                "required": []  # No files need uploading
            }

            mock_client.post.side_effect = [mock_site_response, mock_deploy_response]

            result = tool._run(json.dumps({
                "html": "<!DOCTYPE html><html><head><title>Test</title></head><body>Test</body></html>",
                "project_id": "test",
                "variant_id": "v1"
            }))

            assert "Successfully" in result or "Live URL" in result
            assert "netlify.app" in result

    def test_sanitize_site_name(self):
        """Test site name sanitization."""
        tool = LandingPageDeploymentTool()

        # Test various inputs
        assert tool._sanitize_site_name("My Test Site!") == "my-test-site"
        assert tool._sanitize_site_name("test--double") == "test-double"
        assert tool._sanitize_site_name("-leading-trailing-") == "leading-trailing"
        assert len(tool._sanitize_site_name("a" * 100)) <= 63


# ===========================================================================
# END-TO-END PIPELINE TESTS
# ===========================================================================

class TestLandingPagePipeline:
    """End-to-end tests for the landing page pipeline."""

    def test_generate_validate_pipeline(self):
        """Test the generate → validate pipeline."""
        generator = LandingPageGeneratorTool()
        validator = CodeValidatorTool()

        # Step 1: Generate landing pages
        gen_input = json.dumps({
            "business_idea": "AI Writing Assistant",
            "target_segment": "Content creators",
            "value_proposition": "Write 10x faster with AI",
            "key_benefits": [
                "Smart suggestions",
                "SEO optimization",
                "Grammar checking"
            ],
            "cta_text": "Start Writing Free"
        })

        gen_result = generator._run(gen_input)

        # Verify generation succeeded
        assert "Landing Page Generation Complete" in gen_result
        assert "benefit-v1" in gen_result

        # Step 2: Extract HTML and validate
        html_start = gen_result.find("```html")
        if html_start > -1:
            html_start += 7
            html_end = gen_result.find("```", html_start)
            html = gen_result[html_start:html_end].strip()

            val_result = validator._run(html)

            # Should be deployable
            assert "Error" not in val_result or "Errors: 0" in val_result

    def test_full_pipeline_with_structured_result(self):
        """Test full pipeline using structured result methods."""
        generator = LandingPageGeneratorTool()
        validator = CodeValidatorTool()

        # Generate with structured result
        gen_result = generator.generate_with_result(
            vpc_data={
                "business_idea": "Expense tracker",
                "value_proposition": "Track expenses in seconds",
                "target_segment": "Freelancers",
            },
            num_variants=2
        )

        assert gen_result.success
        assert len(gen_result.data.variants) == 2

        # Validate each variant
        for variant in gen_result.data.variants:
            if variant.html_code:
                val_result = validator.validate_with_result(variant.html_code)
                # All generated pages should be deployment ready
                assert val_result.deployment_ready


# ===========================================================================
# BUILD CREW INITIALIZATION TESTS
# ===========================================================================

class TestBuildCrewInitialization:
    """Tests for Build Crew initialization and tool wiring."""

    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY required for crew instantiation"
    )
    def test_build_crew_has_all_tools(self):
        """Test that Build Crew has all required tools wired."""
        from startupai.crews.build.build_crew import BuildCrew

        crew = BuildCrew()

        # Check tools are instantiated
        assert hasattr(crew, '_landing_page_tool')
        assert hasattr(crew, '_code_validator_tool')
        assert hasattr(crew, '_landing_page_deploy_tool')

        # Check tools are correct types
        assert isinstance(crew._landing_page_tool, LandingPageGeneratorTool)
        assert isinstance(crew._code_validator_tool, CodeValidatorTool)
        assert isinstance(crew._landing_page_deploy_tool, LandingPageDeploymentTool)

    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY required for crew instantiation"
    )
    def test_prototype_designer_has_tools(self):
        """Test that prototype_designer agent has all tools."""
        from startupai.crews.build.build_crew import BuildCrew

        crew = BuildCrew()
        agent = crew.prototype_designer()

        # Agent should have all 3 tools
        assert len(agent.tools) == 3

        tool_names = [t.name for t in agent.tools]
        assert "landing_page_generator" in tool_names
        assert "code_validator" in tool_names
        assert "landing_page_deploy" in tool_names
