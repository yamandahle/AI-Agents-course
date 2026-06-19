"""Unit tests for CrewRunnerV2._load_json and _collect_outputs."""
from __future__ import annotations

from pathlib import Path

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
    (tmp_path / "results").mkdir(parents=True, exist_ok=True)
    return CrewRunnerV2(_gatekeeper(), {}, paths)


# ── _load_json ────────────────────────────────────────────────────────────────

def test_load_json_missing_file_returns_empty_dict(tmp_path: Path) -> None:
    runner = _runner(tmp_path)
    assert runner._load_json("does_not_exist.json") == {}


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
        "v2_graph_summary", "v2_bugs", "v2_fix_proposal", "v2_verification",
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
