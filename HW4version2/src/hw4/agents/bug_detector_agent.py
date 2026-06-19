from __future__ import annotations

from hw4.models.agent_models import ArchitecturalBug, GraphSummary
from hw4.models.graph_models import Graph
from hw4.services.bug_detector import BugDetectorService
from hw4.shared.llm_client import LlmClient


class BugDetectorAgent:
    """Agent 2: detects SPOF, hub, and bridge risks from graph summary."""

    def __init__(
        self,
        detector: BugDetectorService,
        graph: Graph,
        llm: LlmClient | None = None,
    ) -> None:
        self._detector = detector
        self._graph = graph
        self._llm = llm

    def run(self, summary: GraphSummary) -> list[ArchitecturalBug]:
        bugs = self._detector.detect(self._graph, summary)
        if self._llm and self._llm.is_configured() and bugs:
            self._enrich_with_llm(bugs, summary)
        return bugs

    def _enrich_with_llm(self, bugs: list[ArchitecturalBug], summary: GraphSummary) -> None:
        assert self._llm is not None
        names = ", ".join(bug.node_name for bug in bugs[:5])
        prompt = (
            f"Top hubs: {summary.top_hubs[:5]}. "
            f"Detected nodes: {names}. "
            "In one sentence each, explain the architectural risk."
        )
        text = self._llm.complete(
            system="You are a software architect reviewing dependency graphs.",
            user=prompt,
        )
        if not text:
            return
        lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
        for idx, bug in enumerate(bugs):
            if idx < len(lines):
                bug.explanation = lines[idx]
