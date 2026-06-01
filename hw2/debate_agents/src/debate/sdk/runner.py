"""DebateRunner — wires all agents together and runs debates through the SDK layer."""

from __future__ import annotations

import contextlib
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv
from tavily import TavilyClient

from debate.agents.con_agent import ConAgent
from debate.agents.father_agent import FatherAgent
from debate.agents.father_scoring import DebateResult
from debate.agents.pro_agent import ProAgent
from debate.shared.gatekeeper import ApiGatekeeper
from debate.shared.logger import DebateLogger


@dataclass
class _Cfg:  # pragma: no cover
    setup: dict[str, Any]
    rate_limits: dict[str, Any]


class DebateRunner:  # pragma: no cover
    """Loads config + env, wires agents, runs debates, exposes results to the SDK layer."""

    def __init__(self, config_dir: str = "config") -> None:
        self._config_dir = Path(config_dir)
        self._last_result: DebateResult | None = None
        self._gatekeeper: ApiGatekeeper | None = None
        self._logger: DebateLogger | None = None

    def run(self, topic: str, on_event: Callable[..., None] | None = None) -> DebateResult:
        """Load configs, create agents, execute debate, store result."""
        setup = json.loads((self._config_dir / "setup.json").read_text(encoding="utf-8"))
        rate_limits = json.loads((self._config_dir / "rate_limits.json").read_text(encoding="utf-8"))
        log_cfg = json.loads((self._config_dir / "logging_config.json").read_text(encoding="utf-8"))

        load_dotenv()
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        tavily_key = os.environ.get("TAVILY_API_KEY", "")

        client = anthropic.Anthropic(api_key=anthropic_key)
        tavily = TavilyClient(api_key=tavily_key) if tavily_key else None

        self._logger = DebateLogger(log_cfg)
        self._gatekeeper = ApiGatekeeper(rate_limits, client, self._logger)

        cfg = _Cfg(setup=setup, rate_limits=rate_limits)
        gk, lg = self._gatekeeper, self._logger

        pro = ProAgent(role="pro", config_manager=cfg, gatekeeper=gk, logger=lg, tavily=tavily)
        con = ConAgent(role="con", config_manager=cfg, gatekeeper=gk, logger=lg, tavily=tavily)
        father = FatherAgent(role="father", config_manager=cfg, gatekeeper=gk, logger=lg)

        result = father.run_debate(topic, pro, con, on_event=on_event)
        self._last_result = result
        return result

    def get_last_result(self) -> DebateResult | None:
        return self._last_result

    def get_cost_breakdown(self) -> list[dict[str, Any]]:
        if self._gatekeeper is None:
            return []
        return self._gatekeeper.get_cost_table()

    def get_recent_logs(self, n: int = 20) -> list[dict[str, Any]]:
        if self._logger is None:
            return []
        entries: list[dict[str, Any]] = []
        for log_file in self._logger.get_log_files():
            for line in log_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    with contextlib.suppress(json.JSONDecodeError):
                        entries.append(json.loads(line))
        return entries[-n:]
