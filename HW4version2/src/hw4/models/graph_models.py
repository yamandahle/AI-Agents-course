from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Node:
    id: str
    label: str
    file_type: str = ""
    source_file: str = ""
    community: int = -1


@dataclass
class Edge:
    source: str
    target: str
    relation: str


@dataclass
class Graph:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def node_ids(self) -> set[str]:
        return {n.id for n in self.nodes}


@dataclass
class GraphMetrics:
    node_count: int
    edge_count: int
    community_count: int
    top_hubs: list[tuple[str, int]]
    bridge_count: int
    edge_type_counts: dict[str, int] = field(default_factory=dict)
