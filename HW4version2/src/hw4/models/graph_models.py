from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Node:
    """A single Python symbol (function, class, or module) in the dependency graph."""

    id: str
    label: str
    file_type: str = ""
    source_file: str = ""
    community: int = -1


@dataclass
class Edge:
    """A directed dependency relationship between two nodes in the graph."""

    source: str
    target: str
    relation: str


@dataclass
class Graph:
    """In-memory representation of the full code dependency graph."""

    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def node_ids(self) -> set[str]:
        """Return the set of all node IDs in the graph."""
        return {n.id for n in self.nodes}


@dataclass
class GraphMetrics:
    """Computed structural metrics derived from a Graph instance."""

    node_count: int
    edge_count: int
    community_count: int
    top_hubs: list[tuple[str, int]]
    bridge_count: int
    edge_type_counts: dict[str, int] = field(default_factory=dict)
