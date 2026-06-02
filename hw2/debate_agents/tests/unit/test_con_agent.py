"""Unit tests for ConAgent skill and specialist skill integrations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from agent_test_helpers import FakeCfg, make_con, make_mock_response

from debate.agents.base_agent import DebateMessage
from debate.agents.con_agent import ConAgent


class TestConAgentSkill:
    def test_con_skill_prompt_argues_against_remote_work(self) -> None:
        con, _, _ = make_con()
        prompt = con.get_skill_prompt()
        assert any(kw in prompt.lower() for kw in ("office", "in-person", "against remote", "con", "on-site"))

    def test_con_skill_prompt_instructs_never_concede(self) -> None:
        con, _, _ = make_con()
        prompt = con.get_skill_prompt()
        assert "never" in prompt.lower() or "do not concede" in prompt.lower()

    def test_con_skill_prompt_instructs_find_fallacies(self) -> None:
        con, _, _ = make_con()
        prompt = con.get_skill_prompt()
        assert any(kw in prompt.lower() for kw in ("fallac", "weakest", "flaw", "assumption", "logical", "expose", "challenge", "skeptical"))


class TestConNewsAnalysis:
    def test_analyse_evidence_returns_empty_when_no_evidence(self) -> None:
        con, _, _ = make_con()
        assert con._analyse_evidence("") == ""  # noqa: SLF001

    def test_analyse_evidence_returns_empty_for_no_results_sentinel(self) -> None:
        con, _, _ = make_con()
        assert con._analyse_evidence("No search results available.") == ""  # noqa: SLF001

    def test_analyse_evidence_returns_empty_when_skill_file_missing(self, tmp_path: pytest.MonkeyPatch) -> None:
        gk = MagicMock()
        gk.call.return_value = make_mock_response()
        cfg = FakeCfg()
        cfg.setup["debate"]["skills_path"] = str(tmp_path) + "/"
        (tmp_path / "con_skill.md").write_text("CON skill content", encoding="utf-8")
        con = ConAgent(role="con", config_manager=cfg, gatekeeper=gk)
        assert con._analyse_evidence("Some evidence here.") == ""  # noqa: SLF001

    def test_build_con_prompt_without_analysis_still_has_opponent_content(self) -> None:
        con, _, _ = make_con()
        msg = DebateMessage(type="argument", round=2, sender="pro", content="Remote beats offices.")
        prompt = con._build_con_prompt(msg, "some evidence", "", "")  # noqa: SLF001
        assert "Remote beats offices." in prompt

    def test_build_con_prompt_with_analysis_includes_claim_block(self) -> None:
        con, _, _ = make_con()
        msg = DebateMessage(type="argument", round=2, sender="pro", content="Remote beats offices.")
        prompt = con._build_con_prompt(msg, "some evidence", "CLAIM C1: weak premise here", "")  # noqa: SLF001
        assert "EVIDENCE CLAIM ANALYSIS" in prompt
        assert "CLAIM C1: weak premise here" in prompt

    def test_build_con_prompt_with_fallacy_includes_fallacy_block(self) -> None:
        con, _, _ = make_con()
        msg = DebateMessage(type="argument", round=2, sender="pro", content="Remote beats offices.")
        prompt = con._build_con_prompt(msg, "some evidence", "", "FALLACY: hasty generalisation found")  # noqa: SLF001
        assert "OPPONENT REASONING ANALYSIS" in prompt
        assert "hasty generalisation found" in prompt

    def test_detect_fallacies_returns_empty_when_skill_missing(self, tmp_path: pytest.MonkeyPatch) -> None:
        gk = MagicMock()
        gk.call.return_value = make_mock_response()
        cfg = FakeCfg()
        cfg.setup["debate"]["skills_path"] = str(tmp_path) + "/"
        (tmp_path / "con_skill.md").write_text("CON skill content", encoding="utf-8")
        con = ConAgent(role="con", config_manager=cfg, gatekeeper=gk)
        assert con._detect_fallacies("Some argument here.") == ""  # noqa: SLF001

    def test_detect_fallacies_returns_empty_for_empty_argument(self) -> None:
        con, _, _ = make_con()
        assert con._detect_fallacies("") == ""  # noqa: SLF001
