from __future__ import annotations

import json
import os
import subprocess
from collections import Counter
from pathlib import Path

import networkx as nx

from hw4.models.graph_models import Edge, Graph, GraphMetrics, Node
from hw4.shared.gatekeeper import ApiGatekeeper


class GraphBuilderService:
    """Wraps the Grphify CLI to build and load the code dependency graph."""

    def __init__(self, gatekeeper: ApiGatekeeper, config: dict) -> None:
        self._gatekeeper = gatekeeper
        self._config = config

    def clone_repo(self, url: str, dest: str) -> None:
        """Clone a git repository from url into dest via the gatekeeper."""
        self._gatekeeper.execute(
            subprocess.run,
            ["git", "clone", url, dest],
            check=True,
        )

    @staticmethod
    def graphify_out_dir(artifacts_dir: Path) -> Path:
        """Return the path where Grphify writes its output files."""
        return artifacts_dir / "graphify-out"

    @staticmethod
    def package_dir(project_root: Path, paths: dict) -> Path:
        """Return the cookiecutter package directory to scan."""
        return project_root / paths["data"] / "cookiecutter" / "cookiecutter"

    def run_grphify(
        self,
        source_path: str | Path,
        artifacts_dir: str | Path,
        backend: str = "claude",
    ) -> Path:
        """Run the Grphify extract command on source_path and return the output directory."""
        out_parent = Path(artifacts_dir)
        self._gatekeeper.execute(
            subprocess.run,
            [
                "graphify",
                "extract",
                str(source_path),
                "--backend",
                backend,
                "--out",
                str(out_parent),
            ],
            check=True,
        )
        return self.graphify_out_dir(out_parent)

    def run_graphify_update(
        self,
        package: Path,
        graphify_out: Path,
        project_root: Path,
    ) -> None:
        """Run Grphify update to refresh the graph after a code change."""
        env = {**os.environ, "GRAPHIFY_OUT": str(graphify_out.resolve())}
        pkg_arg = package.resolve().relative_to(project_root.resolve()).as_posix()
        self._gatekeeper.execute(
            subprocess.run,
            ["graphify", "update", pkg_arg],
            cwd=project_root,
            env=env,
            check=True,
        )

    def sync_deliverables(
        self,
        graphify_out: Path,
        artifacts: Path,
        *,
        json_name: str = "graph.json",
        html_name: str = "graph.html",
        report_name: str = "GRAPH_REPORT.md",
    ) -> None:
        """Copy graph.json, graph.html, and GRAPH_REPORT.md from graphify_out into artifacts."""
        for src_name, dst_name in (
            ("graph.json", json_name),
            ("graph.html", html_name),
            ("GRAPH_REPORT.md", report_name),
        ):
            src = graphify_out / src_name
            if src.exists():
                (artifacts / dst_name).write_bytes(src.read_bytes())

    def load_graph(self, graph_json_path: str) -> Graph:
        """Parse a Grphify graph.json file and return a Graph instance."""
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
        """Compute degree, community count, bridge count, and top-hub rankings for graph."""
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
