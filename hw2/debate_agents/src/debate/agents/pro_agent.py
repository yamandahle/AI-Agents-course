"""ProAgent — argues FOR remote work; loads its skill from src/debate/skills/pro_skill.md."""

from __future__ import annotations

from pathlib import Path

from debate.agents.base_agent import BaseAgent, DebateMessage


class ProAgent(BaseAgent):
    """Debate agent that always argues remote work is superior to office work.

    Skill file: src/debate/skills/pro_skill.md
    Analysis skill: src/debate/skills/Statistical_Reasoning.md
    Style: analytical, data-driven, validates statistics before using them.
    """

    def get_skill_prompt(self) -> str:
        skill_path = Path(self._skills_path) / "pro_skill.md"
        return skill_path.read_text(encoding="utf-8")

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        """Build opening statement on round 0, then statistically validated rebuttals."""
        if opponent_msg.round == 0:
            prompt = self._build_opening_prompt(opponent_msg.content)
        else:
            query = f"remote work productivity benefits statistics evidence {opponent_msg.content[:80]}"
            results = self.search_web(query)
            evidence = self._format_evidence(results)
            stat_analysis = self._analyse_statistics(evidence)
            prompt = self._build_pro_prompt(opponent_msg, evidence, stat_analysis)
        raw = self._call_llm(prompt)
        concept = self._extract_concept(raw)
        url = self._extract_url(raw)
        text = self._enforce_word_limit(self._extract_argument(raw))
        msg = self.send_message(text, ping_num=opponent_msg.round + 1)
        msg.concept = concept
        msg.evidence_url = url
        return msg

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_stat_skill(self) -> str:
        skill_path = Path(self._skills_path) / "Statistical_Reasoning.md"
        try:
            return skill_path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def _analyse_statistics(self, evidence: str) -> str:
        """Run the Statistical Reasoning skill on raw search evidence.

        Returns a validity-rated breakdown of every statistic found,
        or empty string if evidence is unavailable or the call fails.
        """
        if not evidence or evidence == "No search results available.":
            return ""
        skill = self._load_stat_skill()
        if not skill:
            return ""
        prompt = (
            f"{skill}\n\n"
            f"EVIDENCE TO EVALUATE (from web search):\n{evidence}\n\n"
            f"Apply the full statistical reasoning framework to this evidence. "
            f"Identify the strongest statistics PRO can use and flag any the "
            f"opponent is likely to attack."
        )
        try:
            return self._call_llm(prompt)
        except Exception:  # noqa: BLE001
            return ""

    def _build_pro_prompt(
        self, opponent_msg: DebateMessage, evidence: str, stat_analysis: str
    ) -> str:
        """Build the full PRO prompt including statistical validity analysis."""
        stat_block = (
            f"\nSTATISTICAL VALIDITY ANALYSIS (use STRONG and MODERATE stats only; "
            f"exploit the opponent vulnerabilities listed):\n{stat_analysis}\n"
            if stat_analysis
            else ""
        )
        return (
            f"{self.get_skill_prompt()}\n\n"
            f"OPPONENT'S ARGUMENT (round {opponent_msg.round}):\n{opponent_msg.content}\n\n"
            f"RAW EVIDENCE FROM WEB SEARCH:\n{evidence}\n"
            f"{stat_block}\n"
            f"Use only STRONG or MODERATE statistics from the analysis above. "
            f"If the analysis flagged an opponent vulnerability, pre-emptively "
            f"expose it in your rebuttal.\n\n"
            f"Respond in {self._word_limit} words or fewer. "
            f"Start by directly addressing the opponent's specific claim."
        )
