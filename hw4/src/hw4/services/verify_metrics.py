from __future__ import annotations

from collections import Counter
from typing import Any

from hw4.models.agent_models import GraphSummary
from hw4.models.graph_models import Graph
from hw4.services.bug_detector import BugDetectorService
from hw4.services.graph_builder import GraphBuilderService


def hub_degree(hubs: list, node_id: str) -> int:
    return next((degree for node, degree in hubs if node == node_id), 0)


def build_metrics_dict(
    graph: Graph,
    graph_builder: GraphBuilderService,
    hub_threshold: int = 10,
) -> dict[str, Any]:
    metrics = graph_builder.compute_metrics(graph)
    summary = GraphSummary(
        metrics.node_count,
        metrics.edge_count,
        metrics.community_count,
        metrics.top_hubs,
        metrics.bridge_count,
        "",
        "",
    )
    bugs = BugDetectorService(hub_threshold, max_bugs=20).detect(graph, summary)
    degree: Counter[str] = Counter()
    for edge in graph.edges:
        degree[edge.source] += 1
        degree[edge.target] += 1
    return {
        "scope": "data/cookiecutter/cookiecutter",
        "node_count": metrics.node_count,
        "edge_count": metrics.edge_count,
        "community_count": metrics.community_count,
        "bridge_count": metrics.bridge_count,
        "top_hubs": metrics.top_hubs[:10],
        "edge_type_counts": metrics.edge_type_counts,
        "target_hub_degree": hub_degree(metrics.top_hubs, "main_cookiecutter"),
        "orchestration_hub_sum": sum(
            count for node, count in degree.items() if "orchestration" in node
        ),
        "spof_count": sum(1 for bug in bugs if bug.bug_type == "SPOF"),
        "hub_count": sum(1 for bug in bugs if bug.bug_type == "HUB"),
    }


def compare_metrics(before: dict, after: dict) -> dict[str, Any]:
    before_hub = hub_degree(before.get("top_hubs", []), "main_cookiecutter")
    after_hub = after["target_hub_degree"]
    return {
        "bug_fixed": "cookiecutter() HUB in main.py",
        "node_count": {"before": before["node_count"], "after": after["node_count"]},
        "edge_count": {"before": before["edge_count"], "after": after["edge_count"]},
        "community_count": {
            "before": before["community_count"],
            "after": after["community_count"],
        },
        "bridge_count": {"before": before["bridge_count"], "after": after["bridge_count"]},
        "main_cookiecutter_hub_degree": {"before": before_hub, "after": after_hub},
        "orchestration_hub_sum_after": after["orchestration_hub_sum"],
        "spof_count": {"before": before.get("spof_count"), "after": after["spof_count"]},
        "hub_count": {"before": before.get("hub_count"), "after": after["hub_count"]},
        "improved": after["orchestration_hub_sum"] > 0,
    }
