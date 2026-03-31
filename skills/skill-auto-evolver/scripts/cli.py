#!/usr/bin/env python3
"""CLI for skill-auto-evolver - minimal viable implementation."""
import click
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from data_collector import DataCollector, ExecutionContext
    from optimizer import SkillOptimizer
    from analyzer import PerformanceAnalyzer
    from regression import RegressionTester
    from ab_testing import ABTestManager
    HAS_DATA_COLLECTOR = True
    HAS_FULL_FEATURES = True
except ImportError:
    HAS_DATA_COLLECTOR = False
    HAS_FULL_FEATURES = False
    SkillOptimizer = None
    PerformanceAnalyzer = None
    RegressionTester = None
    ABTestManager = None

@click.group()
def cli():
    """Skills Auto Evolver - analyze and optimize skill performance."""
    pass

@cli.command()
@click.argument('skill_name')
@click.option('--success/--failure', default=True, help='Execution succeeded or failed')
@click.option('--duration', type=int, required=True, help='Execution duration in ms')
@click.option('--error', default=None, help='Error message if failed')
def record(skill_name, success, duration, error):
    """Record a skill execution."""
    if not HAS_DATA_COLLECTOR:
        click.echo("Data collector module not available", err=True)
        sys.exit(1)
    
    try:
        collector = DataCollector()
        ctx = ExecutionContext(
            skill_name=skill_name,
            input_params={},
            output_result={},
            success=success,
            duration_ms=duration,
            error_trace=error
        )
        exec_id = collector.capture_execution(ctx)
        click.echo(f"✓ Recorded execution: {exec_id}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('skill_name')
@click.option('--days', default=30, help='Analysis window in days')
def metrics(skill_name, days):
    """Show performance metrics for a skill."""
    if not HAS_DATA_COLLECTOR:
        click.echo("Data collector module not available", err=True)
        sys.exit(1)
    
    try:
        collector = DataCollector()
        metrics = collector.calculate_metrics(skill_name, days)
        
        if metrics:
            print(f"\nPerformance Metrics for '{skill_name}' (last {days} days):\n")
            print(f"  Total Executions: {metrics['total_executions']}")
            print(f"  Success Rate: {metrics['success_rate']}%")
            print(f"  Avg Duration: {metrics['avg_duration_ms']}ms")
            print(f"  Min Duration: {metrics['min_duration_ms']}ms")
            print(f"  Max Duration: {metrics['max_duration_ms']}ms")
            print(f"  P50 Latency: {metrics['p50_latency_ms']}ms")
            print(f"  P95 Latency: {metrics['p95_latency_ms']}ms")
            print(f"  P99 Latency: {metrics['p99_latency_ms']}ms")
        else:
            print(f"No metrics found for '{skill_name}'")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('skill_name')
@click.option('--limit', default=20, help='Number of recent executions')
def history(skill_name, limit):
    """Show execution history for a skill."""
    if not HAS_DATA_COLLECTOR:
        click.echo("Data collector module not available", err=True)
        sys.exit(1)
    
    try:
        collector = DataCollector()
        history = collector.get_execution_history(skill_name, limit)
        
        print(f"\nExecution History for '{skill_name}' (last {limit}):\n")
        
        for i, exec_data in enumerate(history, 1):
            status = "✓" if exec_data['success'] else "✗"
            print(f"{i}. {status} {exec_data['timestamp']} - {exec_data['duration_ms']}ms")
            if exec_data['error_trace']:
                print(f"   Error: {exec_data['error_trace'][:100]}")
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('skill_name')
def analyze(skill_name):
    """Analyze skill performance and identify bottlenecks."""
    if not HAS_FULL_FEATURES or PerformanceAnalyzer is None:
        click.echo("Performance analyzer requires additional modules", err=True)
        sys.exit(1)

    try:
        analyzer = PerformanceAnalyzer()
        analysis = analyzer.analyze_bottlenecks(skill_name)

        if 'error' in analysis:
            click.echo(f"Error: {analysis['error']}", err=True)
            sys.exit(1)

        print(f"\n=== Performance Analysis for '{skill_name}' ===\n")

        if 'message' in analysis:
            print(f"[INFO] {analysis['message']}")
            return

        metrics = analysis.get('metrics', {})
        print(f"Performance Metrics:")
        print(f"  Success Rate: {metrics.get('success_rate', 0):.1f}%")
        print(f"  Avg Duration: {metrics.get('avg_duration_ms', 0):.0f}ms")
        print(f"  P95 Duration: {metrics.get('p95_duration_ms', 0):.0f}ms")

        bottlenecks = analysis.get('bottlenecks', [])
        if bottlenecks:
            print(f"\nBottlenecks Found ({len(bottlenecks)}):\n")
            for i, bottleneck in enumerate(bottlenecks, 1):
                print(f"{i}. [{bottleneck['severity'].upper()}] {bottleneck['type']}")
                print(f"   {bottleneck['description']}")
                print(f"   Recommendation: {bottleneck['recommendation']}\n")
        else:
            print("\n[OK] No bottlenecks detected")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('skill_name')
def suggest(skill_name):
    """Suggest optimizations for a skill."""
    if not HAS_DATA_COLLECTOR:
        click.echo("Analyzing without metrics data...\n")
    else:
        try:
            collector = DataCollector()
            metrics = collector.calculate_metrics(skill_name, 30)
            
            if metrics:
                print(f"\nOptimization Suggestions for '{skill_name}':\n")
                
                if metrics['success_rate'] < 90:
                    print("⚠ Low success rate detected:")
                    print("  - Review error logs for common failure patterns")
                    print("  - Add input validation and error handling")
                
                if metrics['p95_latency_ms'] > metrics['avg_duration_ms'] * 2:
                    print("\n⚠ High latency variance detected:")
                    print("  - Profile slow executions to find bottlenecks")
                    print("  - Consider adding timeout limits")
                
                if metrics['avg_duration_ms'] > 5000:
                    print("\n⚠ Slow average execution time:")
                    print("  - Consider caching frequently used data")
                    print("  - Review database query performance")
                    print("  - Check for unnecessary API calls")
            else:
                print(f"No metrics available for '{skill_name}'")
                
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

@cli.command()
def status():
    """Show auto-evolver system status."""
    print("\nSkill Auto Evolver Status:\n")
    if HAS_DATA_COLLECTOR:
        print("[OK] Data Collector: Available")
    else:
        print("[NO] Data Collector: Not available")

    if HAS_FULL_FEATURES:
        print("[OK] Performance Analyzer: Available")
        print("[OK] Auto Optimizer: Available")
        print("[OK] A/B Testing: Available")
        print("[OK] Regression Tester: Available")
    else:
        print("[NO] Performance Analyzer: Not available")
        print("[NO] Auto Optimizer: Not available")
        print("[NO] A/B Testing: Not available")
        print("[NO] Regression Tester: Not available")

    print("\nAvailable Features:")
    print("  - Execution recording (record)")
    print("  - Performance metrics (metrics)")
    print("  - Execution history (history)")
    print("  - Performance analysis (analyze)")
    print("  - Optimization suggestions (suggest, optimize)")
    print("  - Regression testing (regression-setup, regression-test)")
    print("  - A/B testing (ab-create, ab-status, ab-promote)")

# New commands for optimizer
@cli.command()
@click.argument('skill_name')
@click.option('--apply', is_flag=True, help='Generate optimized version')
@click.option('--version', default='1.0', help='Version for optimized output')
def optimize(skill_name, apply, version):
    """Analyze and optionally generate optimized skill version."""
    if not HAS_FULL_FEATURES or SkillOptimizer is None:
        click.echo("Optimizer requires additional modules", err=True)
        sys.exit(1)

    try:
        optimizer = SkillOptimizer()

        if apply:
            success = optimizer.generate_optimized_version(skill_name, version)
            sys.exit(0 if success else 1)
        else:
            analysis = optimizer.analyze_skill(skill_name)

            print(f"\n=== Optimization Analysis for '{skill_name}' ===\n")

            if 'error' in analysis:
                print(f"[ERROR] {analysis['error']}")
                sys.exit(1)

            if 'message' in analysis:
                print(f"[INFO] {analysis['message']}")
                return

            opportunities = analysis.get('opportunities', [])
            if opportunities:
                print(f"Found {len(opportunities)} optimization opportunities:\n")
                for i, opp in enumerate(opportunities, 1):
                    print(f"{i}. [{opp['severity'].upper()}] {opp['type']}")
                    print(f"   {opp['description']}")
                    print(f"   Impact: {opp['impact']}\n")
                print(f"Run with --apply --version <ver> to generate optimized version")
            else:
                print("[OK] No optimization opportunities found")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

# Regression testing commands
@cli.command()
@click.argument('skill_name')
def regression_setup(skill_name):
    """Set up regression test baseline for a skill."""
    if not HAS_FULL_FEATURES or RegressionTester is None:
        click.echo("Regression tester requires additional modules", err=True)
        sys.exit(1)

    try:
        tester = RegressionTester()
        success = tester.setup_test_suite(skill_name)
        sys.exit(0 if success else 1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('skill_name')
@click.argument('version')
def regression_test(skill_name, version):
    """Run regression tests for a skill version."""
    if not HAS_FULL_FEATURES or RegressionTester is None:
        click.echo("Regression tester requires additional modules", err=True)
        sys.exit(1)

    try:
        tester = RegressionTester()
        results = tester.run_regression_tests(skill_name, version)

        print(f"\n=== Regression Test Results ===\n")

        if 'message' in results:
            print(f"[INFO] {results['message']}")
            sys.exit(1)

        summary = results['summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

# A/B testing commands
@cli.command()
@click.argument('skill_name')
@click.argument('variant_a')
@click.argument('variant_b')
@click.option('--split', default='50:50', help='Traffic split (e.g., 50:50)')
def ab_create(skill_name, variant_a, variant_b, split):
    """Create an A/B testing experiment."""
    if not HAS_FULL_FEATURES or ABTestManager is None:
        click.echo("A/B testing requires additional modules", err=True)
        sys.exit(1)

    try:
        manager = ABTestManager()
        experiment_id = manager.create_experiment(skill_name, variant_a, variant_b, split)
        print(f"\nExperiment ID: {experiment_id}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('experiment_id')
def ab_status(experiment_id):
    """Show A/B testing experiment status."""
    if not HAS_FULL_FEATURES or ABTestManager is None:
        click.echo("A/B testing requires additional modules", err=True)
        sys.exit(1)

    try:
        manager = ABTestManager()
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

            print(f"\nVariant {variant.upper()} ({status[variant_key]}):")
            print(f"  Executions: {metrics['executions']}")
            print(f"  Success Rate: {metrics.get('success_rate', 0):.1f}%")
            print(f"  Avg Duration: {metrics.get('avg_duration_ms', 0):.0f}ms")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('experiment_id')
def ab_promote(experiment_id):
    """Promote winning variant and complete experiment."""
    if not HAS_FULL_FEATURES or ABTestManager is None:
        click.echo("A/B testing requires additional modules", err=True)
        sys.exit(1)

    try:
        manager = ABTestManager()
        success = manager.promote_winner(experiment_id)
        sys.exit(0 if success else 1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
