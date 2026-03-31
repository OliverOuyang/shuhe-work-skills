"""Dependency checker for skills - checks Python packages and MCP servers."""
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

class DependencyReport:
    def __init__(self):
        self.missing_python: List[str] = []
        self.missing_mcp: List[str] = []
        self.outdated: List[Tuple[str, str, str]] = []
        self.satisfied: List[str] = []

    def to_dict(self):
        return {
            "missing_python": self.missing_python,
            "missing_mcp": self.missing_mcp,
            "outdated": self.outdated,
            "satisfied": self.satisfied
        }

class DependencyChecker:
    def __init__(self, package_json_path: str = "package.json"):
        self.package_json_path = Path(package_json_path)
        self.package_data = self._load_package_json()

    def _load_package_json(self) -> dict:
        """Load and parse package.json."""
        with open(self.package_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_installed_python_packages(self) -> Dict[str, str]:
        """Get list of installed Python packages via pip list."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True, text=True, check=True
            )
            packages = json.loads(result.stdout)
            return {pkg["name"].lower(): pkg["version"] for pkg in packages}
        except Exception as e:
            print(f"Warning: Could not get pip list: {e}")
            return {}

    def check_skill_dependencies(self, skill_name: str) -> DependencyReport:
        """Check dependencies for a specific skill."""
        report = DependencyReport()
        
        # Find skill in package.json
        skills = self.package_data.get("claudePlugin", {}).get("skills", [])
        skill_data = next((s for s in skills if s["name"] == skill_name), None)
        
        if not skill_data:
            raise ValueError(f"Skill '{skill_name}' not found in package.json")
        
        dependencies = skill_data.get("dependencies", {})
        
        # Check Python dependencies
        python_deps = dependencies.get("python", [])
        if python_deps:
            installed = self._get_installed_python_packages()
            for dep in python_deps:
                # Parse requirement (e.g., "click>=8.0.0")
                pkg_name = dep.split(">=")[0].split("==")[0].split("<")[0].strip().lower()
                if pkg_name in installed:
                    report.satisfied.append(f"python:{dep}")
                else:
                    report.missing_python.append(dep)
        
        # Check MCP dependencies
        mcp_deps = dependencies.get("mcp", [])
        if mcp_deps:
            # For now, just mark as needs manual check
            for mcp in mcp_deps:
                report.missing_mcp.append(f"MCP:{mcp} (manual check required)")
        
        return report

    def generate_dependency_graph(self, output_format: str = "mermaid") -> str:
        """Generate dependency graph for all skills."""
        skills = self.package_data.get("claudePlugin", {}).get("skills", [])
        
        if output_format == "mermaid":
            lines = ["graph TD"]
            for skill in skills:
                skill_name = skill["name"]
                deps = skill.get("dependencies", {})
                
                # Python dependencies
                for py_dep in deps.get("python", []):
                    pkg = py_dep.split(">=")[0].split("==")[0].strip()
                    lines.append(f'    {skill_name}["{skill_name}"] --> PY_{pkg}["{pkg} (Python)"]')
                
                # MCP dependencies
                for mcp_dep in deps.get("mcp", []):
                    lines.append(f'    {skill_name}["{skill_name}"] --> MCP_{mcp_dep}["{mcp_dep} (MCP)"]')
            
            return "\n".join(lines)
        
        elif output_format == "json":
            graph = {}
            for skill in skills:
                skill_name = skill["name"]
                deps = skill.get("dependencies", {})
                graph[skill_name] = {
                    "python": deps.get("python", []),
                    "mcp": deps.get("mcp", [])
                }
            return json.dumps(graph, indent=2)
        
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def install_missing_dependencies(self, skill_name: str, auto_approve: bool = False):
        """Install missing Python dependencies."""
        report = self.check_skill_dependencies(skill_name)
        
        if not report.missing_python:
            print(f"All Python dependencies for '{skill_name}' are satisfied.")
            return
        
        print(f"Missing Python packages for '{skill_name}':")
        for dep in report.missing_python:
            print(f"  - {dep}")
        
        if not auto_approve:
            response = input("\nInstall missing packages? (y/n): ")
            if response.lower() != 'y':
                print("Installation cancelled.")
                return
        
        print("\nInstalling packages...")
        for dep in report.missing_python:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    check=True
                )
                print(f"✓ Installed {dep}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {dep}: {e}")

if __name__ == "__main__":
    checker = DependencyChecker()
    print("Dependency Graph (Mermaid):")
    print(checker.generate_dependency_graph())
