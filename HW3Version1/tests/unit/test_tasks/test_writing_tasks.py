"""Tests for tasks/writing_tasks.py — writing pipeline task factories."""
from __future__ import annotations

from unittest.mock import MagicMock, patch


def _mock_agent() -> MagicMock:
    return MagicMock()


def test_make_context_load_task_has_artifact_context() -> None:
    writer = _mock_agent()
    artifact_task = MagicMock()
    with patch("article_writer.tasks.writing_tasks.Task") as MockTask:
        MockTask.return_value = MagicMock()
        from article_writer.tasks.writing_tasks import make_context_load_task
        make_context_load_task(writer, artifact_task)
    kwargs = MockTask.call_args.kwargs
    assert artifact_task in kwargs["context"]


def test_make_draft_generation_task_expects_tex_output() -> None:
    writer = _mock_agent()
    ctx_task = MagicMock()
    with patch("article_writer.tasks.writing_tasks.Task") as MockTask:
        MockTask.return_value = MagicMock()
        from article_writer.tasks.writing_tasks import make_draft_generation_task
        make_draft_generation_task(writer, ctx_task)
    kwargs = MockTask.call_args.kwargs
    assert "draft_v1.tex" in kwargs["expected_output"]


def test_make_evaluation_task_has_draft_context() -> None:
    evaluator = _mock_agent()
    draft_task = MagicMock()
    with patch("article_writer.tasks.writing_tasks.Task") as MockTask:
        MockTask.return_value = MagicMock()
        from article_writer.tasks.writing_tasks import make_evaluation_task
        make_evaluation_task(evaluator, draft_task)
    kwargs = MockTask.call_args.kwargs
    assert draft_task in kwargs["context"]


def test_make_optimization_task_has_eval_context() -> None:
    writer = _mock_agent()
    eval_task = MagicMock()
    with patch("article_writer.tasks.writing_tasks.Task") as MockTask:
        MockTask.return_value = MagicMock()
        from article_writer.tasks.writing_tasks import make_optimization_task
        make_optimization_task(writer, eval_task)
    kwargs = MockTask.call_args.kwargs
    assert eval_task in kwargs["context"]


def test_make_compilation_task_mentions_pdf() -> None:
    writer = _mock_agent()
    opt_task = MagicMock()
    with patch("article_writer.tasks.writing_tasks.Task") as MockTask:
        MockTask.return_value = MagicMock()
        from article_writer.tasks.writing_tasks import make_compilation_task
        make_compilation_task(writer, opt_task)
    kwargs = MockTask.call_args.kwargs
    assert "article_final.pdf" in kwargs["expected_output"]
