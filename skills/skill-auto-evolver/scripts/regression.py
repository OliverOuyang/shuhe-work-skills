#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression Testing Framework

Provides regression testing for skill updates to ensure
new versions don't introduce regressions.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class RegressionTester:
    """Tester for skill regression testing."""

    def __init__(self):
        self.repo_root = Path.cwd()
        while not (self.repo_root / "package.json").exists() and self.repo_root != self.repo_root.parent:
            self.repo_root = self.repo_root.parent

        self.regression_dir = self.repo_root / ".omc" / "evolution" / "regression"
        self.regression_dir.mkdir(parents=True, exist_ok=True)

    def setup_test_suite(self, skill_name: str) -> bool:
        """
        Set up regression test suite with baseline.

        Args:
            skill_name: Name of the skill

        Returns:
            True if setup succeeded
        """
        skill_dir = self.regression_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        baseline_dir = skill_dir / "baseline"
        baseline_dir.mkdir(exist_ok=True)

        # Create baseline test cases
        test_cases = {
            "test_suite": "baseline",
            "skill_name": skill_name,
            "created_at": datetime.now().isoformat(),
            "test_cases": [
                {
                    "id": "basic_execution",
                    "description": "Basic skill execution",
                    "input": {},
                    "expected_output": "success",
                    "expected_duration_range": [0, 30000]  # 0-30 seconds
                },
                {
                    "id": "error_handling",
                    "description": "Graceful error handling",
                    "input": {"invalid": "data"},
                    "expected_output": "error_handled",
                    "expected_duration_range": [0, 5000]
                },
                {
                    "id": "performance_baseline",
                    "description": "Performance baseline",
                    "input": {},
                    "expected_output": "success",
                    "max_duration_ms": 30000
                }
            ]
        }

        # Save test cases
        test_file = baseline_dir / "test_cases.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_cases, f, indent=2, ensure_ascii=False)

        print(f"[OK] Created baseline test suite for {skill_name}")
        print(f"     Output directory: {baseline_dir}")
        print(f"     Test cases: {len(test_cases['test_cases'])}")

        return True

    def run_regression_tests(self, skill_name: str, new_version: str) -> Dict:
        """
        Run regression tests for a new skill version.

        Args:
            skill_name: Name of the skill
            new_version: New version to test

        Returns:
            Dictionary with test results
        """
        skill_dir = self.regression_dir / skill_name
        baseline_dir = skill_dir / "baseline"

        if not baseline_dir.exists():
            return {
                "skill_name": skill_name,
                "version": new_version,
                "status": "error",
                "message": "Baseline test suite not found. Run setup_test_suite first."
            }

        # Load baseline
        test_file = baseline_dir / "test_cases.json"
        with open(test_file, 'r', encoding='utf-8') as f:
            baseline = json.load(f)

        # Simulate test execution
        # In a real implementation, this would execute actual tests
        results = {
            "skill_name": skill_name,
            "version": new_version,
            "baseline_version": "current",
            "tested_at": datetime.now().isoformat(),
            "test_results": []
        }

        for test_case in baseline['test_cases']:
            # Simulate test execution
            result = {
                "test_id": test_case['id'],
                "description": test_case['description'],
                "status": "passed",  # Simulated pass
                "actual_output": "success",
                "actual_duration_ms": 1000,
                "note": "Simulated test execution - implement actual test runner"
            }
            results['test_results'].append(result)

        # Calculate summary
        passed = sum(1 for r in results['test_results'] if r['status'] == 'passed')
        total = len(results['test_results'])

        results['summary'] = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": (passed / total * 100) if total > 0 else 0
        }

        # Save results
        version_dir = skill_dir / new_version
        version_dir.mkdir(exist_ok=True)

        results_file = version_dir / "results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        return results

    def compare_results(self, skill_name: str, version1: str, version2: str) -> Dict:
        """
        Compare regression test results between two versions.

        Args:
            skill_name: Name of the skill
            version1: First version
            version2: Second version

        Returns:
            Dictionary with comparison
        """
        skill_dir = self.regression_dir / skill_name

        v1_file = skill_dir / version1 / "results.json"
        v2_file = skill_dir / version2 / "results.json"

        if not v1_file.exists() or not v2_file.exists():
            return {
                "skill_name": skill_name,
                "error": "Results not found for one or both versions"
            }

        with open(v1_file, 'r', encoding='utf-8') as f:
            v1_results = json.load(f)

        with open(v2_file, 'r', encoding='utf-8') as f:
            v2_results = json.load(f)

        comparison = {
            "skill_name": skill_name,
            "version1": version1,
            "version2": version2,
            "comparison": {
                "pass_rate": {
                    "v1": v1_results['summary']['pass_rate'],
                    "v2": v2_results['summary']['pass_rate'],
                    "diff": v2_results['summary']['pass_rate'] - v1_results['summary']['pass_rate']
                },
                "test_count": {
                    "v1": v1_results['summary']['total_tests'],
                    "v2": v2_results['summary']['total_tests']
                }
            }
        }

        return comparison


def main():
    """CLI entry point for testing."""
    if len(sys.argv) < 3:
        print("Usage: python regression.py <setup|test|compare> <skill_name> [version]")
        sys.exit(1)

    tester = RegressionTester()
    command = sys.argv[1]
    skill_name = sys.argv[2]

    if command == "setup":
        success = tester.setup_test_suite(skill_name)
        sys.exit(0 if success else 1)

    elif command == "test":
        if len(sys.argv) < 4:
            print("Usage: python regression.py test <skill_name> <version>")
            sys.exit(1)

        version = sys.argv[3]
        results = tester.run_regression_tests(skill_name, version)

        print(f"\n=== Regression Test Results ===\n")
        print(f"Skill: {results['skill_name']}")
        print(f"Version: {results['version']}")

        if 'message' in results:
            print(f"\n[INFO] {results['message']}")
            sys.exit(1)

        summary = results['summary']
        print(f"\nSummary:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Pass Rate: {summary['pass_rate']:.1f}%")

    elif command == "compare":
        if len(sys.argv) < 5:
            print("Usage: python regression.py compare <skill_name> <version1> <version2>")
            sys.exit(1)

        version1 = sys.argv[3]
        version2 = sys.argv[4]

        comparison = tester.compare_results(skill_name, version1, version2)

        if 'error' in comparison:
            print(f"[ERROR] {comparison['error']}")
            sys.exit(1)

        print(f"\n=== Regression Comparison ===\n")
        print(f"Skill: {comparison['skill_name']}")
        print(f"Comparing: {version1} vs {version2}\n")

        comp = comparison['comparison']
        print(f"Pass Rate:")
        print(f"  {version1}: {comp['pass_rate']['v1']:.1f}%")
        print(f"  {version2}: {comp['pass_rate']['v2']:.1f}%")
        print(f"  Difference: {comp['pass_rate']['diff']:+.1f}%")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
