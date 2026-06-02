"""ConAgent — argues AGAINST remote work; loads its skill from src/debate/skills/con_skill.md."""

from __future__ import annotations

from pathlib import Path

from debate.agents.base_agent import BaseAgent, DebateMessage


class ConAgent(BaseAgent):
    """Debate agent that always argues office work is superior to remote work.

    Skill files:
      con_skill.md                  — debate role and style
      News_Argumentation_Analysis   — breaks down CON's own search evidence
      Logical_Fallacy_Detection     — exposes flawed reasoning in PRO's argument
    """

    def get_skill_prompt(self) -> str:
        skill_path = Path(self._skills_path) / "con_skill.md"
        return skill_path.read_text(encoding="utf-8")

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        """Search evidence, analyse it and the opponent's reasoning, then rebut."""
        query = (
            f"office work benefits collaboration culture productivity on-site {opponent_msg.content[:80]}"
        )
        results = self.search_web(query)
        evidence = self._format_evidence(results)
        evidence_analysis = self._analyse_evidence(evidence)
        fallacy_analysis = self._detect_fallacies(opponent_msg.content)
        prompt = self._build_con_prompt(opponent_msg, evidence, evidence_analysis, fallacy_analysis)
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

    def _load_skill_file(self, filename: str) -> str:
        try:
            return (Path(self._skills_path) / filename).read_text(encoding="utf-8")
        except OSError:
            return ""

    def _analyse_evidence(self, evidence: str) -> str:
        """Run News_Argumentation_Analysis on CON's own search results.

        Identifies weak premises and exploitable counter-arguments in the evidence.
        """
        if not evidence or evidence == "No search results available.":
            return ""
        skill = self._load_skill_file("News_Argumentation_Analysis.md")
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

    def _detect_fallacies(self, opponent_argument: str) -> str:
        """Run Logical_Fallacy_Detection on the opponent's last argument.

        Returns a structured breakdown of reasoning errors in PRO's argument,
        or empty string if the skill file is missing or the call fails.
        """
        if not opponent_argument:
            return ""
        skill = self._load_skill_file("Logical_Fallacy_Detection.md")
        if not skill:
            return ""
        prompt = (
            f"{skill}\n\n"
            f"OPPONENT'S ARGUMENT TO ANALYSE:\n{opponent_argument}\n\n"
            f"Apply the full fallacy detection framework. "
            f"Identify every reasoning error in the argument above and rate "
            f"each by severity. Prioritise CRITICAL and SIGNIFICANT fallacies "
            f"that the CON debater can lead with."
        )
        try:
            return self._call_llm(prompt)
        except Exception:  # noqa: BLE001
            return ""

    def _build_con_prompt(
        self,
        opponent_msg: DebateMessage,
        evidence: str,
        evidence_analysis: str,
        fallacy_analysis: str,
    ) -> str:
        """Build the full CON prompt with both analysis layers."""
        evidence_block = (
            f"\nEVIDENCE CLAIM ANALYSIS (weak premises and counter-arguments "
            f"from CON's own search results):\n{evidence_analysis}\n"
            if evidence_analysis
            else ""
        )
        fallacy_block = (
            f"\nOPPONENT REASONING ANALYSIS (logical fallacies detected in "
            f"PRO's last argument — lead with the CRITICAL ones):\n{fallacy_analysis}\n"
            if fallacy_analysis
            else ""
        )
        return (
            f"{self.get_skill_prompt()}\n\n"
            f"OPPONENT'S ARGUMENT (round {opponent_msg.round}):\n{opponent_msg.content}\n\n"
            f"RAW EVIDENCE FROM WEB SEARCH:\n{evidence}\n"
            f"{evidence_block}"
            f"{fallacy_block}\n"
            f"Using the analyses above: first expose the most critical logical "
            f"fallacy in the opponent's reasoning, then introduce a new angle "
            f"backed by the strongest evidence from the claim analysis.\n\n"
            f"Respond in {self._word_limit} words or fewer. "
            f"Start by directly addressing the opponent's specific claim."
        )
