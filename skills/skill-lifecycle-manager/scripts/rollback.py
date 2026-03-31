#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Snapshot and Rollback Management

Provides snapshot creation and rollback functionality for skills
with Git integration for version control.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class SnapshotManager:
    """Manager for creating and managing skill snapshots."""

    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.snapshots_dir = Path(self.repo_root) / ".omc" / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def _find_repo_root(self) -> Path:
        """Find the Git repository root directory."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                check=True
            )
            return Path(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to current directory
            return Path.cwd()

    def _is_git_repo(self) -> bool:
        """Check if current directory is in a Git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_current_commit(self) -> Optional[str]:
        """Get the current Git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def _get_git_status(self) -> str:
        """Get current Git status."""
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""

    def create_snapshot(self, label: str) -> str:
        """
        Create a snapshot of the current state.

        Args:
            label: Human-readable label for the snapshot

        Returns:
            Snapshot ID (timestamp-based)
        """
        if not self._is_git_repo():
            raise RuntimeError("Not in a Git repository. Snapshots require Git.")

        # Generate snapshot ID
        timestamp = int(time.time())
        snapshot_id = f"snapshot-{timestamp}"

        # Get current state
        commit_hash = self._get_current_commit()
        git_status = self._get_git_status()

        if not commit_hash:
            raise RuntimeError("Failed to get current Git commit")

        # Create snapshot metadata
        metadata = {
            "id": snapshot_id,
            "label": label,
            "timestamp": timestamp,
            "created_at": datetime.now().isoformat(),
            "commit": commit_hash,
            "has_uncommitted_changes": bool(git_status),
            "git_status": git_status
        }

        # Save metadata
        metadata_file = self.snapshots_dir / f"{snapshot_id}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"[OK] Created snapshot '{snapshot_id}' with label '{label}'")
        print(f"     Commit: {commit_hash[:8]}")

        if git_status:
            print(f"     [WARNING] Snapshot includes uncommitted changes")

        return snapshot_id

    def list_snapshots(self) -> List[Dict]:
        """
        List all available snapshots.

        Returns:
            List of snapshot metadata dictionaries
        """
        snapshots = []

        if not self.snapshots_dir.exists():
            return snapshots

        for metadata_file in sorted(self.snapshots_dir.glob("snapshot-*.json")):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    snapshots.append(metadata)
            except Exception as e:
                print(f"[WARNING] Failed to read {metadata_file.name}: {e}", file=sys.stderr)

        # Sort by timestamp descending (newest first)
        snapshots.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return snapshots

    def get_snapshot(self, snapshot_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific snapshot.

        Args:
            snapshot_id: The snapshot ID

        Returns:
            Snapshot metadata or None if not found
        """
        metadata_file = self.snapshots_dir / f"{snapshot_id}.json"

        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to read snapshot metadata: {e}", file=sys.stderr)
            return None

    def rollback_to_snapshot(self, snapshot_id: str, force: bool = False) -> bool:
        """
        Rollback to a specific snapshot.

        Args:
            snapshot_id: The snapshot ID to rollback to
            force: Whether to force rollback even with uncommitted changes

        Returns:
            True if rollback succeeded, False otherwise
        """
        if not self._is_git_repo():
            print("[ERROR] Not in a Git repository. Rollback requires Git.", file=sys.stderr)
            return False

        # Get snapshot metadata
        metadata = self.get_snapshot(snapshot_id)
        if not metadata:
            print(f"[ERROR] Snapshot '{snapshot_id}' not found", file=sys.stderr)
            return False

        # Check for uncommitted changes
        current_status = self._get_git_status()
        if current_status and not force:
            print("[ERROR] You have uncommitted changes. Commit or stash them first.", file=sys.stderr)
            print("Use --force to rollback anyway (will lose uncommitted changes)", file=sys.stderr)
            return False

        # Get target commit
        target_commit = metadata.get('commit')
        if not target_commit:
            print("[ERROR] Snapshot metadata missing commit hash", file=sys.stderr)
            return False

        try:
            # Perform Git checkout
            print(f"Rolling back to snapshot '{snapshot_id}'...")
            print(f"  Label: {metadata.get('label', 'N/A')}")
            print(f"  Created: {metadata.get('created_at', 'N/A')}")
            print(f"  Commit: {target_commit[:8]}")

            subprocess.run(
                ["git", "checkout", target_commit],
                check=True,
                capture_output=True
            )

            print("[OK] Rollback successful")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Git checkout failed: {e.stderr.decode('utf-8', errors='ignore')}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[ERROR] Rollback failed: {str(e)}", file=sys.stderr)
            return False


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python rollback.py <create|list|rollback> [args]")
        sys.exit(1)

    manager = SnapshotManager()
    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 3:
            print("Usage: python rollback.py create <label>")
            sys.exit(1)

        label = " ".join(sys.argv[2:])
        snapshot_id = manager.create_snapshot(label)
        print(f"\nSnapshot ID: {snapshot_id}")

    elif command == "list":
        snapshots = manager.list_snapshots()

        if not snapshots:
            print("No snapshots found")
            sys.exit(0)

        print(f"\nFound {len(snapshots)} snapshots:\n")
        for snapshot in snapshots:
            print(f"  ID: {snapshot['id']}")
            print(f"  Label: {snapshot.get('label', 'N/A')}")
            print(f"  Created: {snapshot.get('created_at', 'N/A')}")
            print(f"  Commit: {snapshot.get('commit', 'N/A')[:8]}")
            if snapshot.get('has_uncommitted_changes'):
                print(f"  [WARNING] Had uncommitted changes")
            print()

    elif command == "rollback":
        if len(sys.argv) < 3:
            print("Usage: python rollback.py rollback <snapshot_id> [--force]")
            sys.exit(1)

        snapshot_id = sys.argv[2]
        force = "--force" in sys.argv

        success = manager.rollback_to_snapshot(snapshot_id, force=force)
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
