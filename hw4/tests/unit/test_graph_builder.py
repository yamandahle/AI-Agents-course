from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from hw4.services.graph_builder import GraphBuilderService

MOCK_GRAPH = {
    "nodes": [
        {"id": "a", "label": "a.py", "file_type": "code", "source_file": "a.py", "community": 0},
        {"id": "b", "label": "b.py", "file_type": "code", "source_file": "b.py", "community": 0},
        {"id": "c", "label": "c.py", "file_type": "code", "source_file": "c.py", "community": 1},
        {"id": "hub", "label": "hub.py", "file_type": "code", "source_file": "hub.py", "community": 0},
        {"id": "d", "label": "d.py", "file_type": "code", "source_file": "d.py", "community": 1},
    ],
    "links": [
        {"source": "a", "target": "hub", "relation": "calls"},
        {"source": "b", "target": "hub", "relation": "calls"},
        {"source": "c", "target": "hub", "relation": "imports"},
        {"source": "d", "target": "hub", "relation": "imports"},
        {"source": "hub", "target": "b", "relation": "calls"},
        {"source": "c", "target": "d", "relation": "calls"},
    ],
}


@pytest.fixture
def service() -> GraphBuilderService:
    gatekeeper = MagicMock()
    config = {"top_n_nodes": 5}
    return GraphBuilderService(gatekeeper=gatekeeper, config=config)


@pytest.fixture
def graph_json_file() -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(MOCK_GRAPH, f)
        return f.name


def test_load_graph_node_count(service: GraphBuilderService, graph_json_file: str) -> None:
    graph = service.load_graph(graph_json_file)
    assert len(graph.nodes) == 5


def test_load_graph_edge_count(service: GraphBuilderService, graph_json_file: str) -> None:
    graph = service.load_graph(graph_json_file)
    assert len(graph.edges) == 6


def test_load_graph_edge_types(service: GraphBuilderService, graph_json_file: str) -> None:
    graph = service.load_graph(graph_json_file)
    types = {e.relation for e in graph.edges}
    assert "calls" in types
    assert "imports" in types


def test_compute_metrics_detects_hub(service: GraphBuilderService, graph_json_file: str) -> None:
    graph = service.load_graph(graph_json_file)
    metrics = service.compute_metrics(graph)
    top_node, top_degree = metrics.top_hubs[0]
    assert top_node == "hub"
    assert top_degree >= 4


def test_compute_metrics_community_count(service: GraphBuilderService, graph_json_file: str) -> None:
    graph = service.load_graph(graph_json_file)
    metrics = service.compute_metrics(graph)
    assert metrics.community_count == 2


def test_compute_metrics_counts_edge_types(service: GraphBuilderService, graph_json_file: str) -> None:
    graph = service.load_graph(graph_json_file)
    metrics = service.compute_metrics(graph)
    assert "calls" in metrics.edge_type_counts
    assert metrics.edge_type_counts["calls"] == 4


def test_graphify_out_dir_under_artifacts() -> None:
    artifacts = Path("artifacts")
    assert GraphBuilderService.graphify_out_dir(artifacts) == Path("artifacts/graphify-out")


def test_sync_deliverables_copies_outputs(tmp_path: Path) -> None:
    graphify_out = tmp_path / "graphify-out"
    artifacts = tmp_path / "artifacts"
    graphify_out.mkdir()
    artifacts.mkdir()
    (graphify_out / "graph.json").write_text('{"nodes":[],"links":[]}', encoding="utf-8")
    (graphify_out / "graph.html").write_text("<html></html>", encoding="utf-8")

    service = GraphBuilderService(MagicMock(), {"top_n_nodes": 5})
    service.sync_deliverables(
        graphify_out,
        artifacts,
        json_name="graph_after.json",
        html_name="graph_after.html",
    )
    assert (artifacts / "graph_after.json").exists()
    assert (artifacts / "graph_after.html").read_text(encoding="utf-8") == "<html></html>"
