from .agent_base import AgentBase
import time
import json

class DebaterAgent(AgentBase):
    def run(self, pipe):
        """Sequential loop: receive from parent, process, send to parent."""
        # System instructions enforcing persona and protocol
        system_instructions = (
            f"PERSONA: {self.name}, {self.role}. EXPERTISE: {self.expertise}. STANCE: {self.stance}.\n"
            "MANDATE: Stay strictly in character. Maintain your unique persona and stance.\n"
            "PROTOCOL: Address counter-arguments in the conversation history directly. Do not ignore them.\n"
            "TONE: Polite, respectful, and politically correct at all times.\n"
            "FORMAT: Concise. 1 argument (3 sentences) to 3 arguments (with 2 examples).\n"
            "[INSTRUCTION]: Formulate your next response. Do not use conversational filler (like 'Good point'). "
            "Dive directly into your argument utilizing your associated skill."
        )

        while True:
            if pipe.poll():
                raw_input = pipe.recv()
                if raw_input == "STOP":
                    break
                
                try:
                    # Input could be the topic (string) or history (JSON string)
                    history = json.loads(raw_input) if raw_input.startswith("[") or raw_input.startswith("{") else []
                except:
                    history = []

                print(f"[{self.name}] Generating response based on stance: {self.stance}...")
                
                # Logic to formulate the response
                content = self.generate_stance_content(history)
                
                response = {
                    "agent": self.name,
                    "role": self.role,
                    "stance": self.stance,
                    "content": content
                }
                pipe.send(json.dumps(response))
            time.sleep(0.1)

    def generate_stance_content(self, history):
        # Determine if we are responding to someone
        opponent_point = ""
        if history and isinstance(history, list):
            last_msg = history[-1]
            opponent_point = f"Regarding the claim that {last_msg.get('content', '')}: "

        if self.stance == "Cautious":
            return (
                f"{opponent_point}The systemic risks inherent in algorithmic amplification necessitate "
                "immediate implementation of robust regulatory frameworks. Data suggests that without "
                "safety-first guardrails, democratic discourse is vulnerable to polarization. "
                "Example 1: The rise of echo chambers in 2021. Example 2: Documented algorithmic bias."
            )
        elif self.stance == "Optimistic":
            return (
                f"{opponent_point}Market-driven innovation is the primary engine for improving "
                "information accessibility and democratic engagement. Limiting innovation through "
                "regulation would only stifle the tools that empower individual voices globally. "
                "Example 1: Open platforms enabling grassroots movements. Example 2: Real-time translation tools."
            )
        return "Maintaining a balanced perspective on the issue."

def create_ethics_researcher():
    return DebaterAgent(
        name="Dr. Aris Thorne",
        role="Ethics Researcher",
        expertise="Safety and Risk Mitigation",
        stance="Cautious"
    )

def create_tech_entrepreneur():
    return DebaterAgent(
        name="Alex Vanguard",
        role="Tech Entrepreneur",
        expertise="Rapid Innovation",
        stance="Optimistic"
    )
