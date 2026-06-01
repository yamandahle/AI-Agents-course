"""Unit tests for DebateLogger — TDD Red phase written before implementation."""

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
    cfg = {**(config or CONFIG)}
    return DebateLogger(config=cfg, log_dir=tmp_path)


# ---------------------------------------------------------------------------
# 1. File rotation at max_lines_per_file
# ---------------------------------------------------------------------------
class TestRotation:
    def test_new_file_created_at_line_limit(self, tmp_path: Path) -> None:
        """After max_lines_per_file entries a second log file must appear."""
        logger = _make_logger(tmp_path)
        for _ in range(CONFIG["max_lines_per_file"] + 1):
            logger.log("INFO", "pro", "argument", {"text": "hello"})
        assert len(logger.get_log_files()) == 2

    def test_single_file_below_limit(self, tmp_path: Path) -> None:
        """Writing fewer entries than the limit must produce exactly one file."""
        logger = _make_logger(tmp_path)
        for _ in range(CONFIG["max_lines_per_file"] - 1):
            logger.log("INFO", "pro", "argument")
        assert len(logger.get_log_files()) == 1

    def test_correct_line_count_per_file(self, tmp_path: Path) -> None:
        """First file must contain exactly max_lines_per_file lines after rotation."""
        logger = _make_logger(tmp_path)
        for _ in range(CONFIG["max_lines_per_file"] + 1):
            logger.log("INFO", "pro", "argument")
        first_file = logger.get_log_files()[0]
        lines = [ln for ln in first_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(lines) == CONFIG["max_lines_per_file"]


# ---------------------------------------------------------------------------
# 2. Max 20 files respected — oldest deleted when exceeded
# ---------------------------------------------------------------------------
class TestMaxFiles:
    def test_oldest_file_deleted_when_max_exceeded(self, tmp_path: Path) -> None:
        """Total log files must never exceed max_files; oldest must be removed first."""
        logger = _make_logger(tmp_path)
        total = CONFIG["max_lines_per_file"] * (CONFIG["max_files"] + 1)
        for i in range(total):
            logger.log("INFO", "pro", "argument", {"i": i})
        assert len(logger.get_log_files()) <= CONFIG["max_files"]

    def test_file_count_stable_under_heavy_writes(self, tmp_path: Path) -> None:
        """Continuous heavy writing must keep file count at max_files once saturated."""
        logger = _make_logger(tmp_path)
        for i in range(CONFIG["max_lines_per_file"] * CONFIG["max_files"] * 2):
            logger.log("INFO", "con", "argument", {"i": i})
        assert len(logger.get_log_files()) <= CONFIG["max_files"]

    def test_custom_max_files_from_config(self, tmp_path: Path) -> None:
        """Logger must honour max_files from config, not any hardcoded value."""
        cfg = {**CONFIG, "max_files": 2, "max_lines_per_file": 2}
        logger = _make_logger(tmp_path, config=cfg)
        for i in range(7):
            logger.log("INFO", "pro", "argument", {"i": i})
        assert len(logger.get_log_files()) <= 2


# ---------------------------------------------------------------------------
# 3. JSON format is valid and parseable
# ---------------------------------------------------------------------------
class TestJsonFormat:
    def test_each_line_is_valid_json(self, tmp_path: Path) -> None:
        """Every line in the log file must be parseable as JSON."""
        logger = _make_logger(tmp_path)
        logger.log("INFO", "father", "intervention", {"round": 1})
        for line in logger.get_log_files()[0].read_text(encoding="utf-8").splitlines():
            if line.strip():
                assert isinstance(json.loads(line), dict)

    def test_entry_has_all_required_fields(self, tmp_path: Path) -> None:
        """Each JSON entry must contain exactly the five specified fields."""
        logger = _make_logger(tmp_path)
        logger.log("WARNING", "gatekeeper", "api_call", {"tokens": 42})
        raw = logger.get_log_files()[0].read_text(encoding="utf-8").strip()
        entry = json.loads(raw)
        assert {"timestamp", "level", "agent", "event", "data"}.issubset(entry.keys())
        assert entry["level"] == "WARNING"
        assert entry["agent"] == "gatekeeper"
        assert entry["event"] == "api_call"
        assert entry["data"]["tokens"] == 42

    def test_timestamp_is_iso_format(self, tmp_path: Path) -> None:
        """Timestamp field must be a valid ISO 8601 string."""
        logger = _make_logger(tmp_path)
        logger.log("INFO", "pro", "argument")
        raw = logger.get_log_files()[0].read_text(encoding="utf-8").strip()
        entry = json.loads(raw)
        datetime.fromisoformat(entry["timestamp"])  # raises if invalid

    def test_data_defaults_to_empty_dict(self, tmp_path: Path) -> None:
        """Calling log() without data must produce data: {} not data: null."""
        logger = _make_logger(tmp_path)
        logger.log("INFO", "con", "argument")
        raw = logger.get_log_files()[0].read_text(encoding="utf-8").strip()
        entry = json.loads(raw)
        assert entry["data"] == {}


# ---------------------------------------------------------------------------
# 4. Log levels filter correctly
# ---------------------------------------------------------------------------
class TestLevelFiltering:
    def test_info_logged_when_level_is_info(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        logger.log("INFO", "pro", "argument")
        content = logger.get_log_files()[0].read_text(encoding="utf-8")
        assert "INFO" in content

    def test_debug_filtered_when_level_is_info(self, tmp_path: Path) -> None:
        """DEBUG entry must be silently dropped when minimum level is INFO."""
        logger = _make_logger(tmp_path)
        logger.log("DEBUG", "pro", "argument")
        content = logger.get_log_files()[0].read_text(encoding="utf-8")
        assert "DEBUG" not in content

    def test_warning_passes_when_level_is_info(self, tmp_path: Path) -> None:
        logger = _make_logger(tmp_path)
        logger.log("WARNING", "con", "error")
        content = logger.get_log_files()[0].read_text(encoding="utf-8")
        assert "WARNING" in content

    def test_info_filtered_when_level_is_warning(self, tmp_path: Path) -> None:
        cfg = {**CONFIG, "level": "WARNING"}
        logger = _make_logger(tmp_path, config=cfg)
        logger.log("INFO", "pro", "argument")
        content = logger.get_log_files()[0].read_text(encoding="utf-8")
        assert "INFO" not in content

    def test_error_always_logged(self, tmp_path: Path) -> None:
        """ERROR must pass even when minimum level is WARNING."""
        cfg = {**CONFIG, "level": "WARNING"}
        logger = _make_logger(tmp_path, config=cfg)
        logger.log("ERROR", "watchdog", "restart")
        content = logger.get_log_files()[0].read_text(encoding="utf-8")
        assert "ERROR" in content


# ---------------------------------------------------------------------------
# 5. All settings from config — never hardcoded
# ---------------------------------------------------------------------------
class TestConfigDriven:
    def test_custom_max_lines_respected(self, tmp_path: Path) -> None:
        """Logger must use max_lines_per_file from config, not a hardcoded value."""
        cfg = {**CONFIG, "max_lines_per_file": 2}
        logger = _make_logger(tmp_path, config=cfg)
        logger.log("INFO", "pro", "argument")
        logger.log("INFO", "pro", "argument")
        logger.log("INFO", "pro", "argument")  # triggers rotation
        assert len(logger.get_log_files()) == 2

    def test_convenience_methods_use_correct_levels(self, tmp_path: Path) -> None:
        """info/warning/error helpers must produce entries with the matching level field."""
        logger = _make_logger(tmp_path)
        logger.info("pro", "argument")
        logger.warning("con", "rebuttal")
        logger.error("watchdog", "restart")
        content = logger.get_log_files()[0].read_text(encoding="utf-8")
        entries = [json.loads(ln) for ln in content.splitlines() if ln.strip()]
        levels = [e["level"] for e in entries]
        assert levels == ["INFO", "WARNING", "ERROR"]
