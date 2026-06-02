"""Integration tests for full debate completion and verdict constraints."""

from __future__ import annotations

from conftest import Components

from debate.agents.father_scoring import DebateResult


class TestFullDebateFlow:
    def test_debate_completes_3_rounds(self, components: Components) -> None:
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert result.rounds_completed == 3

    def test_transcript_has_two_messages_per_round(self, components: Components) -> None:
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert len(result.transcript) == 6

    def test_transcript_alternates_pro_con_senders(self, components: Components) -> None:
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        senders = [m.sender for m in result.transcript]
        assert senders == ["pro", "con", "pro", "con", "pro", "con"]

    def test_result_is_debate_result_instance(self, components: Components) -> None:
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert isinstance(result, DebateResult)


class TestVerdictProduced:
    def test_winner_is_pro_or_con(self, components: Components) -> None:
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert result.winner in ("pro", "con")

    def test_scores_sum_to_100(self, components: Components) -> None:
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert abs(result.pro_score + result.con_score - 100.0) < 0.01

    def test_scores_differ_by_at_least_2_points(self, components: Components) -> None:
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert abs(result.pro_score - result.con_score) >= 2.0

    def test_no_score_tie(self, components: Components) -> None:
        result = components.father.run_debate("Remote work vs office work", components.pro, components.con)
        assert result.pro_score != result.con_score
