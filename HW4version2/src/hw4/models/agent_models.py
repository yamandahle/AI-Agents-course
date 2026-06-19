from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

BugType = Literal["SPOF", "HUB", "WEAK_BRIDGE"]
Severity = Literal["HIGH", "MEDIUM", "LOW"]
FunctionalBugStatus = Literal["OPEN", "CONFIRMED_HISTORICAL", "NOT_DETECTED"]


@dataclass
class ArchitecturalBug:
    """A structural defect detected in the code dependency graph."""

    bug_type: BugType
    node_name: str
    severity: Severity
    explanation: str
    source_file: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict representation suitable for JSON serialisation."""
        return asdict(self)


@dataclass
class FixProposal:
    """A proposed structural refactor targeting one architectural bug."""

    bug: ArchitecturalBug
    target_file: str
    change_description: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict representation suitable for JSON serialisation."""
        data = asdict(self)
        data["bug"] = self.bug.to_dict()
        return data


@dataclass
class FunctionalBug:
    """A known functional bug from the BugsInPy catalogue cross-referenced with the graph."""

    bugsinpy_id: int
    source_file: str
    description: str
    severity: Severity
    status: FunctionalBugStatus
    graph_hub_match: bool
    buggy_commit: str
    test_file: str

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict representation suitable for JSON serialisation."""
        return asdict(self)


@dataclass
class GraphSummary:
    """Structural summary of the code dependency graph produced by the Graph Navigator."""

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
        """Return a plain dict representation suitable for JSON serialisation."""
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
    """Summary of whether the applied fix passed all quality checks."""

    fix_applied: bool
    tests_passed: bool
    centrality_delta: float
    summary: str
    bugs_found: int = 0
    proposals_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict representation suitable for JSON serialisation."""
        return asdict(self)
