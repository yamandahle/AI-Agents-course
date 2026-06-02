"""ConAgent — argues AGAINST remote work; loads its skill from src/debate/skills/con_skill.md."""

from __future__ import annotations

from pathlib import Path

from debate.agents.base_agent import BaseAgent, DebateMessage


class ConAgent(BaseAgent):
    """Debate agent that always argues office work is superior to remote work.

    Skill file: src/debate/skills/con_skill.md
    Style: skeptical, direct, challenges opponent's evidence and assumptions.
    """

    def get_skill_prompt(self) -> str:
        """Load and return the CON skill definition from the skills directory."""
        skill_path = Path(self._skills_path) / "con_skill.md"
        return skill_path.read_text(encoding="utf-8")

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        """Search for pro-office evidence, then build a skeptical rebuttal."""
        query = (
            f"office work benefits collaboration culture productivity on-site {opponent_msg.content[:80]}"
        )
        results = self.search_web(query)
        evidence = self._format_evidence(results)
        prompt = self._build_prompt(opponent_msg, evidence)
        raw = self._call_llm(prompt)
        concept = self._extract_concept(raw)
        text = self._enforce_word_limit(self._extract_argument(raw))
        msg = self.send_message(text, ping_num=opponent_msg.round + 1)
        msg.concept = concept
        return msg
