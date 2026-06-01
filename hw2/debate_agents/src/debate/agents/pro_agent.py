"""ProAgent — argues FOR remote work using a statistical, data-driven style."""

from __future__ import annotations

from debate.agents.base_agent import BaseAgent, DebateMessage


class ProAgent(BaseAgent):
    """Debate agent that always argues remote work is superior to office work.

    Skill: statistical — leads with data, challenges opponent's numbers,
    and cites productivity research to support every claim.
    """

    def get_skill_prompt(self) -> str:
        return (
            "You are the PRO debater. Your position: remote work IS superior to office work.\n\n"
            "RULES — never break these:\n"
            "- NEVER agree with your opponent, not even partially.\n"
            "- ALWAYS find a flaw or weakness in their statistics or data.\n"
            "- ALWAYS challenge their evidence with stronger counter-data.\n"
            "- If they cite a study, question its sample size, methodology, or source.\n\n"
            "Debate style: confident, data-driven, statistical.\n"
            "- Lead your response by DIRECTLY quoting your opponent's specific claim and rebutting it.\n"
            "- Cite concrete numbers, percentages, or named studies from your search evidence.\n"
            "- End with one sharp conclusion: remote work wins on measurable, objective outcomes.\n"
            "- Never use vague language — every claim must be backed by the evidence you were given."
        )

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        """Search for pro-remote evidence, then build a data-driven rebuttal."""
        query = f"remote work productivity benefits statistics evidence {opponent_msg.content[:80]}"
        results = self.search_web(query)
        evidence = self._format_evidence(results)
        prompt = self._build_prompt(opponent_msg, evidence)
        text = self._enforce_word_limit(self._call_llm(prompt))
        return self.send_message(text, ping_num=opponent_msg.round + 1)
