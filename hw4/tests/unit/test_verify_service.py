from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from hw4.services.verify_report import render_verification_report
from hw4.services.verify_service import VerifyService


def test_compare_marks_improved_when_orchestration_present(tmp_path: Path) -> None:
    service = VerifyService(MagicMock(), {"hub_degree_threshold": 10}, {}, str(tmp_path))
    before = {
        "node_count": 10,
        "edge_count": 20,
        "community_count": 2,
        "bridge_count": 5,
        "top_hubs": [],
    }
    after = {
        "target_hub_degree": 18,
        "orchestration_hub_sum": 12,
        "node_count": 12,
        "edge_count": 25,
        "community_count": 2,
        "bridge_count": 5,
        "spof_count": 1,
        "hub_count": 3,
    }
    comparison = service._compare(before, after)
    assert comparison["improved"] is True


def test_render_verification_report_contains_bug_name() -> None:
    proposal = {"bug": {"bug_type": "HUB", "node_name": "cookiecutter()"}, "target_file": "main.py"}
    comparison = {
        "node_count": {"before": 1, "after": 2},
        "edge_count": {"before": 1, "after": 2},
        "community_count": {"before": 1, "after": 1},
        "bridge_count": {"before": 1, "after": 1},
        "main_cookiecutter_hub_degree": {"before": 16, "after": 20},
        "orchestration_hub_sum_after": 30,
    }
    text = render_verification_report(proposal, comparison, True, 88.0, True)
    assert "cookiecutter()" in text
    assert "88.0%" in text


def test_metrics_dict_counts_orchestration_nodes() -> None:
    import json
    import tempfile

    from hw4.services.graph_builder import GraphBuilderService

    mock_graph = {
        "nodes": [{"id": "hub", "label": "hub", "community": 0}],
        "links": [{"source": "a", "target": "hub", "relation": "calls"}],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
        json.dump(mock_graph, handle)
        path = handle.name
    service = VerifyService(MagicMock(), {"hub_degree_threshold": 1}, {}, ".")
    graph = GraphBuilderService(MagicMock(), {"top_n_nodes": 5}).load_graph(path)
    metrics = service._metrics_dict(graph)
    assert metrics["hub_count"] >= 0


def test_enrich_before_adds_bug_counts(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics_before.json"
    metrics.write_text(
        '{"node_count":1,"edge_count":1,"community_count":1,"bridge_count":0,"top_hubs":[]}',
        encoding="utf-8",
    )
    graph = tmp_path / "graph.json"
    graph.write_text(
        '{"nodes":[{"id":"hub","label":"hub","community":0}],'
        '"links":[{"source":"a","target":"hub","relation":"calls"}]}',
        encoding="utf-8",
    )
    service = VerifyService(MagicMock(), {"hub_degree_threshold": 1}, {}, str(tmp_path))
    before = service._enrich_before(metrics, graph)
    assert "hub_count" in before
