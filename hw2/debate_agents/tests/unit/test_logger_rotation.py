"""Tests for DebateLogger file rotation and max-file limit enforcement."""

from __future__ import annotations

from pathlib import Path

from debate.shared.logger import DebateLogger

CONFIG = {
    "version": "1.00",
    "log_dir": "logs",
    "max_files": 3,
    "max_lines_per_file": 5,
    "level": "INFO",
    "format": "{timestamp} | {level} | {source} | {message}",
}


def _make_logger(tmp_path: Path, config: dict | None = None) -> DebateLogger:
    return DebateLogger(config={**(config or CONFIG)}, log_dir=tmp_path)


class TestRotation:
    def test_new_file_created_at_line_limit(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        for _ in range(CONFIG["max_lines_per_file"] + 1):
            logger.log("INFO", "pro", "argument", {"text": "hello"})
        assert len(logger.get_log_files()) == 2

    def test_single_file_below_limit(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        for _ in range(CONFIG["max_lines_per_file"] - 1):
            logger.log("INFO", "pro", "argument")
        assert len(logger.get_log_files()) == 1

    def test_correct_line_count_per_file(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        for _ in range(CONFIG["max_lines_per_file"] + 1):
            logger.log("INFO", "pro", "argument")
        first_file = logger.get_log_files()[0]
        lines = [ln for ln in first_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(lines) == CONFIG["max_lines_per_file"]


class TestMaxFiles:
    def test_oldest_file_deleted_when_max_exceeded(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        total = CONFIG["max_lines_per_file"] * (CONFIG["max_files"] + 1)
        for i in range(total):
            logger.log("INFO", "pro", "argument", {"i": i})
        assert len(logger.get_log_files()) <= CONFIG["max_files"]

    def test_file_count_stable_under_heavy_writes(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        for i in range(CONFIG["max_lines_per_file"] * CONFIG["max_files"] * 2):
            logger.log("INFO", "con", "argument", {"i": i})
        assert len(logger.get_log_files()) <= CONFIG["max_files"]

    def test_custom_max_files_from_config(self, tmp_path: Path) -> None:
        cfg = {**CONFIG, "max_files": 2, "max_lines_per_file": 2}
        logger = _make_logger(tmp_path, config=cfg)
        for i in range(7):
            logger.log("INFO", "pro", "argument", {"i": i})
        assert len(logger.get_log_files()) <= 2
