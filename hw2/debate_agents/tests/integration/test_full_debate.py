"""Integration tests — full debate flow with mocked LLM calls.

Tests that the entire pipeline from FatherAgent.run_debate() through
ProAgent, ConAgent, ApiGatekeeper, and DebateLogger works end-to-end
without touching any external APIs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

import pytest

from debate.agents.con_agent import ConAgent
from debate.agents.father_agent import FatherAgent
from debate.agents.father_scoring import DebateResult
from debate.agents.pro_agent import ProAgent
from debate.shared.gatekeeper import ApiGatekeeper
from debate.shared.logger import DebateLogger

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

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
            "claude-haiku-4-5": {
                "input_per_million": 0.80,
                "output_per_million": 4.00,
            }
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
    """Return an Anthropic client mock cycling through responses without API calls."""
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
class _Components:
    father: FatherAgent
    pro: ProAgent
    con: ConAgent
    gk: ApiGatekeeper
    logger: DebateLogger
    log_dir: Any  # pathlib.Path


@pytest.fixture()
def components(tmp_path: Any) -> _Components:
    """Wire all real components with a mocked LLM client and a tmp log directory."""
    client = _make_mock_client(_LLM_RESPONSES)
    logger = DebateLogger(_LOG_CFG, log_dir=tmp_path)
    gk = ApiGatekeeper(_RATE_LIMITS, client, logger)
    cfg = _FakeCfg(rounds=3)

    pro = ProAgent(role="pro", config_manager=cfg, gatekeeper=gk, logger=logger, tavily=None)
    con = ConAgent(role="con", config_manager=cfg, gatekeeper=gk, logger=logger, tavily=None)
    father = FatherAgent(role="father", config_manager=cfg, gatekeeper=gk, logger=logger)

    return _Components(father=father, pro=pro, con=con, gk=gk, logger=logger, log_dir=tmp_path)


# ---------------------------------------------------------------------------
# 1. Full flow — completion and transcript structure
# ---------------------------------------------------------------------------


class TestFullDebateFlow:
    def test_debate_completes_3_rounds(self, components: _Components) -> None:
        """run_debate must complete all configured rounds without error."""
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert result.rounds_completed == 3

    def test_transcript_has_two_messages_per_round(self, components: _Components) -> None:
        """Transcript must contain exactly 2 messages per round (one PRO, one CON)."""
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert len(result.transcript) == 6

    def test_transcript_alternates_pro_con_senders(self, components: _Components) -> None:
        """Transcript senders must alternate: pro, con, pro, con, …"""
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        senders = [m.sender for m in result.transcript]
        assert senders == ["pro", "con", "pro", "con", "pro", "con"]

    def test_result_is_debate_result_instance(self, components: _Components) -> None:
        """run_debate must return a DebateResult dataclass instance."""
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert isinstance(result, DebateResult)


# ---------------------------------------------------------------------------
# 2. Verdict — winner and score constraints
# ---------------------------------------------------------------------------


class TestVerdictProduced:
    def test_winner_is_pro_or_con(self, components: _Components) -> None:
        """winner must be exactly 'pro' or 'con'."""
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert result.winner in ("pro", "con")

    def test_scores_sum_to_100(self, components: _Components) -> None:
        """pro_score + con_score must equal 100.0 (within floating-point rounding)."""
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert abs(result.pro_score + result.con_score - 100.0) < 0.01

    def test_winner_has_at_least_60_points(self, components: _Components) -> None:
        """The winning side must hold at least 60 points (60/40 minimum split enforced)."""
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert max(result.pro_score, result.con_score) >= 60.0

    def test_no_score_tie(self, components: _Components) -> None:
        """pro_score and con_score must never be equal (tie is forbidden by no-tie rule)."""
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert result.pro_score != result.con_score


# ---------------------------------------------------------------------------
# 3. Father routing — event ordering
# ---------------------------------------------------------------------------


class TestFatherRouting:
    def test_father_fires_route_event_each_round(self, components: _Components) -> None:
        """FatherAgent must fire exactly one 'father_route' event per round."""
        events: list[str] = []
        components.father.run_debate(
            "Remote work vs office work",
            components.pro,
            components.con,
            on_event=lambda ev, _data: events.append(ev),
        )
        assert events.count("father_route") == 3

    def test_round_start_precedes_pro_argument(self, components: _Components) -> None:
        """'round_start' must be fired before 'pro_argument' in every round."""
        events: list[str] = []
        components.father.run_debate(
            "Remote work vs office work",
            components.pro,
            components.con,
            on_event=lambda ev, _data: events.append(ev),
        )
        round_starts = [i for i, e in enumerate(events) if e == "round_start"]
        pro_args = [i for i, e in enumerate(events) if e == "pro_argument"]
        for rs, pa in zip(round_starts, pro_args, strict=False):
            assert rs < pa

    def test_pro_argument_precedes_father_route(self, components: _Components) -> None:
        """'pro_argument' must be fired before 'father_route' in every round."""
        events: list[str] = []
        components.father.run_debate(
            "Remote work vs office work",
            components.pro,
            components.con,
            on_event=lambda ev, _data: events.append(ev),
        )
        pro_args = [i for i, e in enumerate(events) if e == "pro_argument"]
        routes = [i for i, e in enumerate(events) if e == "father_route"]
        for pa, fr in zip(pro_args, routes, strict=False):
            assert pa < fr

    def test_verdict_event_fired_at_end(self, components: _Components) -> None:
        """A 'verdict' event must be fired after all rounds complete."""
        events: list[str] = []
        components.father.run_debate(
            "Remote work vs office work",
            components.pro,
            components.con,
            on_event=lambda ev, _data: events.append(ev),
        )
        assert events[-1] == "verdict"


# ---------------------------------------------------------------------------
# 4. Cost report — token counts and agent attribution
# ---------------------------------------------------------------------------


class TestCostReport:
    def test_cost_table_has_one_entry_per_llm_call(self, components: _Components) -> None:
        """Cost table must have at least 6 entries (3 rounds × 2 agents)."""
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert len(components.gk.get_cost_table()) >= 6

    def test_cost_entries_contain_token_counts(self, components: _Components) -> None:
        """Every cost entry must have positive input_tokens and output_tokens."""
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        for entry in components.gk.get_cost_table():
            assert "input_tokens" in entry
            assert "output_tokens" in entry
            assert entry["input_tokens"] > 0
            assert entry["output_tokens"] > 0

    def test_cost_entries_attribute_to_correct_agents(self, components: _Components) -> None:
        """Both 'pro' and 'con' must appear as agent values in the cost table."""
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        agents_logged = {e["agent"] for e in components.gk.get_cost_table()}
        assert "pro" in agents_logged
        assert "con" in agents_logged

    def test_cost_entries_have_cumulative_cost(self, components: _Components) -> None:
        """cumulative_cost_usd must be non-negative and non-decreasing."""
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        table = components.gk.get_cost_table()
        cumulative = [e["cumulative_cost_usd"] for e in table]
        assert all(c >= 0 for c in cumulative)
        assert cumulative == sorted(cumulative)


# ---------------------------------------------------------------------------
# 5. Logging — files created and entries are valid JSON
# ---------------------------------------------------------------------------


class TestLogging:
    def test_log_files_created_in_tmp_dir(self, components: _Components) -> None:
        """DebateLogger must create at least one log file after a debate."""
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        log_files = list(components.log_dir.glob("debate_*.log"))
        assert len(log_files) >= 1

    def test_every_log_line_is_valid_json(self, components: _Components) -> None:
        """Every non-empty log line must be valid JSON with required fields."""
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        for log_file in components.log_dir.glob("debate_*.log"):
            for line in log_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    parsed = json.loads(line)
                    assert "timestamp" in parsed
                    assert "level" in parsed
                    assert "event" in parsed

    def test_context_update_logged_for_each_round(self, components: _Components) -> None:
        """Logger must record a 'context_update' event for each completed round."""
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        events: list[str] = []
        for log_file in components.log_dir.glob("debate_*.log"):
            for line in log_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    events.append(json.loads(line)["event"])
        assert events.count("context_update") >= 3

    def test_argument_events_logged_by_agents(self, components: _Components) -> None:
        """ProAgent and ConAgent must log 'argument' events via DebateLogger."""
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        events: list[str] = []
        for log_file in components.log_dir.glob("debate_*.log"):
            for line in log_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    events.append(json.loads(line)["event"])
        assert events.count("argument") >= 6  # 3 rounds × 2 agents
