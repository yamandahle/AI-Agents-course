"""Integration tests for DebateLogger output during a full debate."""

from __future__ import annotations

import json

from conftest import Components


class TestLogging:
    def test_log_files_created_in_tmp_dir(self, components: Components) -> None:
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        log_files = list(components.log_dir.glob("debate_*.log"))
        assert len(log_files) >= 1

    def test_every_log_line_is_valid_json(self, components: Components) -> None:
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        for log_file in components.log_dir.glob("debate_*.log"):
            for line in log_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    parsed = json.loads(line)
                    assert "timestamp" in parsed
                    assert "level" in parsed
                    assert "event" in parsed

    def test_context_update_logged_for_each_round(self, components: Components) -> None:
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        events: list[str] = []
        for log_file in components.log_dir.glob("debate_*.log"):
            for line in log_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    events.append(json.loads(line)["event"])
        assert events.count("context_update") >= 3

    def test_argument_events_logged_by_agents(self, components: Components) -> None:
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        events: list[str] = []
        for log_file in components.log_dir.glob("debate_*.log"):
            for line in log_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    events.append(json.loads(line)["event"])
        assert events.count("argument") >= 6
