"""DebateOrchestrator — runs the full debate as a subprocess with IPC queues and Watchdog.

Architecture:
  - _debate_worker() runs inside a dedicated Process: creates all agents, runs debate
  - DebateOrchestrator.run() spawns that process, drains live events, returns DebateResult
  - Watchdog monitors the debate process and restarts it on unexpected exit
  - All agent→main communication flows through multiprocessing.Queue objects
"""

from __future__ import annotations

import json
import multiprocessing
import queue
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

from debate.agents.father_scoring import DebateResult
from debate.shared.config import ConfigManager
from debate.shared.watchdog import Watchdog

# ---------------------------------------------------------------------------
# Subprocess worker — runs in an isolated process; must be module-level so
# it is picklable by multiprocessing on Windows (spawn start method).
# ---------------------------------------------------------------------------


def _debate_worker(  # pragma: no cover
    config_dir: str,
    topic: str,
    result_queue: multiprocessing.Queue,
    event_queue: multiprocessing.Queue,
) -> None:
    """All-in-one subprocess: create agents, run debate, stream events, push result."""
    import contextlib
    import os

    import anthropic
    from dotenv import load_dotenv
    from tavily import TavilyClient

    from debate.agents.con_agent import ConAgent
    from debate.agents.father_agent import FatherAgent
    from debate.agents.pro_agent import ProAgent
    from debate.shared.gatekeeper import ApiGatekeeper
    from debate.shared.logger import DebateLogger

    cfg = ConfigManager(config_dir)

    load_dotenv()
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    tavily_key = os.environ.get("TAVILY_API_KEY", "")
    tavily = TavilyClient(api_key=tavily_key) if tavily_key else None

    logger = DebateLogger(cfg.logging_config)
    gk = ApiGatekeeper(cfg.rate_limits, client, logger)

    def on_event(event: str, data: dict[str, Any]) -> None:
        with contextlib.suppress(Exception):
            event_queue.put_nowait((event, data))

    pro = ProAgent(role="pro", config_manager=cfg, gatekeeper=gk, logger=logger, tavily=tavily)
    con = ConAgent(role="con", config_manager=cfg, gatekeeper=gk, logger=logger, tavily=tavily)
    father = FatherAgent(role="father", config_manager=cfg, gatekeeper=gk, logger=logger)

    result = father.run_debate(topic, pro, con, on_event=on_event)
    result_queue.put({"result": result, "cost_table": gk.get_cost_table()})
    event_queue.put(("_done", {}))


# ---------------------------------------------------------------------------
# Orchestrator — lives in the main process
# ---------------------------------------------------------------------------


class DebateOrchestrator:  # pragma: no cover
    """Coordinates the debate: spawns subprocess, wires IPC queues, monitors with Watchdog."""

    def __init__(self, config_dir: str = "config") -> None:
        self._config_dir = Path(config_dir)
        self._last_result: DebateResult | None = None
        self._cost_table: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, topic: str, on_event: Callable[..., None] | None = None) -> DebateResult:
        """Start debate subprocess, stream events to caller, return DebateResult."""
        result_queue: multiprocessing.Queue = multiprocessing.Queue()
        event_queue: multiprocessing.Queue = multiprocessing.Queue()
        config_str = str(self._config_dir)

        def make_process() -> multiprocessing.Process:
            p = multiprocessing.Process(
                target=_debate_worker,
                args=(config_str, topic, result_queue, event_queue),
                daemon=True,
            )
            p.start()
            return p

        process = make_process()

        setup = json.loads((self._config_dir / "setup.json").read_text(encoding="utf-8"))
        watchdog = Watchdog({"debate": setup["debate"]})
        watchdog.register("debate_worker", process, factory=make_process)

        watchdog_thread = threading.Thread(target=watchdog.run, daemon=True)
        watchdog_thread.start()

        try:
            self._drain_events(event_queue, on_event)
        finally:
            watchdog.stop()
            watchdog_thread.join(timeout=5)
            process.join(timeout=30)

        data: dict[str, Any] = result_queue.get(timeout=10)
        self._last_result = data["result"]
        self._cost_table = data["cost_table"]
        return self._last_result

    def get_last_result(self) -> DebateResult | None:
        return self._last_result

    def get_cost_breakdown(self) -> list[dict[str, Any]]:
        return list(self._cost_table)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _drain_events(
        event_queue: multiprocessing.Queue,
        on_event: Callable[..., None] | None,
    ) -> None:
        """Block until the debate sends the '_done' sentinel, forwarding all events."""
        while True:
            try:
                event_type, data = event_queue.get(timeout=600)
                if event_type == "_done":
                    return
                if on_event is not None:
                    on_event(event_type, data)
            except queue.Empty:
                return
