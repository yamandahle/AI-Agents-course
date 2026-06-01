"""Unit tests for FatherAgent and ArgumentScorer — TDD Red phase."""

from __future__ import annotations

from unittest.mock import MagicMock

from debate.agents.base_agent import DebateMessage
from debate.agents.father_agent import FatherAgent
from debate.agents.father_scoring import ArgumentScorer, DebateResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeCfg:
    def __init__(self, rounds: int = 3, summarize_after: int = 99, word_limit: int = 150) -> None:
        self.setup = {
            "debate": {
                "model": "claude-haiku-4-5",
                "timeout_seconds": 5.0,
                "word_limit": word_limit,
                "rounds": rounds,
                "max_restarts": 3,
                "watchdog_interval_seconds": 2,
                "context_summarize_after_round": summarize_after,
                "token_estimate_multiplier": 1.3,
                "skills_path": "src/debate/skills/",
            }
        }
        self.rate_limits = {
            "anthropic": {"max_tokens_per_call": 500},
            "tavily": {"max_results_per_search": 3},
        }


class MockAgent:
    """Minimal debate agent that cycles through predefined responses."""

    def __init__(self, role: str, responses: list[str]) -> None:
        self._role = role
        self._responses = responses
        self._idx = 0
        self.received: list[DebateMessage] = []

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        text = self._responses[self._idx % len(self._responses)]
        self._idx += 1
        return DebateMessage(
            type="argument",
            round=opponent_msg.round + 1,
            sender=self._role,
            content=text,
            word_count=len(text.split()),
        )

    def receive_message(self, msg: DebateMessage) -> None:
        self.received.append(msg)


def _make_father(rounds: int = 3, summarize_after: int = 99) -> FatherAgent:
    gk = MagicMock()
    logger = MagicMock()
    return FatherAgent(
        role="father",
        config_manager=FakeCfg(rounds=rounds, summarize_after=summarize_after),
        gatekeeper=gk,
        logger=logger,
    )


def _std_responses() -> list[str]:
    """Distinct, non-agreeing responses with no shared vocabulary."""
    return [
        "Commuting wastes two hours every day according to transportation studies.",
        "Home office setups improve focus and reduce distractions measurably.",
        "Companies report lower overhead costs when employees telecommute regularly.",
        "Research shows remote workers log more hours than office counterparts.",
        "Video conferencing technology bridges collaboration gaps between distributed teams.",
        "Urban congestion decreases substantially when fewer workers commute daily.",
        "Mental health improves when employees control their own workspace environment.",
        "Hiring globally expands talent pools beyond local geographic limitations.",
        "Synchronous collaboration thrives with proper async communication tools established.",
        "Energy consumption falls when office buildings operate at reduced capacity.",
    ]


# ---------------------------------------------------------------------------
# 1. run_debate — basic structure
# ---------------------------------------------------------------------------


class TestRunDebateStructure:
    def test_run_debate_returns_debate_result(self) -> None:
        """run_debate must return a DebateResult instance."""
        father = _make_father(rounds=2)
        result = father.run_debate("Is remote work better?", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert isinstance(result, DebateResult)

    def test_run_debate_completes_all_rounds(self) -> None:
        """rounds_completed in DebateResult must equal config rounds."""
        father = _make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert result.rounds_completed == 3

    def test_transcript_length_equals_two_per_round(self) -> None:
        """Transcript must have exactly 2 messages per round (one PRO, one CON)."""
        father = _make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert len(result.transcript) == 6


# ---------------------------------------------------------------------------
# 2. Routing — alternation
# ---------------------------------------------------------------------------


class TestRouting:
    def test_transcript_alternates_pro_con(self) -> None:
        """Transcript senders must alternate: pro, con, pro, con, ..."""
        father = _make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        senders = [m.sender for m in result.transcript]
        assert senders == ["pro", "con", "pro", "con", "pro", "con"]

    def test_pro_goes_first(self) -> None:
        """PRO agent must speak first in round 1."""
        father = _make_father(rounds=1)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert result.transcript[0].sender == "pro"


# ---------------------------------------------------------------------------
# 3. Agreement detection
# ---------------------------------------------------------------------------


class TestAgreementDetection:
    def test_detect_agreement_true_for_i_agree(self) -> None:
        father = _make_father()
        msg = DebateMessage(type="argument", round=1, sender="pro", content="I agree with your point here.")
        assert father._detect_agreement(msg) is True  # noqa: SLF001

    def test_detect_agreement_true_for_good_point(self) -> None:
        father = _make_father()
        msg = DebateMessage(type="argument", round=1, sender="pro", content="That is a good point, however I disagree.")
        assert father._detect_agreement(msg) is True  # noqa: SLF001

    def test_detect_agreement_false_for_normal_argument(self) -> None:
        father = _make_father()
        msg = DebateMessage(
            type="argument", round=1, sender="pro",
            content="Remote work increases productivity by 13% according to Stanford research.",
        )
        assert father._detect_agreement(msg) is False  # noqa: SLF001


# ---------------------------------------------------------------------------
# 4. Repetition detection
# ---------------------------------------------------------------------------


class TestRepetitionDetection:
    def test_detect_repetition_false_for_empty_history(self) -> None:
        father = _make_father()
        msg = DebateMessage(type="argument", round=1, sender="pro", content="Remote work saves commute time.")
        assert father._detect_repetition(msg, []) is False  # noqa: SLF001

    def test_detect_repetition_true_for_near_duplicate(self) -> None:
        father = _make_father()
        content = "Remote work saves commute time and increases employee productivity significantly."
        history = [
            DebateMessage(type="argument", round=1, sender="pro", content=content)
        ]
        msg = DebateMessage(type="argument", round=2, sender="pro", content=content)
        assert father._detect_repetition(msg, history) is True  # noqa: SLF001

    def test_detect_repetition_false_for_different_argument(self) -> None:
        father = _make_father()
        history = [
            DebateMessage(type="argument", round=1, sender="pro", content="Remote work saves commute time.")
        ]
        msg = DebateMessage(
            type="argument", round=2, sender="pro",
            content="Office buildings drain municipal energy resources and generate pollution.",
        )
        assert father._detect_repetition(msg, history) is False  # noqa: SLF001


# ---------------------------------------------------------------------------
# 5. Intervention counting
# ---------------------------------------------------------------------------


class TestInterventionCounting:
    def test_agreement_increments_intervention_count(self) -> None:
        """An agreement phrase triggers an intervention; total_interventions must be >= 1."""
        father = _make_father(rounds=1)
        pro = MockAgent("pro", ["I agree with your point, office culture matters.", "Remote work is better, data proves it."])
        con = MockAgent("con", ["Office work builds team trust and collaboration."])
        result = father.run_debate("topic", pro, con)
        assert result.total_interventions >= 1

    def test_repetition_increments_intervention_count(self) -> None:
        """A repeated argument triggers an intervention; total_interventions must be >= 1."""
        father = _make_father(rounds=2)
        repeated = "Remote work saves commute time and increases employee productivity significantly."
        pro = MockAgent("pro", [repeated, repeated, "A completely new point about flexibility and autonomy."])
        con = MockAgent("con", _std_responses())
        result = father.run_debate("topic", pro, con)
        assert result.total_interventions >= 1

    def test_no_intervention_for_clean_debate(self) -> None:
        """A clean debate with unique, non-agreeing arguments must yield 0 interventions."""
        father = _make_father(rounds=2)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert result.total_interventions == 0


# ---------------------------------------------------------------------------
# 6. No-tie rule
# ---------------------------------------------------------------------------


class TestNoTieRule:
    def test_scores_never_equal(self) -> None:
        """pro_score and con_score must never be equal (tie is forbidden)."""
        father = _make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert result.pro_score != result.con_score

    def test_scores_sum_to_100(self) -> None:
        """pro_score + con_score must equal 100.0."""
        father = _make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert abs(result.pro_score + result.con_score - 100.0) < 0.01

    def test_minimum_60_40_split(self) -> None:
        """The winning side must have at least 60 points (minimum 60/40 split enforced)."""
        father = _make_father(rounds=3)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert max(result.pro_score, result.con_score) >= 60.0


# ---------------------------------------------------------------------------
# 7. Context token tracking
# ---------------------------------------------------------------------------


class TestContextTracking:
    def test_context_tokens_positive_after_debate(self) -> None:
        """context_tokens must be > 0 after at least one round."""
        father = _make_father(rounds=2)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert result.context_tokens > 0

    def test_context_tokens_formula(self) -> None:
        """context_tokens must follow WCn = WCn-1 + round((words_pro + words_con) × 1.3)."""
        father = _make_father(rounds=1)
        pro_text = "alpha beta gamma delta epsilon"  # 5 words
        con_text = "one two three four five six"     # 6 words
        result = father.run_debate(
            "topic",
            MockAgent("pro", [pro_text]),
            MockAgent("con", [con_text]),
        )
        assert result.context_tokens == round((5 + 6) * 1.3)


# ---------------------------------------------------------------------------
# 8. Verdict fields
# ---------------------------------------------------------------------------


class TestVerdictFields:
    def test_verdict_has_winner_string(self) -> None:
        """winner must be exactly 'pro' or 'con'."""
        father = _make_father(rounds=2)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert result.winner in ("pro", "con")

    def test_verdict_has_non_empty_transcript(self) -> None:
        """transcript in DebateResult must be a non-empty list of DebateMessage."""
        father = _make_father(rounds=2)
        result = father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        assert isinstance(result.transcript, list)
        assert len(result.transcript) > 0


# ---------------------------------------------------------------------------
# 9. Skill prompt and generate_argument pass-through
# ---------------------------------------------------------------------------


class TestSkillAndRouting:
    def test_get_skill_prompt_loads_father_skill_file(self) -> None:
        """get_skill_prompt must return content from father_skill.md containing 'FATHER'."""
        father = _make_father()
        prompt = father.get_skill_prompt()
        assert "father" in prompt.lower()

    def test_generate_argument_returns_debate_message(self) -> None:
        """generate_argument on FatherAgent must return a DebateMessage (routing stub)."""
        father = _make_father()
        msg = DebateMessage(type="argument", round=1, sender="pro", content="test argument here.")
        result = father.generate_argument(msg)
        assert isinstance(result, DebateMessage)


# ---------------------------------------------------------------------------
# 10. ArgumentScorer unit tests
# ---------------------------------------------------------------------------


class TestArgumentScorer:
    def test_score_returns_float_in_range(self) -> None:
        """ArgumentScorer.score must return a float in [0.0, 100.0]."""
        scorer = ArgumentScorer()
        history = [
            DebateMessage(type="argument", round=1, sender="pro",
                          content="According to research, remote work shows 13% productivity gain.",
                          word_count=10)
        ]
        score = scorer.score(history, word_limit=150)
        assert 0.0 <= score <= 100.0

    def test_evidence_marker_boosts_score(self) -> None:
        """Arguments with evidence markers must score higher than those without."""
        scorer = ArgumentScorer()
        with_evidence = [
            DebateMessage(type="argument", round=1, sender="pro",
                          content="Studies show 13% gain. See http://study.com for research data.",
                          word_count=12)
        ]
        without_evidence = [
            DebateMessage(type="argument", round=1, sender="pro",
                          content="I think remote work might be better for certain individuals.",
                          word_count=10)
        ]
        assert scorer.score(with_evidence, word_limit=150) > scorer.score(without_evidence, word_limit=150)


# ---------------------------------------------------------------------------
# 11. Context compaction logging
# ---------------------------------------------------------------------------


class TestCompaction:
    def test_compaction_logged_after_summarize_round(self) -> None:
        """Logger must receive a 'context_compact' event after the summarize_after round."""
        logger = MagicMock()
        gk = MagicMock()
        father = FatherAgent(
            role="father",
            config_manager=FakeCfg(rounds=4, summarize_after=2),
            gatekeeper=gk,
            logger=logger,
        )
        father.run_debate("topic", MockAgent("pro", _std_responses()), MockAgent("con", _std_responses()))
        calls = [str(c) for c in logger.info.call_args_list]
        assert any("compact" in c for c in calls)
