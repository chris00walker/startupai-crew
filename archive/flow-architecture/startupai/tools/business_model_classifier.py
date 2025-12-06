"""
Business Model Classifier for Automatic Model Type Detection.

Uses heuristics and keyword analysis to classify a startup's business model
for appropriate unit economics calculations.

Area 7 Implementation: Phase 2 & 3 Depth - Business Model Classification
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from pydantic import BaseModel

from startupai.flows.state_schemas import (
    BusinessModelType,
    StartupValidationState,
)
from startupai.models.tool_contracts import ToolResult


# =======================================================================================
# CLASSIFICATION SIGNALS
# =======================================================================================

@dataclass
class ClassificationSignals:
    """Signals extracted from business description for classification."""
    # Revenue model indicators
    has_subscription: bool = False
    has_transaction_fees: bool = False
    has_marketplace_fees: bool = False
    has_project_billing: bool = False
    has_freemium: bool = False

    # Customer type indicators
    is_b2b: bool = False
    is_b2c: bool = False
    targets_enterprise: bool = False
    targets_smb: bool = False

    # Industry indicators
    is_fintech: bool = False
    is_ecommerce: bool = False
    is_saas: bool = False
    is_services: bool = False

    # Business characteristics
    has_physical_goods: bool = False
    is_platform: bool = False
    requires_compliance: bool = False

    # Extracted keywords
    keywords_found: List[str] = field(default_factory=list)


class ClassificationResult(BaseModel):
    """Result of business model classification."""
    classified_type: BusinessModelType
    confidence: float  # 0.0 to 1.0
    signals: Dict[str, bool]
    reasoning: str
    alternative_types: List[BusinessModelType] = []


# =======================================================================================
# KEYWORD DICTIONARIES
# =======================================================================================

SAAS_KEYWORDS = [
    'saas', 'software as a service', 'cloud software', 'subscription software',
    'monthly subscription', 'annual subscription', 'recurring revenue', 'mrr',
    'arr', 'per seat', 'per user', 'platform', 'dashboard', 'api',
]

B2B_KEYWORDS = [
    'b2b', 'business to business', 'enterprise', 'companies', 'businesses',
    'corporate', 'teams', 'organizations', 'professional', 'industry',
]

B2C_KEYWORDS = [
    'b2c', 'consumer', 'individuals', 'personal', 'retail', 'customers',
    'users', 'people', 'mass market', 'consumer app',
]

ENTERPRISE_KEYWORDS = [
    'enterprise', 'fortune 500', 'large companies', 'corporate',
    'compliance', 'soc 2', 'hipaa', 'gdpr', 'security',
]

SMB_KEYWORDS = [
    'smb', 'small business', 'startups', 'freelancers', 'solopreneurs',
    'small teams', 'self-serve', 'no sales team',
]

FINTECH_KEYWORDS = [
    'fintech', 'payments', 'banking', 'lending', 'credit', 'insurance',
    'trading', 'investment', 'financial services', 'money transfer',
    'neobank', 'debit', 'credit card', 'loan', 'mortgage',
]

ECOMMERCE_KEYWORDS = [
    'ecommerce', 'e-commerce', 'online store', 'shop', 'retail',
    'products', 'inventory', 'shipping', 'fulfillment', 'cart',
]

MARKETPLACE_KEYWORDS = [
    'marketplace', 'two-sided', 'platform', 'buyers and sellers',
    'commission', 'take rate', 'gmv', 'transaction fee', 'matching',
]

DTC_KEYWORDS = [
    'dtc', 'direct to consumer', 'brand', 'our products', 'we sell',
    'inventory', 'warehouse', 'fulfillment', 'shipping directly',
]

FREEMIUM_KEYWORDS = [
    'freemium', 'free tier', 'free plan', 'free users', 'upgrade',
    'premium', 'pro plan', 'conversion rate', 'free to paid',
]

CONSULTING_KEYWORDS = [
    'consulting', 'services', 'agency', 'advisory', 'professional services',
    'project-based', 'hourly', 'retainer', 'engagement',
]


# =======================================================================================
# CLASSIFIER
# =======================================================================================

class BusinessModelClassifier:
    """
    Classifier for determining business model type from description.

    Uses keyword matching and heuristics to identify the most likely
    business model type for unit economics calculations.
    """

    def classify(
        self,
        business_description: str,
        revenue_model: Optional[str] = None,
        target_customers: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> ToolResult[ClassificationResult]:
        """
        Classify the business model from provided information.

        Args:
            business_description: Description of the business/product
            revenue_model: Optional explicit revenue model description
            target_customers: Optional target customer description
            industry: Optional industry classification

        Returns:
            ToolResult containing ClassificationResult
        """
        try:
            # Combine all text for analysis
            combined_text = ' '.join(filter(None, [
                business_description,
                revenue_model,
                target_customers,
                industry,
            ])).lower()

            # Extract signals
            signals = self._extract_signals(combined_text)

            # Score each business model type
            scores = self._score_business_models(signals)

            # Get best match
            best_type, confidence = self._select_best_match(scores)

            # Get alternatives
            alternatives = self._get_alternatives(scores, best_type)

            # Generate reasoning
            reasoning = self._generate_reasoning(signals, best_type)

            result = ClassificationResult(
                classified_type=best_type,
                confidence=confidence,
                signals={
                    'has_subscription': signals.has_subscription,
                    'is_b2b': signals.is_b2b,
                    'is_b2c': signals.is_b2c,
                    'targets_enterprise': signals.targets_enterprise,
                    'is_fintech': signals.is_fintech,
                    'is_ecommerce': signals.is_ecommerce,
                    'is_saas': signals.is_saas,
                    'is_platform': signals.is_platform,
                    'has_freemium': signals.has_freemium,
                },
                reasoning=reasoning,
                alternative_types=alternatives,
            )

            return ToolResult.success(data=result)

        except Exception as e:
            return ToolResult.failure(
                message=f"Classification failed: {str(e)}",
                code="CLASSIFICATION_ERROR",
            )

    def _extract_signals(self, text: str) -> ClassificationSignals:
        """Extract classification signals from text."""
        signals = ClassificationSignals()

        # Check each keyword category
        signals.is_saas = self._has_keywords(text, SAAS_KEYWORDS)
        signals.is_b2b = self._has_keywords(text, B2B_KEYWORDS)
        signals.is_b2c = self._has_keywords(text, B2C_KEYWORDS)
        signals.targets_enterprise = self._has_keywords(text, ENTERPRISE_KEYWORDS)
        signals.targets_smb = self._has_keywords(text, SMB_KEYWORDS)
        signals.is_fintech = self._has_keywords(text, FINTECH_KEYWORDS)
        signals.is_ecommerce = self._has_keywords(text, ECOMMERCE_KEYWORDS)
        signals.is_platform = self._has_keywords(text, MARKETPLACE_KEYWORDS)
        signals.has_freemium = self._has_keywords(text, FREEMIUM_KEYWORDS)
        signals.is_services = self._has_keywords(text, CONSULTING_KEYWORDS)
        signals.has_physical_goods = self._has_keywords(text, DTC_KEYWORDS)

        # Subscription detection
        signals.has_subscription = self._has_keywords(text, [
            'subscription', 'monthly', 'annual', 'recurring', 'mrr', 'arr'
        ])

        # Transaction fee detection
        signals.has_transaction_fees = self._has_keywords(text, [
            'transaction fee', 'per transaction', 'commission', 'take rate'
        ])

        # Marketplace fee detection
        signals.has_marketplace_fees = self._has_keywords(text, [
            'marketplace', 'platform fee', 'listing fee', 'gmv'
        ])

        # Compliance requirements
        signals.requires_compliance = self._has_keywords(text, [
            'compliance', 'regulated', 'license', 'soc 2', 'hipaa', 'pci'
        ])

        # Collect all found keywords
        all_keyword_lists = [
            SAAS_KEYWORDS, B2B_KEYWORDS, B2C_KEYWORDS, ENTERPRISE_KEYWORDS,
            SMB_KEYWORDS, FINTECH_KEYWORDS, ECOMMERCE_KEYWORDS, MARKETPLACE_KEYWORDS,
            FREEMIUM_KEYWORDS, CONSULTING_KEYWORDS, DTC_KEYWORDS,
        ]
        for keyword_list in all_keyword_lists:
            for keyword in keyword_list:
                if keyword in text:
                    signals.keywords_found.append(keyword)

        return signals

    def _has_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords."""
        for keyword in keywords:
            if keyword in text:
                return True
        return False

    def _score_business_models(
        self,
        signals: ClassificationSignals
    ) -> Dict[BusinessModelType, float]:
        """Score each business model type based on signals."""
        scores = {model_type: 0.0 for model_type in BusinessModelType}

        # SaaS B2B Enterprise
        if signals.is_saas and signals.is_b2b and signals.targets_enterprise:
            scores[BusinessModelType.SAAS_B2B_ENTERPRISE] += 3.0
        if signals.requires_compliance:
            scores[BusinessModelType.SAAS_B2B_ENTERPRISE] += 1.0

        # SaaS B2B Mid-Market
        if signals.is_saas and signals.is_b2b and not signals.targets_enterprise and not signals.targets_smb:
            scores[BusinessModelType.SAAS_B2B_MIDMARKET] += 2.0
        if signals.is_saas and signals.is_b2b:
            scores[BusinessModelType.SAAS_B2B_MIDMARKET] += 1.0

        # SaaS B2B SMB
        if signals.is_saas and signals.is_b2b and signals.targets_smb:
            scores[BusinessModelType.SAAS_B2B_SMB] += 3.0
        if signals.is_saas and signals.is_b2b and not signals.targets_enterprise:
            scores[BusinessModelType.SAAS_B2B_SMB] += 1.0

        # SaaS B2C Freemium
        if signals.is_saas and signals.is_b2c and signals.has_freemium:
            scores[BusinessModelType.SAAS_B2C_FREEMIUM] += 3.0

        # SaaS B2C Subscription
        if signals.is_saas and signals.is_b2c and signals.has_subscription and not signals.has_freemium:
            scores[BusinessModelType.SAAS_B2C_SUBSCRIPTION] += 3.0
        if signals.is_saas and signals.is_b2c:
            scores[BusinessModelType.SAAS_B2C_SUBSCRIPTION] += 1.0

        # E-commerce DTC
        if signals.is_ecommerce and signals.has_physical_goods and not signals.is_platform:
            scores[BusinessModelType.ECOMMERCE_DTC] += 3.0
        if signals.is_ecommerce and signals.is_b2c and not signals.is_platform:
            scores[BusinessModelType.ECOMMERCE_DTC] += 1.0

        # E-commerce Marketplace
        if signals.is_ecommerce and signals.is_platform:
            scores[BusinessModelType.ECOMMERCE_MARKETPLACE] += 3.0
        if signals.has_marketplace_fees or signals.has_transaction_fees:
            scores[BusinessModelType.ECOMMERCE_MARKETPLACE] += 2.0

        # Fintech B2B
        if signals.is_fintech and signals.is_b2b:
            scores[BusinessModelType.FINTECH_B2B] += 3.0
        if signals.is_fintech and signals.requires_compliance:
            scores[BusinessModelType.FINTECH_B2B] += 1.0

        # Fintech B2C
        if signals.is_fintech and signals.is_b2c:
            scores[BusinessModelType.FINTECH_B2C] += 3.0
        if signals.is_fintech and not signals.is_b2b:
            scores[BusinessModelType.FINTECH_B2C] += 1.0

        # Consulting
        if signals.is_services:
            scores[BusinessModelType.CONSULTING] += 3.0
        if signals.has_project_billing:
            scores[BusinessModelType.CONSULTING] += 2.0

        # Default scoring for unknowns
        if not any(s > 0 for s in scores.values()):
            # Default to SaaS B2B SMB as generic fallback
            scores[BusinessModelType.SAAS_B2B_SMB] = 0.5
            scores[BusinessModelType.UNKNOWN] = 1.0

        return scores

    def _select_best_match(
        self,
        scores: Dict[BusinessModelType, float]
    ) -> Tuple[BusinessModelType, float]:
        """Select the best matching business model type."""
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        # Calculate confidence (normalized score)
        total_score = sum(scores.values())
        confidence = best_score / total_score if total_score > 0 else 0.0

        # Cap confidence
        confidence = min(confidence, 0.95)

        return best_type, confidence

    def _get_alternatives(
        self,
        scores: Dict[BusinessModelType, float],
        best_type: BusinessModelType,
    ) -> List[BusinessModelType]:
        """Get alternative business model types."""
        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        alternatives = []

        for model_type, score in sorted_types[1:4]:  # Top 3 alternatives
            if score > 0:
                alternatives.append(model_type)

        return alternatives

    def _generate_reasoning(
        self,
        signals: ClassificationSignals,
        best_type: BusinessModelType,
    ) -> str:
        """Generate human-readable reasoning for the classification."""
        reasons = []

        if signals.is_saas:
            reasons.append("SaaS indicators detected (subscription-based software)")
        if signals.is_b2b:
            reasons.append("B2B focus (business customers)")
        if signals.is_b2c:
            reasons.append("B2C focus (consumer customers)")
        if signals.targets_enterprise:
            reasons.append("Enterprise targeting (large companies, compliance)")
        if signals.targets_smb:
            reasons.append("SMB targeting (small businesses)")
        if signals.is_fintech:
            reasons.append("Fintech indicators (financial services)")
        if signals.is_ecommerce:
            reasons.append("E-commerce indicators (online retail)")
        if signals.is_platform:
            reasons.append("Platform/marketplace model")
        if signals.has_freemium:
            reasons.append("Freemium conversion model")
        if signals.is_services:
            reasons.append("Services/consulting model")

        if reasons:
            return f"Classified as {best_type.value} based on: " + "; ".join(reasons)
        else:
            return f"Classified as {best_type.value} (default - insufficient signals)"


def classify_from_state(
    state: StartupValidationState,
) -> ToolResult[ClassificationResult]:
    """
    Classify business model from validation state.

    Args:
        state: Current validation state with business info

    Returns:
        ToolResult containing ClassificationResult
    """
    classifier = BusinessModelClassifier()

    # Extract relevant info from state
    business_description = state.business_idea or ""
    revenue_model = state.revenue_model or ""
    target_customers = " ".join(state.target_segments) if state.target_segments else ""
    industry = None  # Could extract from competitive analysis if available

    return classifier.classify(
        business_description=business_description,
        revenue_model=revenue_model,
        target_customers=target_customers,
        industry=industry,
    )


def update_state_with_classification(
    state: StartupValidationState,
    classification: ClassificationResult,
) -> StartupValidationState:
    """
    Update state with business model classification.

    Args:
        state: Current validation state
        classification: Classification result

    Returns:
        Updated state with business model fields set
    """
    state.business_model_type = classification.classified_type
    state.business_model_inferred_from = classification.reasoning

    return state
