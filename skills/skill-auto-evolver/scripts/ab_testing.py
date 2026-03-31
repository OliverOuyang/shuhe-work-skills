#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A/B Testing Framework

Provides A/B testing for comparing skill versions with
traffic routing, metrics collection, and winner determination.
"""

import json
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict


class ABTestManager:
    """Manager for A/B testing experiments."""

    def __init__(self):
        self.repo_root = Path.cwd()
        while not (self.repo_root / "package.json").exists() and self.repo_root != self.repo_root.parent:
            self.repo_root = self.repo_root.parent

        self.ab_tests_dir = self.repo_root / ".omc" / "evolution" / "ab_tests"
        self.ab_tests_dir.mkdir(parents=True, exist_ok=True)

    def create_experiment(self, skill_name: str, variant_a: str, variant_b: str,
                         traffic_split: str = "50:50") -> str:
        """
        Create a new A/B testing experiment.

        Args:
            skill_name: Name of the skill
            variant_a: Version A identifier
            variant_b: Version B identifier
            traffic_split: Traffic split ratio (e.g., "50:50", "80:20")

        Returns:
            Experiment ID
        """
        # Parse traffic split
        parts = traffic_split.split(':')
        if len(parts) != 2:
            raise ValueError("Traffic split must be in format 'A:B' (e.g., '50:50')")

        split_a = int(parts[0])
        split_b = int(parts[1])

        if split_a + split_b != 100:
            raise ValueError("Traffic split must sum to 100")

        # Generate experiment ID
        timestamp = int(datetime.now().timestamp())
        experiment_id = f"{skill_name}-{timestamp}"

        # Create experiment directory
        exp_dir = self.ab_tests_dir / experiment_id
        exp_dir.mkdir(exist_ok=True)

        # Create experiment config
        config = {
            "experiment_id": experiment_id,
            "skill_name": skill_name,
            "variant_a": variant_a,
            "variant_b": variant_b,
            "traffic_split": {
                "a": split_a,
                "b": split_b
            },
            "created_at": datetime.now().isoformat(),
            "status": "running",
            "metrics": {
                "variant_a": {
                    "executions": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_duration_ms": 0
                },
                "variant_b": {
                    "executions": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_duration_ms": 0
                }
            }
        }

        # Save config
        config_file = exp_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"[OK] Created A/B test experiment: {experiment_id}")
        print(f"     Variant A ({variant_a}): {split_a}% traffic")
        print(f"     Variant B ({variant_b}): {split_b}% traffic")

        return experiment_id

    def route_execution(self, skill_name: str, experiment_id: str,
                       execution_id: Optional[str] = None) -> str:
        """
        Route execution to a variant based on traffic split.

        Args:
            skill_name: Name of the skill
            experiment_id: Experiment ID
            execution_id: Optional execution ID for consistent routing

        Returns:
            Variant identifier ('a' or 'b')
        """
        # Load config
        exp_dir = self.ab_tests_dir / experiment_id
        config_file = exp_dir / "config.json"

        if not config_file.exists():
            raise ValueError(f"Experiment {experiment_id} not found")

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Hash-based deterministic routing
        if execution_id:
            hash_input = f"{experiment_id}:{execution_id}"
        else:
            hash_input = f"{experiment_id}:{datetime.now().timestamp()}"

        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = hash_value % 100

        # Route based on traffic split
        split_a = config['traffic_split']['a']

        if bucket < split_a:
            return 'a'
        else:
            return 'b'

    def collect_metrics(self, experiment_id: str, variant: str,
                       success: bool, duration_ms: int):
        """
        Collect metrics for an experiment execution.

        Args:
            experiment_id: Experiment ID
            variant: Variant identifier ('a' or 'b')
            success: Whether execution succeeded
            duration_ms: Execution duration in milliseconds
        """
        exp_dir = self.ab_tests_dir / experiment_id
        config_file = exp_dir / "config.json"

        if not config_file.exists():
            raise ValueError(f"Experiment {experiment_id} not found")

        # Load config
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Update metrics
        variant_key = f"variant_{variant}"
        metrics = config['metrics'][variant_key]

        metrics['executions'] += 1
        if success:
            metrics['successes'] += 1
        else:
            metrics['failures'] += 1
        metrics['total_duration_ms'] += duration_ms

        # Save updated config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def get_experiment_status(self, experiment_id: str) -> Dict:
        """
        Get current status and metrics for an experiment.

        Args:
            experiment_id: Experiment ID

        Returns:
            Dictionary with experiment status
        """
        exp_dir = self.ab_tests_dir / experiment_id
        config_file = exp_dir / "config.json"

        if not config_file.exists():
            return {"error": f"Experiment {experiment_id} not found"}

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Calculate derived metrics
        for variant_key in ['variant_a', 'variant_b']:
            metrics = config['metrics'][variant_key]
            if metrics['executions'] > 0:
                metrics['success_rate'] = (metrics['successes'] / metrics['executions']) * 100
                metrics['avg_duration_ms'] = metrics['total_duration_ms'] / metrics['executions']
            else:
                metrics['success_rate'] = 0
                metrics['avg_duration_ms'] = 0

        return config

    def determine_winner(self, experiment_id: str, confidence_threshold: float = 0.95) -> Dict:
        """
        Determine the winning variant with statistical significance.

        Args:
            experiment_id: Experiment ID
            confidence_threshold: Confidence threshold (default 0.95 = 95%)

        Returns:
            Dictionary with winner determination results
        """
        status = self.get_experiment_status(experiment_id)

        if 'error' in status:
            return status

        metrics_a = status['metrics']['variant_a']
        metrics_b = status['metrics']['variant_b']

        # Check minimum sample size
        min_samples = 30
        if metrics_a['executions'] < min_samples or metrics_b['executions'] < min_samples:
            return {
                "experiment_id": experiment_id,
                "winner": None,
                "reason": f"Insufficient samples (need {min_samples}, have {metrics_a['executions']} and {metrics_b['executions']})",
                "recommendation": "Continue running experiment"
            }

        # Simple comparison (in real implementation, use chi-square test)
        success_rate_a = metrics_a.get('success_rate', 0)
        success_rate_b = metrics_b.get('success_rate', 0)
        avg_duration_a = metrics_a.get('avg_duration_ms', 0)
        avg_duration_b = metrics_b.get('avg_duration_ms', 0)

        # Calculate scores (higher is better)
        score_a = success_rate_a - (avg_duration_a / 1000)  # Penalize latency
        score_b = success_rate_b - (avg_duration_b / 1000)

        diff_threshold = 5.0  # 5% difference threshold

        if abs(score_a - score_b) < diff_threshold:
            winner = None
            reason = "No statistically significant difference"
        elif score_a > score_b:
            winner = "a"
            reason = f"Variant A performs better (score: {score_a:.2f} vs {score_b:.2f})"
        else:
            winner = "b"
            reason = f"Variant B performs better (score: {score_b:.2f} vs {score_a:.2f})"

        return {
            "experiment_id": experiment_id,
            "winner": winner,
            "reason": reason,
            "metrics": {
                "variant_a": {
                    "success_rate": success_rate_a,
                    "avg_duration_ms": avg_duration_a,
                    "score": score_a
                },
                "variant_b": {
                    "success_rate": success_rate_b,
                    "avg_duration_ms": avg_duration_b,
                    "score": score_b
                }
            },
            "note": "Statistical significance testing requires scipy library for chi-square test"
        }

    def promote_winner(self, experiment_id: str) -> bool:
        """
        Promote the winning variant and stop the experiment.

        Args:
            experiment_id: Experiment ID

        Returns:
            True if promotion succeeded
        """
        winner_result = self.determine_winner(experiment_id)

        if 'error' in winner_result:
            print(f"[ERROR] {winner_result['error']}")
            return False

        winner = winner_result.get('winner')
        if not winner:
            print(f"[WARNING] No clear winner: {winner_result['reason']}")
            return False

        # Load config
        exp_dir = self.ab_tests_dir / experiment_id
        config_file = exp_dir / "config.json"

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Mark as completed
        config['status'] = 'completed'
        config['winner'] = winner
        config['completed_at'] = datetime.now().isoformat()
        config['winner_result'] = winner_result

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        winning_variant = config[f'variant_{winner}']
        print(f"[OK] Promoted variant {winner.upper()} ({winning_variant}) as winner")
        print(f"     Reason: {winner_result['reason']}")

        return True


def main():
    """CLI entry point for testing."""
    if len(sys.argv) < 2:
        print("Usage: python ab_testing.py <create|route|status|winner|promote> [args]")
        sys.exit(1)

    manager = ABTestManager()
    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 5:
            print("Usage: python ab_testing.py create <skill> <variant_a> <variant_b> [split]")
            sys.exit(1)

        skill_name = sys.argv[2]
        variant_a = sys.argv[3]
        variant_b = sys.argv[4]
        traffic_split = sys.argv[5] if len(sys.argv) > 5 else "50:50"

        experiment_id = manager.create_experiment(skill_name, variant_a, variant_b, traffic_split)
        print(f"\nExperiment ID: {experiment_id}")

    elif command == "status":
        if len(sys.argv) < 3:
            print("Usage: python ab_testing.py status <experiment_id>")
            sys.exit(1)

        experiment_id = sys.argv[2]
        status = manager.get_experiment_status(experiment_id)

        if 'error' in status:
            print(f"[ERROR] {status['error']}")
            sys.exit(1)

        print(f"\n=== Experiment Status ===\n")
        print(f"ID: {status['experiment_id']}")
        print(f"Skill: {status['skill_name']}")
        print(f"Status: {status['status']}")

        for variant in ['a', 'b']:
            variant_key = f'variant_{variant}'
            metrics = status['metrics'][variant_key]
            variant_name = status[variant_key]

            print(f"\nVariant {variant.upper()} ({variant_name}):")
            print(f"  Executions: {metrics['executions']}")
            print(f"  Success Rate: {metrics.get('success_rate', 0):.1f}%")
            print(f"  Avg Duration: {metrics.get('avg_duration_ms', 0):.0f}ms")

    elif command == "winner":
        if len(sys.argv) < 3:
            print("Usage: python ab_testing.py winner <experiment_id>")
            sys.exit(1)

        experiment_id = sys.argv[2]
        result = manager.determine_winner(experiment_id)

        if 'error' in result:
            print(f"[ERROR] {result['error']}")
            sys.exit(1)

        print(f"\n=== Winner Determination ===\n")
        print(f"Experiment: {result['experiment_id']}")
        print(f"Winner: {result['winner'] if result['winner'] else 'None'}")
        print(f"Reason: {result['reason']}")

        if 'note' in result:
            print(f"\nNote: {result['note']}")

    elif command == "promote":
        if len(sys.argv) < 3:
            print("Usage: python ab_testing.py promote <experiment_id>")
            sys.exit(1)

        experiment_id = sys.argv[2]
        success = manager.promote_winner(experiment_id)
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
