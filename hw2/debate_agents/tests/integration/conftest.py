"""Shared fixtures and setup for integration tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

import pytest

from debate.agents.con_agent import ConAgent
from debate.agents.father_agent import FatherAgent
from debate.agents.pro_agent import ProAgent
from debate.shared.gatekeeper import ApiGatekeeper
from debate.shared.logger import DebateLogger

_LOG_CFG: dict[str, Any] = {
    "log_dir": "logs",
    "max_files": 5,
    "max_lines_per_file": 200,
    "level": "INFO",
}

_RATE_LIMITS: dict[str, Any] = {
    "anthropic": {
        "requests_per_minute": 1000,
        "max_tokens_per_call": 500,
        "daily_budget_usd": 100.0,
        "retry_attempts": 1,
        "retry_backoff_seconds": [0],
        "model_costs": {
            "claude-haiku-4-5": {"input_per_million": 0.80, "output_per_million": 4.00}
        },
    },
    "tavily": {"max_results_per_search": 3},
}

_LLM_RESPONSES: list[str] = [
    "Remote work eliminates two hours of daily commuting, reclaiming time for productivity.",
    "Office collaboration fosters spontaneous creativity that video calls fundamentally cannot replicate.",
    "Stanford research demonstrates 13% productivity gains among remote workers over eighteen months.",
    "In-person mentorship accelerates junior developer growth through direct observation and feedback.",
    "Distributed hiring removes geographic barriers, expanding talent access across global markets.",
    "Physical proximity builds psychological safety crucial for high-stakes team decision making.",
    "Home office setups reduce overhead costs by 30% according to Global Workplace Analytics surveys.",
    "Cultural cohesion erodes without shared physical spaces for informal daily social interaction.",
    "Asynchronous communication tools enable deep work blocks impossible amid open office interruptions.",
    "Organizational trust and accountability improve when teams share visible dedicated workspaces.",
    "Carbon footprints shrink dramatically when millions of workers eliminate daily vehicle commutes.",
    "Spontaneous whiteboard sessions solve complex architectural problems faster than scheduled calls.",
]


class _FakeCfg:
    def __init__(self, rounds: int = 3, summarize_after: int = 99) -> None:
        self.setup = {
            "debate": {
                "model": "claude-haiku-4-5",
                "timeout_seconds": 10.0,
                "word_limit": 150,
                "rounds": rounds,
                "max_restarts": 3,
                "watchdog_interval_seconds": 2,
                "context_summarize_after_round": summarize_after,
                "token_estimate_multiplier": 1.3,
                "skills_path": "src/debate/skills/",
            }
        }
        self.rate_limits = _RATE_LIMITS


def _make_mock_client(responses: list[str]) -> MagicMock:
    call_count = [0]

    def _create(**_: Any) -> MagicMock:
        text = responses[call_count[0] % len(responses)]
        call_count[0] += 1
        resp = MagicMock()
        resp.content = [MagicMock(text=text)]
        resp.usage.input_tokens = 50
        resp.usage.output_tokens = len(text.split())
        return resp

    client = MagicMock()
    client.messages.create.side_effect = _create
    return client


@dataclass
class Components:
    father: FatherAgent
    pro: ProAgent
    con: ConAgent
    gk: ApiGatekeeper
    logger: DebateLogger
    log_dir: Any


@pytest.fixture()
def components(tmp_path: Any) -> Components:
    client = _make_mock_client(_LLM_RESPONSES)
    logger = DebateLogger(_LOG_CFG, log_dir=tmp_path)
    gk = ApiGatekeeper(_RATE_LIMITS, client, logger)
    cfg = _FakeCfg(rounds=3)
    pro = ProAgent(role="pro", config_manager=cfg, gatekeeper=gk, logger=logger, tavily=None)
    con = ConAgent(role="con", config_manager=cfg, gatekeeper=gk, logger=logger, tavily=None)
    father = FatherAgent(role="father", config_manager=cfg, gatekeeper=gk, logger=logger)
    return Components(father=father, pro=pro, con=con, gk=gk, logger=logger, log_dir=tmp_path)
