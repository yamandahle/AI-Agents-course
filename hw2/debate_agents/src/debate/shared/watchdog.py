"""Watchdog — monitors agent processes and restarts them on failure.

All configuration (interval, max_restarts) comes from the debate section of
setup.json. Every event is logged through DebateLogger when one is provided.
"""

from __future__ import annotations

import contextlib
import threading
from collections.abc import Callable
from typing import Any


class MaxRestartsExceededError(Exception):
    """Raised when a process has been restarted more than max_restarts times."""


class Watchdog:
    """Monitors multiprocessing.Process objects and restarts them on failure."""

    def __init__(self, config: dict[str, Any], logger: Any = None) -> None:
        debate_cfg = config["debate"]
        self._interval: float = debate_cfg["watchdog_interval_seconds"]
        self._max_restarts: int = debate_cfg["max_restarts"]
        self._logger = logger

        # {name: {"process": Process, "factory": callable, "restarts": int}}
        self._processes: dict[str, dict[str, Any]] = {}
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def register(self, name: str, process: Any, factory: Callable[[], Any]) -> None:
        """Register a process for monitoring with its restart factory."""
        self._processes[name] = {"process": process, "factory": factory, "restarts": 0}

    def check_once(self) -> None:
        """Run one monitoring pass — raise MaxRestartsExceeded if a process is exhausted."""
        for name, info in self._processes.items():
            if not info["process"].is_alive():
                self._restart(name, info)

    def run(self) -> None:
        """Block and monitor until stop() is called or a process exhausts all restarts."""
        while not self._stop_event.is_set():
            try:
                self.check_once()
            except MaxRestartsExceededError:
                self._emit("ERROR", "watchdog", "max_restarts_exceeded", {})
                break
            self._stop_event.wait(timeout=self._interval)

    def stop(self) -> None:
        """Signal the run loop to exit cleanly on the next cycle."""
        self._stop_event.set()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _restart(self, name: str, info: dict[str, Any]) -> None:
        """Kill and restart a dead process, or raise MaxRestartsExceeded."""
        if info["restarts"] >= self._max_restarts:
            raise MaxRestartsExceededError(
                f"Process '{name}' exceeded max_restarts={self._max_restarts}"
            )

        info["restarts"] += 1
        self._emit("WARNING", "watchdog", "restart", {"process": name, "attempt": info["restarts"]})

        with contextlib.suppress(Exception):
            info["process"].kill()

        new_process = info["factory"]()
        info["process"] = new_process

        if info["process"].is_alive():
            info["restarts"] = 0
            self._emit("INFO", "watchdog", "restart_success", {"process": name})

    def _emit(self, level: str, agent: str, event: str, data: dict[str, Any]) -> None:
        if self._logger is not None:
            self._logger.log(level, agent, event, data)
