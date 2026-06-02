"""DebateLogger — structured JSON log writer with FIFO file rotation.

Thread-safe: a single threading.Lock serialises all writes and rotations.
All settings (max_files, max_lines_per_file, level, log_dir) come from the
config dict passed at construction — nothing is hardcoded.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ordered severity levels — used for minimum-level filtering.
_LEVELS: tuple[str, ...] = ("DEBUG", "INFO", "WARNING", "ERROR")


class DebateLogger:
    """Writes structured JSON log entries with automatic FIFO file rotation."""

    def __init__(self, config: dict[str, Any], log_dir: Path | str | None = None) -> None:
        self._max_files: int = config["max_files"]
        self._max_lines: int = config["max_lines_per_file"]
        self._min_level: str = config["level"]

        self._log_dir = Path(log_dir) if log_dir is not None else Path(config["log_dir"])
        self._log_dir.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._current_file: Path | None = None
        self._line_count: int = 0
        self._file_counter: int = 0

        self._open_new_file()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def log(
        self,
        level: str,
        agent: str,
        event: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Write one structured JSON entry if level passes the minimum filter."""
        if not self._passes_level(level):
            return

        entry: dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level": level,
            "agent": agent,
            "event": event,
            "data": data if data is not None else {},
        }

        with self._lock:
            self._rotate_if_needed()
            assert self._current_file is not None
            with self._current_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
            self._line_count += 1

    def info(self, agent: str, event: str, data: dict[str, Any] | None = None) -> None:
        self.log("INFO", agent, event, data)

    def warning(self, agent: str, event: str, data: dict[str, Any] | None = None) -> None:
        self.log("WARNING", agent, event, data)

    def error(self, agent: str, event: str, data: dict[str, Any] | None = None) -> None:
        self.log("ERROR", agent, event, data)

    def get_log_files(self) -> list[Path]:
        """Return all log files sorted oldest-first by mtime then filename."""
        files = list(self._log_dir.glob("debate_*_*.log"))
        return sorted(files, key=lambda p: (p.stat().st_mtime, p.name))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _passes_level(self, level: str) -> bool:
        try:
            return _LEVELS.index(level) >= _LEVELS.index(self._min_level)
        except ValueError:
            return False

    def _open_new_file(self) -> None:
        """Create a fresh log file and reset the line counter."""
        self._file_counter += 1
        ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        self._current_file = self._log_dir / f"debate_{ts}_{self._file_counter:04d}.log"
        self._current_file.touch()
        self._line_count = 0

    def _rotate_if_needed(self) -> None:
        """Open a new file when the current one is full, then prune excess files."""
        if self._line_count >= self._max_lines:
            self._open_new_file()
            self._prune_old_files()

    def _prune_old_files(self) -> None:
        """Delete the oldest files until total count is within max_files."""
        files = self.get_log_files()
        while len(files) > self._max_files:
            files[0].unlink(missing_ok=True)
            files = files[1:]
