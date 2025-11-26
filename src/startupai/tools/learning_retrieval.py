"""
Learning Retrieval Tool for Flywheel System.

Retrieves relevant learnings from past validations using semantic
similarity search to inform current decisions.
"""

import os
from typing import Dict, List, Optional, Any

from crewai.tools import BaseTool
from pydantic import Field

from startupai.persistence.connection import get_supabase_client


class LearningRetrievalTool(BaseTool):
    """
    CrewAI tool for retrieving relevant learnings from the Flywheel system.

    Uses vector similarity search to find learnings that are semantically
    similar to the current context.
    """

    name: str = "retrieve_learnings"
    description: str = """
    Retrieve relevant learnings from past startup validations.
    Use this to inform decisions based on patterns and outcomes
    from similar situations in the past.

    Provide a query describing your current situation or question,
    and optionally filter by phase, learning type, or industry.
    """

    def _run(
        self,
        query: str,
        founder: Optional[str] = None,
        learning_type: Optional[str] = None,
        phase: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7,
    ) -> str:
        """
        Retrieve relevant learnings based on semantic similarity.

        Args:
            query: The query describing the current situation
            founder: Optional founder context (for personalization)
            learning_type: Optional filter by type (pattern, outcome, domain)
            phase: Optional filter by phase
            industry: Optional filter by industry
            limit: Maximum number of learnings to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            Formatted string with relevant learnings
        """
        try:
            # 1. Generate embedding for query
            query_embedding = self._generate_embedding(query)

            # 2. Search using Supabase RPC
            client = get_supabase_client()

            # Call the search_learnings function
            result = client.rpc(
                "search_learnings",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": similarity_threshold,
                    "match_count": limit,
                    "filter_phase": phase,
                    "filter_type": learning_type,
                    "filter_industry": industry,
                }
            ).execute()

            # 3. Format results
            if not result.data:
                return "No relevant learnings found for your query."

            return self._format_learnings(result.data)

        except Exception as e:
            return f"Failed to retrieve learnings: {str(e)}"

    async def _arun(
        self,
        query: str,
        founder: Optional[str] = None,
        learning_type: Optional[str] = None,
        phase: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7,
    ) -> str:
        """Async version of _run."""
        return self._run(
            query, founder, learning_type, phase,
            industry, limit, similarity_threshold
        )

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the query text."""
        try:
            import openai

            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding

        except Exception as e:
            raise RuntimeError(f"Failed to generate query embedding: {e}")

    def _format_learnings(self, learnings: List[Dict[str, Any]]) -> str:
        """Format learnings for agent consumption."""
        parts = ["## Relevant Learnings from Past Validations\n"]

        for i, learning in enumerate(learnings, 1):
            similarity = learning.get('similarity', 0) * 100
            parts.append(f"### {i}. {learning['title']} ({similarity:.0f}% match)")
            parts.append(f"**Type:** {learning['learning_type']} | **Phase:** {learning['phase']}")

            if learning.get('industry'):
                parts.append(f"**Industry:** {learning['industry']}")

            parts.append(f"\n{learning['description']}")

            if learning.get('context_abstract'):
                parts.append(f"\n*Context:* {learning['context_abstract']}")

            if learning.get('tags'):
                parts.append(f"\n*Tags:* {', '.join(learning['tags'])}")

            if learning.get('confidence_score'):
                parts.append(f"\n*Confidence:* {learning['confidence_score']:.0%}")

            parts.append("")  # Empty line between learnings

        return "\n".join(parts)


def retrieve_similar_patterns(
    situation: str,
    phase: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 3,
) -> str:
    """
    Convenience function to retrieve similar patterns.

    Args:
        situation: Description of the current situation
        phase: Optional phase filter
        industry: Optional industry filter
        limit: Maximum number of patterns to return

    Returns:
        Formatted string with relevant patterns
    """
    tool = LearningRetrievalTool()
    return tool._run(
        query=situation,
        learning_type="pattern",
        phase=phase,
        industry=industry,
        limit=limit,
    )


def retrieve_similar_outcomes(
    situation: str,
    phase: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 3,
) -> str:
    """
    Convenience function to retrieve similar outcomes.

    Args:
        situation: Description of the current situation
        phase: Optional phase filter
        industry: Optional industry filter
        limit: Maximum number of outcomes to return

    Returns:
        Formatted string with relevant outcomes
    """
    tool = LearningRetrievalTool()
    return tool._run(
        query=situation,
        learning_type="outcome",
        phase=phase,
        industry=industry,
        limit=limit,
    )


def get_guidance_for_decision(
    decision_context: str,
    phase: str,
    industry: Optional[str] = None,
) -> str:
    """
    Get guidance for a specific decision based on past learnings.

    Args:
        decision_context: Description of the decision to make
        phase: Current validation phase
        industry: Optional industry for filtering

    Returns:
        Formatted guidance based on similar past situations
    """
    tool = LearningRetrievalTool()

    # Get patterns
    patterns = tool._run(
        query=decision_context,
        learning_type="pattern",
        phase=phase,
        industry=industry,
        limit=3,
    )

    # Get outcomes
    outcomes = tool._run(
        query=decision_context,
        learning_type="outcome",
        phase=phase,
        industry=industry,
        limit=2,
    )

    return f"""
## Decision Guidance

### Similar Patterns Observed
{patterns}

### Related Outcomes
{outcomes}

---
*Use these learnings to inform your decision, but adapt to your specific context.*
"""
