"""Unit tests for ProAgent and ConAgent — TDD Red phase written before implementation."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from debate.agents.base_agent import DebateMessage
from debate.agents.con_agent import ConAgent
from debate.agents.pro_agent import ProAgent

# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------


class FakeCfg:
    def __init__(self, word_limit: int = 150) -> None:
        self.setup = {
            "debate": {
                "model": "claude-haiku-4-5",
                "timeout_seconds": 5.0,
                "word_limit": word_limit,
                "rounds": 10,
            }
        }
        self.rate_limits = {
            "anthropic": {"max_tokens_per_call": 500},
            "tavily": {"max_results_per_search": 3},
        }


def _make_mock_response(text: str = "This is a test argument.") -> MagicMock:
    resp = MagicMock()
    resp.usage.input_tokens = 10
    resp.usage.output_tokens = 20
    resp.content = [MagicMock(text=text)]
    return resp


def _make_mock_tavily(snippet: str = "Remote work increases productivity by 13%.") -> MagicMock:
    tavily = MagicMock()
    tavily.search.return_value = {
        "results": [{"title": "Study 1", "url": "https://study1.com", "content": snippet}]
    }
    return tavily


def _make_pro(
    word_limit: int = 150,
    response_text: str = "Remote work is clearly superior.",
) -> tuple[ProAgent, MagicMock, MagicMock]:
    gk = MagicMock()
    gk.call.return_value = _make_mock_response(response_text)
    tavily = _make_mock_tavily()
    agent = ProAgent(
        role="pro", config_manager=FakeCfg(word_limit), gatekeeper=gk, tavily=tavily
    )
    return agent, gk, tavily


def _make_con(
    word_limit: int = 150,
    response_text: str = "Office work is clearly superior.",
) -> tuple[ConAgent, MagicMock, MagicMock]:
    gk = MagicMock()
    gk.call.return_value = _make_mock_response(response_text)
    tavily = _make_mock_tavily("Office collaboration improves output by 20%.")
    agent = ConAgent(
        role="con", config_manager=FakeCfg(word_limit), gatekeeper=gk, tavily=tavily
    )
    return agent, gk, tavily


def _opponent_msg(
    content: str = "Office work builds team culture and trust.",
    round_num: int = 1,
    sender: str = "con",
) -> DebateMessage:
    return DebateMessage(type="argument", round=round_num, sender=sender, content=content)


# ---------------------------------------------------------------------------
# 1. ProAgent always argues FOR (never agrees)
# ---------------------------------------------------------------------------
class TestProAgentSkill:
    def test_pro_skill_prompt_argues_for_remote_work(self) -> None:
        """PRO skill prompt must express a position in favour of remote work."""
        pro, _, _ = _make_pro()
        prompt = pro.get_skill_prompt()
        # Must advocate FOR remote work — not office work
        assert any(
            kw in prompt.lower()
            for kw in ("remote work", "remote is", "pro", "for remote", "superior")
        )

    def test_pro_skill_prompt_instructs_never_agree(self) -> None:
        """PRO prompt must explicitly instruct the agent to never agree with the opponent."""
        pro, _, _ = _make_pro()
        prompt = pro.get_skill_prompt()
        assert "never" in prompt.lower() or "do not agree" in prompt.lower()

    def test_pro_skill_prompt_instructs_challenge_evidence(self) -> None:
        """PRO prompt must tell the agent to challenge the opponent's evidence."""
        pro, _, _ = _make_pro()
        prompt = pro.get_skill_prompt()
        assert any(
            kw in prompt.lower()
            for kw in ("challenge", "flaw", "counter", "attack", "rebut", "doesn't hold", "point doesn't")
        )


# ---------------------------------------------------------------------------
# 2. ConAgent always argues AGAINST (never agrees)
# ---------------------------------------------------------------------------
class TestConAgentSkill:
    def test_con_skill_prompt_argues_against_remote_work(self) -> None:
        """CON skill prompt must express a position in favour of office work."""
        con, _, _ = _make_con()
        prompt = con.get_skill_prompt()
        assert any(
            kw in prompt.lower()
            for kw in ("office", "in-person", "against remote", "con", "on-site")
        )

    def test_con_skill_prompt_instructs_never_concede(self) -> None:
        """CON prompt must explicitly instruct the agent to never concede any point."""
        con, _, _ = _make_con()
        prompt = con.get_skill_prompt()
        assert "never" in prompt.lower() or "do not concede" in prompt.lower()

    def test_con_skill_prompt_instructs_find_fallacies(self) -> None:
        """CON prompt must instruct the agent to expose logical flaws or question evidence."""
        con, _, _ = _make_con()
        prompt = con.get_skill_prompt()
        assert any(
            kw in prompt.lower()
            for kw in (
                "fallac", "weakest", "flaw", "assumption", "logical", "expose",
                "challenge", "skeptical", "doesn't convince",
            )
        )


# ---------------------------------------------------------------------------
# 3. Each agent's skill prompt is different from the other
# ---------------------------------------------------------------------------
class TestDistinctSkills:
    def test_skill_prompts_are_different(self) -> None:
        """PRO and CON must have distinct, non-identical skill prompts."""
        pro, _, _ = _make_pro()
        con, _, _ = _make_con()
        assert pro.get_skill_prompt() != con.get_skill_prompt()

    def test_pro_and_con_search_in_opposite_directions(self) -> None:
        """PRO and CON must submit different search queries reflecting their positions."""
        pro, _, pro_tavily = _make_pro()
        con, _, con_tavily = _make_con()
        msg = _opponent_msg()

        pro.generate_argument(msg)
        con.generate_argument(msg)

        pro_query = pro_tavily.search.call_args.kwargs["query"]
        con_query = con_tavily.search.call_args.kwargs["query"]
        assert pro_query != con_query


# ---------------------------------------------------------------------------
# 4. Each agent references opponent's last argument
# ---------------------------------------------------------------------------
class TestOpponentReference:
    def test_pro_prompt_contains_opponent_content(self) -> None:
        """The LLM prompt built by ProAgent must contain the opponent's argument text."""
        pro, gk, _ = _make_pro()
        msg = _opponent_msg(content="Office workers collaborate 40% better on complex tasks.")
        pro.generate_argument(msg)
        sent_messages = gk.call.call_args.kwargs["messages"]
        user_content = sent_messages[0]["content"]
        assert "Office workers collaborate 40% better on complex tasks." in user_content

    def test_con_prompt_contains_opponent_content(self) -> None:
        """The LLM prompt built by ConAgent must contain the opponent's argument text."""
        con, gk, _ = _make_con()
        msg = _opponent_msg(content="Stanford study shows 13% productivity gain from remote work.", sender="pro")
        con.generate_argument(msg)
        sent_messages = gk.call.call_args.kwargs["messages"]
        user_content = sent_messages[0]["content"]
        assert "Stanford study shows 13% productivity gain from remote work." in user_content


# ---------------------------------------------------------------------------
# 5. Web search called and result included in argument
# ---------------------------------------------------------------------------
class TestWebSearch:
    def test_pro_calls_web_search_during_argument(self) -> None:
        """ProAgent must call Tavily search exactly once per generate_argument."""
        pro, _, tavily = _make_pro()
        pro.generate_argument(_opponent_msg())
        tavily.search.assert_called_once()

    def test_con_calls_web_search_during_argument(self) -> None:
        """ConAgent must call Tavily search exactly once per generate_argument."""
        con, _, tavily = _make_con()
        con.generate_argument(_opponent_msg())
        tavily.search.assert_called_once()

    def test_pro_search_result_included_in_llm_prompt(self) -> None:
        """Search result snippet must appear in the prompt sent to the LLM."""
        snippet = "Studies show remote workers save 2 hours per day commuting."
        gk = MagicMock()
        gk.call.return_value = _make_mock_response()
        tavily = MagicMock()
        tavily.search.return_value = {
            "results": [{"title": "Study", "url": "https://ex.com", "content": snippet}]
        }
        pro = ProAgent(role="pro", config_manager=FakeCfg(), gatekeeper=gk, tavily=tavily)
        pro.generate_argument(_opponent_msg())
        user_content = gk.call.call_args.kwargs["messages"][0]["content"]
        assert snippet in user_content

    def test_con_search_result_included_in_llm_prompt(self) -> None:
        """ConAgent must include Tavily evidence in the LLM prompt."""
        snippet = "In-person brainstorming produces 42% more creative solutions."
        gk = MagicMock()
        gk.call.return_value = _make_mock_response()
        tavily = MagicMock()
        tavily.search.return_value = {
            "results": [{"title": "Research", "url": "https://r.com", "content": snippet}]
        }
        con = ConAgent(role="con", config_manager=FakeCfg(), gatekeeper=gk, tavily=tavily)
        con.generate_argument(_opponent_msg())
        user_content = gk.call.call_args.kwargs["messages"][0]["content"]
        assert snippet in user_content


# ---------------------------------------------------------------------------
# 6. Arguments within word limit from config
# ---------------------------------------------------------------------------
class TestWordLimit:
    def test_pro_argument_within_word_limit(self) -> None:
        """ProAgent response must be truncated to word_limit when LLM returns more words."""
        long_response = " ".join(f"word{i}" for i in range(20))  # 20 words
        pro, _, _ = _make_pro(word_limit=5, response_text=long_response)
        msg = pro.generate_argument(_opponent_msg())
        assert len(msg.content.split()) <= 5

    def test_con_argument_within_word_limit(self) -> None:
        """ConAgent response must be truncated to word_limit when LLM returns more words."""
        long_response = " ".join(f"word{i}" for i in range(20))
        con, _, _ = _make_con(word_limit=5, response_text=long_response)
        msg = con.generate_argument(_opponent_msg())
        assert len(msg.content.split()) <= 5

    def test_enforce_word_limit_truncates(self) -> None:
        """_enforce_word_limit must cut text to exactly word_limit words."""
        pro, _, _ = _make_pro(word_limit=3)
        result = pro._enforce_word_limit("one two three four five six")  # noqa: SLF001
        assert result == "one two three"

    def test_enforce_word_limit_passes_short_text(self) -> None:
        """_enforce_word_limit must leave text unchanged when already within limit."""
        pro, _, _ = _make_pro(word_limit=10)
        result = pro._enforce_word_limit("just three words")  # noqa: SLF001
        assert result == "just three words"


# ---------------------------------------------------------------------------
# 7. JSON format correct and valid
# ---------------------------------------------------------------------------
class TestJsonFormat:
    def test_pro_generate_argument_returns_debate_message(self) -> None:
        """ProAgent.generate_argument must return a DebateMessage instance."""
        pro, _, _ = _make_pro()
        msg = pro.generate_argument(_opponent_msg())
        assert isinstance(msg, DebateMessage)

    def test_con_generate_argument_returns_debate_message(self) -> None:
        """ConAgent.generate_argument must return a DebateMessage instance."""
        con, _, _ = _make_con()
        msg = con.generate_argument(_opponent_msg())
        assert isinstance(msg, DebateMessage)

    def test_pro_output_is_json_serializable(self) -> None:
        """DebateMessage from ProAgent must be valid JSON."""
        pro, _, _ = _make_pro()
        msg = pro.generate_argument(_opponent_msg())
        parsed = json.loads(msg.to_json())
        assert parsed["sender"] == "pro"
        assert parsed["type"] == "argument"

    def test_con_output_is_json_serializable(self) -> None:
        """DebateMessage from ConAgent must be valid JSON."""
        con, _, _ = _make_con()
        msg = con.generate_argument(_opponent_msg())
        parsed = json.loads(msg.to_json())
        assert parsed["sender"] == "con"
        assert parsed["type"] == "argument"

    def test_round_incremented_by_one(self) -> None:
        """Round in the returned message must be opponent_round + 1."""
        pro, _, _ = _make_pro()
        msg = pro.generate_argument(_opponent_msg(round_num=3))
        assert msg.round == 4


# ---------------------------------------------------------------------------
# 8. Agents never communicate directly
# ---------------------------------------------------------------------------
class TestNoDirectCommunication:
    def test_pro_has_no_con_agent_reference(self) -> None:
        """ProAgent must not hold a reference to ConAgent."""
        pro, _, _ = _make_pro()
        assert not hasattr(pro, "_con_agent")
        assert not hasattr(pro, "_opponent_agent")
        assert not hasattr(pro, "_opponent")

    def test_con_has_no_pro_agent_reference(self) -> None:
        """ConAgent must not hold a reference to ProAgent."""
        con, _, _ = _make_con()
        assert not hasattr(con, "_pro_agent")
        assert not hasattr(con, "_opponent_agent")
        assert not hasattr(con, "_opponent")

    def test_generate_argument_accepts_only_debate_message(self) -> None:
        """generate_argument must accept a DebateMessage, not another agent instance."""
        pro, _, _ = _make_pro()
        con_instance = _make_con()[0]
        with pytest.raises((AttributeError, TypeError)):
            pro.generate_argument(con_instance)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 9. Statistical Reasoning skill integration (ProAgent)
# ---------------------------------------------------------------------------

class TestProStatisticalReasoning:
    def test_analyse_statistics_returns_empty_when_no_evidence(self) -> None:
        """_analyse_statistics must return '' when evidence is empty string."""
        pro, _, _ = _make_pro()
        assert pro._analyse_statistics("") == ""

    def test_analyse_statistics_returns_empty_for_no_results_sentinel(self) -> None:
        """_analyse_statistics must return '' for the 'No search results' sentinel."""
        pro, _, _ = _make_pro()
        assert pro._analyse_statistics("No search results available.") == ""

    def test_analyse_statistics_returns_empty_when_skill_file_missing(self, tmp_path: pytest.fixture) -> None:
        """_analyse_statistics must return '' gracefully when skill file does not exist."""
        gk = MagicMock()
        gk.call.return_value = _make_mock_response()
        cfg = FakeCfg()
        cfg.setup["debate"]["skills_path"] = str(tmp_path) + "/"
        # Write only pro_skill.md so Statistical_Reasoning.md is absent
        (tmp_path / "pro_skill.md").write_text("PRO skill content", encoding="utf-8")
        pro = ProAgent(role="pro", config_manager=cfg, gatekeeper=gk)
        assert pro._analyse_statistics("Some evidence here.") == ""

    def test_build_pro_prompt_without_analysis_still_has_opponent_content(self) -> None:
        """_build_pro_prompt with empty stat_analysis must still include opponent argument."""
        pro, _, _ = _make_pro()
        msg = DebateMessage(type="argument", round=2, sender="con", content="Offices beat remote.")
        prompt = pro._build_pro_prompt(msg, "some evidence", "")
        assert "Offices beat remote." in prompt

    def test_build_pro_prompt_with_analysis_includes_stat_block(self) -> None:
        """_build_pro_prompt with stat_analysis must inject the analysis block."""
        pro, _, _ = _make_pro()
        msg = DebateMessage(type="argument", round=2, sender="con", content="Offices beat remote.")
        prompt = pro._build_pro_prompt(msg, "some evidence", "S1: STRONG stat here")
        assert "STATISTICAL VALIDITY ANALYSIS" in prompt
        assert "S1: STRONG stat here" in prompt


# ---------------------------------------------------------------------------
# 10. News Argumentation Analysis skill integration (ConAgent)
# ---------------------------------------------------------------------------

class TestConNewsAnalysis:
    def test_analyse_evidence_returns_empty_when_no_evidence(self) -> None:
        """_analyse_evidence must return '' when evidence is empty string."""
        con, _, _ = _make_con()
        assert con._analyse_evidence("") == ""

    def test_analyse_evidence_returns_empty_for_no_results_sentinel(self) -> None:
        """_analyse_evidence must return '' for the 'No search results' sentinel."""
        con, _, _ = _make_con()
        assert con._analyse_evidence("No search results available.") == ""

    def test_analyse_evidence_returns_empty_when_skill_file_missing(self, tmp_path: pytest.fixture) -> None:
        """_analyse_evidence must return '' gracefully when skill file does not exist."""
        gk = MagicMock()
        gk.call.return_value = _make_mock_response()
        cfg = FakeCfg()
        cfg.setup["debate"]["skills_path"] = str(tmp_path) + "/"
        (tmp_path / "con_skill.md").write_text("CON skill content", encoding="utf-8")
        con = ConAgent(role="con", config_manager=cfg, gatekeeper=gk)
        assert con._analyse_evidence("Some evidence here.") == ""

    def test_build_con_prompt_without_analysis_still_has_opponent_content(self) -> None:
        """_build_con_prompt with empty analysis must still include opponent argument."""
        con, _, _ = _make_con()
        msg = DebateMessage(type="argument", round=2, sender="pro", content="Remote beats offices.")
        prompt = con._build_con_prompt(msg, "some evidence", "")
        assert "Remote beats offices." in prompt

    def test_build_con_prompt_with_analysis_includes_claim_block(self) -> None:
        """_build_con_prompt with analysis must inject the structured claim block."""
        con, _, _ = _make_con()
        msg = DebateMessage(type="argument", round=2, sender="pro", content="Remote beats offices.")
        prompt = con._build_con_prompt(msg, "some evidence", "CLAIM C1: weak premise here")
        assert "STRUCTURED CLAIM ANALYSIS" in prompt
        assert "CLAIM C1: weak premise here" in prompt
