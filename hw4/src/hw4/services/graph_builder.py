from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path

import networkx as nx

from hw4.models.graph_models import Edge, Graph, GraphMetrics, Node
from hw4.shared.gatekeeper import ApiGatekeeper


class GraphBuilderService:
    def __init__(self, gatekeeper: ApiGatekeeper, config: dict) -> None:
        self._gatekeeper = gatekeeper
        self._config = config

    def clone_repo(self, url: str, dest: str) -> None:
        self._gatekeeper.execute(
            subprocess.run,
            ["git", "clone", url, dest],
            check=True,
        )

    def run_grphify(self, source_path: str, backend: str = "claude") -> None:
        self._gatekeeper.execute(
            subprocess.run,
            ["graphify", "extract", source_path, "--backend", backend],
            check=True,
        )

    def load_graph(self, graph_json_path: str) -> Graph:
        data = json.loads(Path(graph_json_path).read_text(encoding="utf-8"))
        nodes = [
            Node(
                id=n["id"],
                label=n.get("label", n["id"]),
                file_type=n.get("file_type", ""),
                source_file=n.get("source_file", ""),
                community=n.get("community", -1),
            )
            for n in data.get("nodes", [])
        ]
        edges = [
            Edge(
                source=e["source"],
                target=e["target"],
                relation=e.get("relation", ""),
            )
            for e in data.get("links", [])
        ]
        return Graph(nodes=nodes, edges=edges)

    def compute_metrics(self, graph: Graph) -> GraphMetrics:
        degree: Counter = Counter()
        for e in graph.edges:
            degree[e.source] += 1
            degree[e.target] += 1

        edge_types = Counter(e.relation for e in graph.edges)
        communities = {n.community for n in graph.nodes if n.community >= 0}

        g = nx.DiGraph()
        g.add_nodes_from(n.id for n in graph.nodes)
        g.add_edges_from((e.source, e.target) for e in graph.edges)
        bridge_count = sum(1 for _ in nx.bridges(g.to_undirected()))

        top_n = self._config.get("top_n_nodes", 20)
        top_hubs = degree.most_common(top_n)

        return GraphMetrics(
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            community_count=len(communities),
            top_hubs=top_hubs,
            bridge_count=bridge_count,
            edge_type_counts=dict(edge_types),
        )
