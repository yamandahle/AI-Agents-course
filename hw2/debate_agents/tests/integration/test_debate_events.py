"""Integration tests for father routing events and cost reporting."""

from __future__ import annotations

from conftest import Components


class TestFatherRouting:
    def test_father_fires_route_event_each_round(self, components: Components) -> None:
        events: list[str] = []
        components.father.run_debate(
            "Remote work vs office work", components.pro, components.con,
            on_event=lambda ev, _data: events.append(ev),
        )
        assert events.count("father_route") == 3

    def test_round_start_precedes_pro_argument(self, components: Components) -> None:
        events: list[str] = []
        components.father.run_debate(
            "Remote work vs office work", components.pro, components.con,
            on_event=lambda ev, _data: events.append(ev),
        )
        round_starts = [i for i, e in enumerate(events) if e == "round_start"]
        pro_args = [i for i, e in enumerate(events) if e == "pro_argument"]
        for rs, pa in zip(round_starts, pro_args, strict=False):
            assert rs < pa

    def test_pro_argument_precedes_father_route(self, components: Components) -> None:
        events: list[str] = []
        components.father.run_debate(
            "Remote work vs office work", components.pro, components.con,
            on_event=lambda ev, _data: events.append(ev),
        )
        pro_args = [i for i, e in enumerate(events) if e == "pro_argument"]
        routes = [i for i, e in enumerate(events) if e == "father_route"]
        for pa, fr in zip(pro_args, routes, strict=False):
            assert pa < fr

    def test_verdict_event_fired_at_end(self, components: Components) -> None:
        events: list[str] = []
        components.father.run_debate(
            "Remote work vs office work", components.pro, components.con,
            on_event=lambda ev, _data: events.append(ev),
        )
        assert events[-1] == "verdict"


class TestCostReport:
    def test_cost_table_has_one_entry_per_llm_call(self, components: Components) -> None:
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert len(components.gk.get_cost_table()) >= 6

    def test_cost_entries_contain_token_counts(self, components: Components) -> None:
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        for entry in components.gk.get_cost_table():
            assert entry["input_tokens"] > 0
            assert entry["output_tokens"] > 0

    def test_cost_entries_attribute_to_correct_agents(self, components: Components) -> None:
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        agents_logged = {e["agent"] for e in components.gk.get_cost_table()}
        assert "pro" in agents_logged
        assert "con" in agents_logged

    def test_cost_entries_have_cumulative_cost(self, components: Components) -> None:
        components.father.run_debate("Remote work vs office work", components.pro, components.con)
        table = components.gk.get_cost_table()
        cumulative = [e["cumulative_cost_usd"] for e in table]
        assert all(c >= 0 for c in cumulative)
        assert cumulative == sorted(cumulative)
