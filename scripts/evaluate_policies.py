#!/usr/bin/env python3
"""
Offline Policy Evaluation Script.

Evaluates policy performance from experiment outcomes data and generates
reports for A/B testing analysis.

Area 3 Implementation: Policy Versioning - Offline Evaluation

Usage:
    python scripts/evaluate_policies.py
    python scripts/evaluate_policies.py --experiment-type ad_creative
    python scripts/evaluate_policies.py --output reports/policy_eval.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from startupai.persistence.connection import get_supabase_client
from startupai.flows.state_schemas import PolicyVersion


def get_experiment_outcomes(
    experiment_type: Optional[str] = None,
    days_back: int = 30,
) -> List[Dict[str, Any]]:
    """
    Fetch experiment outcomes from database.

    Args:
        experiment_type: Optional filter by experiment type
        days_back: Number of days to look back

    Returns:
        List of experiment outcome records
    """
    client = get_supabase_client()

    cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()

    query = client.table('experiment_outcomes') \
        .select('*') \
        .eq('status', 'completed') \
        .gte('created_at', cutoff_date)

    if experiment_type:
        query = query.eq('experiment_type', experiment_type)

    result = query.execute()
    return result.data if result.data else []


def calculate_policy_stats(outcomes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Calculate statistics for each policy.

    Args:
        outcomes: List of experiment outcomes

    Returns:
        Dict mapping policy_version to statistics
    """
    from collections import defaultdict
    import statistics

    policy_data = defaultdict(list)

    for outcome in outcomes:
        policy = outcome.get('policy_version', 'unknown')
        value = outcome.get('primary_value')
        if value is not None:
            policy_data[policy].append(value)

    stats = {}
    for policy, values in policy_data.items():
        if len(values) >= 2:
            stats[policy] = {
                'count': len(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
            }
        elif len(values) == 1:
            stats[policy] = {
                'count': 1,
                'mean': values[0],
                'median': values[0],
                'stdev': 0,
                'min': values[0],
                'max': values[0],
            }

    return stats


def calculate_statistical_significance(
    stats: Dict[str, Dict[str, Any]],
    baseline: str = 'yaml_baseline',
    treatment: str = 'retrieval_v1',
) -> Dict[str, Any]:
    """
    Calculate statistical significance between policies.

    Uses a simple Z-test for comparing means.

    Args:
        stats: Policy statistics
        baseline: Baseline policy name
        treatment: Treatment policy name

    Returns:
        Dict with significance test results
    """
    import math

    if baseline not in stats or treatment not in stats:
        return {
            'can_compare': False,
            'reason': f"Missing data for {baseline} or {treatment}",
        }

    b_stats = stats[baseline]
    t_stats = stats[treatment]

    min_samples = 10
    if b_stats['count'] < min_samples or t_stats['count'] < min_samples:
        return {
            'can_compare': False,
            'reason': f"Insufficient samples (need {min_samples} each)",
            'baseline_count': b_stats['count'],
            'treatment_count': t_stats['count'],
        }

    # Calculate effect size (Cohen's d)
    pooled_std = math.sqrt(
        (b_stats['stdev']**2 + t_stats['stdev']**2) / 2
    )
    if pooled_std > 0:
        effect_size = (t_stats['mean'] - b_stats['mean']) / pooled_std
    else:
        effect_size = 0

    # Calculate Z-score
    se = math.sqrt(
        (b_stats['stdev']**2 / b_stats['count']) +
        (t_stats['stdev']**2 / t_stats['count'])
    )
    if se > 0:
        z_score = (t_stats['mean'] - b_stats['mean']) / se
    else:
        z_score = 0

    # Approximate p-value (two-tailed)
    # Using approximation: p ≈ 2 * exp(-0.5 * z^2) for large |z|
    p_value = 2 * math.exp(-0.5 * z_score**2) if abs(z_score) < 10 else 0

    return {
        'can_compare': True,
        'baseline_mean': b_stats['mean'],
        'treatment_mean': t_stats['mean'],
        'absolute_difference': t_stats['mean'] - b_stats['mean'],
        'relative_difference_pct': (
            (t_stats['mean'] - b_stats['mean']) / b_stats['mean'] * 100
            if b_stats['mean'] != 0 else 0
        ),
        'effect_size': effect_size,
        'effect_magnitude': (
            'large' if abs(effect_size) > 0.8 else
            'medium' if abs(effect_size) > 0.5 else
            'small' if abs(effect_size) > 0.2 else
            'negligible'
        ),
        'z_score': z_score,
        'p_value': p_value,
        'statistically_significant': p_value < 0.05,
        'winner': (
            treatment if t_stats['mean'] > b_stats['mean'] else
            baseline if b_stats['mean'] > t_stats['mean'] else
            'tie'
        ),
    }


def generate_report(
    experiment_type: Optional[str] = None,
    days_back: int = 30,
) -> Dict[str, Any]:
    """
    Generate full evaluation report.

    Args:
        experiment_type: Optional filter
        days_back: Days to analyze

    Returns:
        Full report dict
    """
    print(f"Fetching experiment outcomes (last {days_back} days)...")
    outcomes = get_experiment_outcomes(experiment_type, days_back)
    print(f"Found {len(outcomes)} completed experiments")

    if not outcomes:
        return {
            'status': 'no_data',
            'message': 'No experiment outcomes found',
            'generated_at': datetime.now().isoformat(),
        }

    # Group by experiment type
    by_type = {}
    for outcome in outcomes:
        exp_type = outcome.get('experiment_type', 'unknown')
        if exp_type not in by_type:
            by_type[exp_type] = []
        by_type[exp_type].append(outcome)

    report = {
        'status': 'success',
        'generated_at': datetime.now().isoformat(),
        'analysis_window_days': days_back,
        'total_experiments': len(outcomes),
        'by_experiment_type': {},
    }

    for exp_type, type_outcomes in by_type.items():
        print(f"\nAnalyzing {exp_type}: {len(type_outcomes)} experiments")
        stats = calculate_policy_stats(type_outcomes)
        significance = calculate_statistical_significance(stats)

        report['by_experiment_type'][exp_type] = {
            'experiment_count': len(type_outcomes),
            'policy_stats': stats,
            'significance_test': significance,
        }

    # Overall summary
    all_stats = calculate_policy_stats(outcomes)
    report['overall'] = {
        'policy_stats': all_stats,
        'significance_test': calculate_statistical_significance(all_stats),
    }

    # Recommendations
    report['recommendations'] = generate_recommendations(report)

    return report


def generate_recommendations(report: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations from report."""
    recs = []

    overall = report.get('overall', {})
    sig = overall.get('significance_test', {})

    if sig.get('can_compare'):
        if sig.get('statistically_significant'):
            winner = sig.get('winner')
            diff = sig.get('relative_difference_pct', 0)
            recs.append(
                f"SIGNIFICANT: {winner} outperforms by {abs(diff):.1f}%. "
                "Consider increasing weight for winning policy."
            )
        else:
            recs.append(
                "NOT SIGNIFICANT: Policies perform similarly. "
                "Continue data collection before making changes."
            )

        effect = sig.get('effect_magnitude')
        if effect in ('large', 'medium'):
            recs.append(
                f"Effect size is {effect}. The difference is practically meaningful."
            )
    else:
        reason = sig.get('reason', 'Unknown')
        recs.append(f"Cannot compare policies: {reason}")
        recs.append("Recommendation: Collect more experiment data.")

    # Check individual experiment types
    for exp_type, data in report.get('by_experiment_type', {}).items():
        type_sig = data.get('significance_test', {})
        if type_sig.get('can_compare') and type_sig.get('statistically_significant'):
            recs.append(
                f"{exp_type}: {type_sig.get('winner')} is significantly better "
                f"(effect size: {type_sig.get('effect_magnitude')})"
            )

    if not recs:
        recs.append("Insufficient data for recommendations. Continue experiments.")

    return recs


def print_report(report: Dict[str, Any]) -> None:
    """Pretty print the report to console."""
    print("\n" + "=" * 60)
    print("POLICY EVALUATION REPORT")
    print("=" * 60)

    print(f"\nGenerated: {report.get('generated_at')}")
    print(f"Analysis Window: {report.get('analysis_window_days')} days")
    print(f"Total Experiments: {report.get('total_experiments')}")

    # Overall stats
    overall = report.get('overall', {})
    print("\n--- OVERALL POLICY PERFORMANCE ---")
    for policy, stats in overall.get('policy_stats', {}).items():
        print(f"\n{policy}:")
        print(f"  Count: {stats.get('count')}")
        print(f"  Mean: {stats.get('mean', 0):.4f}")
        print(f"  Median: {stats.get('median', 0):.4f}")
        print(f"  Stdev: {stats.get('stdev', 0):.4f}")

    # Significance test
    sig = overall.get('significance_test', {})
    print("\n--- SIGNIFICANCE TEST ---")
    if sig.get('can_compare'):
        print(f"  Effect Size: {sig.get('effect_size', 0):.3f} ({sig.get('effect_magnitude')})")
        print(f"  Relative Difference: {sig.get('relative_difference_pct', 0):.2f}%")
        print(f"  P-value: {sig.get('p_value', 1):.4f}")
        print(f"  Statistically Significant: {'YES' if sig.get('statistically_significant') else 'NO'}")
        print(f"  Winner: {sig.get('winner')}")
    else:
        print(f"  Cannot compare: {sig.get('reason')}")

    # Per experiment type
    print("\n--- BY EXPERIMENT TYPE ---")
    for exp_type, data in report.get('by_experiment_type', {}).items():
        print(f"\n{exp_type} ({data.get('experiment_count')} experiments):")
        type_sig = data.get('significance_test', {})
        if type_sig.get('can_compare'):
            print(f"  Winner: {type_sig.get('winner')}")
            print(f"  Difference: {type_sig.get('relative_difference_pct', 0):.2f}%")
        else:
            print(f"  {type_sig.get('reason')}")

    # Recommendations
    print("\n--- RECOMMENDATIONS ---")
    for i, rec in enumerate(report.get('recommendations', []), 1):
        print(f"{i}. {rec}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate policy performance from experiment outcomes"
    )
    parser.add_argument(
        '--experiment-type',
        type=str,
        help='Filter by experiment type (ad_creative, landing_page, etc.)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to analyze (default: 30)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for JSON report'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON instead of formatted text'
    )

    args = parser.parse_args()

    try:
        report = generate_report(
            experiment_type=args.experiment_type,
            days_back=args.days,
        )

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_path}")

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_report(report)

    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
