#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NPX Skills Marketplace Integration

Provides integration with the NPX skills marketplace for searching,
installing, and updating skills from the ecosystem.
"""

import json
import subprocess
import sys
from typing import List, Dict, Optional


class MarketplaceClient:
    """Client for interacting with NPX skills marketplace."""

    def __init__(self):
        self.npx_command = "npx"

    def search_skills(self, query: str) -> List[Dict[str, str]]:
        """
        Search for skills in the marketplace.

        Args:
            query: Search query string

        Returns:
            List of skill dictionaries with name, description, and install command
        """
        try:
            # Run npx skills find command
            result = subprocess.run(
                [self.npx_command, "skills", "find", query],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )

            if result.returncode != 0:
                print(f"[WARNING] Search command failed: {result.stderr}", file=sys.stderr)
                return []

            # Parse output to extract skills
            skills = []
            lines = result.stdout.strip().split('\n')

            for line in lines:
                line = line.strip()
                # Look for lines with skill package format: owner/repo@skill-name
                if '@' in line and '/' in line and not line.startswith('Install'):
                    # Extract skill package name
                    parts = line.split()
                    package_name = parts[0] if parts else line

                    skills.append({
                        'name': package_name,
                        'description': line,
                        'install_command': f"npx skills add {package_name}"
                    })

            return skills

        except subprocess.TimeoutExpired:
            print("[ERROR] Search command timed out after 30 seconds", file=sys.stderr)
            return []
        except Exception as e:
            print(f"[ERROR] Search failed: {str(e)}", file=sys.stderr)
            return []

    def install_skill(self, package_name: str, global_install: bool = True) -> bool:
        """
        Install a skill from the marketplace.

        Args:
            package_name: Full package name (e.g., owner/repo@skill-name)
            global_install: Whether to install globally (-g flag)

        Returns:
            True if installation succeeded, False otherwise
        """
        try:
            # Validate package name format
            if '@' not in package_name or '/' not in package_name:
                print(f"[ERROR] Invalid package name format: {package_name}", file=sys.stderr)
                print("Expected format: owner/repo@skill-name", file=sys.stderr)
                return False

            # Build install command
            cmd = [self.npx_command, "skills", "add", package_name]
            if global_install:
                cmd.append("-g")
            cmd.append("-y")  # Skip confirmation prompts

            print(f"Installing {package_name}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=120
            )

            if result.returncode == 0:
                print(f"[OK] Successfully installed {package_name}")
                return True
            else:
                print(f"[ERROR] Installation failed: {result.stderr}", file=sys.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("[ERROR] Installation timed out after 120 seconds", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[ERROR] Installation failed: {str(e)}", file=sys.stderr)
            return False

    def check_updates(self) -> List[Dict[str, str]]:
        """
        Check for available updates to installed skills.

        Returns:
            List of skills with available updates
        """
        try:
            result = subprocess.run(
                [self.npx_command, "skills", "check"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )

            if result.returncode != 0:
                print(f"[WARNING] Update check failed: {result.stderr}", file=sys.stderr)
                return []

            # Parse output to find outdated skills
            outdated = []
            lines = result.stdout.strip().split('\n')

            for line in lines:
                if 'update available' in line.lower() or 'outdated' in line.lower():
                    outdated.append({
                        'info': line.strip()
                    })

            return outdated

        except subprocess.TimeoutExpired:
            print("[ERROR] Update check timed out after 30 seconds", file=sys.stderr)
            return []
        except Exception as e:
            print(f"[ERROR] Update check failed: {str(e)}", file=sys.stderr)
            return []

    def update_all_skills(self) -> bool:
        """
        Update all installed skills to their latest versions.

        Returns:
            True if update succeeded, False otherwise
        """
        try:
            print("Updating all skills...")
            result = subprocess.run(
                [self.npx_command, "skills", "update"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=180
            )

            if result.returncode == 0:
                print("[OK] All skills updated successfully")
                print(result.stdout)
                return True
            else:
                print(f"[ERROR] Update failed: {result.stderr}", file=sys.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("[ERROR] Update timed out after 180 seconds", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[ERROR] Update failed: {str(e)}", file=sys.stderr)
            return False


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python marketplace.py <search|install|check|update> [args]")
        sys.exit(1)

    client = MarketplaceClient()
    command = sys.argv[1]

    if command == "search":
        if len(sys.argv) < 3:
            print("Usage: python marketplace.py search <query>")
            sys.exit(1)

        query = " ".join(sys.argv[2:])
        results = client.search_skills(query)

        if results:
            print(f"\nFound {len(results)} skills:\n")
            for skill in results:
                print(f"  {skill['name']}")
                print(f"  Install: {skill['install_command']}\n")
        else:
            print("No skills found")

    elif command == "install":
        if len(sys.argv) < 3:
            print("Usage: python marketplace.py install <package-name>")
            sys.exit(1)

        package = sys.argv[2]
        success = client.install_skill(package)
        sys.exit(0 if success else 1)

    elif command == "check":
        updates = client.check_updates()
        if updates:
            print(f"\n{len(updates)} skills have updates available:\n")
            for item in updates:
                print(f"  {item['info']}")
        else:
            print("All skills are up to date")

    elif command == "update":
        success = client.update_all_skills()
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
