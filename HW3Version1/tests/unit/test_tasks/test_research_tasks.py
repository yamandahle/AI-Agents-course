"""Tests for tasks/research_tasks.py — research pipeline task factories."""
from __future__ import annotations

from unittest.mock import MagicMock, patch


def _mock_agent() -> MagicMock:
    return MagicMock()


def test_make_research_batch_task_creates_task_with_human_input() -> None:
    agent = _mock_agent()
    with patch("article_writer.tasks.research_tasks.Task") as MockTask:
        MockTask.return_value = MagicMock()
        from article_writer.tasks.research_tasks import make_research_batch_task
        make_research_batch_task(agent, "AI in healthcare")
    kwargs = MockTask.call_args.kwargs
    assert kwargs["human_input"] is False
    assert "AI in healthcare" in kwargs["description"]


def test_make_research_filter_task_has_context() -> None:
    agent = _mock_agent()
    batch_task = MagicMock()
    with patch("article_writer.tasks.research_tasks.Task") as MockTask:
        MockTask.return_value = MagicMock()
        from article_writer.tasks.research_tasks import make_research_filter_task
        make_research_filter_task(agent, batch_task)
    kwargs = MockTask.call_args.kwargs
    assert batch_task in kwargs["context"]


def test_make_research_artifact_task_has_context() -> None:
    agent = _mock_agent()
    filter_task = MagicMock()
    with patch("article_writer.tasks.research_tasks.Task") as MockTask:
        MockTask.return_value = MagicMock()
        from article_writer.tasks.research_tasks import make_research_artifact_task
        make_research_artifact_task(agent, filter_task)
    kwargs = MockTask.call_args.kwargs
    assert filter_task in kwargs["context"]
    assert "research.md" in kwargs["expected_output"]
