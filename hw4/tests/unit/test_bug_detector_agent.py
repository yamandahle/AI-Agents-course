from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from hw4.agents.bug_detector_agent import BugDetectorAgent
from hw4.models.agent_models import GraphSummary
from hw4.services.bug_detector import BugDetectorService
from hw4.services.graph_builder import GraphBuilderService

MOCK_GRAPH = {
    "nodes": [
        {"id": "hub", "label": "hub.py", "file_type": "code", "source_file": "hub.py", "community": 0},
        {"id": "a", "label": "a.py", "file_type": "code", "source_file": "a.py", "community": 0},
        {"id": "b", "label": "b.py", "file_type": "code", "source_file": "b.py", "community": 0},
    ],
    "links": [
        {"source": "a", "target": "hub", "relation": "calls"},
        {"source": "b", "target": "hub", "relation": "calls"},
        {"source": "hub", "target": "a", "relation": "calls"},
        {"source": "hub", "target": "b", "relation": "calls"},
    ],
}


def test_bug_detector_agent_without_llm(tmp_path: Path) -> None:
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(MOCK_GRAPH), encoding="utf-8")
    graph = GraphBuilderService(MagicMock(), {"top_n_nodes": 5}).load_graph(str(path))
    summary = GraphSummary(
        node_count=3,
        edge_count=4,
        community_count=1,
        top_hubs=[("hub", 4)],
        bridge_count=0,
        hot_excerpt="",
        index_excerpt="",
    )
    agent = BugDetectorAgent(BugDetectorService(hub_degree_threshold=3), graph, llm=None)
    bugs = agent.run(summary)
    assert bugs
