"""Unit tests for CrewRunnerV2.run() — retry logic and verdict handling."""
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
    gk.execute = lambda fn, *a, **kw: fn(*a, **kw)
    return gk


def _runner(tmp_path: Path) -> CrewRunnerV2:
    paths = {
        "artifacts": str(tmp_path / "artifacts"),
        "data": str(tmp_path / "data"),
        "obsidian": str(tmp_path / "obsidian"),
        "results": str(tmp_path / "results"),
    }
    artifacts = tmp_path / "artifacts"
    obsidian = tmp_path / "obsidian"
    results = tmp_path / "results"
    for folder in (artifacts, obsidian, results):
        folder.mkdir(parents=True, exist_ok=True)
    (artifacts / "graph.json").write_text('{"nodes":[],"links":[]}', encoding="utf-8")
    (obsidian / "hot.md").write_text("# hot", encoding="utf-8")
    (obsidian / "index.md").write_text("# index", encoding="utf-8")
    return CrewRunnerV2(_gatekeeper(), {}, paths)


def _fake_agents() -> dict:
    fix_strategist = MagicMock()
    fix_strategist.backstory = "initial backstory"
    return {
        "graph_navigator": MagicMock(),
        "architect_detective": MagicMock(),
        "fix_strategist": fix_strategist,
        "quality_gate": MagicMock(),
    }


# ── run() ─────────────────────────────────────────────────────────────────────

def test_run_stops_on_pass_verdict(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    agents = _fake_agents()

    with (
        patch("hw4.services.crew_runner_v2.build_agents", return_value=agents),
        patch("hw4.services.crew_runner_v2.build_tasks", return_value=[]),
        patch("hw4.services.crew_runner_v2.Crew") as mock_crew_cls,
        patch.object(runner, "_run_functional_bugs", return_value=[]),
    ):
        mock_crew_cls.return_value.kickoff = MagicMock()
        runner._load_json = lambda f: {"verdict": "PASS"} if "verification" in f else {}
        result = runner.run()

    assert isinstance(result, dict)
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
        patch.object(runner, "_run_functional_bugs", return_value=[]),
    ):
        mock_crew_cls.return_value.kickoff = MagicMock()
        runner._load_json = fake_load_json
        runner.run()

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
        patch.object(runner, "_run_functional_bugs", return_value=[]),
    ):
        mock_crew_cls.return_value.kickoff = MagicMock()
        runner._load_json = fake_load_json
        runner.run()

    assert "move X to Y" in agents["fix_strategist"].backstory
