"""Tests for FatherAgent agreement and repetition detection."""

from __future__ import annotations

from father_test_helpers import make_father

from debate.agents.base_agent import DebateMessage


class TestAgreementDetection:
    def test_detect_agreement_true_for_i_agree(self) -> None:
        father = make_father()
        msg = DebateMessage(type="argument", round=1, sender="pro", content="I agree with your point here.")
        assert father._detect_agreement(msg) is True  # noqa: SLF001

    def test_detect_agreement_true_for_good_point(self) -> None:
        father = make_father()
        msg = DebateMessage(
            type="argument", round=1, sender="pro",
            content="That is a good point, however I disagree.",
        )
        assert father._detect_agreement(msg) is True  # noqa: SLF001

    def test_detect_agreement_false_for_normal_argument(self) -> None:
        father = make_father()
        msg = DebateMessage(
            type="argument", round=1, sender="pro",
            content="Remote work increases productivity by 13% according to Stanford research.",
        )
        assert father._detect_agreement(msg) is False  # noqa: SLF001


class TestRepetitionDetection:
    def test_detect_repetition_false_for_empty_history(self) -> None:
        father = make_father()
        msg = DebateMessage(type="argument", round=1, sender="pro", content="Remote work saves commute time.")
        assert father._detect_repetition(msg, []) is False  # noqa: SLF001

    def test_detect_repetition_true_for_near_duplicate(self) -> None:
        father = make_father()
        content = "Remote work saves commute time and increases employee productivity significantly."
        history = [DebateMessage(type="argument", round=1, sender="pro", content=content)]
        msg = DebateMessage(type="argument", round=2, sender="pro", content=content)
        assert father._detect_repetition(msg, history) is True  # noqa: SLF001

    def test_detect_repetition_false_for_different_argument(self) -> None:
        father = make_father()
        history = [DebateMessage(type="argument", round=1, sender="pro",
                                 content="Remote work saves commute time.")]
        msg = DebateMessage(
            type="argument", round=2, sender="pro",
            content="Office buildings drain municipal energy resources and generate pollution.",
        )
        assert father._detect_repetition(msg, history) is False  # noqa: SLF001
