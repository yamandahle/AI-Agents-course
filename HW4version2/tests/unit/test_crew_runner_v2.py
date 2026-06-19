"""Unit tests for services/crew_runner_v2.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from hw4.services.crew_runner_v2 import CrewRunnerV2
from hw4.shared.gatekeeper import ApiGatekeeper, RateLimitConfig


def _gatekeeper() -> ApiGatekeeper:
    cfg = RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        concurrent_max=5,
        retry_after_seconds=0,
        max_retries=1,
    )
    gk = ApiGatekeeper(config=cfg)
    # make execute a passthrough so tests don't hit real APIs
    gk.execute = lambda fn, *a, **kw: fn(*a, **kw)
    return gk


def _runner(tmp_path: Path) -> CrewRunnerV2:
    paths = {
        "artifacts": str(tmp_path / "artifacts"),
        "data": str(tmp_path / "data"),
        "obsidian": str(tmp_path / "obsidian"),
        "results": str(tmp_path / "results"),
    }
    (tmp_path / "results").mkdir(parents=True, exist_ok=True)
    return CrewRunnerV2(_gatekeeper(), {}, paths)


# ── _load_json ────────────────────────────────────────────────────────────────

def test_load_json_missing_file_returns_empty_dict(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    result = runner._load_json("does_not_exist.json")
    assert result == {}


def test_load_json_reads_valid_json(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "test.json").write_text('{"key": "val"}', encoding="utf-8")
    runner = _runner(tmp_path)
    assert runner._load_json("test.json") == {"key": "val"}


def test_load_json_invalid_json_returns_empty_dict(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "broken.json").write_text("not json {{", encoding="utf-8")
    runner = _runner(tmp_path)
    assert runner._load_json("broken.json") == {}


# ── _collect_outputs ──────────────────────────────────────────────────────────

def test_collect_outputs_returns_all_keys_even_when_files_missing(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    outputs = runner._collect_outputs()
    assert set(outputs.keys()) == {
        "v2_graph_summary",
        "v2_bugs",
        "v2_fix_proposal",
        "v2_verification",
    }
    for v in outputs.values():
        assert v == {}


def test_collect_outputs_reads_existing_files(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "v2_bugs.json").write_text('[{"bug_type":"HUB"}]', encoding="utf-8")

    runner = _runner(tmp_path)
    outputs = runner._collect_outputs()
    assert outputs["v2_bugs"] == [{"bug_type": "HUB"}]
    assert outputs["v2_graph_summary"] == {}


# ── run() ─────────────────────────────────────────────────────────────────────

def _fake_agents() -> dict:
    fix_strategist = MagicMock()
    fix_strategist.backstory = "initial backstory"
    return {
        "graph_navigator": MagicMock(),
        "architect_detective": MagicMock(),
        "fix_strategist": fix_strategist,
        "quality_gate": MagicMock(),
    }


def test_run_stops_on_pass_verdict(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    agents = _fake_agents()

    with (
        patch("hw4.services.crew_runner_v2.build_agents", return_value=agents),
        patch("hw4.services.crew_runner_v2.build_tasks", return_value=[]),
        patch("hw4.services.crew_runner_v2.Crew") as mock_crew_cls,
    ):
        mock_crew_cls.return_value.kickoff = MagicMock()
        runner._load_json = lambda f: {"verdict": "PASS"} if "verification" in f else {}
        result = runner.run()

    assert isinstance(result, dict)
    # crew was kicked off once (PASS on first attempt)
    assert mock_crew_cls.return_value.kickoff.call_count == 1


def test_run_retries_on_fail_then_passes(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    agents = _fake_agents()
    call_count = [0]

    def fake_load_json(filename: str) -> dict:
        if "verification" not in filename:
            return {}
        call_count[0] += 1
        if call_count[0] == 1:
            return {"verdict": "FAIL", "retry_instruction": "do better"}
        return {"verdict": "PASS"}

    with (
        patch("hw4.services.crew_runner_v2.build_agents", return_value=agents),
        patch("hw4.services.crew_runner_v2.build_tasks", return_value=[]),
        patch("hw4.services.crew_runner_v2.Crew") as mock_crew_cls,
    ):
        mock_crew_cls.return_value.kickoff = MagicMock()
        runner._load_json = fake_load_json
        runner.run()

    # Two kickoff calls: attempt 0 (FAIL) + attempt 1 (PASS)
    assert mock_crew_cls.return_value.kickoff.call_count == 2


def test_run_injects_retry_instruction_into_backstory(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    agents = _fake_agents()
    call_count = [0]

    def fake_load_json(filename: str) -> dict:
        if "verification" not in filename:
            return {}
        call_count[0] += 1
        if call_count[0] == 1:
            return {"verdict": "FAIL", "retry_instruction": "move X to Y"}
        return {"verdict": "PASS"}

    with (
        patch("hw4.services.crew_runner_v2.build_agents", return_value=agents),
        patch("hw4.services.crew_runner_v2.build_tasks", return_value=[]),
        patch("hw4.services.crew_runner_v2.Crew") as mock_crew_cls,
    ):
        mock_crew_cls.return_value.kickoff = MagicMock()
        runner._load_json = fake_load_json
        runner.run()

    assert "move X to Y" in agents["fix_strategist"].backstory
