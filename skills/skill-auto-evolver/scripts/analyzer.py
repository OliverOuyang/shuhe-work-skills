#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Analyzer

Identifies performance bottlenecks and provides detailed analysis
of skill execution patterns.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

try:
    from data_collector import DataCollector
    HAS_DATA_COLLECTOR = True
except ImportError:
    HAS_DATA_COLLECTOR = False


class PerformanceAnalyzer:
    """Analyzer for skill performance and bottleneck identification."""

    def __init__(self):
        if HAS_DATA_COLLECTOR:
            self.collector = DataCollector()
        else:
            self.collector = None

    def analyze_bottlenecks(self, skill_name: str, window_days: int = 30) -> Dict:
        """
        Identify performance bottlenecks in a skill.

        Args:
            skill_name: Name of the skill to analyze
            window_days: Number of days to analyze

        Returns:
            Dictionary with bottleneck analysis
        """
        if not self.collector:
            return {
                "skill_name": skill_name,
                "bottlenecks": [],
                "error": "Data collector not available"
            }

        # Get execution history
        history = self.collector.get_execution_history(skill_name, limit=1000)

        if not history:
            return {
                "skill_name": skill_name,
                "bottlenecks": [],
                "message": "No execution history available"
            }

        # Get metrics
        metrics = self.collector.calculate_metrics(skill_name, window_days)

        bottlenecks = []

        # Analyze error patterns
        error_patterns = defaultdict(int)
        for record in history:
            if not record['success'] and record['error']:
                # Extract error type
                error_msg = record['error']
                error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg[:50]
                error_patterns[error_type] += 1

        if error_patterns:
            most_common_error = max(error_patterns.items(), key=lambda x: x[1])
            bottlenecks.append({
                "type": "error_pattern",
                "severity": "high",
                "description": f"Most common error: {most_common_error[0]}",
                "frequency": most_common_error[1],
                "total_errors": sum(error_patterns.values()),
                "recommendation": "Focus on fixing this error pattern first"
            })

        # Analyze latency distribution
        durations = [r['duration_ms'] for r in history if r['success']]
        if durations:
            avg = sum(durations) / len(durations)
            slow_executions = [d for d in durations if d > avg * 3]

            if len(slow_executions) > len(durations) * 0.05:  # More than 5% are slow
                bottlenecks.append({
                    "type": "latency_spike",
                    "severity": "medium",
                    "description": f"{len(slow_executions)} executions are 3x slower than average",
                    "slow_count": len(slow_executions),
                    "total_count": len(durations),
                    "recommendation": "Investigate slow execution paths"
                })

        # Analyze resource usage patterns
        if metrics['avg_duration_ms'] > 10000:  # > 10 seconds
            bottlenecks.append({
                "type": "resource_intensive",
                "severity": "medium",
                "description": f"Average execution time is {metrics['avg_duration_ms']/1000:.1f} seconds",
                "recommendation": "Consider optimization or async execution"
            })

        return {
            "skill_name": skill_name,
            "metrics": metrics,
            "bottlenecks": bottlenecks,
            "error_patterns": dict(error_patterns)
        }

    def compare_versions(self, skill_name: str, version1: str, version2: str) -> Dict:
        """
        Compare performance between two skill versions.

        Args:
            skill_name: Name of the skill
            version1: First version to compare
            version2: Second version to compare

        Returns:
            Dictionary with comparison results
        """
        # For now, simulate version comparison
        # In a real implementation, this would query actual version-specific metrics

        comparison = {
            "skill_name": skill_name,
            "version1": version1,
            "version2": version2,
            "comparison": {
                "success_rate": {
                    "v1": "N/A",
                    "v2": "N/A",
                    "diff": "N/A",
                    "note": "Version-specific metrics not yet implemented"
                },
                "avg_latency": {
                    "v1": "N/A",
                    "v2": "N/A",
                    "diff": "N/A",
                    "note": "Version-specific metrics not yet implemented"
                },
                "error_rate": {
                    "v1": "N/A",
                    "v2": "N/A",
                    "diff": "N/A",
                    "note": "Version-specific metrics not yet implemented"
                }
            },
            "recommendation": "Implement version tagging in data_collector to enable version comparison"
        }

        return comparison


def main():
    """CLI entry point for testing."""
    if len(sys.argv) < 3:
        print("Usage: python analyzer.py <analyze|compare> <skill_name> [v1 v2]")
        sys.exit(1)

    analyzer = PerformanceAnalyzer()
    command = sys.argv[1]
    skill_name = sys.argv[2]

    if command == "analyze":
        analysis = analyzer.analyze_bottlenecks(skill_name)

        print(f"\n=== Performance Analysis for '{skill_name}' ===\n")

        if 'error' in analysis:
            print(f"[ERROR] {analysis['error']}")
            sys.exit(1)

        if 'message' in analysis:
            print(f"[INFO] {analysis['message']}")
            sys.exit(0)

        metrics = analysis.get('metrics', {})
        print(f"Performance Metrics:")
        print(f"  Success Rate: {metrics.get('success_rate', 0):.1f}%")
        print(f"  Avg Duration: {metrics.get('avg_duration_ms', 0):.0f}ms")
        print(f"  P50 Duration: {metrics.get('p50_duration_ms', 0):.0f}ms")
        print(f"  P95 Duration: {metrics.get('p95_duration_ms', 0):.0f}ms")
        print(f"  P99 Duration: {metrics.get('p99_duration_ms', 0):.0f}ms")

        bottlenecks = analysis.get('bottlenecks', [])
        if bottlenecks:
            print(f"\nBottlenecks Found ({len(bottlenecks)}):\n")
            for i, bottleneck in enumerate(bottlenecks, 1):
                print(f"{i}. [{bottleneck['severity'].upper()}] {bottleneck['type']}")
                print(f"   {bottleneck['description']}")
                print(f"   Recommendation: {bottleneck['recommendation']}\n")
        else:
            print("\n[OK] No bottlenecks detected")

        error_patterns = analysis.get('error_patterns', {})
        if error_patterns:
            print(f"\nError Patterns ({len(error_patterns)} unique):")
            for error_type, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {count}x: {error_type}")

    elif command == "compare":
        if len(sys.argv) < 5:
            print("Usage: python analyzer.py compare <skill_name> <version1> <version2>")
            sys.exit(1)

        version1 = sys.argv[3]
        version2 = sys.argv[4]

        comparison = analyzer.compare_versions(skill_name, version1, version2)

        print(f"\n=== Version Comparison for '{skill_name}' ===\n")
        print(f"Comparing: {version1} vs {version2}\n")

        comp_data = comparison['comparison']
        for metric, values in comp_data.items():
            print(f"{metric}:")
            print(f"  {version1}: {values['v1']}")
            print(f"  {version2}: {values['v2']}")
            print(f"  Difference: {values['diff']}")
            if 'note' in values:
                print(f"  Note: {values['note']}")
            print()

        print(f"Recommendation: {comparison['recommendation']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
