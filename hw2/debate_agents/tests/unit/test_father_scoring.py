"""Tests for FatherAgent verdict fields, scoring, compaction, and LLM evaluation."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from father_test_helpers import FakeCfg, MockAgent, make_father, std_responses

from debate.agents.base_agent import DebateMessage
from debate.agents.father_agent import FatherAgent
from debate.agents.father_scoring import ArgumentScorer


class TestVerdictFields:
    def test_verdict_has_winner_string(self) -> None:
        father = make_father(rounds=2)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert result.winner in ("pro", "con")

    def test_verdict_has_non_empty_transcript(self) -> None:
        father = make_father(rounds=2)
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert isinstance(result.transcript, list) and len(result.transcript) > 0


class TestSkillAndRouting:
    def test_get_skill_prompt_loads_father_skill_file(self) -> None:
        father = make_father()
        assert "father" in father.get_skill_prompt().lower()

    def test_generate_argument_returns_debate_message(self) -> None:
        father = make_father()
        msg = DebateMessage(type="argument", round=1, sender="pro", content="test argument here.")
        assert isinstance(father.generate_argument(msg), DebateMessage)


class TestArgumentScorer:
    def test_score_returns_float_in_range(self) -> None:
        scorer = ArgumentScorer()
        history = [DebateMessage(type="argument", round=1, sender="pro",
                                 content="According to research, remote work shows 13% productivity gain.",
                                 word_count=10)]
        score = scorer.score(history, word_limit=150)
        assert 0.0 <= score <= 100.0

    def test_evidence_marker_boosts_score(self) -> None:
        scorer = ArgumentScorer()
        with_evidence = [DebateMessage(type="argument", round=1, sender="pro",
                                       content="Studies show 13% gain. See http://study.com for research.",
                                       word_count=12)]
        without_evidence = [DebateMessage(type="argument", round=1, sender="pro",
                                          content="I think remote work might be better for certain individuals.",
                                          word_count=10)]
        assert scorer.score(with_evidence, word_limit=150) > scorer.score(without_evidence, word_limit=150)


class TestCompaction:
    def test_compaction_logged_after_summarize_round(self) -> None:
        logger = MagicMock()
        gk = MagicMock()
        father = FatherAgent(role="father", config_manager=FakeCfg(rounds=4, summarize_after=2),
                             gatekeeper=gk, logger=logger)
        father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        calls = [str(c) for c in logger.info.call_args_list]
        assert any("compact" in c for c in calls)


class TestLlmEvaluate:
    _VALID_JSON = (
        '{"q1_novelty":8,"q2_evidence":7,"q3_rebuttal":6,"q4_logic":7,"q5_persuasion":7,'
        '"reasoning":"PRO introduced stronger evidence in every round."}'
    )
    _FENCED_JSON = (
        '```json\n{"q1_novelty":5,"q2_evidence":6,"q3_rebuttal":5,"q4_logic":5,"q5_persuasion":5,'
        '"reasoning":"Closely matched debate overall."}\n```'
    )

    def test_llm_evaluate_returns_pro_pct_from_valid_json(self, monkeypatch: pytest.MonkeyPatch) -> None:
        father = make_father()
        monkeypatch.setattr(father, "_call_llm", lambda _: self._VALID_JSON)
        pro = [DebateMessage(type="argument", round=1, sender="pro", content="remote")]
        con = [DebateMessage(type="argument", round=1, sender="con", content="office")]
        pct, reasoning = father._llm_evaluate(pro, con, 2, 1)  # noqa: SLF001
        expected = (8 + 7 + 6 + 7 + 7) / 5 / 10 * 100
        assert pct is not None and abs(pct - expected) < 0.1
        assert "PRO" in reasoning

    def test_llm_evaluate_handles_fenced_json(self, monkeypatch: pytest.MonkeyPatch) -> None:
        father = make_father()
        monkeypatch.setattr(father, "_call_llm", lambda _: self._FENCED_JSON)
        pro = [DebateMessage(type="argument", round=1, sender="pro", content="remote")]
        con = [DebateMessage(type="argument", round=1, sender="con", content="office")]
        pct, _ = father._llm_evaluate(pro, con, 1, 1)  # noqa: SLF001
        expected = (5 + 6 + 5 + 5 + 5) / 5 / 10 * 100
        assert pct is not None and abs(pct - expected) < 0.1

    def test_llm_evaluate_returns_none_on_invalid_json(self, monkeypatch: pytest.MonkeyPatch) -> None:
        father = make_father()
        monkeypatch.setattr(father, "_call_llm", lambda _: "not valid json at all")
        pro = [DebateMessage(type="argument", round=1, sender="pro", content="remote")]
        con = [DebateMessage(type="argument", round=1, sender="con", content="office")]
        pct, reasoning = father._llm_evaluate(pro, con, 1, 1)  # noqa: SLF001
        assert pct is None and reasoning == ""

    def test_verdict_reasoning_propagated_to_result(self, monkeypatch: pytest.MonkeyPatch) -> None:
        father = make_father(rounds=3)
        monkeypatch.setattr(father, "_llm_evaluate",
                            lambda *_: (70.0, "PRO dominated every round with superior evidence."))
        result = father.run_debate("topic", MockAgent("pro", std_responses()), MockAgent("con", std_responses()))
        assert result.verdict_reasoning == "PRO dominated every round with superior evidence."
