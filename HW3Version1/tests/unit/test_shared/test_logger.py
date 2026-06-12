"""Unit tests for shared/logger.py."""
from __future__ import annotations

import json
from pathlib import Path

from article_writer.shared.logger import ArticleLogger, get_logger


def test_get_logger_returns_article_logger(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    log = get_logger("test.logger")
    assert isinstance(log, ArticleLogger)


def test_log_eval_score_creates_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    log = get_logger("test.eval")
    log.log_eval_score(1, {"coverage": 8, "accuracy": 7})
    log_file = tmp_path / "results" / "eval_log.json"
    assert log_file.exists()
    records = json.loads(log_file.read_text())
    assert len(records) == 1
    assert records[0]["iteration"] == 1


def test_log_eval_score_appends(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    log = get_logger("test.eval2")
    log.log_eval_score(1, {"score": 7})
    log.log_eval_score(2, {"score": 9})
    records = json.loads((tmp_path / "results" / "eval_log.json").read_text())
    assert len(records) == 2


def test_log_api_call_does_not_raise(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    log = get_logger("test.api")
    log.log_api_call("gemini", "test query", "test response")
