from __future__ import annotations

from pathlib import Path

from hw4.agents.fix_proposer import FixProposerAgent
from hw4.models.agent_models import ArchitecturalBug, GraphSummary


def test_fix_proposer_returns_proposal(tmp_path: Path) -> None:
    repo = tmp_path / "cookiecutter"
    repo.mkdir()
    (repo / "main.py").write_text("def cookiecutter():\n    pass\n", encoding="utf-8")
    bug = ArchitecturalBug(
        bug_type="SPOF",
        node_name="cookiecutter",
        severity="HIGH",
        explanation="entry point risk",
        source_file="cookiecutter/main.py",
    )
    summary = GraphSummary(
        node_count=1,
        edge_count=0,
        community_count=1,
        top_hubs=[],
        bridge_count=0,
        hot_excerpt="cookiecutter suspect",
        index_excerpt="",
    )
    agent = FixProposerAgent(str(tmp_path))
    proposals = agent.run([bug], summary)
    assert len(proposals) == 1
    assert proposals[0].target_file == "cookiecutter/main.py"
    assert "orchestration" in proposals[0].change_description.lower()
