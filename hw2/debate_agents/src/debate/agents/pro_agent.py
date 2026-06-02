"""ProAgent — argues FOR remote work; loads its skill from src/debate/skills/pro_skill.md."""

from __future__ import annotations

from pathlib import Path

from debate.agents.base_agent import BaseAgent, DebateMessage


class ProAgent(BaseAgent):
    """Debate agent that always argues remote work is superior to office work.

    Skill file: src/debate/skills/pro_skill.md
    Style: conversational, data-driven, responds to opponent first.
    """

    def get_skill_prompt(self) -> str:
        """Load and return the PRO skill definition from the skills directory."""
        skill_path = Path(self._skills_path) / "pro_skill.md"
        return skill_path.read_text(encoding="utf-8")

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        """Build opening statement on round 0, then data-driven rebuttals for all later rounds."""
        if opponent_msg.round == 0:
            prompt = self._build_opening_prompt(opponent_msg.content)
        else:
            query = f"remote work productivity benefits statistics evidence {opponent_msg.content[:80]}"
            results = self.search_web(query)
            evidence = self._format_evidence(results)
            prompt = self._build_prompt(opponent_msg, evidence)
        text = self._enforce_word_limit(self._extract_argument(self._call_llm(prompt)))
        return self.send_message(text, ping_num=opponent_msg.round + 1)
