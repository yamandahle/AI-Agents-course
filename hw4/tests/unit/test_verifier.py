from __future__ import annotations

import json
from pathlib import Path

from hw4.agents.verifier import VerifierAgent
from hw4.models.agent_models import ArchitecturalBug, FixProposal, GraphSummary


def test_verifier_reports_counts(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics_before.json"
    metrics.write_text(json.dumps({"top_hubs": [["hub", 10]]}), encoding="utf-8")
    summary = GraphSummary(
        node_count=10,
        edge_count=20,
        community_count=2,
        top_hubs=[("hub", 12)],
        bridge_count=1,
        hot_excerpt="",
        index_excerpt="",
    )
    bug = ArchitecturalBug("HUB", "hub", "HIGH", "too connected")
    proposal = FixProposal(bug, "hub.py", "split module", "reduce coupling")
    report = VerifierAgent(str(metrics)).run(summary, 1, [proposal])
    assert report.bugs_found == 1
    assert report.proposals_count == 1
    assert report.tests_passed is True
