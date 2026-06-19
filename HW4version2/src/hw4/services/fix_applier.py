from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from hw4.services.cookiecutter_refactor import apply_main_hub_refactor
from hw4.shared.gatekeeper import ApiGatekeeper


@dataclass
class FixResult:
    """Result of applying a fix proposal to the cookiecutter source tree."""

    branch: str
    patch_path: str
    target_file: str
    committed: bool


class FixApplierService:
    """Applies the chosen fix proposal to the cookiecutter source via git."""

    def __init__(self, gatekeeper: ApiGatekeeper, paths: dict) -> None:
        self._gatekeeper = gatekeeper
        self._results = Path(paths["results"])
        self._repo_root = Path(paths["data"]) / "cookiecutter"

    def apply_from_file(self, proposals_path: str | None = None) -> FixResult:
        """Load fix proposals from disk, apply the best one, and return the FixResult."""
        path = Path(proposals_path) if proposals_path else self._results / "fix_proposals.json"
        proposals = json.loads(path.read_text(encoding="utf-8"))
        proposal = self._select_proposal(proposals)
        self._save_chosen_proposal(proposal)
        branch = self._branch_name(proposal)
        self._git(["checkout", "-b", branch])
        changed = apply_main_hub_refactor(self._repo_root)
        if changed:
            self._git(["add", "cookiecutter/main.py", "cookiecutter/orchestration.py"])
            message = (
                f"refactor: fix {proposal['bug']['bug_type']} "
                f"in {proposal['bug']['node_name']} (EX04)"
            )
            self._git(["commit", "-m", message])
        patch_path = self._export_diff()
        return FixResult(
            branch=branch,
            patch_path=str(patch_path),
            target_file=proposal["target_file"],
            committed=changed,
        )

    def _select_proposal(self, proposals: list[dict]) -> dict:
        for item in proposals:
            if item.get("target_file") == "main.py":
                return item
        return proposals[0]

    def _save_chosen_proposal(self, proposal: dict) -> None:
        self._results.mkdir(parents=True, exist_ok=True)
        (self._results / "fix_proposal.json").write_text(
            json.dumps(proposal, indent=2),
            encoding="utf-8",
        )

    def _branch_name(self, proposal: dict) -> str:
        bug_type = proposal["bug"]["bug_type"].lower()
        node = re.sub(r"[^a-z0-9]+", "-", proposal["bug"]["node_name"].lower()).strip("-")
        return f"fix/{bug_type}-{node[:40]}"

    def _export_diff(self) -> Path:
        result = self._gatekeeper.execute(
            subprocess.run,
            ["git", "diff", "HEAD~1", "HEAD", "--", "cookiecutter/"],
            cwd=self._repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        patch_path = self._results / "fix_diff.patch"
        patch_path.write_text(result.stdout or "", encoding="utf-8")
        return patch_path

    def _git(self, args: list[str]) -> None:
        self._gatekeeper.execute(
            subprocess.run,
            ["git", *args],
            cwd=self._repo_root,
            check=True,
        )
