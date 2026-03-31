#!/usr/bin/env python3
"""CLI for skill-lifecycle-manager - minimal viable implementation."""
import click
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from version_manager import VersionManager
try:
    from dependency_checker import DependencyChecker
    from stats_tracker import StatsTracker
    HAS_FULL_FEATURES = True
except ImportError:
    HAS_FULL_FEATURES = False

@click.group()
def cli():
    """Skills Lifecycle Manager - manage skill versions, dependencies, and statistics."""
    pass

@cli.command()
def list():
    """List all installed skills with versions."""
    try:
        vm = VersionManager()
        plugin_version = vm.get_plugin_version()
        print(f"Plugin Version: {plugin_version}\n")
        print("Skills:")
        
        skills = vm.list_skills()
        for skill in skills:
            version = skill.get('version', plugin_version)
            print(f"  {skill['name']}: {version}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('skill_name')
def info(skill_name):
    """Show detailed info about a skill."""
    try:
        vm = VersionManager()
        skill = vm.get_skill_info(skill_name)
        if skill:
            print(f"Name: {skill['name']}")
            print(f"Version: {skill.get('version', 'N/A')}")
            print(f"Description: {skill.get('description', 'N/A')}")
            print(f"Command: {skill.get('command', 'N/A')}")
            if 'tags' in skill:
                print(f"Tags: {', '.join(skill['tags'])}")
        else:
            click.echo(f"Skill '{skill_name}' not found", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('skill_name')
@click.option('--type', 'bump_type', type=click.Choice(['major', 'minor', 'patch']), 
              default='patch', help='Version bump type')
def bump(skill_name, bump_type):
    """Bump skill version."""
    try:
        vm = VersionManager()
        new_version = vm.bump_skill_version(skill_name, bump_type)
        print(f"✓ Bumped {skill_name} to {new_version}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('skill_name')
def check_deps(skill_name):
    """Check dependencies for a skill."""
    if not HAS_FULL_FEATURES:
        click.echo("Dependency checking requires additional modules", err=True)
        sys.exit(1)
    
    try:
        checker = DependencyChecker()
        report = checker.check_skill_dependencies(skill_name)
        
        print(f"\nDependency Report for '{skill_name}':\n")
        
        if report.satisfied:
            print("✓ Satisfied dependencies:")
            for dep in report.satisfied:
                print(f"  {dep}")
        
        if report.missing_python:
            print("\n✗ Missing Python packages:")
            for dep in report.missing_python:
                print(f"  {dep}")
        
        if report.missing_mcp:
            print("\n? MCP servers (manual check):")
            for dep in report.missing_mcp:
                print(f"  {dep}")
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def dep_graph():
    """Generate and display dependency graph."""
    if not HAS_FULL_FEATURES:
        click.echo("Dependency graph requires additional modules", err=True)
        sys.exit(1)
    
    try:
        checker = DependencyChecker()
        graph = checker.generate_dependency_graph("mermaid")
        print(graph)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('skill_name', required=False)
@click.option('--days', default=30, help='Number of days to analyze')
def stats(skill_name, days):
    """Show usage statistics."""
    if not HAS_FULL_FEATURES:
        click.echo("Stats tracking requires additional modules", err=True)
        sys.exit(1)
    
    try:
        tracker = StatsTracker()
        
        if skill_name:
            stats_obj = tracker.get_skill_stats(skill_name, days)
            if stats_obj:
                print(f"\nStats for '{skill_name}' (last {days} days):\n")
                print(f"  Executions: {stats_obj.total_executions}")
                print(f"  Success Rate: {stats_obj.success_rate}%")
                print(f"  Avg Duration: {stats_obj.avg_duration_ms}ms")
                print(f"  Errors: {stats_obj.error_count}")
                print(f"  Last Used: {stats_obj.last_used}")
            else:
                print(f"No statistics found for '{skill_name}'")
        else:
            popular = tracker.get_popular_skills(10, days)
            print(f"\nTop 10 Most Used Skills (last {days} days):\n")
            for i, stat in enumerate(popular, 1):
                print(f"{i}. {stat.skill_name}: {stat.total_executions} executions "
                      f"({stat.success_rate}% success)")
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def health():
    """Generate health report (basic version)."""
    try:
        vm = VersionManager()
        skills = vm.list_skills()
        
        print("\n=== Skills Health Report ===\n")
        print(f"Total Skills: {len(skills)}")
        print(f"Plugin Version: {vm.get_plugin_version()}")
        
        # Count skills with dependencies
        with_deps = sum(1 for s in skills if 'dependencies' in s)
        print(f"Skills with dependencies: {with_deps}")
        
        print("\nNote: Full health report requires additional modules")
        print("Run with stats tracking enabled for detailed metrics")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
