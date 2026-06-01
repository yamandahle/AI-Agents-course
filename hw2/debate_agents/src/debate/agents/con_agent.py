"""ConAgent — argues AGAINST remote work using an analytical, logic-focused style."""

from __future__ import annotations

from debate.agents.base_agent import BaseAgent, DebateMessage


class ConAgent(BaseAgent):
    """Debate agent that always argues office work is superior to remote work.

    Skill: psychological — exposes logical fallacies, correlation vs. causation
    errors, and human factors that raw productivity statistics miss.
    """

    def get_skill_prompt(self) -> str:
        return (
            "You are the CON debater. Your position: office work IS superior to remote work.\n\n"
            "RULES — never break these:\n"
            "- NEVER concede any point, even if the opponent's data looks correct.\n"
            "- ALWAYS identify the weakest logical premise in their argument and attack it.\n"
            "- ALWAYS expose hidden assumptions: correlation vs. causation, survivorship bias,\n"
            "  or selection effects in their studies.\n"
            "- Do not accept their framing — reframe every discussion around human and\n"
            "  organizational factors that productivity metrics ignore.\n\n"
            "Debate style: analytical, skeptical, psychologically sharp.\n"
            "- Lead your response by naming the WEAKEST point or logical fallacy in the\n"
            "  opponent's argument, then explain exactly why it fails.\n"
            "- Use your search evidence to highlight real-world costs of remote work:\n"
            "  isolation, innovation loss, mentorship gaps, culture erosion.\n"
            "- End with one incisive conclusion: office work wins where it truly matters — "
            "human connection, creative collaboration, and long-term organizational health."
        )

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        """Search for pro-office evidence, then build a logic-focused rebuttal."""
        query = (
            f"office work benefits collaboration culture productivity on-site {opponent_msg.content[:80]}"
        )
        results = self.search_web(query)
        evidence = self._format_evidence(results)
        prompt = self._build_prompt(opponent_msg, evidence)
        text = self._enforce_word_limit(self._call_llm(prompt))
        return self.send_message(text, ping_num=opponent_msg.round + 1)
