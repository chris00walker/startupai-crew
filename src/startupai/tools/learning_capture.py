"""
Learning Capture Tool for Flywheel System.

Captures anonymized learnings from validation flows and stores them
with vector embeddings for future retrieval.
"""

import os
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
import uuid

from crewai.tools import BaseTool
from pydantic import Field

from startupai.tools.anonymizer import anonymize_text, abstract_business_context
from startupai.persistence.connection import get_supabase_client


class LearningCaptureTool(BaseTool):
    """
    CrewAI tool for capturing learnings into the Flywheel system.

    This tool:
    1. Anonymizes the context
    2. Generates embeddings via OpenAI
    3. Stores the learning in Supabase with vector index
    """

    name: str = "capture_learning"
    description: str = """
    Capture a learning from the validation process for the Flywheel system.
    This stores anonymized, generalized insights that can help future validations.

    Use this when you identify a pattern, outcome, or domain-specific insight
    that could benefit future startup validations.
    """

    def _run(
        self,
        learning_type: Literal["pattern", "outcome", "domain"],
        title: str,
        description: str,
        context: Dict[str, Any],
        founder: str,
        phase: str,
        tags: Optional[List[str]] = None,
        confidence_score: Optional[float] = None,
        industry: Optional[str] = None,
    ) -> str:
        """
        Capture a learning into the Flywheel system.

        Args:
            learning_type: Type of learning (pattern, outcome, domain)
            title: Short title for the learning
            description: Detailed description of what was learned
            context: The business context (will be anonymized)
            founder: Identifier for the founder (will be anonymized)
            phase: Phase where learning was captured
            tags: Optional tags for categorization
            confidence_score: Optional confidence in the learning (0-1)
            industry: Optional industry classification

        Returns:
            Status message with learning ID
        """
        try:
            # 1. Anonymize the context
            anonymized_context = abstract_business_context(context, industry)
            anonymized_description = anonymize_text(description)
            anonymized_title = anonymize_text(title)

            # Create abstract representation of context
            context_abstract = self._create_context_abstract(anonymized_context)

            # 2. Generate embedding
            embedding = self._generate_embedding(
                f"{anonymized_title} {anonymized_description} {context_abstract}"
            )

            # 3. Store in Supabase
            learning_id = str(uuid.uuid4())
            record = {
                "id": learning_id,
                "learning_type": learning_type,
                "founder": f"founder_{hash(founder) % 10000:04d}",  # Anonymize founder
                "phase": phase,
                "industry": industry,
                "title": anonymized_title,
                "description": anonymized_description,
                "context_abstract": context_abstract,
                "tags": tags or [],
                "embedding": embedding,
                "confidence_score": confidence_score,
                "created_at": datetime.now().isoformat(),
            }

            client = get_supabase_client()
            client.table("learnings").insert(record).execute()

            return f"Learning captured successfully with ID: {learning_id}"

        except Exception as e:
            return f"Failed to capture learning: {str(e)}"

    async def _arun(
        self,
        learning_type: Literal["pattern", "outcome", "domain"],
        title: str,
        description: str,
        context: Dict[str, Any],
        founder: str,
        phase: str,
        tags: Optional[List[str]] = None,
        confidence_score: Optional[float] = None,
        industry: Optional[str] = None,
    ) -> str:
        """Async version of _run."""
        return self._run(
            learning_type, title, description, context,
            founder, phase, tags, confidence_score, industry
        )

    def _create_context_abstract(self, context: Dict[str, Any]) -> str:
        """Create a text abstract of the context for embedding."""
        parts = []

        # Extract key signals
        if 'desirability_signal' in context:
            parts.append(f"Desirability: {context['desirability_signal']}")
        if 'feasibility_signal' in context:
            parts.append(f"Feasibility: {context['feasibility_signal']}")
        if 'viability_signal' in context:
            parts.append(f"Viability: {context['viability_signal']}")

        # Extract phase info
        if 'phase' in context:
            parts.append(f"Phase: {context['phase']}")

        # Extract pivot info
        if 'pivot_history' in context:
            pivot_count = len(context['pivot_history'])
            parts.append(f"Pivots: {pivot_count}")

        # Extract industry
        if '_industry' in context:
            parts.append(f"Industry: {context['_industry']}")

        return " | ".join(parts) if parts else "No context available"

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the learning text.

        Uses OpenAI's text-embedding-3-small model (1536 dimensions).
        """
        try:
            import openai

            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding

        except Exception as e:
            # Return zero vector on failure (will have low similarity)
            print(f"Warning: Failed to generate embedding: {e}")
            return [0.0] * 1536


def capture_pattern_learning(
    title: str,
    description: str,
    context: Dict[str, Any],
    founder: str,
    phase: str,
    tags: Optional[List[str]] = None,
    confidence_score: Optional[float] = None,
    industry: Optional[str] = None,
) -> str:
    """Convenience function to capture a pattern learning."""
    tool = LearningCaptureTool()
    return tool._run(
        learning_type="pattern",
        title=title,
        description=description,
        context=context,
        founder=founder,
        phase=phase,
        tags=tags,
        confidence_score=confidence_score,
        industry=industry,
    )


def capture_outcome_learning(
    title: str,
    description: str,
    context: Dict[str, Any],
    founder: str,
    phase: str,
    tags: Optional[List[str]] = None,
    confidence_score: Optional[float] = None,
    industry: Optional[str] = None,
) -> str:
    """Convenience function to capture an outcome learning."""
    tool = LearningCaptureTool()
    return tool._run(
        learning_type="outcome",
        title=title,
        description=description,
        context=context,
        founder=founder,
        phase=phase,
        tags=tags,
        confidence_score=confidence_score,
        industry=industry,
    )
