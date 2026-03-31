#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Optimizer

Analyzes skill execution patterns and generates optimized versions
based on performance metrics and usage patterns.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

try:
    from data_collector import DataCollector
    HAS_DATA_COLLECTOR = True
except ImportError:
    HAS_DATA_COLLECTOR = False


class SkillOptimizer:
    """Optimizer for generating improved skill versions."""

    def __init__(self):
        self.repo_root = Path.cwd()
        while not (self.repo_root / "package.json").exists() and self.repo_root != self.repo_root.parent:
            self.repo_root = self.repo_root.parent

        self.optimized_dir = self.repo_root / ".omc" / "evolution" / "optimized"
        self.optimized_dir.mkdir(parents=True, exist_ok=True)

        if HAS_DATA_COLLECTOR:
            self.collector = DataCollector()
        else:
            self.collector = None

    def analyze_skill(self, skill_name: str, window_days: int = 30) -> Dict:
        """
        Analyze a skill and identify optimization opportunities.

        Args:
            skill_name: Name of the skill to analyze
            window_days: Number of days to analyze

        Returns:
            Dictionary with optimization recommendations
        """
        if not self.collector:
            return {
                "skill_name": skill_name,
                "opportunities": [],
                "error": "Data collector not available"
            }

        # Get metrics
        metrics = self.collector.calculate_metrics(skill_name, window_days)

        if not metrics:
            return {
                "skill_name": skill_name,
                "opportunities": [],
                "message": "No execution data available"
            }

        opportunities = []

        # Analyze success rate
        if metrics['success_rate'] < 90:
            opportunities.append({
                "type": "error_handling",
                "severity": "high",
                "description": f"Success rate is {metrics['success_rate']:.1f}%, below 90% threshold",
                "recommendation": "Add better error handling and retry logic",
                "impact": "Improve reliability"
            })

        # Analyze latency
        p95 = metrics.get('p95_duration_ms', 0)
        avg = metrics.get('avg_duration_ms', 0)

        if p95 > avg * 2:
            opportunities.append({
                "type": "performance",
                "severity": "medium",
                "description": f"P95 latency ({p95:.0f}ms) is 2x higher than average ({avg:.0f}ms)",
                "recommendation": "Add caching or optimize slow paths",
                "impact": "Reduce tail latency"
            })

        if avg > 5000:
            opportunities.append({
                "type": "optimization",
                "severity": "medium",
                "description": f"Average execution time ({avg:.0f}ms) exceeds 5 seconds",
                "recommendation": "Consider parallel execution or async operations",
                "impact": "Faster execution"
            })

        # Analyze execution patterns
        total_execs = metrics.get('total_executions', 0)
        if total_execs > 100 and avg > 1000:
            opportunities.append({
                "type": "caching",
                "severity": "low",
                "description": f"Frequently used skill ({total_execs} executions) with high latency",
                "recommendation": "Implement result caching",
                "impact": "Reduce repeated work"
            })

        return {
            "skill_name": skill_name,
            "metrics": metrics,
            "opportunities": opportunities,
            "analyzed_at": datetime.now().isoformat()
        }

    def generate_optimized_version(self, skill_name: str, version: str) -> bool:
        """
        Generate an optimized version of a skill.

        Args:
            skill_name: Name of the skill
            version: Version string for the optimized version

        Returns:
            True if generation succeeded
        """
        # Analyze first
        analysis = self.analyze_skill(skill_name)

        if not analysis.get('opportunities'):
            print(f"[INFO] No optimization opportunities found for {skill_name}")
            return False

        # Create version directory
        version_dir = self.optimized_dir / skill_name / f"v{version}"
        version_dir.mkdir(parents=True, exist_ok=True)

        # Save analysis
        analysis_file = version_dir / "analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        # Generate optimization plan
        plan = {
            "skill_name": skill_name,
            "version": version,
            "base_version": "current",
            "optimizations": [],
            "created_at": datetime.now().isoformat()
        }

        for opp in analysis['opportunities']:
            opt_type = opp['type']

            if opt_type == "error_handling":
                plan['optimizations'].append({
                    "type": "error_handling",
                    "changes": [
                        "Add try-catch blocks around risky operations",
                        "Implement exponential backoff retry logic",
                        "Add detailed error logging with context"
                    ]
                })

            elif opt_type == "performance":
                plan['optimizations'].append({
                    "type": "performance",
                    "changes": [
                        "Profile execution to identify bottlenecks",
                        "Add caching for repeated operations",
                        "Optimize data structures and algorithms"
                    ]
                })

            elif opt_type == "optimization":
                plan['optimizations'].append({
                    "type": "async_parallel",
                    "changes": [
                        "Convert synchronous operations to async",
                        "Parallelize independent operations",
                        "Use background tasks for non-critical work"
                    ]
                })

            elif opt_type == "caching":
                plan['optimizations'].append({
                    "type": "caching",
                    "changes": [
                        "Implement LRU cache for repeated queries",
                        "Add TTL-based cache invalidation",
                        "Cache intermediate computation results"
                    ]
                })

        # Save optimization plan
        plan_file = version_dir / "optimization_plan.json"
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)

        print(f"[OK] Generated optimization plan for {skill_name} v{version}")
        print(f"     Output directory: {version_dir}")
        print(f"     Found {len(plan['optimizations'])} optimization strategies")

        return True


def main():
    """CLI entry point for testing."""
    if len(sys.argv) < 3:
        print("Usage: python optimizer.py <analyze|generate> <skill_name> [version]")
        sys.exit(1)

    optimizer = SkillOptimizer()
    command = sys.argv[1]
    skill_name = sys.argv[2]

    if command == "analyze":
        analysis = optimizer.analyze_skill(skill_name)

        print(f"\n=== Optimization Analysis for '{skill_name}' ===\n")

        if 'error' in analysis:
            print(f"[ERROR] {analysis['error']}")
            sys.exit(1)

        if 'message' in analysis:
            print(f"[INFO] {analysis['message']}")
            sys.exit(0)

        metrics = analysis.get('metrics', {})
        print(f"Metrics (last 30 days):")
        print(f"  Executions: {metrics.get('total_executions', 0)}")
        print(f"  Success Rate: {metrics.get('success_rate', 0):.1f}%")
        print(f"  Avg Duration: {metrics.get('avg_duration_ms', 0):.0f}ms")
        print(f"  P95 Duration: {metrics.get('p95_duration_ms', 0):.0f}ms")

        opportunities = analysis.get('opportunities', [])
        if opportunities:
            print(f"\nOptimization Opportunities ({len(opportunities)}):\n")
            for i, opp in enumerate(opportunities, 1):
                print(f"{i}. [{opp['severity'].upper()}] {opp['type']}")
                print(f"   {opp['description']}")
                print(f"   Recommendation: {opp['recommendation']}")
                print(f"   Impact: {opp['impact']}\n")
        else:
            print("\n[OK] No optimization opportunities found")

    elif command == "generate":
        if len(sys.argv) < 4:
            print("Usage: python optimizer.py generate <skill_name> <version>")
            sys.exit(1)

        version = sys.argv[3]
        success = optimizer.generate_optimized_version(skill_name, version)
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
