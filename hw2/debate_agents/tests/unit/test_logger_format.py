"""Tests for DebateLogger JSON format, level filtering, and config-driven settings."""

from __future__ import annotations

import json
from datetime import datetime
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


class TestJsonFormat:
    def test_each_line_is_valid_json(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        logger.log("INFO", "father", "intervention", {"round": 1})
        for line in logger.get_log_files()[0].read_text(encoding="utf-8").splitlines():
            if line.strip():
                assert isinstance(json.loads(line), dict)

    def test_entry_has_all_required_fields(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        logger.log("WARNING", "gatekeeper", "api_call", {"tokens": 42})
        entry = json.loads(logger.get_log_files()[0].read_text(encoding="utf-8").strip())
        assert {"timestamp", "level", "agent", "event", "data"}.issubset(entry.keys())
        assert entry["level"] == "WARNING"
        assert entry["agent"] == "gatekeeper"
        assert entry["event"] == "api_call"
        assert entry["data"]["tokens"] == 42

    def test_timestamp_is_iso_format(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        logger.log("INFO", "pro", "argument")
        entry = json.loads(logger.get_log_files()[0].read_text(encoding="utf-8").strip())
        datetime.fromisoformat(entry["timestamp"])

    def test_data_defaults_to_empty_dict(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        logger.log("INFO", "con", "argument")
        entry = json.loads(logger.get_log_files()[0].read_text(encoding="utf-8").strip())
        assert entry["data"] == {}


class TestLevelFiltering:
    def test_info_logged_when_level_is_info(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        logger.log("INFO", "pro", "argument")
        assert "INFO" in logger.get_log_files()[0].read_text(encoding="utf-8")

    def test_debug_filtered_when_level_is_info(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        logger.log("DEBUG", "pro", "argument")
        assert "DEBUG" not in logger.get_log_files()[0].read_text(encoding="utf-8")

    def test_warning_passes_when_level_is_info(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        logger.log("WARNING", "con", "error")
        assert "WARNING" in logger.get_log_files()[0].read_text(encoding="utf-8")

    def test_info_filtered_when_level_is_warning(self, tmp_path: Path) -> None:
        cfg = {**CONFIG, "level": "WARNING"}
        logger = _make_logger(tmp_path, config=cfg)
        logger.log("INFO", "pro", "argument")
        assert "INFO" not in logger.get_log_files()[0].read_text(encoding="utf-8")

    def test_error_always_logged(self, tmp_path: Path) -> None:
        cfg = {**CONFIG, "level": "WARNING"}
        logger = _make_logger(tmp_path, config=cfg)
        logger.log("ERROR", "watchdog", "restart")
        assert "ERROR" in logger.get_log_files()[0].read_text(encoding="utf-8")


class TestConfigDriven:
    def test_custom_max_lines_respected(self, tmp_path: Path) -> None:
        cfg = {**CONFIG, "max_lines_per_file": 2}
        logger = _make_logger(tmp_path, config=cfg)
        logger.log("INFO", "pro", "argument")
        logger.log("INFO", "pro", "argument")
        logger.log("INFO", "pro", "argument")
        assert len(logger.get_log_files()) == 2

    def test_convenience_methods_use_correct_levels(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        logger.info("pro", "argument")
        logger.warning("con", "rebuttal")
        logger.error("watchdog", "restart")
        content = logger.get_log_files()[0].read_text(encoding="utf-8")
        entries = [json.loads(ln) for ln in content.splitlines() if ln.strip()]
        assert [e["level"] for e in entries] == ["INFO", "WARNING", "ERROR"]
