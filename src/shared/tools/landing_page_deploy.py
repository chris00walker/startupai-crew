"""
Landing Page Deployment Tool for StartupAI.

Deploys generated landing page HTML to Netlify for live A/B testing.
Returns a publicly accessible URL for the deployed page.

Environment Variables Required:
- NETLIFY_ACCESS_TOKEN: Netlify personal access token for API authentication
- NETLIFY_SITE_ID (optional): Default site ID for deployments
"""

import os
import json
import hashlib
from typing import Optional, Dict
from datetime import datetime

from crewai.tools import BaseTool
from pydantic import Field, BaseModel

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# =======================================================================================
# MODELS
# =======================================================================================

class DeploymentResult(BaseModel):
    """Result from deploying a landing page to Netlify."""
    success: bool
    deployed_url: Optional[str] = None
    deploy_id: Optional[str] = None
    site_id: Optional[str] = None
    site_name: Optional[str] = None
    variant_id: Optional[str] = None

    # Timing
    deployed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    deploy_time_ms: int = 0

    # Error info
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class LandingPageDeployInput(BaseModel):
    """Input schema for LandingPageDeploymentTool."""
    html: str = Field(..., description="The complete HTML string to deploy")
    project_id: str = Field(..., description="Unique identifier for the validation project")
    variant_id: str = Field(default="default", description="Identifier for this landing page variant (e.g., 'benefit-v1')")
    site_name: Optional[str] = Field(default=None, description="Optional custom subdomain name (auto-generated if not provided)")


# =======================================================================================
# LANDING PAGE DEPLOYMENT TOOL
# =======================================================================================

class LandingPageDeploymentTool(BaseTool):
    """
    Deploy landing page HTML to Netlify for live A/B testing.

    Creates a new Netlify site (or deploys to existing site) with the provided
    HTML content. Returns a publicly accessible URL for validation experiments.

    Use this tool to:
    - Deploy generated landing page variants for split testing
    - Get live URLs for desirability validation experiments
    - Create trackable deployment for experiment attribution

    Requires NETLIFY_ACCESS_TOKEN environment variable.
    """

    name: str = "landing_page_deploy"
    description: str = """
    Deploy landing page HTML to Netlify and return a live URL.

    Input should be a JSON object containing:
    - html: The complete HTML string to deploy
    - project_id: Unique identifier for the validation project
    - variant_id: Identifier for this landing page variant (e.g., "benefit-v1")
    - site_name: Optional custom subdomain name (auto-generated if not provided)

    Returns:
    - deployed_url: The live URL where the page is accessible
    - deploy_id: Netlify deploy ID for reference
    - site_name: The Netlify site name

    Example input:
    {
        "html": "<!DOCTYPE html><html>...</html>",
        "project_id": "proj-123",
        "variant_id": "benefit-v1"
    }
    """

    # Input schema for typed argument validation
    args_schema: type[BaseModel] = LandingPageDeployInput

    # Netlify API configuration
    netlify_api_base: str = Field(
        default="https://api.netlify.com/api/v1",
        description="Netlify API base URL"
    )

    def _run(
        self,
        html: str,
        project_id: str,
        variant_id: str = "default",
        site_name: Optional[str] = None,
    ) -> str:
        """
        Deploy landing page HTML to Netlify.

        Args:
            html: The complete HTML string to deploy
            project_id: Unique identifier for the validation project
            variant_id: Identifier for this landing page variant
            site_name: Optional custom subdomain name

        Returns:
            Formatted deployment result with URL
        """
        try:
            start_time = datetime.now()

            # Get Netlify token (accept either NETLIFY_ACCESS_TOKEN or NETLIFY_AUTH_TOKEN)
            netlify_token = os.environ.get("NETLIFY_ACCESS_TOKEN") or os.environ.get("NETLIFY_AUTH_TOKEN")
            if not netlify_token:
                return self._format_error(
                    "NETLIFY_ACCESS_TOKEN or NETLIFY_AUTH_TOKEN environment variable not set",
                    "MISSING_TOKEN"
                )

            # Generate site name if not provided
            if site_name:
                actual_site_name = site_name
            else:
                # Create deterministic but unique site name
                hash_input = f"{project_id}-{variant_id}-{datetime.now().strftime('%Y%m%d')}"
                short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
                actual_site_name = f"startupai-{project_id[:20]}-{variant_id[:10]}-{short_hash}"
                # Netlify site names must be lowercase alphanumeric with hyphens
                actual_site_name = self._sanitize_site_name(actual_site_name)

            # Deploy to Netlify
            result = self._deploy_to_netlify(
                html=html,
                site_name=actual_site_name,
                project_id=project_id,
                variant_id=variant_id,
                netlify_token=netlify_token,
            )

            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            result.deploy_time_ms = elapsed_ms

            return self._format_output(result)

        except Exception as e:
            return self._format_error(f"Deployment failed: {str(e)}", "DEPLOY_ERROR")

    async def _arun(
        self,
        html: str,
        project_id: str,
        variant_id: str = "default",
        site_name: Optional[str] = None,
    ) -> str:
        """Async version - delegates to sync."""
        return self._run(html, project_id, variant_id, site_name)

    def _sanitize_site_name(self, name: str) -> str:
        """Sanitize site name for Netlify requirements."""
        # Lowercase, replace invalid chars with hyphens
        sanitized = name.lower()
        sanitized = ''.join(c if c.isalnum() or c == '-' else '-' for c in sanitized)
        # Remove consecutive hyphens
        while '--' in sanitized:
            sanitized = sanitized.replace('--', '-')
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        # Truncate to 63 chars (DNS subdomain limit)
        return sanitized[:63]

    def _deploy_to_netlify(
        self,
        html: str,
        site_name: str,
        project_id: str,
        variant_id: str,
        netlify_token: str,
    ) -> DeploymentResult:
        """Deploy HTML to Netlify using the API."""

        headers = {
            "Authorization": f"Bearer {netlify_token}",
            "Content-Type": "application/json",
        }

        # Use httpx if available, fall back to requests
        if HTTPX_AVAILABLE:
            return self._deploy_with_httpx(
                html, site_name, project_id, variant_id, netlify_token, headers
            )
        elif REQUESTS_AVAILABLE:
            return self._deploy_with_requests(
                html, site_name, project_id, variant_id, netlify_token, headers
            )
        else:
            return DeploymentResult(
                success=False,
                error_message="Neither httpx nor requests library available",
                error_code="MISSING_HTTP_LIBRARY",
                variant_id=variant_id,
            )

    def _deploy_with_httpx(
        self,
        html: str,
        site_name: str,
        project_id: str,
        variant_id: str,
        netlify_token: str,
        headers: Dict[str, str],
    ) -> DeploymentResult:
        """Deploy using httpx library."""

        with httpx.Client(timeout=60.0) as client:
            # Step 1: Create or get existing site
            site_id = os.environ.get("NETLIFY_SITE_ID")

            if not site_id:
                # Create a new site
                create_response = client.post(
                    f"{self.netlify_api_base}/sites",
                    headers=headers,
                    json={"name": site_name}
                )

                if create_response.status_code == 201:
                    site_data = create_response.json()
                    site_id = site_data.get("id")
                    actual_site_name = site_data.get("name")
                elif create_response.status_code == 422:
                    # Site name taken, try with timestamp
                    timestamp = datetime.now().strftime('%H%M%S')
                    site_name = f"{site_name[:50]}-{timestamp}"
                    create_response = client.post(
                        f"{self.netlify_api_base}/sites",
                        headers=headers,
                        json={"name": site_name}
                    )
                    if create_response.status_code != 201:
                        return DeploymentResult(
                            success=False,
                            error_message=f"Failed to create site: {create_response.text}",
                            error_code="SITE_CREATE_FAILED",
                            variant_id=variant_id,
                        )
                    site_data = create_response.json()
                    site_id = site_data.get("id")
                    actual_site_name = site_data.get("name")
                else:
                    return DeploymentResult(
                        success=False,
                        error_message=f"Failed to create site: {create_response.text}",
                        error_code="SITE_CREATE_FAILED",
                        variant_id=variant_id,
                    )
            else:
                actual_site_name = site_name

            # Step 2: Create a deploy with the HTML content
            # Netlify expects a zip file or individual file uploads
            # We'll use the digest-based deploy API

            # Create index.html content
            file_content = html.encode('utf-8')
            file_hash = hashlib.sha1(file_content).hexdigest()

            # Create deploy with file digest
            deploy_payload = {
                "files": {
                    "/index.html": file_hash
                }
            }

            deploy_response = client.post(
                f"{self.netlify_api_base}/sites/{site_id}/deploys",
                headers=headers,
                json=deploy_payload
            )

            if deploy_response.status_code not in [200, 201]:
                return DeploymentResult(
                    success=False,
                    site_id=site_id,
                    site_name=actual_site_name,
                    error_message=f"Failed to create deploy: {deploy_response.text}",
                    error_code="DEPLOY_CREATE_FAILED",
                    variant_id=variant_id,
                )

            deploy_data = deploy_response.json()
            deploy_id = deploy_data.get("id")
            required_files = deploy_data.get("required", [])

            # Step 3: Upload the file if required
            if file_hash in required_files:
                upload_headers = {
                    "Authorization": f"Bearer {netlify_token}",
                    "Content-Type": "application/octet-stream",
                }

                upload_response = client.put(
                    f"{self.netlify_api_base}/deploys/{deploy_id}/files/index.html",
                    headers=upload_headers,
                    content=file_content
                )

                if upload_response.status_code not in [200, 201]:
                    return DeploymentResult(
                        success=False,
                        site_id=site_id,
                        site_name=actual_site_name,
                        deploy_id=deploy_id,
                        error_message=f"Failed to upload file: {upload_response.text}",
                        error_code="FILE_UPLOAD_FAILED",
                        variant_id=variant_id,
                    )

            # Get final deploy URL
            deployed_url = f"https://{actual_site_name}.netlify.app"

            return DeploymentResult(
                success=True,
                deployed_url=deployed_url,
                deploy_id=deploy_id,
                site_id=site_id,
                site_name=actual_site_name,
                variant_id=variant_id,
            )

    def _deploy_with_requests(
        self,
        html: str,
        site_name: str,
        project_id: str,
        variant_id: str,
        netlify_token: str,
        headers: Dict[str, str],
    ) -> DeploymentResult:
        """Deploy using requests library (fallback)."""

        import requests

        # Step 1: Create or get existing site
        site_id = os.environ.get("NETLIFY_SITE_ID")

        if not site_id:
            # Create a new site
            create_response = requests.post(
                f"{self.netlify_api_base}/sites",
                headers=headers,
                json={"name": site_name},
                timeout=30
            )

            if create_response.status_code == 201:
                site_data = create_response.json()
                site_id = site_data.get("id")
                actual_site_name = site_data.get("name")
            elif create_response.status_code == 422:
                # Site name taken, try with timestamp
                timestamp = datetime.now().strftime('%H%M%S')
                site_name = f"{site_name[:50]}-{timestamp}"
                create_response = requests.post(
                    f"{self.netlify_api_base}/sites",
                    headers=headers,
                    json={"name": site_name},
                    timeout=30
                )
                if create_response.status_code != 201:
                    return DeploymentResult(
                        success=False,
                        error_message=f"Failed to create site: {create_response.text}",
                        error_code="SITE_CREATE_FAILED",
                        variant_id=variant_id,
                    )
                site_data = create_response.json()
                site_id = site_data.get("id")
                actual_site_name = site_data.get("name")
            else:
                return DeploymentResult(
                    success=False,
                    error_message=f"Failed to create site: {create_response.text}",
                    error_code="SITE_CREATE_FAILED",
                    variant_id=variant_id,
                )
        else:
            actual_site_name = site_name

        # Step 2: Create a deploy with the HTML content
        file_content = html.encode('utf-8')
        file_hash = hashlib.sha1(file_content).hexdigest()

        deploy_payload = {
            "files": {
                "/index.html": file_hash
            }
        }

        deploy_response = requests.post(
            f"{self.netlify_api_base}/sites/{site_id}/deploys",
            headers=headers,
            json=deploy_payload,
            timeout=30
        )

        if deploy_response.status_code not in [200, 201]:
            return DeploymentResult(
                success=False,
                site_id=site_id,
                site_name=actual_site_name,
                error_message=f"Failed to create deploy: {deploy_response.text}",
                error_code="DEPLOY_CREATE_FAILED",
                variant_id=variant_id,
            )

        deploy_data = deploy_response.json()
        deploy_id = deploy_data.get("id")
        required_files = deploy_data.get("required", [])

        # Step 3: Upload the file if required
        if file_hash in required_files:
            upload_headers = {
                "Authorization": f"Bearer {netlify_token}",
                "Content-Type": "application/octet-stream",
            }

            upload_response = requests.put(
                f"{self.netlify_api_base}/deploys/{deploy_id}/files/index.html",
                headers=upload_headers,
                data=file_content,
                timeout=30
            )

            if upload_response.status_code not in [200, 201]:
                return DeploymentResult(
                    success=False,
                    site_id=site_id,
                    site_name=actual_site_name,
                    deploy_id=deploy_id,
                    error_message=f"Failed to upload file: {upload_response.text}",
                    error_code="FILE_UPLOAD_FAILED",
                    variant_id=variant_id,
                )

        deployed_url = f"https://{actual_site_name}.netlify.app"

        return DeploymentResult(
            success=True,
            deployed_url=deployed_url,
            deploy_id=deploy_id,
            site_id=site_id,
            site_name=actual_site_name,
            variant_id=variant_id,
        )

    def _format_output(self, result: DeploymentResult) -> str:
        """Format deployment result for agent consumption."""
        if result.success:
            return f"""## Landing Page Deployed Successfully

**Live URL:** {result.deployed_url}
**Variant ID:** {result.variant_id}
**Site Name:** {result.site_name}
**Deploy ID:** {result.deploy_id}
**Deploy Time:** {result.deploy_time_ms}ms

The landing page is now live and accessible for A/B testing.
Use this URL in your validation experiments to measure conversion rates.
"""
        else:
            return f"""## Landing Page Deployment Failed

**Error:** {result.error_message}
**Error Code:** {result.error_code}
**Variant ID:** {result.variant_id}

Please check:
1. NETLIFY_ACCESS_TOKEN environment variable is set correctly
2. Your Netlify account has permissions to create sites
3. Network connectivity to Netlify API
"""

    def _format_error(self, message: str, code: str) -> str:
        """Format error message."""
        return f"""## Landing Page Deployment Failed

**Error:** {message}
**Error Code:** {code}

Please check your input and try again.
"""


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def deploy_landing_page(
    html: str,
    project_id: str,
    variant_id: str = "default",
    site_name: Optional[str] = None,
) -> str:
    """
    Convenience function to deploy a landing page.

    Args:
        html: Complete HTML content to deploy
        project_id: Validation project identifier
        variant_id: Landing page variant identifier
        site_name: Optional custom site name

    Returns:
        Formatted string with deployment result and URL
    """
    tool = LandingPageDeploymentTool()
    return tool._run(html=html, project_id=project_id, variant_id=variant_id, site_name=site_name)
