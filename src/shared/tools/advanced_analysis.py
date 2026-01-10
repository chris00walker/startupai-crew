"""
Advanced Analysis Tools for StartupAI Validation Engine (Phase B).

Provides:
- TranscriptionTool: Audio-to-text transcription using OpenAI Whisper API
- InsightExtractorTool: Extract themes and insights from interview/research text
- BehaviorPatternTool: Identify behavioral patterns from evidence data
- ABTestTool: Statistical analysis of A/B test results

Target agents: D1, D2, D3, D4, P1, P2, W1
"""

import os
import json
import math
from typing import List, Optional, Dict, Any
from datetime import datetime

from crewai.tools import BaseTool
from pydantic import Field, BaseModel


# =======================================================================================
# OUTPUT MODELS
# =======================================================================================


class TranscriptionOutput(BaseModel):
    """Structured output from audio transcription."""

    source_type: str  # "audio_file", "audio_url", "text_input"
    transcript: str
    duration_seconds: Optional[float] = None
    language: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class InsightOutput(BaseModel):
    """Individual insight extracted from text."""

    category: str  # "pain_point", "desire", "behavior", "opportunity", "quote"
    content: str
    confidence: float = 0.8
    evidence_quote: Optional[str] = None


class InsightExtractionOutput(BaseModel):
    """Structured output from insight extraction."""

    source_text_preview: str
    insights: List[InsightOutput]
    key_themes: List[str]
    pain_points: List[str]
    opportunities: List[str]
    notable_quotes: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)


class PatternOutput(BaseModel):
    """Individual behavioral pattern identified."""

    pattern_name: str
    description: str
    frequency: str  # "common", "occasional", "rare"
    evidence_sources: List[str]
    implications: List[str]


class BehaviorPatternOutput(BaseModel):
    """Structured output from pattern identification."""

    topic: str
    patterns: List[PatternOutput]
    say_vs_do_discrepancies: List[str]
    behavioral_signals: List[str]
    recommendations: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)


class ABTestResult(BaseModel):
    """Structured output from A/B test analysis."""

    test_name: str
    variant_a_name: str
    variant_b_name: str
    variant_a_conversions: int
    variant_a_total: int
    variant_b_conversions: int
    variant_b_total: int
    variant_a_rate: float
    variant_b_rate: float
    relative_lift: float  # Percentage improvement of B over A
    p_value: float
    is_significant: bool
    confidence_level: float
    winner: Optional[str]  # "A", "B", or None if inconclusive
    recommendation: str
    timestamp: datetime = Field(default_factory=datetime.now)


# =======================================================================================
# TRANSCRIPTION TOOL
# =======================================================================================


class TranscriptionTool(BaseTool):
    """
    Transcribe audio recordings from customer interviews to text.

    Uses OpenAI's Whisper API for accurate transcription.
    Can also process pre-transcribed text for analysis.

    Target agent: D1 (Customer Interview Agent)
    """

    name: str = "transcribe_audio"
    description: str = """
    Transcribe audio recordings from customer interviews to text.

    Use this tool to:
    - Convert interview recordings to searchable text
    - Process audio from customer discovery calls
    - Prepare interview content for insight extraction

    Input can be:
    - A file path to an audio file (.mp3, .wav, .m4a, .webm)
    - A URL to an audio file
    - Pre-transcribed text (will be returned formatted)

    Returns structured transcript ready for analysis.
    """

    model: str = Field(default="whisper-1", description="OpenAI Whisper model to use")

    def _get_openai_client(self):
        """Get OpenAI client for Whisper API."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        try:
            from openai import OpenAI

            return OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def _run(self, input_source: str) -> str:
        """
        Transcribe audio or process pre-transcribed text.

        Args:
            input_source: File path, URL, or pre-transcribed text

        Returns:
            Formatted transcript
        """
        try:
            # Check if input is likely pre-transcribed text (multi-line or long)
            if "\n" in input_source or len(input_source) > 500:
                return self._format_text_input(input_source)

            # Check if input is a file path
            if os.path.isfile(input_source):
                return self._transcribe_file(input_source)

            # Check if input looks like a URL
            if input_source.startswith(("http://", "https://")):
                return self._transcribe_url(input_source)

            # Treat as text input
            return self._format_text_input(input_source)

        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except ImportError as e:
            return f"Dependency error: {str(e)}"
        except Exception as e:
            return f"Transcription failed: {str(e)}"

    def _transcribe_file(self, file_path: str) -> str:
        """Transcribe an audio file using Whisper API."""
        client = self._get_openai_client()

        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                response_format="verbose_json",
            )

        output = TranscriptionOutput(
            source_type="audio_file",
            transcript=response.text,
            duration_seconds=getattr(response, "duration", None),
            language=getattr(response, "language", None),
        )

        return self._format_output(output)

    def _transcribe_url(self, url: str) -> str:
        """Transcribe audio from URL (downloads first)."""
        import tempfile
        import urllib.request

        # Download to temp file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            urllib.request.urlretrieve(url, tmp.name)
            result = self._transcribe_file(tmp.name)
            os.unlink(tmp.name)
            return result

    def _format_text_input(self, text: str) -> str:
        """Format pre-transcribed text for analysis."""
        output = TranscriptionOutput(
            source_type="text_input",
            transcript=text,
        )
        return self._format_output(output)

    def _format_output(self, output: TranscriptionOutput) -> str:
        """Format transcription output for agent consumption."""
        lines = [
            "# Interview Transcript",
            "",
            f"**Source Type:** {output.source_type}",
        ]

        if output.duration_seconds:
            minutes = int(output.duration_seconds // 60)
            seconds = int(output.duration_seconds % 60)
            lines.append(f"**Duration:** {minutes}:{seconds:02d}")

        if output.language:
            lines.append(f"**Language:** {output.language}")

        lines.extend(
            [
                "",
                "## Full Transcript",
                "",
                output.transcript,
                "",
                "---",
                f"*Transcribed at {output.timestamp.isoformat()}*",
            ]
        )

        return "\n".join(lines)

    async def _arun(self, input_source: str) -> str:
        """Async version - delegates to sync."""
        return self._run(input_source)


# =======================================================================================
# INSIGHT EXTRACTOR TOOL
# =======================================================================================


class InsightExtractorTool(BaseTool):
    """
    Extract structured insights from interview transcripts and research text.

    Uses LLM to identify pain points, desires, behavioral patterns,
    and opportunities from qualitative research data.

    Target agents: D1 (Customer Interview), D4 (Evidence Triangulation)
    """

    name: str = "extract_insights"
    description: str = """
    Extract structured insights from interview transcripts or research text.

    Use this tool to:
    - Identify pain points and frustrations from customer interviews
    - Extract desires, goals, and Jobs-to-be-Done
    - Find notable quotes that illustrate key insights
    - Discover opportunities for product/service improvements

    Input should be text content (transcript, notes, or research findings).

    Returns structured insights organized by category.
    """

    model: str = Field(
        default="gpt-4o-mini", description="OpenAI model for insight extraction"
    )

    def _get_openai_client(self):
        """Get OpenAI client."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        try:
            from openai import OpenAI

            return OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def _run(self, text: str) -> str:
        """
        Extract insights from text using LLM.

        Args:
            text: Interview transcript or research text

        Returns:
            Formatted insights
        """
        try:
            client = self._get_openai_client()

            prompt = f"""Analyze the following text and extract structured insights.

TEXT TO ANALYZE:
{text[:8000]}  # Limit to avoid token limits

Please extract:
1. KEY THEMES (3-5 main themes that emerge)
2. PAIN POINTS (specific frustrations or challenges mentioned)
3. OPPORTUNITIES (potential improvements or solutions suggested)
4. NOTABLE QUOTES (verbatim quotes that illustrate key insights)
5. BEHAVIORAL INSIGHTS (what actions or behaviors are described)

Format your response as JSON:
{{
    "key_themes": ["theme1", "theme2", ...],
    "pain_points": ["pain1", "pain2", ...],
    "opportunities": ["opportunity1", "opportunity2", ...],
    "notable_quotes": ["quote1", "quote2", ...],
    "behavioral_insights": ["behavior1", "behavior2", ...]
}}"""

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert qualitative researcher skilled at extracting insights from customer interviews. Respond only with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)

            output = InsightExtractionOutput(
                source_text_preview=text[:200] + "..." if len(text) > 200 else text,
                insights=[],
                key_themes=result.get("key_themes", []),
                pain_points=result.get("pain_points", []),
                opportunities=result.get("opportunities", []),
                notable_quotes=result.get("notable_quotes", []),
            )

            return self._format_output(output)

        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except ImportError as e:
            return f"Dependency error: {str(e)}"
        except json.JSONDecodeError as e:
            return f"Failed to parse LLM response: {str(e)}"
        except Exception as e:
            return f"Insight extraction failed: {str(e)}"

    def _format_output(self, output: InsightExtractionOutput) -> str:
        """Format insights for agent consumption."""
        lines = [
            "# Extracted Insights",
            "",
            f"**Source Preview:** {output.source_text_preview}",
            "",
        ]

        if output.key_themes:
            lines.append("## Key Themes")
            for theme in output.key_themes:
                lines.append(f"- {theme}")
            lines.append("")

        if output.pain_points:
            lines.append("## Pain Points Identified")
            for pain in output.pain_points:
                lines.append(f"- {pain}")
            lines.append("")

        if output.opportunities:
            lines.append("## Opportunities")
            for opp in output.opportunities:
                lines.append(f"- {opp}")
            lines.append("")

        if output.notable_quotes:
            lines.append("## Notable Quotes")
            for quote in output.notable_quotes:
                lines.append(f'> "{quote}"')
            lines.append("")

        lines.append(f"*Extracted at {output.timestamp.isoformat()}*")

        return "\n".join(lines)

    async def _arun(self, text: str) -> str:
        """Async version - delegates to sync."""
        return self._run(text)


# =======================================================================================
# BEHAVIOR PATTERN TOOL
# =======================================================================================


class BehaviorPatternTool(BaseTool):
    """
    Identify behavioral patterns from evidence data.

    Analyzes SAY vs DO discrepancies and identifies recurring patterns
    in customer behavior from research evidence.

    Target agents: D2 (Observation Agent), D3 (CTA Test Agent)
    """

    name: str = "identify_patterns"
    description: str = """
    Identify behavioral patterns from evidence and research data.

    Use this tool to:
    - Find recurring behavioral patterns in customer data
    - Identify SAY vs DO discrepancies (what customers say vs what they do)
    - Detect behavioral signals that indicate intent or preference
    - Synthesize patterns across multiple evidence sources

    Input should be evidence text, research findings, or behavioral data.

    Returns identified patterns with implications.
    """

    model: str = Field(
        default="gpt-4o-mini", description="OpenAI model for pattern identification"
    )

    def _get_openai_client(self):
        """Get OpenAI client."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        try:
            from openai import OpenAI

            return OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def _run(self, evidence_text: str, topic: Optional[str] = None) -> str:
        """
        Identify patterns from evidence.

        Args:
            evidence_text: Evidence data to analyze
            topic: Optional topic context

        Returns:
            Formatted pattern analysis
        """
        try:
            client = self._get_openai_client()

            # Handle case where topic is passed as part of evidence_text
            if topic is None and "|" in evidence_text:
                parts = evidence_text.split("|", 1)
                topic = parts[0].strip()
                evidence_text = parts[1].strip()

            topic = topic or "customer behavior"

            prompt = f"""Analyze the following evidence about "{topic}" and identify behavioral patterns.

EVIDENCE TO ANALYZE:
{evidence_text[:8000]}

Please identify:
1. BEHAVIORAL PATTERNS (recurring behaviors with frequency: common/occasional/rare)
2. SAY vs DO DISCREPANCIES (differences between stated preferences and actual behavior)
3. BEHAVIORAL SIGNALS (indicators of intent, preference, or commitment)
4. RECOMMENDATIONS (how to leverage these patterns)

Format your response as JSON:
{{
    "patterns": [
        {{
            "pattern_name": "Pattern Name",
            "description": "Description of the pattern",
            "frequency": "common|occasional|rare",
            "evidence": ["evidence1", "evidence2"],
            "implications": ["implication1", "implication2"]
        }}
    ],
    "say_vs_do_discrepancies": ["discrepancy1", "discrepancy2"],
    "behavioral_signals": ["signal1", "signal2"],
    "recommendations": ["recommendation1", "recommendation2"]
}}"""

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert behavioral analyst skilled at identifying patterns in customer research. Respond only with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)

            patterns = []
            for p in result.get("patterns", []):
                patterns.append(
                    PatternOutput(
                        pattern_name=p.get("pattern_name", "Unknown"),
                        description=p.get("description", ""),
                        frequency=p.get("frequency", "occasional"),
                        evidence_sources=p.get("evidence", []),
                        implications=p.get("implications", []),
                    )
                )

            output = BehaviorPatternOutput(
                topic=topic,
                patterns=patterns,
                say_vs_do_discrepancies=result.get("say_vs_do_discrepancies", []),
                behavioral_signals=result.get("behavioral_signals", []),
                recommendations=result.get("recommendations", []),
            )

            return self._format_output(output)

        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except ImportError as e:
            return f"Dependency error: {str(e)}"
        except json.JSONDecodeError as e:
            return f"Failed to parse LLM response: {str(e)}"
        except Exception as e:
            return f"Pattern identification failed: {str(e)}"

    def _format_output(self, output: BehaviorPatternOutput) -> str:
        """Format patterns for agent consumption."""
        lines = [
            f"# Behavioral Pattern Analysis: {output.topic}",
            "",
        ]

        if output.patterns:
            lines.append("## Identified Patterns")
            for pattern in output.patterns:
                lines.extend(
                    [
                        f"### {pattern.pattern_name}",
                        f"**Frequency:** {pattern.frequency}",
                        f"**Description:** {pattern.description}",
                        "",
                    ]
                )
                if pattern.evidence_sources:
                    lines.append("**Evidence:**")
                    for ev in pattern.evidence_sources:
                        lines.append(f"- {ev}")
                if pattern.implications:
                    lines.append("**Implications:**")
                    for imp in pattern.implications:
                        lines.append(f"- {imp}")
                lines.append("")

        if output.say_vs_do_discrepancies:
            lines.append("## SAY vs DO Discrepancies")
            for disc in output.say_vs_do_discrepancies:
                lines.append(f"- {disc}")
            lines.append("")

        if output.behavioral_signals:
            lines.append("## Behavioral Signals")
            for sig in output.behavioral_signals:
                lines.append(f"- {sig}")
            lines.append("")

        if output.recommendations:
            lines.append("## Recommendations")
            for rec in output.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        lines.append(f"*Analysis completed at {output.timestamp.isoformat()}*")

        return "\n".join(lines)

    async def _arun(self, evidence_text: str, topic: Optional[str] = None) -> str:
        """Async version - delegates to sync."""
        return self._run(evidence_text, topic)


# =======================================================================================
# A/B TEST TOOL
# =======================================================================================


class ABTestTool(BaseTool):
    """
    Analyze A/B test results with statistical significance testing.

    Uses scipy for proper statistical analysis of conversion data.

    Target agents: P1 (Ad Creative), P2 (Communications), W1 (Pricing Experiment)
    """

    name: str = "run_ab_test"
    description: str = """
    Analyze A/B test results and determine statistical significance.

    Use this tool to:
    - Calculate conversion rates for each variant
    - Determine if results are statistically significant
    - Compute relative lift and confidence intervals
    - Get clear winner/loser recommendations

    Input should be a JSON string with test data:
    {
        "test_name": "Button Color Test",
        "variant_a": {"name": "Blue", "conversions": 45, "total": 500},
        "variant_b": {"name": "Green", "conversions": 62, "total": 500}
    }

    Returns statistical analysis with significance testing.
    """

    confidence_level: float = Field(
        default=0.95, description="Confidence level for significance testing (0.95 = 95%)"
    )

    def _run(self, test_data: str) -> str:
        """
        Analyze A/B test results.

        Args:
            test_data: JSON string with test data

        Returns:
            Formatted statistical analysis
        """
        try:
            # Parse input
            if isinstance(test_data, str):
                data = json.loads(test_data)
            else:
                data = test_data

            test_name = data.get("test_name", "A/B Test")
            variant_a = data.get("variant_a", {})
            variant_b = data.get("variant_b", {})

            a_name = variant_a.get("name", "Control")
            b_name = variant_b.get("name", "Treatment")
            a_conv = variant_a.get("conversions", 0)
            a_total = variant_a.get("total", 1)
            b_conv = variant_b.get("conversions", 0)
            b_total = variant_b.get("total", 1)

            # Calculate conversion rates
            a_rate = a_conv / a_total if a_total > 0 else 0
            b_rate = b_conv / b_total if b_total > 0 else 0

            # Calculate relative lift
            relative_lift = ((b_rate - a_rate) / a_rate * 100) if a_rate > 0 else 0

            # Calculate p-value using two-proportion z-test
            p_value = self._calculate_p_value(a_conv, a_total, b_conv, b_total)

            # Determine significance
            alpha = 1 - self.confidence_level
            is_significant = p_value < alpha

            # Determine winner
            winner = None
            if is_significant:
                winner = "B" if b_rate > a_rate else "A"

            # Generate recommendation
            recommendation = self._generate_recommendation(
                a_name, b_name, a_rate, b_rate, is_significant, winner
            )

            output = ABTestResult(
                test_name=test_name,
                variant_a_name=a_name,
                variant_b_name=b_name,
                variant_a_conversions=a_conv,
                variant_a_total=a_total,
                variant_b_conversions=b_conv,
                variant_b_total=b_total,
                variant_a_rate=a_rate,
                variant_b_rate=b_rate,
                relative_lift=relative_lift,
                p_value=p_value,
                is_significant=is_significant,
                confidence_level=self.confidence_level,
                winner=winner,
                recommendation=recommendation,
            )

            return self._format_output(output)

        except json.JSONDecodeError as e:
            return f"Invalid JSON input: {str(e)}"
        except Exception as e:
            return f"A/B test analysis failed: {str(e)}"

    def _calculate_p_value(
        self, a_conv: int, a_total: int, b_conv: int, b_total: int
    ) -> float:
        """Calculate p-value using two-proportion z-test."""
        try:
            from scipy import stats

            # Use scipy's Fisher exact test for small samples
            if a_total < 30 or b_total < 30:
                table = [[a_conv, a_total - a_conv], [b_conv, b_total - b_conv]]
                _, p_value = stats.fisher_exact(table)
                return p_value

            # Two-proportion z-test for larger samples
            p1 = a_conv / a_total
            p2 = b_conv / b_total
            p_pooled = (a_conv + b_conv) / (a_total + b_total)

            se = math.sqrt(p_pooled * (1 - p_pooled) * (1 / a_total + 1 / b_total))
            if se == 0:
                return 1.0

            z = (p2 - p1) / se
            p_value = 2 * (1 - stats.norm.cdf(abs(z)))  # Two-tailed test

            return p_value

        except ImportError:
            # Fallback without scipy - approximate using normal distribution
            return self._approximate_p_value(a_conv, a_total, b_conv, b_total)

    def _approximate_p_value(
        self, a_conv: int, a_total: int, b_conv: int, b_total: int
    ) -> float:
        """Approximate p-value without scipy (fallback)."""
        p1 = a_conv / a_total if a_total > 0 else 0
        p2 = b_conv / b_total if b_total > 0 else 0
        p_pooled = (a_conv + b_conv) / (a_total + b_total) if (a_total + b_total) > 0 else 0

        se = math.sqrt(p_pooled * (1 - p_pooled) * (1 / a_total + 1 / b_total)) if a_total > 0 and b_total > 0 else 1

        if se == 0:
            return 1.0

        z = abs((p2 - p1) / se)

        # Approximate using standard normal table for common z values
        if z >= 2.576:
            return 0.01
        elif z >= 1.96:
            return 0.05
        elif z >= 1.645:
            return 0.10
        else:
            return 0.20

    def _generate_recommendation(
        self,
        a_name: str,
        b_name: str,
        a_rate: float,
        b_rate: float,
        is_significant: bool,
        winner: Optional[str],
    ) -> str:
        """Generate a clear recommendation based on results."""
        if not is_significant:
            return f"Results are not statistically significant. Continue testing or increase sample size. Current difference between {a_name} ({a_rate:.1%}) and {b_name} ({b_rate:.1%}) could be due to chance."

        if winner == "B":
            return f"{b_name} is the winner with {b_rate:.1%} conversion rate vs {a_name}'s {a_rate:.1%}. Implement {b_name} as the new default."
        else:
            return f"{a_name} (control) outperforms {b_name}. Keep {a_name} with {a_rate:.1%} conversion rate. {b_name}'s {b_rate:.1%} is significantly worse."

    def _format_output(self, output: ABTestResult) -> str:
        """Format A/B test results for agent consumption."""
        lines = [
            f"# A/B Test Results: {output.test_name}",
            "",
            "## Conversion Rates",
            f"| Variant | Conversions | Total | Rate |",
            f"|---------|-------------|-------|------|",
            f"| **{output.variant_a_name}** (A) | {output.variant_a_conversions} | {output.variant_a_total} | {output.variant_a_rate:.2%} |",
            f"| **{output.variant_b_name}** (B) | {output.variant_b_conversions} | {output.variant_b_total} | {output.variant_b_rate:.2%} |",
            "",
            "## Statistical Analysis",
            f"- **Relative Lift:** {output.relative_lift:+.1f}% (B vs A)",
            f"- **P-Value:** {output.p_value:.4f}",
            f"- **Confidence Level:** {output.confidence_level:.0%}",
            f"- **Statistically Significant:** {'Yes' if output.is_significant else 'No'}",
            "",
        ]

        if output.winner:
            lines.extend(
                [
                    f"## Winner: Variant {output.winner} ({output.variant_b_name if output.winner == 'B' else output.variant_a_name})",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## Result: Inconclusive",
                    "",
                ]
            )

        lines.extend(
            [
                "## Recommendation",
                output.recommendation,
                "",
                f"*Analysis completed at {output.timestamp.isoformat()}*",
            ]
        )

        return "\n".join(lines)

    async def _arun(self, test_data: str) -> str:
        """Async version - delegates to sync."""
        return self._run(test_data)


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================


def transcribe_audio(input_source: str) -> str:
    """
    Convenience function for audio transcription.

    Args:
        input_source: File path, URL, or pre-transcribed text

    Returns:
        Formatted transcript
    """
    tool = TranscriptionTool()
    return tool._run(input_source)


def extract_insights(text: str) -> str:
    """
    Convenience function for insight extraction.

    Args:
        text: Text to analyze

    Returns:
        Formatted insights
    """
    tool = InsightExtractorTool()
    return tool._run(text)


def identify_patterns(evidence_text: str, topic: Optional[str] = None) -> str:
    """
    Convenience function for pattern identification.

    Args:
        evidence_text: Evidence to analyze
        topic: Optional topic context

    Returns:
        Formatted patterns
    """
    tool = BehaviorPatternTool()
    return tool._run(evidence_text, topic)


def run_ab_test(
    test_name: str,
    variant_a_name: str,
    variant_a_conversions: int,
    variant_a_total: int,
    variant_b_name: str,
    variant_b_conversions: int,
    variant_b_total: int,
) -> str:
    """
    Convenience function for A/B test analysis.

    Args:
        test_name: Name of the test
        variant_a_name: Name of control variant
        variant_a_conversions: Conversions for A
        variant_a_total: Total visitors for A
        variant_b_name: Name of treatment variant
        variant_b_conversions: Conversions for B
        variant_b_total: Total visitors for B

    Returns:
        Formatted A/B test results
    """
    test_data = {
        "test_name": test_name,
        "variant_a": {
            "name": variant_a_name,
            "conversions": variant_a_conversions,
            "total": variant_a_total,
        },
        "variant_b": {
            "name": variant_b_name,
            "conversions": variant_b_conversions,
            "total": variant_b_total,
        },
    }
    tool = ABTestTool()
    return tool._run(json.dumps(test_data))
