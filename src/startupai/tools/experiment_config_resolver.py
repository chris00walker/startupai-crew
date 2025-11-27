"""
Experiment Config Resolver with Policy Bandit Integration.

Resolves experiment configurations using either YAML baselines or
retrieval-augmented configurations based on policy selection.

Area 3 Implementation: Policy Versioning - Config Resolution
"""

import os
from typing import Dict, Optional, Any, List
from pathlib import Path
from datetime import datetime

import yaml
from pydantic import BaseModel, Field

from startupai.flows.state_schemas import (
    PolicyVersion,
    StartupValidationState,
    AdVariant,
)
from startupai.tools.policy_bandit import PolicyBandit, select_experiment_policy
from startupai.tools.learning_retrieval import LearningRetrievalTool
from startupai.persistence.decision_log import log_policy_selection
from startupai.models.tool_contracts import ToolResult


# =======================================================================================
# DATA MODELS
# =======================================================================================

class ExperimentConfig(BaseModel):
    """Configuration for an experiment."""
    experiment_type: str
    config_source: str  # yaml_baseline, retrieval_v1, hybrid
    policy_version: PolicyVersion

    # Creative config
    hook_types: List[str] = Field(default_factory=list)
    tones: List[str] = Field(default_factory=list)
    headline_templates: List[str] = Field(default_factory=list)
    cta_options: List[str] = Field(default_factory=list)

    # Targeting config
    audience_segments: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=list)

    # Budget config
    daily_budget_usd: float = 50.0
    duration_days: int = 7

    # Metadata
    resolved_at: datetime = Field(default_factory=datetime.now)
    retrieval_context: Optional[str] = None


class ResolverResult(BaseModel):
    """Result from config resolution."""
    config: ExperimentConfig
    selection_reason: str
    retrieved_learnings: int = 0


# =======================================================================================
# YAML BASELINE CONFIGS
# =======================================================================================

BASELINE_CONFIGS = {
    'ad_creative': {
        'hook_types': ['problem-agitate-solve', 'social-proof', 'curiosity'],
        'tones': ['direct', 'playful', 'empathetic'],
        'headline_templates': [
            "Struggling with {problem}?",
            "The {adjective} way to {benefit}",
            "{number}+ {customers} already {action}",
        ],
        'cta_options': ['Learn More', 'Get Started', 'Try Free'],
        'audience_segments': ['early_adopters', 'problem_aware'],
        'platforms': ['meta', 'google'],
        'daily_budget_usd': 50.0,
        'duration_days': 7,
    },
    'landing_page': {
        'hook_types': ['problem-agitate-solve', 'testimonial'],
        'tones': ['direct', 'premium'],
        'headline_templates': [
            "{benefit} without {pain}",
            "Finally, a {solution} that works",
        ],
        'cta_options': ['Start Free Trial', 'Schedule Demo', 'Get Early Access'],
        'audience_segments': ['solution_aware'],
        'platforms': ['web'],
        'daily_budget_usd': 0.0,  # No budget for LP
        'duration_days': 14,
    },
    'interview_question': {
        'hook_types': [],
        'tones': ['empathetic', 'technical'],
        'headline_templates': [],
        'cta_options': [],
        'audience_segments': ['target_customers'],
        'platforms': ['survey', 'interview'],
        'daily_budget_usd': 0.0,
        'duration_days': 7,
    },
    'pricing_test': {
        'hook_types': ['urgency', 'social-proof'],
        'tones': ['direct', 'premium'],
        'headline_templates': [
            "Limited time: {offer}",
            "Join {number}+ {customers}",
        ],
        'cta_options': ['Get Pricing', 'Start Trial', 'Buy Now'],
        'audience_segments': ['comparison_shoppers', 'ready_to_buy'],
        'platforms': ['web', 'email'],
        'daily_budget_usd': 25.0,
        'duration_days': 14,
    },
}


# =======================================================================================
# CONFIG RESOLVER
# =======================================================================================

class ExperimentConfigResolver:
    """
    Resolves experiment configurations using policy-based selection.

    Can use:
    - YAML baseline: Static configurations from BASELINE_CONFIGS
    - Retrieval v1: Augmented with learnings from Flywheel
    - Hybrid: Baseline + retrieval augmentation
    """

    def __init__(self):
        """Initialize the resolver."""
        self._bandit = None
        self._retrieval_tool = None

    @property
    def bandit(self) -> PolicyBandit:
        """Lazy load policy bandit."""
        if self._bandit is None:
            self._bandit = PolicyBandit()
        return self._bandit

    @property
    def retrieval_tool(self) -> LearningRetrievalTool:
        """Lazy load retrieval tool."""
        if self._retrieval_tool is None:
            self._retrieval_tool = LearningRetrievalTool()
        return self._retrieval_tool

    def resolve(
        self,
        experiment_type: str,
        state: StartupValidationState,
        force_policy: Optional[PolicyVersion] = None,
    ) -> ToolResult[ResolverResult]:
        """
        Resolve experiment configuration.

        Args:
            experiment_type: Type of experiment
            state: Current validation state (for context)
            force_policy: Optional policy to force (bypasses bandit)

        Returns:
            ToolResult containing ResolverResult
        """
        try:
            # Select policy (or use forced policy)
            if force_policy:
                policy = force_policy
                reason = f"Forced policy: {policy.value}"
            else:
                policy, reason = select_experiment_policy(experiment_type)

            # Log the policy selection
            log_policy_selection(
                project_id=state.project_id,
                policy_version=policy.value,
                selection_reason=reason,
                experiment_type=experiment_type,
            )

            # Resolve config based on policy
            if policy == PolicyVersion.YAML_BASELINE:
                config = self._resolve_baseline(experiment_type)
                retrieved_count = 0
            elif policy == PolicyVersion.RETRIEVAL_V1:
                config, retrieved_count = self._resolve_retrieval(
                    experiment_type, state
                )
            else:
                # Default to baseline
                config = self._resolve_baseline(experiment_type)
                retrieved_count = 0

            # Set policy version on config
            config.policy_version = policy

            result = ResolverResult(
                config=config,
                selection_reason=reason,
                retrieved_learnings=retrieved_count,
            )

            return ToolResult.success(
                data=result,
                policy_version=policy.value,
                experiment_type=experiment_type,
            )

        except Exception as e:
            # Fallback to baseline on error
            config = self._resolve_baseline(experiment_type)
            return ToolResult.partial(
                data=ResolverResult(
                    config=config,
                    selection_reason=f"Fallback to baseline due to error: {str(e)}",
                    retrieved_learnings=0,
                ),
                warnings=[f"Resolution error: {str(e)}"],
            )

    def _resolve_baseline(self, experiment_type: str) -> ExperimentConfig:
        """Resolve using YAML baseline config."""
        baseline = BASELINE_CONFIGS.get(experiment_type, BASELINE_CONFIGS['ad_creative'])

        return ExperimentConfig(
            experiment_type=experiment_type,
            config_source='yaml_baseline',
            policy_version=PolicyVersion.YAML_BASELINE,
            hook_types=baseline.get('hook_types', []),
            tones=baseline.get('tones', []),
            headline_templates=baseline.get('headline_templates', []),
            cta_options=baseline.get('cta_options', []),
            audience_segments=baseline.get('audience_segments', []),
            platforms=baseline.get('platforms', []),
            daily_budget_usd=baseline.get('daily_budget_usd', 50.0),
            duration_days=baseline.get('duration_days', 7),
        )

    def _resolve_retrieval(
        self,
        experiment_type: str,
        state: StartupValidationState,
    ) -> tuple[ExperimentConfig, int]:
        """Resolve using retrieval-augmented config."""
        # Start with baseline
        config = self._resolve_baseline(experiment_type)
        config.config_source = 'retrieval_v1'
        config.policy_version = PolicyVersion.RETRIEVAL_V1

        # Build context for retrieval
        context = self._build_retrieval_context(state)

        # Try to retrieve relevant learnings
        try:
            retrieval_result = self.retrieval_tool._run(
                query=f"{experiment_type} {context}",
                learning_type="pattern",
                limit=5,
            )

            # Parse and apply learnings
            learnings = self._parse_retrieval_result(retrieval_result)
            retrieved_count = len(learnings)

            if learnings:
                config = self._augment_config(config, learnings)
                config.retrieval_context = context

            return config, retrieved_count

        except Exception as e:
            print(f"Warning: Retrieval failed: {e}")
            return config, 0

    def _build_retrieval_context(self, state: StartupValidationState) -> str:
        """Build context string for retrieval."""
        parts = []

        if state.business_idea:
            parts.append(state.business_idea[:100])
        if state.target_segments:
            parts.append(f"targeting {', '.join(state.target_segments[:3])}")
        if state.desirability_signal:
            parts.append(f"desirability: {state.desirability_signal}")
        if state.current_phase:
            parts.append(f"phase: {state.current_phase}")

        return " | ".join(parts) if parts else "startup validation"

    def _parse_retrieval_result(self, result: str) -> List[Dict[str, Any]]:
        """Parse retrieval result into learnings."""
        # Simple parsing - in production would be more sophisticated
        learnings = []
        try:
            # Assume result is a string with learning descriptions
            if 'No relevant learnings' not in result:
                # Extract patterns (simplified)
                learnings.append({'type': 'pattern', 'content': result})
        except Exception:
            pass
        return learnings

    def _augment_config(
        self,
        config: ExperimentConfig,
        learnings: List[Dict[str, Any]],
    ) -> ExperimentConfig:
        """Augment config with retrieved learnings."""
        # Apply learnings to augment config
        # In production, this would parse learnings and modify config accordingly

        for learning in learnings:
            content = learning.get('content', '')

            # Look for hook type patterns
            if 'problem-agitate-solve' in content.lower():
                if 'problem-agitate-solve' not in config.hook_types:
                    config.hook_types.insert(0, 'problem-agitate-solve')

            # Look for tone patterns
            if 'empathetic' in content.lower() and 'empathetic' not in config.tones:
                config.tones.append('empathetic')

            # Look for successful CTAs
            if 'free trial' in content.lower() and 'Start Free Trial' not in config.cta_options:
                config.cta_options.insert(0, 'Start Free Trial')

        return config


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def resolve_ad_config(
    state: StartupValidationState,
    force_policy: Optional[PolicyVersion] = None,
) -> ExperimentConfig:
    """
    Resolve ad creative configuration.

    Args:
        state: Current validation state
        force_policy: Optional policy to force

    Returns:
        ExperimentConfig for ad creatives
    """
    resolver = ExperimentConfigResolver()
    result = resolver.resolve('ad_creative', state, force_policy)

    if result.is_usable:
        return result.data.config
    else:
        # Return baseline on failure
        return resolver._resolve_baseline('ad_creative')


def resolve_landing_page_config(
    state: StartupValidationState,
    force_policy: Optional[PolicyVersion] = None,
) -> ExperimentConfig:
    """
    Resolve landing page configuration.

    Args:
        state: Current validation state
        force_policy: Optional policy to force

    Returns:
        ExperimentConfig for landing pages
    """
    resolver = ExperimentConfigResolver()
    result = resolver.resolve('landing_page', state, force_policy)

    if result.is_usable:
        return result.data.config
    else:
        return resolver._resolve_baseline('landing_page')


def create_ad_variant_from_config(
    config: ExperimentConfig,
    index: int = 0,
) -> AdVariant:
    """
    Create an AdVariant from experiment config.

    Args:
        config: Experiment configuration
        index: Which variant to create (for A/B testing)

    Returns:
        AdVariant populated from config
    """
    hook_type = config.hook_types[index % len(config.hook_types)] if config.hook_types else None
    tone = config.tones[index % len(config.tones)] if config.tones else None

    return AdVariant(
        variant_id=f"variant_{index}",
        hook_type=hook_type,
        tone=tone,
        headline=config.headline_templates[index % len(config.headline_templates)] if config.headline_templates else "Default headline",
        body_copy="",  # To be filled by creative generation
        cta=config.cta_options[index % len(config.cta_options)] if config.cta_options else "Learn More",
        platform=config.platforms[0] if config.platforms else "meta",
    )


def update_state_with_policy(
    state: StartupValidationState,
    config: ExperimentConfig,
    selection_reason: str,
) -> StartupValidationState:
    """
    Update state with policy selection info.

    Args:
        state: Current validation state
        config: Resolved experiment config
        selection_reason: Reason for policy selection

    Returns:
        Updated state
    """
    state.current_policy_version = config.policy_version
    state.experiment_config_source = config.config_source
    state.policy_selection_reason = selection_reason

    return state
