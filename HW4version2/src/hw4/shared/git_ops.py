"""Git helper utilities for applying fixes and exporting diffs."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from hw4.shared.gatekeeper import ApiGatekeeper


def find_git_root(path: Path) -> Path:
    """Walk up from *path* until a .git directory is found."""
    current = path.parent
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise FileNotFoundError(f"No .git directory found above {path}")


def branch_name(proposal: dict) -> str:
    """Derive a branch name from the bug entry in *proposal*."""
    bug = proposal.get("bug", {})
    bug_type = bug.get("bug_type", "fix").lower()
    node = re.sub(r"[^a-z0-9]+", "-", bug.get("node_name", "unknown").lower()).strip("-")
    return f"fix/{bug_type}-{node[:40]}"


def git_run(repo_root: Path, args: list[str], gatekeeper: ApiGatekeeper) -> None:
    """Run a git command inside *repo_root* through the gatekeeper."""
    gatekeeper.execute(
        subprocess.run,
        ["git", *args],
        cwd=repo_root,
        check=True,
    )


def export_diff(
    repo_root: Path,
    results_dir: Path,
    gatekeeper: ApiGatekeeper,
) -> Path:
    """Export HEAD~1..HEAD diff to results/fix_diff.patch and return its path."""
    result = gatekeeper.execute(
        subprocess.run,
        ["git", "diff", "HEAD~1", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    patch_path = results_dir / "fix_diff.patch"
    patch_path.write_text(result.stdout or "", encoding="utf-8")
    return patch_path
