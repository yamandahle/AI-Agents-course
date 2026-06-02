"""DebateRunner — thin CLI adapter over DebateSDK (no business logic here)."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from debate.agents.father_scoring import DebateResult
from debate.sdk.sdk import DebateSDK


class DebateRunner:
    """Exposes debate results to the terminal menu via the SDK entry point only."""

    def __init__(self, config_dir: str = "config") -> None:
        self._sdk = DebateSDK()
        self._config_dir = config_dir
        self._session_id: str | None = None

    def run(self, topic: str, on_event: Callable[..., None] | None = None) -> DebateResult:
        """Start and execute a debate through DebateSDK → DebateOrchestrator."""
        session = self._sdk.start_debate(topic=topic, config_path=self._config_dir)
        self._session_id = session.session_id
        completed = self._sdk.execute_debate(self._session_id, on_event=on_event)
        if completed.result is None:
            raise RuntimeError("Debate completed without a result")
        return completed.result

    def get_last_result(self) -> DebateResult | None:
        if self._session_id is None:
            return None
        session = self._sdk._get(self._session_id)  # noqa: SLF001
        return session.result

    def get_cost_breakdown(self) -> list[dict[str, Any]]:
        if self._session_id is None:
            return []
        report = self._sdk.get_cost_report(self._session_id)
        return list(report.get("entries", []))

    def get_recent_logs(self, n: int = 20) -> list[dict[str, Any]]:
        """Read structured log lines from the latest debate log file only."""
        log_dir = Path("logs")
        if not log_dir.is_dir():
            return []
        log_files = sorted(log_dir.glob("debate_*.log"), key=lambda p: p.stat().st_mtime)
        if not log_files:
            return []
        entries: list[dict[str, Any]] = []
        for line in log_files[-1].read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return entries[-n:]
