"""CrewAI tools — stateless functions the agents can call during reasoning."""

from __future__ import annotations

import contextlib
import json
import subprocess
from collections import Counter
from pathlib import Path

import networkx as nx
from crewai.tools import tool


@tool("Load Graph Metrics")
def load_graph_metrics(graph_json_path: str) -> str:
    """Read graph.json and return node_count, edge_count, community_count, bridge_count,
    top_20_hubs (node_id + degree), and edge_type_counts. Always call this first."""
    data = json.loads(Path(graph_json_path).read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("links", [])

    degree: Counter = Counter()
    for e in edges:
        degree[e["source"]] += 1
        degree[e["target"]] += 1

    communities = {n.get("community", -1) for n in nodes if n.get("community", -1) >= 0}
    edge_types = Counter(e.get("relation", "") for e in edges)

    g = nx.DiGraph()
    g.add_nodes_from(n["id"] for n in nodes)
    g.add_edges_from((e["source"], e["target"]) for e in edges)
    bridge_count = sum(1 for _ in nx.bridges(g.to_undirected()))

    return json.dumps({
        "node_count": len(nodes),
        "edge_count": len(edges),
        "community_count": len(communities),
        "bridge_count": bridge_count,
        "top_20_hubs": degree.most_common(20),
        "edge_type_counts": dict(edge_types),
    }, indent=2)


@tool("Read Obsidian Navigation Files")
def read_obsidian_files(obsidian_dir: str, max_chars: int = 2000) -> str:
    """Read hot.md and index.md from the Obsidian vault. Returns the first max_chars
    characters of each. Use this to understand which files are architecturally hot."""
    result = {}
    for filename in ("hot.md", "index.md"):
        path = Path(obsidian_dir) / filename
        if path.exists():
            result[filename] = path.read_text(encoding="utf-8")[:max_chars]
    return json.dumps(result, indent=2)


@tool("Read Source File Snippet")
def read_source_snippet(file_path: str, max_chars: int = 1500) -> str:
    """Read the first max_chars characters of a source file by full or relative path.
    Use this to inspect a hot file before proposing a fix — never read more than needed."""
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"
    return path.read_text(encoding="utf-8")[:max_chars]


@tool("Run Unit Tests")
def run_unit_tests(project_root: str = ".") -> str:
    """Run pytest on tests/unit with coverage. Returns verdict, coverage_percent, and
    the last 800 chars of pytest output. Call this after a fix is applied."""
    result = subprocess.run(
        ["uv", "run", "pytest", "tests/unit", "-q", "--cov=src", "--cov-report=term-missing"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    coverage = 0.0
    for line in result.stdout.splitlines():
        if line.strip().startswith("TOTAL"):
            with contextlib.suppress(ValueError):
                coverage = float(line.split()[-1].rstrip("%"))
    return json.dumps({
        "passed": result.returncode == 0,
        "coverage_percent": coverage,
        "output_tail": result.stdout[-800:],
    }, indent=2)
