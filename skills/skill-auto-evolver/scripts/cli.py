#!/usr/bin/env python3
"""CLI for skill-auto-evolver - minimal viable implementation."""
import click
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from data_collector import DataCollector, ExecutionContext
    HAS_DATA_COLLECTOR = True
except ImportError:
    HAS_DATA_COLLECTOR = False

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
    click.echo("Analysis feature - coming soon")
    click.echo(f"Will analyze: {skill_name}")
    click.echo("\nPlaceholder suggestions:")
    click.echo("  - Consider adding caching for repeated operations")
    click.echo("  - Review error patterns in execution history")
    click.echo("  - Check P95 latency for performance outliers")

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
    print("[NO] Performance Analyzer: Not yet implemented")
    print("[NO] Auto Optimizer: Not yet implemented")
    print("[NO] A/B Testing: Not yet implemented")
    print("[NO] Regression Tester: Not yet implemented")
    print("\nCurrent Features:")
    print("  - Execution recording (record)")
    print("  - Performance metrics (metrics)")
    print("  - Execution history (history)")
    print("  - Basic optimization suggestions (suggest)")

if __name__ == '__main__':
    cli()
