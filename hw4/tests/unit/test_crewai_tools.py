"""Unit tests for crewai_tools/tools.py — covers all 4 @tool decorated functions."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from hw4.crewai_tools.tools import (
    load_graph_metrics,
    read_obsidian_files,
    read_source_snippet,
    run_unit_tests,
)

_GRAPH = {
    "nodes": [
        {"id": "a", "community": 0},
        {"id": "b", "community": 0},
        {"id": "c", "community": 1},
    ],
    "links": [
        {"source": "a", "target": "b", "relation": "calls"},
        {"source": "b", "target": "c", "relation": "imports"},
    ],
}


def _graph_file(tmp_path: Path, data: dict | None = None) -> Path:
    p = tmp_path / "graph.json"
    p.write_text(json.dumps(data or _GRAPH), encoding="utf-8")
    return p


# ── load_graph_metrics ────────────────────────────────────────────────────────

def test_load_graph_metrics_returns_correct_counts(tmp_path: Path) -> None:
    path = _graph_file(tmp_path)
    result = load_graph_metrics.run(str(path))
    data = json.loads(result)
    assert data["node_count"] == 3
    assert data["edge_count"] == 2
    assert data["community_count"] == 2
    assert "bridge_count" in data
    assert "top_20_hubs" in data


def test_load_graph_metrics_empty_graph(tmp_path: Path) -> None:
    path = _graph_file(tmp_path, {"nodes": [], "links": []})
    result = load_graph_metrics.run(str(path))
    data = json.loads(result)
    assert data["node_count"] == 0
    assert data["edge_count"] == 0
    assert data["community_count"] == 0
    assert data["bridge_count"] == 0


def test_load_graph_metrics_edge_type_counts(tmp_path: Path) -> None:
    path = _graph_file(tmp_path)
    result = load_graph_metrics.run(str(path))
    data = json.loads(result)
    edge_types = data["edge_type_counts"]
    assert edge_types.get("calls") == 1
    assert edge_types.get("imports") == 1


# ── read_obsidian_files ───────────────────────────────────────────────────────

def test_read_obsidian_files_reads_both_files(tmp_path: Path) -> None:
    (tmp_path / "hot.md").write_text("hot content here", encoding="utf-8")
    (tmp_path / "index.md").write_text("index content", encoding="utf-8")
    result = read_obsidian_files.run(obsidian_dir=str(tmp_path), max_chars=100)
    data = json.loads(result)
    assert "hot.md" in data
    assert "index.md" in data
    assert data["hot.md"] == "hot content here"


def test_read_obsidian_files_missing_files_returns_empty_dict(tmp_path: Path) -> None:
    result = read_obsidian_files.run(obsidian_dir=str(tmp_path), max_chars=100)
    data = json.loads(result)
    assert data == {}


def test_read_obsidian_files_truncates_at_max_chars(tmp_path: Path) -> None:
    (tmp_path / "hot.md").write_text("A" * 500, encoding="utf-8")
    result = read_obsidian_files.run(obsidian_dir=str(tmp_path), max_chars=10)
    data = json.loads(result)
    assert len(data["hot.md"]) == 10


# ── read_source_snippet ───────────────────────────────────────────────────────

def test_read_source_snippet_returns_content(tmp_path: Path) -> None:
    src = tmp_path / "hello.py"
    src.write_text("def foo(): pass\n", encoding="utf-8")
    result = read_source_snippet.run(file_path=str(src), max_chars=50)
    assert "def foo" in result


def test_read_source_snippet_file_not_found() -> None:
    result = read_source_snippet.run("/nonexistent/path/foo.py")
    assert "not found" in result.lower() or "File not found" in result


def test_read_source_snippet_truncates(tmp_path: Path) -> None:
    src = tmp_path / "big.py"
    src.write_text("x" * 200, encoding="utf-8")
    result = read_source_snippet.run(file_path=str(src), max_chars=5)
    assert len(result) == 5


# ── run_unit_tests ────────────────────────────────────────────────────────────

def test_run_unit_tests_passes(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "...\nTOTAL    100    5    95%\n"

    with patch("hw4.crewai_tools.tools.subprocess.run", return_value=mock_result):
        result = run_unit_tests.run(str(tmp_path))

    data = json.loads(result)
    assert data["passed"] is True
    assert data["coverage_percent"] == 95.0


def test_run_unit_tests_fails(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = "FAILED\nTOTAL    100    20    80%\n"

    with patch("hw4.crewai_tools.tools.subprocess.run", return_value=mock_result):
        result = run_unit_tests.run(str(tmp_path))

    data = json.loads(result)
    assert data["passed"] is False
    assert data["coverage_percent"] == 80.0


def test_run_unit_tests_no_total_line(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "collected 0 items\n"

    with patch("hw4.crewai_tools.tools.subprocess.run", return_value=mock_result):
        result = run_unit_tests.run(str(tmp_path))

    data = json.loads(result)
    assert data["coverage_percent"] == 0.0
