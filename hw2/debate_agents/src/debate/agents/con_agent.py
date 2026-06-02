"""ConAgent — argues AGAINST remote work; loads its skill from src/debate/skills/con_skill.md."""

from __future__ import annotations

from pathlib import Path

from debate.agents.base_agent import BaseAgent, DebateMessage


class ConAgent(BaseAgent):
    """Debate agent that always argues office work is superior to remote work.

    Skill file: src/debate/skills/con_skill.md
    Analysis skill: src/debate/skills/News_Argumentation_Analysis.md
    Style: skeptical, direct, exposes weak premises using structured claim analysis.
    """

    def get_skill_prompt(self) -> str:
        skill_path = Path(self._skills_path) / "con_skill.md"
        return skill_path.read_text(encoding="utf-8")

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        """Search for evidence, analyse it with News_Argumentation_Analysis, then rebut."""
        query = (
            f"office work benefits collaboration culture productivity on-site {opponent_msg.content[:80]}"
        )
        results = self.search_web(query)
        evidence = self._format_evidence(results)
        analysis = self._analyse_evidence(evidence)
        prompt = self._build_con_prompt(opponent_msg, evidence, analysis)
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

    def _load_analysis_skill(self) -> str:
        skill_path = Path(self._skills_path) / "News_Argumentation_Analysis.md"
        try:
            return skill_path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def _analyse_evidence(self, evidence: str) -> str:
        """Run the News Argumentation Analysis skill on raw search evidence.

        Returns a structured claim breakdown, or empty string if evidence is
        unavailable or the analysis call fails.
        """
        if not evidence or evidence == "No search results available.":
            return ""
        skill = self._load_analysis_skill()
        if not skill:
            return ""
        prompt = (
            f"{skill}\n\n"
            f"EVIDENCE TO ANALYSE (from web search):\n{evidence}\n\n"
            f"Apply the full analysis framework to this evidence. "
            f"Focus on identifying weak premises and missing counter-arguments "
            f"that the CON debater can exploit."
        )
        try:
            return self._call_llm(prompt)
        except Exception:  # noqa: BLE001
            return ""

    def _build_con_prompt(
        self, opponent_msg: DebateMessage, evidence: str, analysis: str
    ) -> str:
        """Build the full CON prompt including structured evidence analysis."""
        analysis_block = (
            f"\nSTRUCTURED CLAIM ANALYSIS (use this to find weak premises and "
            f"counter-arguments in the evidence):\n{analysis}\n"
            if analysis
            else ""
        )
        return (
            f"{self.get_skill_prompt()}\n\n"
            f"OPPONENT'S ARGUMENT (round {opponent_msg.round}):\n{opponent_msg.content}\n\n"
            f"RAW EVIDENCE FROM WEB SEARCH:\n{evidence}\n"
            f"{analysis_block}\n"
            f"Using the claim analysis above, identify the weakest premise in the "
            f"opponent's argument and expose it. Then introduce a new angle backed "
            f"by the strongest evidence from the analysis.\n\n"
            f"Respond in {self._word_limit} words or fewer. "
            f"Start by directly addressing the opponent's specific claim."
        )
