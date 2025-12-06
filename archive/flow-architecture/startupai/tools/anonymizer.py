"""
Anonymizer Tool for Privacy-Preserving Learning.

Removes PII and abstracts business-specific details to enable
safe storage of learnings in the Flywheel system.
"""

import re
from typing import Dict, List, Optional, Any
from crewai.tools import BaseTool
from pydantic import Field


# Common patterns for PII detection
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b')
URL_PATTERN = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
IP_PATTERN = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
CREDIT_CARD_PATTERN = re.compile(r'\b(?:\d[ -]*?){13,19}\b')

# Common company name indicators
COMPANY_SUFFIXES = [
    'Inc', 'LLC', 'Ltd', 'Corp', 'Corporation', 'Company', 'Co',
    'GmbH', 'AG', 'SA', 'Pty', 'PLC', 'LLP', 'LP'
]


def anonymize_text(
    text: str,
    entities: Optional[Dict[str, str]] = None,
    preserve_structure: bool = True
) -> str:
    """
    Anonymize text by removing PII and business-specific details.

    Args:
        text: The text to anonymize
        entities: Optional dict of entity -> replacement mappings
        preserve_structure: If True, replace with category placeholders

    Returns:
        Anonymized text
    """
    result = text

    # Apply custom entity replacements first
    if entities:
        for entity, replacement in entities.items():
            result = result.replace(entity, replacement)

    # Remove emails
    if preserve_structure:
        result = EMAIL_PATTERN.sub('[EMAIL]', result)
    else:
        result = EMAIL_PATTERN.sub('', result)

    # Remove phone numbers
    if preserve_structure:
        result = PHONE_PATTERN.sub('[PHONE]', result)
    else:
        result = PHONE_PATTERN.sub('', result)

    # Remove URLs
    if preserve_structure:
        result = URL_PATTERN.sub('[URL]', result)
    else:
        result = URL_PATTERN.sub('', result)

    # Remove IP addresses
    if preserve_structure:
        result = IP_PATTERN.sub('[IP]', result)
    else:
        result = IP_PATTERN.sub('', result)

    # Remove SSNs
    if preserve_structure:
        result = SSN_PATTERN.sub('[SSN]', result)
    else:
        result = SSN_PATTERN.sub('', result)

    # Remove credit card numbers
    if preserve_structure:
        result = CREDIT_CARD_PATTERN.sub('[CARD]', result)
    else:
        result = CREDIT_CARD_PATTERN.sub('', result)

    return result


def abstract_business_context(
    context: Dict[str, Any],
    industry: Optional[str] = None
) -> Dict[str, Any]:
    """
    Abstract business-specific details to general categories.

    Args:
        context: The business context to abstract
        industry: Optional industry classification

    Returns:
        Abstracted context with general categories
    """
    abstracted = {}

    # Abstract common fields
    field_mappings = {
        'company_name': '[COMPANY]',
        'product_name': '[PRODUCT]',
        'founder_name': '[FOUNDER]',
        'customer_name': '[CUSTOMER]',
        'investor_name': '[INVESTOR]',
        'competitor_name': '[COMPETITOR]',
    }

    for key, value in context.items():
        # Check if this is a known field to abstract
        if key in field_mappings:
            abstracted[key] = field_mappings[key]
        elif isinstance(value, str):
            # Anonymize string values
            abstracted[key] = anonymize_text(value)
        elif isinstance(value, dict):
            # Recursively abstract nested dicts
            abstracted[key] = abstract_business_context(value, industry)
        elif isinstance(value, list):
            # Abstract list items
            abstracted[key] = [
                abstract_business_context(item, industry) if isinstance(item, dict)
                else anonymize_text(str(item)) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            # Keep non-string, non-dict, non-list values as-is
            abstracted[key] = value

    # Add industry classification if provided
    if industry:
        abstracted['_industry'] = industry

    return abstracted


def extract_patterns(
    context: Dict[str, Any],
    pattern_type: str = 'general'
) -> List[str]:
    """
    Extract generalizable patterns from a specific context.

    Args:
        context: The context to extract patterns from
        pattern_type: Type of patterns to extract

    Returns:
        List of extracted patterns
    """
    patterns = []

    # Extract signal-based patterns
    if 'desirability_signal' in context:
        signal = context['desirability_signal']
        if signal == 'no_interest':
            patterns.append("Low problem resonance indicates segment mismatch")
        elif signal == 'weak_interest':
            patterns.append("Weak interest without commitment suggests value prop needs iteration")
        elif signal == 'strong_commitment':
            patterns.append("Strong commitment with high conversion validates problem-solution fit")

    if 'feasibility_signal' in context:
        signal = context['feasibility_signal']
        if signal == 'red_impossible':
            patterns.append("Technical impossibility requires value proposition downgrade")
        elif signal == 'orange_constrained':
            patterns.append("Constrained feasibility needs customer acceptance testing")

    if 'viability_signal' in context:
        signal = context['viability_signal']
        if signal == 'underwater':
            patterns.append("Underwater unit economics require price or cost pivot")
        elif signal == 'zombie_market':
            patterns.append("High interest with poor economics indicates pricing mismatch")

    # Extract pivot patterns
    if 'pivot_history' in context and context['pivot_history']:
        for pivot in context['pivot_history']:
            pivot_type = pivot.get('type', 'unknown')
            patterns.append(f"Pivot type '{pivot_type}' was triggered by evidence signals")

    return patterns


class AnonymizerTool(BaseTool):
    """
    CrewAI tool for anonymizing data before storage.

    This tool removes PII and abstracts business-specific details
    to enable safe storage of learnings in the Flywheel system.
    """

    name: str = "anonymize_data"
    description: str = """
    Anonymize text and data by removing personally identifiable information (PII)
    and abstracting business-specific details. Use this before storing learnings
    to protect privacy and enable safe knowledge sharing.

    Input should be text or JSON data containing potentially sensitive information.
    """

    preserve_structure: bool = Field(
        default=True,
        description="If True, replace PII with category placeholders"
    )

    def _run(
        self,
        text: str,
        entities: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Anonymize the provided text.

        Args:
            text: The text to anonymize
            entities: Optional dict of entity -> replacement mappings

        Returns:
            Anonymized text
        """
        return anonymize_text(text, entities, self.preserve_structure)

    async def _arun(
        self,
        text: str,
        entities: Optional[Dict[str, str]] = None
    ) -> str:
        """Async version of _run."""
        return self._run(text, entities)
