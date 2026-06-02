"""Unit tests for ProAgent skill and Statistical Reasoning integration."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from agent_test_helpers import FakeCfg, make_mock_response, make_pro

from debate.agents.base_agent import DebateMessage
from debate.agents.pro_agent import ProAgent


class TestProAgentSkill:
    def test_pro_skill_prompt_argues_for_remote_work(self) -> None:
        pro, _, _ = make_pro()
        prompt = pro.get_skill_prompt()
        assert any(kw in prompt.lower() for kw in ("remote work", "remote is", "pro", "for remote", "superior"))

    def test_pro_skill_prompt_instructs_never_agree(self) -> None:
        pro, _, _ = make_pro()
        prompt = pro.get_skill_prompt()
        assert "never" in prompt.lower() or "do not agree" in prompt.lower()

    def test_pro_skill_prompt_instructs_challenge_evidence(self) -> None:
        pro, _, _ = make_pro()
        prompt = pro.get_skill_prompt()
        assert any(kw in prompt.lower() for kw in ("challenge", "flaw", "counter", "attack", "rebut"))


class TestProStatisticalReasoning:
    def test_analyse_statistics_returns_empty_when_no_evidence(self) -> None:
        pro, _, _ = make_pro()
        assert pro._analyse_statistics("") == ""  # noqa: SLF001

    def test_analyse_statistics_returns_empty_for_no_results_sentinel(self) -> None:
        pro, _, _ = make_pro()
        assert pro._analyse_statistics("No search results available.") == ""  # noqa: SLF001

    def test_analyse_statistics_returns_empty_when_skill_file_missing(self, tmp_path: pytest.MonkeyPatch) -> None:
        gk = MagicMock()
        gk.call.return_value = make_mock_response()
        cfg = FakeCfg()
        cfg.setup["debate"]["skills_path"] = str(tmp_path) + "/"
        (tmp_path / "pro_skill.md").write_text("PRO skill content", encoding="utf-8")
        pro = ProAgent(role="pro", config_manager=cfg, gatekeeper=gk)
        assert pro._analyse_statistics("Some evidence here.") == ""  # noqa: SLF001

    def test_build_pro_prompt_without_analysis_still_has_opponent_content(self) -> None:
        pro, _, _ = make_pro()
        msg = DebateMessage(type="argument", round=2, sender="con", content="Offices beat remote.")
        prompt = pro._build_pro_prompt(msg, "some evidence", "")  # noqa: SLF001
        assert "Offices beat remote." in prompt

    def test_build_pro_prompt_with_analysis_includes_stat_block(self) -> None:
        pro, _, _ = make_pro()
        msg = DebateMessage(type="argument", round=2, sender="con", content="Offices beat remote.")
        prompt = pro._build_pro_prompt(msg, "some evidence", "S1: STRONG stat here")  # noqa: SLF001
        assert "STATISTICAL VALIDITY ANALYSIS" in prompt
        assert "S1: STRONG stat here" in prompt
