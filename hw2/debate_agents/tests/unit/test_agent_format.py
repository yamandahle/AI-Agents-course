"""Tests for word limits, JSON format, and agent isolation."""

from __future__ import annotations

import json

import pytest
from agent_test_helpers import make_con, make_pro, opponent_msg

from debate.agents.base_agent import DebateMessage


class TestWordLimit:
    def test_pro_argument_within_word_limit(self) -> None:
        long_response = " ".join(f"word{i}" for i in range(20))
        pro, _, _ = make_pro(word_limit=5, response_text=long_response)
        msg = pro.generate_argument(opponent_msg())
        assert len(msg.content.split()) <= 5

    def test_con_argument_within_word_limit(self) -> None:
        long_response = " ".join(f"word{i}" for i in range(20))
        con, _, _ = make_con(word_limit=5, response_text=long_response)
        msg = con.generate_argument(opponent_msg())
        assert len(msg.content.split()) <= 5

    def test_enforce_word_limit_truncates(self) -> None:
        pro, _, _ = make_pro(word_limit=3)
        assert pro._enforce_word_limit("one two three four five six") == "one two three"  # noqa: SLF001

    def test_enforce_word_limit_passes_short_text(self) -> None:
        pro, _, _ = make_pro(word_limit=10)
        assert pro._enforce_word_limit("just three words") == "just three words"  # noqa: SLF001


class TestJsonFormat:
    def test_pro_generate_argument_returns_debate_message(self) -> None:
        pro, _, _ = make_pro()
        assert isinstance(pro.generate_argument(opponent_msg()), DebateMessage)

    def test_con_generate_argument_returns_debate_message(self) -> None:
        con, _, _ = make_con()
        assert isinstance(con.generate_argument(opponent_msg()), DebateMessage)

    def test_pro_output_is_json_serializable(self) -> None:
        pro, _, _ = make_pro()
        msg = pro.generate_argument(opponent_msg())
        parsed = json.loads(msg.to_json())
        assert parsed["sender"] == "pro"
        assert parsed["type"] == "argument"

    def test_con_output_is_json_serializable(self) -> None:
        con, _, _ = make_con()
        msg = con.generate_argument(opponent_msg())
        parsed = json.loads(msg.to_json())
        assert parsed["sender"] == "con"
        assert parsed["type"] == "argument"

    def test_round_incremented_by_one(self) -> None:
        pro, _, _ = make_pro()
        msg = pro.generate_argument(opponent_msg(round_num=3))
        assert msg.round == 4


class TestNoDirectCommunication:
    def test_pro_has_no_con_agent_reference(self) -> None:
        pro, _, _ = make_pro()
        assert not hasattr(pro, "_con_agent")
        assert not hasattr(pro, "_opponent_agent")

    def test_con_has_no_pro_agent_reference(self) -> None:
        con, _, _ = make_con()
        assert not hasattr(con, "_pro_agent")
        assert not hasattr(con, "_opponent_agent")

    def test_generate_argument_accepts_only_debate_message(self) -> None:
        pro, _, _ = make_pro()
        con_instance = make_con()[0]
        with pytest.raises((AttributeError, TypeError)):
            pro.generate_argument(con_instance)  # type: ignore[arg-type]
