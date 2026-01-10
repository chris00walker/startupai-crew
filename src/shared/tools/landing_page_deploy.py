"""
Landing Page Deployment Tool for StartupAI.

Deploys generated landing page HTML to Supabase Storage for live A/B testing.
Returns a publicly accessible URL for the deployed page.

Architecture: ADR-003 - Supabase Storage for Landing Pages
- Storage: HTML files in public 'landing-pages' bucket
- Analytics: Pageviews tracked via client-side JS
- Forms: Submissions captured via client-side JS to Supabase

Environment Variables Required:
- SUPABASE_URL: Supabase project URL
- SUPABASE_KEY: Supabase service role key
- SUPABASE_ANON_KEY: Supabase anon key (for client-side tracking)
"""

import os
import hashlib
import logging
from typing import Optional
from datetime import datetime

from crewai.tools import BaseTool
from pydantic import Field, BaseModel

# Configure logging
logger = logging.getLogger(__name__)


# =======================================================================================
# MODELS
# =======================================================================================

class DeploymentResult(BaseModel):
    """Result from deploying a landing page to Supabase Storage."""
    success: bool
    deployed_url: Optional[str] = None
    deploy_id: Optional[str] = None  # Maps to storage path
    site_id: Optional[str] = None    # Maps to variant record ID
    site_name: Optional[str] = None  # Storage bucket/path
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
    site_name: Optional[str] = Field(default=None, description="Ignored - preserved for backward compatibility")


# =======================================================================================
# TRACKING JAVASCRIPT TEMPLATE
# =======================================================================================

TRACKING_JS_TEMPLATE = """
<script>
(function() {{
  var SUPABASE_URL = '{supabase_url}';
  var SUPABASE_ANON_KEY = '{supabase_anon_key}';
  var VARIANT_ID = '{variant_id}';

  // Generate or retrieve session ID
  function getSessionId() {{
    var sid = sessionStorage.getItem('lp_sid');
    if (!sid) {{
      sid = 'sess_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
      sessionStorage.setItem('lp_sid', sid);
    }}
    return sid;
  }}

  // Track pageview on load
  function trackPageview() {{
    fetch(SUPABASE_URL + '/rest/v1/lp_pageviews', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': 'Bearer ' + SUPABASE_ANON_KEY,
        'Prefer': 'return=minimal'
      }},
      body: JSON.stringify({{
        variant_id: VARIANT_ID,
        session_id: getSessionId(),
        user_agent: navigator.userAgent,
        referrer: document.referrer || null
      }})
    }}).catch(function(e) {{ console.log('LP tracking error:', e); }});
  }}

  // Handle form submissions
  function setupFormTracking() {{
    document.addEventListener('submit', function(e) {{
      var form = e.target;
      // Skip forms explicitly marked to not track
      if (form.dataset.lpTrack === 'false') return;

      e.preventDefault();
      var formData = {{}};
      new FormData(form).forEach(function(value, key) {{
        formData[key] = value;
      }});

      fetch(SUPABASE_URL + '/rest/v1/lp_submissions', {{
        method: 'POST',
        headers: {{
          'Content-Type': 'application/json',
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': 'Bearer ' + SUPABASE_ANON_KEY,
          'Prefer': 'return=minimal'
        }},
        body: JSON.stringify({{
          variant_id: VARIANT_ID,
          email: formData.email || null,
          form_data: formData,
          user_agent: navigator.userAgent
        }})
      }}).then(function() {{
        // Show success message
        form.innerHTML = '<div style="padding: 20px; text-align: center; color: #16a34a; font-weight: 600;">Thank you! We\\'ll be in touch soon.</div>';
      }}).catch(function(e) {{
        console.log('LP submission error:', e);
        form.innerHTML = '<div style="padding: 20px; text-align: center; color: #dc2626;">Something went wrong. Please try again.</div>';
      }});
    }});
  }}

  // Initialize
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', function() {{
      trackPageview();
      setupFormTracking();
    }});
  }} else {{
    trackPageview();
    setupFormTracking();
  }}
}})();
</script>
"""


# =======================================================================================
# LANDING PAGE DEPLOYMENT TOOL
# =======================================================================================

class LandingPageDeploymentTool(BaseTool):
    """
    Deploy landing page HTML to Supabase Storage for live A/B testing.

    Creates a publicly accessible URL for validation experiments.
    Automatically injects analytics tracking for pageviews and form submissions.

    Use this tool to:
    - Deploy generated landing page variants for split testing
    - Get live URLs for desirability validation experiments
    - Create trackable deployment for experiment attribution
    """

    name: str = "landing_page_deploy"
    description: str = """
    Deploy landing page HTML to Supabase Storage and return a live URL.

    Input should be a JSON object containing:
    - html: The complete HTML string to deploy
    - project_id: Unique identifier for the validation project
    - variant_id: Identifier for this landing page variant (e.g., "benefit-v1")
    - site_name: Optional (ignored, for backward compatibility)

    Returns:
    - deployed_url: The live URL where the page is accessible
    - deploy_id: Storage path for reference
    - site_name: Full storage path

    Example input:
    {
        "html": "<!DOCTYPE html><html>...</html>",
        "project_id": "proj-123",
        "variant_id": "benefit-v1"
    }
    """

    # Input schema for typed argument validation
    args_schema: type[BaseModel] = LandingPageDeployInput

    def _run(
        self,
        html: str,
        project_id: str,
        variant_id: str = "default",
        site_name: Optional[str] = None,  # Ignored, for backward compatibility
    ) -> str:
        """
        Deploy landing page HTML to Supabase Storage.

        Args:
            html: The complete HTML string to deploy
            project_id: Unique identifier for the validation project
            variant_id: Identifier for this landing page variant
            site_name: Ignored (preserved for backward compatibility)

        Returns:
            Formatted deployment result with URL
        """
        try:
            start_time = datetime.now()

            # Get Supabase client
            from state.persistence import get_supabase
            supabase = get_supabase()

            # Sanitize project_id and variant_id for storage path
            safe_project = self._sanitize_path_segment(project_id)
            safe_variant = self._sanitize_path_segment(variant_id)
            storage_path = f"{safe_project}/{safe_variant}.html"

            # Get environment variables for tracking
            supabase_url = os.environ.get("SUPABASE_URL", "")
            supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY", "")

            if not supabase_anon_key:
                logger.warning("SUPABASE_ANON_KEY not set - tracking will not work")

            # Inject tracking JavaScript
            html_with_tracking = self._inject_tracking(html, variant_id, supabase_url, supabase_anon_key)

            # Compute hash for change detection
            html_bytes = html_with_tracking.encode('utf-8')
            html_hash = hashlib.sha256(html_bytes).hexdigest()[:16]

            # Upload to Supabase Storage
            try:
                # Try to upload (upsert)
                upload_result = supabase.storage.from_("landing-pages").upload(
                    path=storage_path,
                    file=html_bytes,
                    file_options={"content-type": "text/html", "upsert": "true"}
                )
            except Exception as upload_error:
                # Handle case where bucket doesn't exist or other upload errors
                error_msg = str(upload_error)
                if "bucket" in error_msg.lower() or "not found" in error_msg.lower():
                    return self._format_error(
                        "Storage bucket 'landing-pages' not found. Please create it in Supabase Dashboard.",
                        "BUCKET_NOT_FOUND"
                    )
                raise

            # Get public URL
            public_url = supabase.storage.from_("landing-pages").get_public_url(storage_path)

            # Record metadata in landing_page_variants table
            try:
                supabase.table("landing_page_variants").upsert({
                    "run_id": project_id,
                    "variant_name": variant_id,
                    "storage_path": storage_path,
                    "public_url": public_url,
                    "html_hash": html_hash,
                    "metadata": {
                        "deployed_at": datetime.now().isoformat(),
                        "html_size": len(html_bytes),
                    }
                }, on_conflict="storage_path").execute()
            except Exception as db_error:
                logger.warning(f"Failed to record variant metadata: {db_error}")
                # Continue - the file was uploaded successfully

            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            result = DeploymentResult(
                success=True,
                deployed_url=public_url,
                deploy_id=storage_path,
                site_id=storage_path,
                site_name=f"landing-pages/{storage_path}",
                variant_id=variant_id,
                deploy_time_ms=elapsed_ms,
            )

            logger.info(f"Landing page deployed: {public_url}")
            return self._format_output(result)

        except Exception as e:
            logger.error(f"Landing page deployment failed: {str(e)}")
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

    def _sanitize_path_segment(self, segment: str) -> str:
        """Sanitize a string for use in storage path."""
        # Replace unsafe characters with hyphens
        safe = ''.join(c if c.isalnum() or c == '-' else '-' for c in segment.lower())
        # Remove consecutive hyphens
        while '--' in safe:
            safe = safe.replace('--', '-')
        # Remove leading/trailing hyphens
        safe = safe.strip('-')
        # Truncate to reasonable length
        return safe[:50] or 'default'

    def _inject_tracking(
        self,
        html: str,
        variant_id: str,
        supabase_url: str,
        supabase_anon_key: str,
    ) -> str:
        """Inject tracking JavaScript before </body>."""
        # Skip if no anon key (tracking won't work anyway)
        if not supabase_anon_key:
            return html

        tracking_js = TRACKING_JS_TEMPLATE.format(
            supabase_url=supabase_url,
            supabase_anon_key=supabase_anon_key,
            variant_id=variant_id,
        )

        # Find </body> tag (case-insensitive)
        lower_html = html.lower()
        body_end_idx = lower_html.rfind("</body>")

        if body_end_idx != -1:
            # Insert before </body>
            return html[:body_end_idx] + tracking_js + html[body_end_idx:]
        else:
            # No </body> found, append at end
            return html + tracking_js

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
1. SUPABASE_URL and SUPABASE_KEY environment variables are set correctly
2. The 'landing-pages' storage bucket exists and is public
3. Network connectivity to Supabase
"""

    def _format_error(self, message: str, code: str) -> str:
        """Format error message."""
        return f"""## Landing Page Deployment Failed

**Error:** {message}
**Error Code:** {code}

Please check:
1. SUPABASE_URL and SUPABASE_KEY environment variables are set correctly
2. The 'landing-pages' storage bucket exists and is public
3. Network connectivity to Supabase
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
        site_name: Ignored (for backward compatibility)

    Returns:
        Formatted string with deployment result and URL
    """
    tool = LandingPageDeploymentTool()
    return tool._run(html=html, project_id=project_id, variant_id=variant_id, site_name=site_name)
