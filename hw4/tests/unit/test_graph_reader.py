from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from hw4.agents.graph_reader import GraphReaderAgent
from hw4.services.graph_builder import GraphBuilderService

MOCK_GRAPH = {
    "nodes": [
        {"id": "hub", "label": "hub_fn", "file_type": "code", "source_file": "main.py", "community": 0},
        {"id": "a", "label": "a.py", "file_type": "code", "source_file": "a.py", "community": 0},
    ],
    "links": [
        {"source": "a", "target": "hub", "relation": "calls"},
    ],
}


@pytest.fixture
def obsidian_dir(tmp_path: Path) -> Path:
    vault = tmp_path / "obsidian"
    vault.mkdir()
    (vault / "hot.md").write_text("# Hot\nhub_fn is primary suspect.", encoding="utf-8")
    (vault / "index.md").write_text("# Index\n| main | entry |", encoding="utf-8")
    return vault


@pytest.fixture
def graph_file(tmp_path: Path) -> Path:
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(MOCK_GRAPH), encoding="utf-8")
    return path


def test_graph_reader_builds_summary(obsidian_dir: Path, graph_file: Path) -> None:
    service = GraphBuilderService(MagicMock(), {"top_n_nodes": 5})
    agent = GraphReaderAgent(service, str(graph_file), str(obsidian_dir), max_chars=100)
    summary = agent.run()
    assert summary.node_count == 2
    assert "hub_fn" in summary.hot_excerpt
    assert summary.files_read == 2
    assert summary.estimated_tokens > 0
