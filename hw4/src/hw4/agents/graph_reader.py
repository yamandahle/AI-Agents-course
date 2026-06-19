from __future__ import annotations

from pathlib import Path

from hw4.models.agent_models import GraphSummary
from hw4.services.graph_builder import GraphBuilderService


class GraphReaderAgent:
    """Agent 1: graph-guided navigation — metrics + index/hot excerpts only."""

    def __init__(
        self,
        graph_builder: GraphBuilderService,
        graph_path: str,
        obsidian_dir: str,
        max_chars: int = 2000,
    ) -> None:
        self._graph_builder = graph_builder
        self._graph_path = graph_path
        self._obsidian_dir = Path(obsidian_dir)
        self._max_chars = max_chars

    def run(self) -> GraphSummary:
        graph = self._graph_builder.load_graph(self._graph_path)
        metrics = self._graph_builder.compute_metrics(graph)
        hot_excerpt = self._read_excerpt("hot.md")
        index_excerpt = self._read_excerpt("index.md")
        text = hot_excerpt + index_excerpt + str(metrics.top_hubs[:10])
        return GraphSummary(
            node_count=metrics.node_count,
            edge_count=metrics.edge_count,
            community_count=metrics.community_count,
            top_hubs=metrics.top_hubs[:10],
            bridge_count=metrics.bridge_count,
            hot_excerpt=hot_excerpt,
            index_excerpt=index_excerpt,
            navigation_files=["index.md", "hot.md", self._graph_path],
            files_read=2,
            estimated_tokens=max(1, len(text) // 4),
        )

    def _read_excerpt(self, filename: str) -> str:
        path = self._obsidian_dir / filename
        if not path.exists():
            return ""
        content = path.read_text(encoding="utf-8")
        return content[: self._max_chars]
