"""Tests for FatherAgent debate flow, routing, interventions, context, and no-tie rule."""

from __future__ import annotations

from father_test_helpers import MockAgent, make_father, std_responses

from debate.agents.father_scoring import DebateResult


class TestRunDebateStructure:
    def test_run_debate_returns_debate_result(self) -> None:
        father = make_father(rounds=2)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert isinstance(result, DebateResult)

    def test_run_debate_completes_all_rounds(self) -> None:
        father = make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert result.rounds_completed == 3

    def test_transcript_length_equals_two_per_round(self) -> None:
        father = make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert len(result.transcript) == 6


class TestRouting:
    def test_transcript_alternates_pro_con(self) -> None:
        father = make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        senders = [m.sender for m in result.transcript]
        assert senders == ["pro", "con", "pro", "con", "pro", "con"]

    def test_pro_goes_first(self) -> None:
        father = make_father(rounds=1)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert result.transcript[0].sender == "pro"


class TestInterventionCounting:
    def test_agreement_increments_intervention_count(self) -> None:
        father = make_father(rounds=1)
        pro = MockAgent("pro", ["I agree with your point, office culture matters.", "Remote work is better, data proves it."])
        con = MockAgent("con", ["Office work builds team trust and collaboration."])
        result = father.run_debate("topic", pro, con)
        assert result.total_interventions >= 1

    def test_repetition_increments_intervention_count(self) -> None:
        father = make_father(rounds=2)
        repeated = "Remote work saves commute time and increases employee productivity significantly."
        pro = MockAgent("pro", [repeated, repeated, "A completely new point about flexibility."])
        con = MockAgent("con", std_responses())
        result = father.run_debate("topic", pro, con)
        assert result.total_interventions >= 1

    def test_no_intervention_for_clean_debate(self) -> None:
        father = make_father(rounds=2)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert result.total_interventions == 0


class TestNoTieRule:
    def test_scores_never_equal(self) -> None:
        father = make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert result.pro_score != result.con_score

    def test_scores_sum_to_100(self) -> None:
        father = make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert abs(result.pro_score + result.con_score - 100.0) < 0.01

    def test_minimum_gap_enforced(self) -> None:
        father = make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert abs(result.pro_score - result.con_score) >= 2.0


class TestContextTracking:
    def test_context_tokens_positive_after_debate(self) -> None:
        father = make_father(rounds=2)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert result.context_tokens > 0

    def test_context_tokens_formula(self) -> None:
        father = make_father(rounds=1)
        result = father.run_debate("topic", MockAgent("pro", ["alpha beta gamma delta epsilon"]), MockAgent("con", ["one two three four five six"]))
        assert result.context_tokens == round((5 + 6) * 1.3)
