"""
Policy Bandit Tool for Weighted Policy Selection.

Implements Upper Confidence Bound (UCB) algorithm for selecting between
yaml_baseline and retrieval_v1 policies in experiment configuration.

Area 3 Implementation: Policy Versioning & A/B Testing
"""

import os
import math
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from startupai.flows.state_schemas import PolicyVersion
from startupai.persistence.connection import get_supabase_client
from startupai.models.tool_contracts import ToolResult


class PolicyWeight(BaseModel):
    """Weight data for a policy in the bandit."""
    policy_version: PolicyVersion
    sample_count: int = 0
    mean_reward: float = 0.0
    ucb_score: float = 0.0
    last_updated: Optional[datetime] = None


class PolicySelectionResult(BaseModel):
    """Result of a policy selection."""
    selected_policy: PolicyVersion
    selection_reason: str
    weights: Dict[str, PolicyWeight] = Field(default_factory=dict)
    exploration_used: bool = False


class PolicyBandit:
    """
    Weighted Bandit for policy selection.

    Uses Upper Confidence Bound (UCB) algorithm to balance exploration
    (trying less-tested policies) and exploitation (using policies with
    proven higher rewards).
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the policy bandit.

        Args:
            config_path: Path to policy_weights.yaml config file.
                        If None, uses default location.
        """
        self.config_path = config_path or self._default_config_path()
        self.config = self._load_config()
        self._supabase = None

    def _default_config_path(self) -> str:
        """Get default config path."""
        return str(
            Path(__file__).parent.parent / "config" / "policy_weights.yaml"
        )

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return sensible defaults if config doesn't exist
            return {
                'global': {
                    'min_samples_for_selection': 10,
                    'exploration_bonus': 0.1,
                    'default_policy': 'yaml_baseline',
                    'bandit_enabled': True,
                },
                'policies': {
                    'yaml_baseline': {'prior_weight': 0.5},
                    'retrieval_v1': {'prior_weight': 0.5},
                },
                'ucb': {
                    'confidence_level': 0.95,
                    'time_decay_factor': 0.99,
                    'observation_window_days': 30,
                },
            }

    @property
    def supabase(self):
        """Lazy load Supabase client."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    def select_policy(
        self,
        experiment_type: str,
        force_exploration: bool = False,
    ) -> ToolResult[PolicySelectionResult]:
        """
        Select a policy using UCB algorithm.

        Args:
            experiment_type: Type of experiment (ad_creative, landing_page, etc.)
            force_exploration: If True, always use exploration

        Returns:
            ToolResult containing the selected policy and metadata
        """
        try:
            # Check if bandit is enabled
            if not self.config.get('global', {}).get('bandit_enabled', True):
                return ToolResult.success(
                    data=PolicySelectionResult(
                        selected_policy=PolicyVersion.YAML_BASELINE,
                        selection_reason="Bandit disabled, using default policy",
                        exploration_used=False,
                    )
                )

            # Get weights from database
            weights = self._get_policy_weights(experiment_type)

            # Check minimum samples
            min_samples = self.config.get('global', {}).get('min_samples_for_selection', 10)
            total_samples = sum(w.sample_count for w in weights.values())

            if total_samples < min_samples or force_exploration:
                # Not enough data, use exploration (random or round-robin)
                selected = self._exploration_selection(weights)
                return ToolResult.success(
                    data=PolicySelectionResult(
                        selected_policy=selected,
                        selection_reason=f"Exploration mode: {total_samples} samples < {min_samples} minimum",
                        weights={k: v for k, v in weights.items()},
                        exploration_used=True,
                    )
                )

            # Use UCB for selection
            selected, reason = self._ucb_selection(weights)

            return ToolResult.success(
                data=PolicySelectionResult(
                    selected_policy=selected,
                    selection_reason=reason,
                    weights={k: v for k, v in weights.items()},
                    exploration_used=False,
                )
            )

        except Exception as e:
            # Fall back to default policy on error
            return ToolResult.failure(
                message=f"Policy selection failed: {str(e)}",
                code="BANDIT_ERROR",
                fallback_policy=PolicyVersion.YAML_BASELINE.value,
            )

    def _get_policy_weights(self, experiment_type: str) -> Dict[str, PolicyWeight]:
        """
        Get policy weights from database.

        Uses the get_policy_weights SQL function created in migration 004.
        """
        weights = {}

        # Initialize with prior weights
        for policy_name, policy_config in self.config.get('policies', {}).items():
            try:
                policy_version = PolicyVersion(policy_name)
            except ValueError:
                continue

            weights[policy_name] = PolicyWeight(
                policy_version=policy_version,
                mean_reward=policy_config.get('prior_weight', 0.5),
                sample_count=0,
            )

        # Try to get actual weights from database
        try:
            exploration_bonus = self.config.get('global', {}).get('exploration_bonus', 0.1)
            min_samples = self.config.get('global', {}).get('min_samples_for_selection', 10)

            result = self.supabase.rpc(
                'get_policy_weights',
                {
                    'p_experiment_type': experiment_type,
                    'p_min_samples': min_samples,
                    'p_exploration_bonus': exploration_bonus,
                }
            ).execute()

            if result.data:
                for row in result.data:
                    policy_name = row['policy_version']
                    if policy_name in weights:
                        weights[policy_name] = PolicyWeight(
                            policy_version=PolicyVersion(policy_name),
                            sample_count=row['sample_count'],
                            mean_reward=row['mean_reward'] or 0.0,
                            ucb_score=row['ucb_score'] or 0.0,
                            last_updated=datetime.now(),
                        )

        except Exception as e:
            # Log but don't fail - use prior weights
            print(f"Warning: Could not fetch policy weights from DB: {e}")

        return weights

    def _ucb_selection(
        self,
        weights: Dict[str, PolicyWeight]
    ) -> Tuple[PolicyVersion, str]:
        """
        Select policy using Upper Confidence Bound algorithm.

        UCB balances exploitation (high mean reward) with exploration
        (policies with fewer samples get a bonus).
        """
        best_policy = None
        best_score = float('-inf')
        reason_parts = []

        total_samples = sum(w.sample_count for w in weights.values())
        exploration_bonus = self.config.get('global', {}).get('exploration_bonus', 0.1)

        for policy_name, weight in weights.items():
            # Calculate UCB score
            if weight.sample_count > 0:
                # UCB1 formula: mean + c * sqrt(ln(n) / n_i)
                exploration_term = exploration_bonus * math.sqrt(
                    math.log(max(total_samples, 1)) / max(weight.sample_count, 1)
                )
                ucb_score = weight.mean_reward + exploration_term
            else:
                # Unseen policy gets maximum exploration bonus
                ucb_score = 1.0 + exploration_bonus

            reason_parts.append(
                f"{policy_name}: UCB={ucb_score:.3f} (mean={weight.mean_reward:.3f}, n={weight.sample_count})"
            )

            if ucb_score > best_score:
                best_score = ucb_score
                best_policy = weight.policy_version

        reason = f"UCB selection: {' | '.join(reason_parts)}"
        return best_policy or PolicyVersion.YAML_BASELINE, reason

    def _exploration_selection(
        self,
        weights: Dict[str, PolicyWeight]
    ) -> PolicyVersion:
        """
        Select policy in exploration mode.

        Uses round-robin based on sample counts to ensure even coverage.
        """
        # Find policy with fewest samples
        min_samples = float('inf')
        selected = PolicyVersion.YAML_BASELINE

        for policy_name, weight in weights.items():
            if weight.sample_count < min_samples:
                min_samples = weight.sample_count
                selected = weight.policy_version

        return selected

    def record_outcome(
        self,
        project_id: str,
        experiment_id: str,
        experiment_type: str,
        policy_version: PolicyVersion,
        primary_metric: str,
        primary_value: float,
        config_snapshot: Dict[str, Any],
        secondary_metrics: Optional[Dict[str, float]] = None,
    ) -> ToolResult[str]:
        """
        Record an experiment outcome for bandit learning.

        Args:
            project_id: Project identifier
            experiment_id: Unique experiment identifier
            experiment_type: Type of experiment
            policy_version: Policy used for this experiment
            primary_metric: Name of primary metric
            primary_value: Value of primary metric
            config_snapshot: Configuration used for experiment
            secondary_metrics: Optional additional metrics

        Returns:
            ToolResult with the outcome record ID
        """
        try:
            record = {
                'project_id': project_id,
                'experiment_id': experiment_id,
                'experiment_type': experiment_type,
                'policy_version': policy_version.value,
                'config_source': policy_version.value,
                'config_snapshot': config_snapshot,
                'primary_metric': primary_metric,
                'primary_value': primary_value,
                'secondary_metrics': secondary_metrics or {},
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
            }

            result = self.supabase.table('experiment_outcomes').insert(record).execute()

            return ToolResult.success(
                data=result.data[0]['id'] if result.data else 'unknown',
                experiment_type=experiment_type,
                policy_version=policy_version.value,
            )

        except Exception as e:
            return ToolResult.failure(
                message=f"Failed to record outcome: {str(e)}",
                code="OUTCOME_RECORD_ERROR",
            )

    def get_policy_performance(
        self,
        experiment_type: Optional[str] = None,
    ) -> ToolResult[Dict[str, Any]]:
        """
        Get policy performance summary for analysis.

        Args:
            experiment_type: Optional filter by experiment type

        Returns:
            ToolResult with performance summary data
        """
        try:
            query = self.supabase.from_('policy_performance_summary').select('*')

            if experiment_type:
                query = query.eq('experiment_type', experiment_type)

            result = query.execute()

            return ToolResult.success(
                data={
                    'summary': result.data,
                    'generated_at': datetime.now().isoformat(),
                }
            )

        except Exception as e:
            return ToolResult.failure(
                message=f"Failed to get performance data: {str(e)}",
                code="PERFORMANCE_QUERY_ERROR",
            )


# Convenience functions for use in flows

def select_experiment_policy(
    experiment_type: str,
    force_exploration: bool = False,
) -> Tuple[PolicyVersion, str]:
    """
    Convenience function to select a policy for an experiment.

    Returns:
        Tuple of (selected_policy, selection_reason)
    """
    bandit = PolicyBandit()
    result = bandit.select_policy(experiment_type, force_exploration)

    if result.is_usable:
        return result.data.selected_policy, result.data.selection_reason
    else:
        # Fallback to default
        return PolicyVersion.YAML_BASELINE, f"Fallback: {result.error_message}"


def record_experiment_outcome(
    project_id: str,
    experiment_id: str,
    experiment_type: str,
    policy_version: PolicyVersion,
    primary_metric: str,
    primary_value: float,
    config_snapshot: Dict[str, Any],
    secondary_metrics: Optional[Dict[str, float]] = None,
) -> bool:
    """
    Convenience function to record an experiment outcome.

    Returns:
        True if recorded successfully, False otherwise
    """
    bandit = PolicyBandit()
    result = bandit.record_outcome(
        project_id=project_id,
        experiment_id=experiment_id,
        experiment_type=experiment_type,
        policy_version=policy_version,
        primary_metric=primary_metric,
        primary_value=primary_value,
        config_snapshot=config_snapshot,
        secondary_metrics=secondary_metrics,
    )
    return result.is_success
