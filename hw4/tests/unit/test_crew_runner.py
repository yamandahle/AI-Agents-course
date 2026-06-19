from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from hw4.services.crew_runner import CrewRunnerService

MOCK_GRAPH = {
    "nodes": [
        {"id": f"n{i}", "label": f"fn{i}", "file_type": "code", "source_file": f"f{i}.py", "community": 0}
        for i in range(12)
    ],
    "links": [
        {"source": f"n{i}", "target": "n0", "relation": "calls"}
        for i in range(1, 12)
    ],
}


@pytest.fixture
def workspace(tmp_path: Path) -> dict[str, Path]:
    artifacts = tmp_path / "artifacts"
    obsidian = tmp_path / "obsidian"
    results = tmp_path / "results"
    data = tmp_path / "data" / "cookiecutter" / "cookiecutter"
    for folder in (artifacts, obsidian, results, data):
        folder.mkdir(parents=True)
    (artifacts / "graph.json").write_text(json.dumps(MOCK_GRAPH), encoding="utf-8")
    (obsidian / "hot.md").write_text("# hot", encoding="utf-8")
    (obsidian / "index.md").write_text("# index", encoding="utf-8")
    (data / "main.py").write_text("def main():\n    pass\n", encoding="utf-8")
    (results / "metrics_before.json").write_text(
        json.dumps({"top_hubs": [["n0", 11]]}),
        encoding="utf-8",
    )
    return {
        "artifacts": artifacts,
        "obsidian": obsidian,
        "results": results,
        "data": tmp_path / "data",
        "root": tmp_path,
    }


def test_crew_runner_saves_json(workspace: dict[str, Path]) -> None:
    paths = {
        "artifacts": str(workspace["artifacts"]) + "/",
        "obsidian": str(workspace["obsidian"]) + "/",
        "results": str(workspace["results"]) + "/",
        "data": str(workspace["data"]) + "/",
    }
    runner = CrewRunnerService(
        MagicMock(),
        {"top_n_nodes": 5, "hub_degree_threshold": 5, "max_prompt_tokens": 500},
        paths,
    )
    payload = runner.run()
    assert payload["bugs"]
    assert payload["proposals"]
    assert (workspace["results"] / "agent_run.json").exists()
    assert "savings_percent" in payload["token_stats"]
    assert payload["token_stats"]["graph_guided_tokens_estimated"] > 0
