"""Generic LLM-driven fix applier — works on any Python codebase."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from hw4.shared.gatekeeper import ApiGatekeeper
from hw4.shared.git_ops import branch_name, export_diff, find_git_root, git_run
from hw4.shared.llm_client import LlmClient


@dataclass
class FixResult:
    """Result of applying a fix proposal."""

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
    """Reads a fix proposal produced by the CrewAI agents and applies it via LLM.

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
        """Load proposal, generate code via LLM, write files, commit, export diff."""
        proposal = self._load_proposal(proposal_path)
        target = self._resolve_target(Path(proposal["target_file"]).resolve())
        new_module_name = proposal["new_module_name"]
        description = proposal["change_description"]

        original = target.read_text(encoding="utf-8")
        modified, new_module_content = self._generate_fix(
            original, target.name, new_module_name, description
        )

        new_module_path = target.parent / new_module_name
        target.write_text(modified, encoding="utf-8")
        new_module_path.write_text(new_module_content, encoding="utf-8")

        repo_root = find_git_root(target)
        br = branch_name(proposal)
        git_run(repo_root, ["checkout", "-b", br], self._gatekeeper)
        git_run(
            repo_root,
            ["add", str(target.relative_to(repo_root)),
             str(new_module_path.relative_to(repo_root))],
            self._gatekeeper,
        )
        bug = proposal.get("bug", {})
        git_run(
            repo_root,
            ["commit", "-m",
             f"refactor: fix {bug.get('bug_type', 'HUB')} "
             f"in {bug.get('node_name', target.stem)} (EX04)"],
            self._gatekeeper,
        )
        patch_path = export_diff(repo_root, self._results, self._gatekeeper)
        return FixResult(
            branch=br,
            patch_path=str(patch_path),
            target_file=str(target),
            committed=True,
        )

    # ── internal ─────────────────────────────────────────────────────────────

    def _load_proposal(self, path: str | None) -> dict:
        """Read proposal JSON, stripping markdown fences if present."""
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
        """Call LLM to produce modified file and new module content."""
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
        return self._parse_response(self._llm.complete(_SYSTEM, user))

    def _parse_response(self, response: str) -> tuple[str, str]:
        """Split LLM response on delimiters; raise ValueError if malformed."""
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
        """Return resolved path; fall back to searching under data/ if not found."""
        if path.exists():
            return path.resolve()
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
