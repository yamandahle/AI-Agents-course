from __future__ import annotations

from pathlib import Path

from hw4.models.agent_models import ArchitecturalBug, FixProposal, GraphSummary
from hw4.shared.llm_client import LlmClient

_FIX_TEMPLATES: dict[str, tuple[str, str]] = {
    "SPOF": (
        "Extract orchestration logic into a dedicated module so callers do not "
        "all depend on one entry function.",
        "Split responsibilities to reduce single-point-of-failure risk.",
    ),
    "HUB": (
        "Move helper utilities into smaller focused modules and keep the hub "
        "as a thin coordinator.",
        "Lower fan-in/fan-out so changes stay localized.",
    ),
    "WEAK_BRIDGE": (
        "Introduce a shared interface module so communities connect through a "
        "stable contract instead of one bridge edge.",
        "Reduces coupling between otherwise separate subgraphs.",
    ),
}


class FixProposerAgent:
    """Agent 3: proposes fixes using only affected files and graph context."""

    def __init__(
        self,
        repo_root: str,
        llm: LlmClient | None = None,
        max_file_chars: int = 1500,
    ) -> None:
        self._repo_root = Path(repo_root)
        self._llm = llm
        self._max_file_chars = max_file_chars

    def run(self, bugs: list[ArchitecturalBug], summary: GraphSummary) -> list[FixProposal]:
        """Generate one FixProposal per bug, optionally refined by LLM."""
        proposals: list[FixProposal] = []
        for bug in bugs:
            proposals.append(self._propose(bug, summary))
        return proposals

    def _propose(self, bug: ArchitecturalBug, summary: GraphSummary) -> FixProposal:
        target = bug.source_file or self._guess_file(bug.node_name)
        snippet = self._read_snippet(target)
        change, rationale = _FIX_TEMPLATES.get(bug.bug_type, _FIX_TEMPLATES["HUB"])
        if self._llm and self._llm.is_configured() and snippet:
            llm_text = self._llm.complete(
                system="Propose a minimal architectural refactor.",
                user=(
                    f"Bug: {bug.bug_type} on {bug.node_name}. "
                    f"Hot context: {summary.hot_excerpt[:400]}. "
                    f"Code snippet:\n{snippet[:800]}"
                ),
            )
            if llm_text:
                change = llm_text.splitlines()[0][:300]
        return FixProposal(
            bug=bug,
            target_file=target,
            change_description=change,
            rationale=rationale,
        )

    def _guess_file(self, node_name: str) -> str:
        if node_name.endswith(".py"):
            return node_name
        return f"cookiecutter/{node_name.split('(')[0]}.py"

    def _read_snippet(self, relative_path: str) -> str:
        path = self._repo_root / relative_path
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")[: self._max_file_chars]
