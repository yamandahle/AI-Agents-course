from __future__ import annotations

import networkx as nx

from hw4.models.agent_models import ArchitecturalBug, GraphSummary
from hw4.models.graph_models import Graph


class BugDetectorService:
    """Detects HUB, SPOF, and WEAK_BRIDGE defects from a code dependency graph."""

    def __init__(self, hub_degree_threshold: int = 10, max_bugs: int = 5) -> None:
        self._hub_threshold = hub_degree_threshold
        self._max_bugs = max_bugs

    def detect(self, graph: Graph, summary: GraphSummary) -> list[ArchitecturalBug]:
        """Return up to max_bugs ranked architectural bugs found in graph."""
        bugs: list[ArchitecturalBug] = []
        bugs.extend(self._find_hubs(graph))
        bugs.extend(self._find_spofs(graph))
        bugs.extend(self._find_bridges(graph, summary.bridge_count))
        return self._rank(bugs)[: self._max_bugs]

    def _find_hubs(self, graph: Graph) -> list[ArchitecturalBug]:
        degree = self._degree_map(graph)
        bugs: list[ArchitecturalBug] = []
        for node_id, count in degree.items():
            if count <= self._hub_threshold:
                continue
            node = self._node_by_id(graph, node_id)
            label = node.label if node else node_id
            bugs.append(
                ArchitecturalBug(
                    bug_type="HUB",
                    node_name=label,
                    severity="HIGH" if count >= self._hub_threshold + 5 else "MEDIUM",
                    explanation=f"Hub degree {count} exceeds threshold {self._hub_threshold}.",
                    source_file=node.source_file if node else "",
                )
            )
        return bugs

    def _find_spofs(self, graph: Graph) -> list[ArchitecturalBug]:
        base = self._nx_graph(graph)
        if base.number_of_nodes() == 0:
            return []
        base_components = nx.number_connected_components(base)
        degree = self._degree_map(graph)
        bugs: list[ArchitecturalBug] = []
        for node_id in sorted(degree, key=degree.get, reverse=True)[:15]:
            trial = base.copy()
            if node_id not in trial:
                continue
            trial.remove_node(node_id)
            if nx.number_connected_components(trial) <= base_components:
                continue
            node = self._node_by_id(graph, node_id)
            label = node.label if node else node_id
            bugs.append(
                ArchitecturalBug(
                    bug_type="SPOF",
                    node_name=label,
                    severity="HIGH",
                    explanation="Removing this node increases disconnected components.",
                    source_file=node.source_file if node else "",
                )
            )
        return bugs

    def _find_bridges(self, graph: Graph, bridge_count: int) -> list[ArchitecturalBug]:
        if bridge_count == 0:
            return []
        undirected = self._nx_graph(graph).to_undirected()
        bugs: list[ArchitecturalBug] = []
        for source, target in list(nx.bridges(undirected))[:3]:
            bugs.append(
                ArchitecturalBug(
                    bug_type="WEAK_BRIDGE",
                    node_name=f"{source} -> {target}",
                    severity="MEDIUM",
                    explanation="Bridge edge connects communities; single dependency risk.",
                    source_file="",
                )
            )
        return bugs

    def _rank(self, bugs: list[ArchitecturalBug]) -> list[ArchitecturalBug]:
        order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        return sorted(bugs, key=lambda bug: (order[bug.severity], bug.bug_type))

    def _degree_map(self, graph: Graph) -> dict[str, int]:
        degree: dict[str, int] = {}
        for edge in graph.edges:
            degree[edge.source] = degree.get(edge.source, 0) + 1
            degree[edge.target] = degree.get(edge.target, 0) + 1
        return degree

    def _nx_graph(self, graph: Graph) -> nx.Graph:
        g = nx.Graph()
        g.add_nodes_from(n.id for n in graph.nodes)
        g.add_edges_from((e.source, e.target) for e in graph.edges)
        return g

    def _node_by_id(self, graph: Graph, node_id: str):
        for node in graph.nodes:
            if node.id == node_id:
                return node
        return None
