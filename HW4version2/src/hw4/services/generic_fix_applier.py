"""Generic LLM-driven fix applier — works on any Python codebase."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from hw4.shared.gatekeeper import ApiGatekeeper
from hw4.shared.llm_client import LlmClient


@dataclass
class FixResult:
    branch: str
    patch_path: str
    target_file: str
    committed: bool


_DELIMITER_MODIFIED = "===MODIFIED_FILE==="
_DELIMITER_NEW = "===NEW_MODULE==="

_SYSTEM = (
    "You are an expert Python refactoring engineer. "
    "Follow the instruction exactly and output ONLY the two requested file "
    "contents separated by the given delimiters. No prose, no markdown fences."
)


class GenericFixApplier:
    """Reads a fix proposal produced by the CrewAI agents and applies it to the
    target source file using the LLM to generate the actual code changes.

    Works on any Python codebase — no paths are hardcoded.
    """

    def __init__(
        self,
        llm_client: LlmClient,
        gatekeeper: ApiGatekeeper,
        paths: dict,
    ) -> None:
        self._llm = llm_client
        self._gatekeeper = gatekeeper
        self._results = Path(paths["results"])

    def apply_from_proposal(self, proposal_path: str | None = None) -> FixResult:
        proposal = self._load_proposal(proposal_path)
        target = Path(proposal["target_file"]).resolve()
        new_module_name = proposal["new_module_name"]
        description = proposal["change_description"]

        target = self._resolve_target(target)
        original = target.read_text(encoding="utf-8")
        modified, new_module_content = self._generate_fix(
            original, target.name, new_module_name, description
        )

        new_module_path = target.parent / new_module_name
        target.write_text(modified, encoding="utf-8")
        new_module_path.write_text(new_module_content, encoding="utf-8")

        repo_root = self._find_git_root(target)
        branch = self._branch_name(proposal)
        self._git(repo_root, ["checkout", "-b", branch])
        self._git(repo_root, ["add", str(target.relative_to(repo_root)),
                              str(new_module_path.relative_to(repo_root))])
        bug = proposal.get("bug", {})
        self._git(repo_root, ["commit", "-m",
                              f"refactor: fix {bug.get('bug_type','HUB')} "
                              f"in {bug.get('node_name', target.stem)} (EX04)"])

        patch_path = self._export_diff(repo_root)
        return FixResult(
            branch=branch,
            patch_path=str(patch_path),
            target_file=str(target),
            committed=True,
        )

    # ── internal ─────────────────────────────────────────────────────────────

    def _load_proposal(self, path: str | None) -> dict:
        p = Path(path) if path else self._results / "v2_fix_proposal.json"
        text = p.read_text(encoding="utf-8").strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        return json.loads(text.strip())

    def _generate_fix(
        self,
        original: str,
        filename: str,
        new_module: str,
        description: str,
    ) -> tuple[str, str]:
        user = (
            f"Refactor the Python file '{filename}' according to the instruction below.\n\n"
            f"INSTRUCTION:\n{description}\n\n"
            f"NEW MODULE NAME: {new_module}\n\n"
            f"FILE CONTENT:\n{original}\n\n"
            f"Output EXACTLY in this format with no other text:\n"
            f"{_DELIMITER_MODIFIED}\n"
            f"<complete modified content of {filename}>\n"
            f"{_DELIMITER_NEW}\n"
            f"<complete content of {new_module}>"
        )
        response = self._llm.complete(_SYSTEM, user)
        return self._parse_response(response)

    def _parse_response(self, response: str) -> tuple[str, str]:
        if _DELIMITER_MODIFIED not in response or _DELIMITER_NEW not in response:
            raise ValueError(
                f"LLM response missing required delimiters.\n"
                f"Expected '{_DELIMITER_MODIFIED}' and '{_DELIMITER_NEW}'.\n"
                f"Got: {response[:400]}"
            )
        after_modified = response.split(_DELIMITER_MODIFIED, 1)[1]
        modified, new_module = after_modified.split(_DELIMITER_NEW, 1)
        return modified.strip(), new_module.strip()

    def _resolve_target(self, path: Path) -> Path:
        """Resolve target file; fall back to searching under data/ if not found directly."""
        if path.exists():
            return path.resolve()
        # LLM sometimes returns just the filename — search under data/
        matches = list(Path("data").rglob(path.name)) if Path("data").exists() else []
        if len(matches) == 1:
            return matches[0].resolve()
        if len(matches) > 1:
            path_parts = set(path.parts)
            return max(matches, key=lambda m: len(set(m.parts) & path_parts)).resolve()
        raise FileNotFoundError(
            f"Cannot find '{path}'. "
            "Ensure target_file in the fix proposal is the full relative path from project root."
        )

    def _find_git_root(self, path: Path) -> Path:
        current = path.parent
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise FileNotFoundError(f"No .git directory found above {path}")

    def _branch_name(self, proposal: dict) -> str:
        bug = proposal.get("bug", {})
        bug_type = bug.get("bug_type", "fix").lower()
        node = re.sub(r"[^a-z0-9]+", "-", bug.get("node_name", "unknown").lower()).strip("-")
        return f"fix/{bug_type}-{node[:40]}"

    def _git(self, repo_root: Path, args: list[str]) -> None:
        self._gatekeeper.execute(
            subprocess.run,
            ["git", *args],
            cwd=repo_root,
            check=True,
        )

    def _export_diff(self, repo_root: Path) -> Path:
        result = self._gatekeeper.execute(
            subprocess.run,
            ["git", "diff", "HEAD~1", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        patch_path = self._results / "fix_diff.patch"
        patch_path.write_text(result.stdout or "", encoding="utf-8")
        return patch_path
