from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from hw4.models.agent_models import GraphSummary
from hw4.services.bug_detector import BugDetectorService
from hw4.services.graph_builder import GraphBuilderService

MOCK_GRAPH = {
    "nodes": [
        {"id": "a", "label": "a.py", "file_type": "code", "source_file": "a.py", "community": 0},
        {"id": "b", "label": "b.py", "file_type": "code", "source_file": "b.py", "community": 0},
        {"id": "hub", "label": "hub.py", "file_type": "code", "source_file": "hub.py", "community": 0},
    ],
    "links": [
        {"source": "a", "target": "hub", "relation": "calls"},
        {"source": "b", "target": "hub", "relation": "calls"},
        {"source": "hub", "target": "a", "relation": "calls"},
        {"source": "hub", "target": "b", "relation": "calls"},
        {"source": "a", "target": "b", "relation": "calls"},
    ],
}


@pytest.fixture
def graph(tmp_path: Path):
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(MOCK_GRAPH), encoding="utf-8")
    return GraphBuilderService(MagicMock(), {"top_n_nodes": 5}).load_graph(str(path))


@pytest.fixture
def summary() -> GraphSummary:
    return GraphSummary(
        node_count=3,
        edge_count=5,
        community_count=1,
        top_hubs=[("hub", 4)],
        bridge_count=0,
        hot_excerpt="",
        index_excerpt="",
    )


def test_detects_hub(graph, summary: GraphSummary) -> None:
    detector = BugDetectorService(hub_degree_threshold=3, max_bugs=5)
    bugs = detector.detect(graph, summary)
    types = {bug.bug_type for bug in bugs}
    assert "HUB" in types
    hub = next(bug for bug in bugs if bug.bug_type == "HUB")
    assert hub.node_name == "hub.py"


def test_limits_max_bugs(graph, summary: GraphSummary) -> None:
    detector = BugDetectorService(hub_degree_threshold=1, max_bugs=1)
    bugs = detector.detect(graph, summary)
    assert len(bugs) == 1
