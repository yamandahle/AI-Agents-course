"""Unit tests for crewai_tasks/tasks.py."""
from __future__ import annotations

from unittest.mock import MagicMock, patch


def _make_agents() -> dict:
    return {
        "graph_navigator": MagicMock(),
        "architect_detective": MagicMock(),
        "fix_strategist": MagicMock(),
        "quality_gate": MagicMock(),
    }


def test_build_tasks_returns_four_tasks() -> None:
    from hw4.crewai_tasks.tasks import build_tasks

    agents = _make_agents()
    with patch("hw4.crewai_tasks.tasks.Task") as mock_task:
        mock_task.return_value = MagicMock()
        tasks = build_tasks(agents, "/g.json", "/ga.json", "/obs", "/cook", ".")
    assert len(tasks) == 4
    assert mock_task.call_count == 4


def test_tasks_reference_correct_agents() -> None:
    from hw4.crewai_tasks.tasks import build_tasks

    agents = _make_agents()
    created_calls = []

    def capture(**kwargs):
        created_calls.append(kwargs)
        return MagicMock()

    with patch("hw4.crewai_tasks.tasks.Task", side_effect=capture):
        build_tasks(agents, "/g.json", "/ga.json", "/obs", "/cook", ".")

    assert created_calls[0]["agent"] is agents["graph_navigator"]
    assert created_calls[1]["agent"] is agents["architect_detective"]
    assert created_calls[2]["agent"] is agents["fix_strategist"]
    assert created_calls[3]["agent"] is agents["quality_gate"]


def test_tasks_have_context_chaining() -> None:
    from hw4.crewai_tasks.tasks import build_tasks

    agents = _make_agents()
    task_mocks = [MagicMock() for _ in range(4)]
    call_idx = [0]

    def make_task(**kwargs):
        t = task_mocks[call_idx[0]]
        call_idx[0] += 1
        return t

    with patch("hw4.crewai_tasks.tasks.Task", side_effect=make_task):
        build_tasks(agents, "/g.json", "/ga.json", "/obs", "/cook", ".")

    # bug_detection_task should get graph_summary_task in context
    # We verify by inspecting the Task constructor calls via a fresh run
    call_records = []

    def capture_context(**kwargs):
        call_records.append(kwargs.get("context", []))
        return MagicMock()

    with patch("hw4.crewai_tasks.tasks.Task", side_effect=capture_context):
        build_tasks(agents, "/g.json", "/ga.json", "/obs", "/cook", ".")

    assert call_records[0] == []  # graph_summary: no context
    assert len(call_records[1]) == 1  # bug_detection: context = [graph_summary]
    assert len(call_records[2]) == 2  # fix_proposal: context = [graph_summary, bug_detection]
    assert len(call_records[3]) == 3  # verification: context = [graph_summary, bug_detection, fix_proposal]


def test_tasks_embed_paths_in_description() -> None:
    from hw4.crewai_tasks.tasks import build_tasks

    agents = _make_agents()
    descriptions = []

    def capture(**kwargs):
        descriptions.append(kwargs.get("description", ""))
        return MagicMock()

    with patch("hw4.crewai_tasks.tasks.Task", side_effect=capture):
        build_tasks(agents, "/my/graph.json", "/my/graph_after.json", "/obs_dir", "/cook_dir", "/root")

    assert "/my/graph.json" in descriptions[0]
    assert "/obs_dir" in descriptions[0]
    assert "/cook_dir" in descriptions[2]
    assert "/root" in descriptions[3]
