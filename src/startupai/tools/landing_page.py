"""
Landing Page Generation Tools for StartupAI.

Generates landing page code variants for A/B testing based on
Value Proposition Canvas data.

These tools enable:
- Rapid experiment deployment for desirability testing
- A/B testing of different value proposition framings
- Conversion-optimized landing page generation
"""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from crewai.tools import BaseTool
from pydantic import Field, BaseModel

from startupai.models.tool_contracts import ToolResult


# =======================================================================================
# MODELS
# =======================================================================================

class LandingPageStyle(str, Enum):
    """Landing page style variants."""
    MINIMAL = "minimal"          # Clean, focused on core message
    FEATURE_RICH = "feature_rich"  # Detailed feature breakdown
    SOCIAL_PROOF = "social_proof"  # Emphasis on testimonials/trust
    PROBLEM_FOCUSED = "problem_focused"  # Lead with pain points
    BENEFIT_FOCUSED = "benefit_focused"  # Lead with outcomes


class LandingPageVariant(BaseModel):
    """A generated landing page variant for A/B testing."""
    variant_id: str
    style: LandingPageStyle
    headline: str
    subheadline: str
    value_props: List[str]
    cta_text: str
    cta_url: str = "#signup"

    # Generated code
    html_code: Optional[str] = None
    react_code: Optional[str] = None

    # Metadata
    target_segment: Optional[str] = None
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class LandingPageOutput(BaseModel):
    """Output from landing page generation."""
    project_id: str
    variants: List[LandingPageVariant]
    base_template: str = "tailwind"
    generation_time_ms: int = 0


# =======================================================================================
# LANDING PAGE GENERATOR TOOL
# =======================================================================================

class LandingPageGeneratorTool(BaseTool):
    """
    Generate landing page code variants from Value Proposition Canvas.

    Creates conversion-optimized landing pages for A/B testing during
    desirability validation. Outputs clean HTML with Tailwind CSS.

    Use this tool to:
    - Create landing page variants for split testing
    - Generate pages optimized for different value propositions
    - Produce deployable HTML code for validation experiments
    """

    name: str = "landing_page_generator"
    description: str = """
    Generate landing page HTML variants from a Value Proposition Canvas.

    Takes the VPC data (customer jobs, pains, gains, and value map) and
    produces multiple landing page variants for A/B testing.

    Input should be a JSON object containing:
    - business_idea: Brief description of the product/service
    - target_segment: Who the page is for
    - value_proposition: Core value message
    - key_benefits: List of 3-5 main benefits
    - pain_points: Customer problems being solved (optional)
    - cta_text: Call-to-action button text (optional, defaults to "Get Started")

    Returns HTML code for multiple landing page variants.
    """

    num_variants: int = Field(default=2, description="Number of variants to generate")

    def _run(self, input_data: str) -> str:
        """
        Generate landing page variants from VPC data.

        Args:
            input_data: JSON string with VPC data or a simple business description

        Returns:
            Formatted output with generated landing page HTML variants
        """
        try:
            start_time = datetime.now()

            # Parse input
            try:
                data = json.loads(input_data)
            except json.JSONDecodeError:
                # Treat as simple business description
                data = {"business_idea": input_data}

            # Extract key information
            business_idea = data.get("business_idea", "Your Business")
            target_segment = data.get("target_segment", "customers")
            value_proposition = data.get("value_proposition", business_idea)
            key_benefits = data.get("key_benefits", [])
            pain_points = data.get("pain_points", [])
            cta_text = data.get("cta_text", "Get Started")

            # Generate variants
            variants = []

            # Variant 1: Benefit-focused
            variants.append(self._generate_benefit_variant(
                business_idea=business_idea,
                target_segment=target_segment,
                value_proposition=value_proposition,
                benefits=key_benefits,
                cta_text=cta_text,
            ))

            # Variant 2: Problem-focused
            if self.num_variants >= 2:
                variants.append(self._generate_problem_variant(
                    business_idea=business_idea,
                    target_segment=target_segment,
                    pain_points=pain_points or ["common challenges"],
                    value_proposition=value_proposition,
                    cta_text=cta_text,
                ))

            # Variant 3: Minimal
            if self.num_variants >= 3:
                variants.append(self._generate_minimal_variant(
                    business_idea=business_idea,
                    value_proposition=value_proposition,
                    cta_text=cta_text,
                ))

            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            output = LandingPageOutput(
                project_id=data.get("project_id", "unknown"),
                variants=variants,
                generation_time_ms=elapsed_ms,
            )

            return self._format_output(output)

        except Exception as e:
            return f"Landing page generation failed: {str(e)}"

    async def _arun(self, input_data: str) -> str:
        """Async version - delegates to sync."""
        return self._run(input_data)

    def _generate_benefit_variant(
        self,
        business_idea: str,
        target_segment: str,
        value_proposition: str,
        benefits: List[str],
        cta_text: str,
    ) -> LandingPageVariant:
        """Generate a benefit-focused landing page variant."""

        # Create compelling headline from value prop
        headline = value_proposition if len(value_proposition) < 60 else f"Transform Your {target_segment.title()} Experience"
        subheadline = f"Discover how {business_idea[:100]} helps you achieve better results."

        # Ensure we have benefits
        if not benefits:
            benefits = [
                "Save time and increase efficiency",
                "Get better results with less effort",
                "Join thousands of satisfied users"
            ]

        html_code = self._generate_tailwind_html(
            headline=headline,
            subheadline=subheadline,
            benefits=benefits[:5],
            cta_text=cta_text,
            style="benefit",
            accent_color="indigo",
        )

        return LandingPageVariant(
            variant_id="benefit-v1",
            style=LandingPageStyle.BENEFIT_FOCUSED,
            headline=headline,
            subheadline=subheadline,
            value_props=benefits[:5],
            cta_text=cta_text,
            html_code=html_code,
            target_segment=target_segment,
        )

    def _generate_problem_variant(
        self,
        business_idea: str,
        target_segment: str,
        pain_points: List[str],
        value_proposition: str,
        cta_text: str,
    ) -> LandingPageVariant:
        """Generate a problem-focused landing page variant."""

        # Lead with the problem
        headline = f"Tired of {pain_points[0].lower() if pain_points else 'struggling'}?"
        subheadline = f"There's a better way. {value_proposition}"

        # Convert pain points to solutions
        solutions = [f"No more {p.lower()}" for p in pain_points[:3]]
        if len(solutions) < 3:
            solutions.extend([
                "Finally, a solution that works",
                "Built for people like you"
            ])

        html_code = self._generate_tailwind_html(
            headline=headline,
            subheadline=subheadline,
            benefits=solutions[:5],
            cta_text=cta_text,
            style="problem",
            accent_color="rose",
        )

        return LandingPageVariant(
            variant_id="problem-v1",
            style=LandingPageStyle.PROBLEM_FOCUSED,
            headline=headline,
            subheadline=subheadline,
            value_props=solutions[:5],
            cta_text=cta_text,
            html_code=html_code,
            target_segment=target_segment,
        )

    def _generate_minimal_variant(
        self,
        business_idea: str,
        value_proposition: str,
        cta_text: str,
    ) -> LandingPageVariant:
        """Generate a minimal, conversion-focused variant."""

        headline = value_proposition[:80] if value_proposition else business_idea[:80]
        subheadline = "Sign up for early access."

        html_code = self._generate_tailwind_html(
            headline=headline,
            subheadline=subheadline,
            benefits=[],
            cta_text=cta_text,
            style="minimal",
            accent_color="emerald",
        )

        return LandingPageVariant(
            variant_id="minimal-v1",
            style=LandingPageStyle.MINIMAL,
            headline=headline,
            subheadline=subheadline,
            value_props=[],
            cta_text=cta_text,
            html_code=html_code,
        )

    def _generate_tailwind_html(
        self,
        headline: str,
        subheadline: str,
        benefits: List[str],
        cta_text: str,
        style: str,
        accent_color: str = "indigo",
    ) -> str:
        """Generate Tailwind CSS HTML landing page."""

        # Build benefits section if provided
        benefits_html = ""
        if benefits:
            benefit_items = "\n".join([
                f'''        <div class="flex items-start space-x-3">
          <svg class="h-6 w-6 text-{accent_color}-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span class="text-gray-700">{benefit}</span>
        </div>'''
                for benefit in benefits
            ])
            benefits_html = f'''
    <!-- Benefits Section -->
    <div class="mt-12 space-y-4">
{benefit_items}
    </div>'''

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{headline}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
  <!-- Hero Section -->
  <div class="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8">
    <div class="max-w-2xl text-center">
      <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 tracking-tight">
        {headline}
      </h1>
      <p class="mt-6 text-xl text-gray-600">
        {subheadline}
      </p>
{benefits_html}
      <!-- CTA Section -->
      <div class="mt-10">
        <form class="sm:flex sm:justify-center" action="#" method="POST">
          <input
            type="email"
            name="email"
            required
            class="w-full sm:max-w-xs px-5 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-{accent_color}-500 focus:border-{accent_color}-500"
            placeholder="Enter your email"
          />
          <button
            type="submit"
            class="mt-3 sm:mt-0 sm:ml-3 w-full sm:w-auto px-8 py-3 bg-{accent_color}-600 text-white font-semibold rounded-lg hover:bg-{accent_color}-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-{accent_color}-500 transition-colors"
          >
            {cta_text}
          </button>
        </form>
        <p class="mt-3 text-sm text-gray-500">
          No spam. Unsubscribe anytime.
        </p>
      </div>
    </div>
  </div>

  <!-- Analytics placeholder -->
  <script>
    // Add your analytics tracking here (PostHog, GA, etc.)
    document.querySelector('form').addEventListener('submit', function(e) {{
      e.preventDefault();
      const email = this.querySelector('input[name="email"]').value;
      console.log('Signup:', email);
      // Track conversion event
      if (window.posthog) {{
        posthog.capture('landing_page_signup', {{ email: email, variant: '{style}' }});
      }}
      alert('Thanks for signing up! We\\'ll be in touch soon.');
    }});
  </script>
</body>
</html>'''

        return html

    def _format_output(self, output: LandingPageOutput) -> str:
        """Format output for agent consumption."""
        lines = [
            f"## Landing Page Generation Complete",
            f"Generated {len(output.variants)} variants in {output.generation_time_ms}ms",
            "",
        ]

        for variant in output.variants:
            lines.extend([
                f"### Variant: {variant.variant_id} ({variant.style.value})",
                f"**Headline:** {variant.headline}",
                f"**Subheadline:** {variant.subheadline}",
                f"**CTA:** {variant.cta_text}",
                "",
                "```html",
                variant.html_code[:2000] + "..." if variant.html_code and len(variant.html_code) > 2000 else (variant.html_code or ""),
                "```",
                "",
            ])

        return "\n".join(lines)

    def generate_with_result(
        self,
        vpc_data: Dict[str, Any],
        num_variants: int = 2,
    ) -> ToolResult[LandingPageOutput]:
        """
        Generate landing pages and return structured ToolResult.

        Use this method when you need programmatic access to the variants.
        """
        try:
            start_time = datetime.now()
            self.num_variants = num_variants

            # Use the main _run logic
            result_str = self._run(json.dumps(vpc_data))

            # Parse back to structured output (simplified)
            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Re-generate to get the actual output object
            variants = []
            business_idea = vpc_data.get("business_idea", "")
            target_segment = vpc_data.get("target_segment", "")
            value_proposition = vpc_data.get("value_proposition", business_idea)
            key_benefits = vpc_data.get("key_benefits", [])
            pain_points = vpc_data.get("pain_points", [])
            cta_text = vpc_data.get("cta_text", "Get Started")

            variants.append(self._generate_benefit_variant(
                business_idea, target_segment, value_proposition, key_benefits, cta_text
            ))

            if num_variants >= 2:
                variants.append(self._generate_problem_variant(
                    business_idea, target_segment, pain_points, value_proposition, cta_text
                ))

            output = LandingPageOutput(
                project_id=vpc_data.get("project_id", "unknown"),
                variants=variants,
                generation_time_ms=elapsed_ms,
            )

            return ToolResult.success(output, execution_time_ms=elapsed_ms)

        except Exception as e:
            return ToolResult.failure(str(e), code="LANDING_PAGE_ERROR")


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def generate_landing_pages(
    business_idea: str,
    value_proposition: str,
    target_segment: str = "customers",
    key_benefits: List[str] = None,
    pain_points: List[str] = None,
    num_variants: int = 2,
) -> str:
    """
    Convenience function to generate landing pages.

    Args:
        business_idea: What the product/service does
        value_proposition: Core value message
        target_segment: Who it's for
        key_benefits: List of main benefits
        pain_points: Customer problems being solved
        num_variants: Number of variants to generate

    Returns:
        Formatted string with landing page HTML
    """
    tool = LandingPageGeneratorTool(num_variants=num_variants)

    input_data = {
        "business_idea": business_idea,
        "value_proposition": value_proposition,
        "target_segment": target_segment,
        "key_benefits": key_benefits or [],
        "pain_points": pain_points or [],
    }

    return tool._run(json.dumps(input_data))
