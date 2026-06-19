from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

BugType = Literal["SPOF", "HUB", "WEAK_BRIDGE"]
Severity = Literal["HIGH", "MEDIUM", "LOW"]


@dataclass
class ArchitecturalBug:
    bug_type: BugType
    node_name: str
    severity: Severity
    explanation: str
    source_file: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FixProposal:
    bug: ArchitecturalBug
    target_file: str
    change_description: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["bug"] = self.bug.to_dict()
        return data


@dataclass
class GraphSummary:
    node_count: int
    edge_count: int
    community_count: int
    top_hubs: list[tuple[str, int]]
    bridge_count: int
    hot_excerpt: str
    index_excerpt: str
    navigation_files: list[str] = field(default_factory=list)
    files_read: int = 0
    estimated_tokens: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "community_count": self.community_count,
            "top_hubs": self.top_hubs,
            "bridge_count": self.bridge_count,
            "hot_excerpt": self.hot_excerpt,
            "index_excerpt": self.index_excerpt,
            "navigation_files": self.navigation_files,
            "files_read": self.files_read,
            "estimated_tokens": self.estimated_tokens,
        }


@dataclass
class VerificationReport:
    fix_applied: bool
    tests_passed: bool
    centrality_delta: float
    summary: str
    bugs_found: int = 0
    proposals_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
