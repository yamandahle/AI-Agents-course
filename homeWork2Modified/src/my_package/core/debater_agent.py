from .agent_base import AgentBase
import time
import json
import os

class DebaterAgent(AgentBase):
    def run(self, pipe):
        """Sequential loop: receive from parent, process, send to parent."""
        # System instructions enforcing persona and protocol
        system_instructions = (
            f"PERSONA: {self.name}, {self.role}. EXPERTISE: {self.expertise}. STANCE: {self.stance}.\n"
            "MANDATE: Stay strictly in character. Maintain your unique persona and stance.\n"
            "PROTOCOL: Address counter-arguments in the conversation history directly. Do not ignore them.\n"
            "RULE 1: NEVER quote your opponent verbatim. Summarize their points or reference their key terminology.\n"
            "RULE 2: NO REPETITION. Do not reuse sentences or examples from your previous turns.\n"
            "RULE 3: ADVANCE THE DEBATE. Reread the session history and judge summaries to provide a new argument every turn.\n"
            "TONE: Polite, respectful, and politically correct at all times.\n"
            "FORMAT: Concise. 1 argument (3 sentences) to 3 arguments (with 2 examples).\n"
            "[INSTRUCTION]: Formulate your next response utilizing your associated skill."
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
        # Reread history from Judge Summary if possible
        memory_content = ""
        if os.path.exists("memory/MEMORY.md"):
            with open("memory/MEMORY.md", "r") as f:
                memory_content = f.read()

        # Determine if we are responding to someone
        opponent_summary = ""
        turn_count = 0
        if history and isinstance(history, list):
            turn_count = len([msg for msg in history if msg.get('agent') == self.name])
            last_msg = history[-1]
            last_content = last_msg.get('content', '').lower()
            
            # Simple keyword extraction to avoid verbatim quoting
            keywords = []
            if "risk" in last_content or "amplification" in last_content: keywords.append("algorithmic risks")
            if "innovation" in last_content or "market" in last_content: keywords.append("innovation-led growth")
            if "regulation" in last_content or "guardrails" in last_content: keywords.append("regulatory frameworks")
            
            if keywords:
                opponent_summary = f"Addressing your focus on {', '.join(keywords)}: "
            else:
                opponent_summary = "Regarding your previous points: "

        # Dynamic arguments and examples to avoid repetition
        cautious_args = [
            ("The systemic risks inherent in algorithmic amplification necessitate immediate implementation of robust regulatory frameworks.", "The rise of echo chambers in 2021", "Documented algorithmic bias"),
            ("Data privacy concerns are paramount as predictive models often ingest sensitive user data without explicit informed consent.", "Data harvesting scandals", "Unauthorized profiling"),
            ("The psychological impact of engagement-optimized feeds contributes significantly to the erosion of mental well-being in youth.", "Increased anxiety rates", "Addictive UI patterns"),
            ("Algorithmic opacity prevents independent audits, making it impossible to verify if platforms are adhering to safety standards.", "Black-box decision making", "Lack of transparency reports"),
            ("The concentration of power in a few tech giants undermines the decentralized nature of democratic discourse.", "Market monopolies", "Censorship concerns")
        ]

        optimistic_args = [
            ("Market-driven innovation is the primary engine for improving information accessibility and democratic engagement.", "Open platforms enabling grassroots movements", "Real-time translation tools"),
            ("Algorithms can effectively surface high-quality educational content, democratizing access to specialized knowledge.", "AI-driven tutoring", "Personalized learning paths"),
            ("AI-enhanced moderation tools are essential for scaling safety measures and protecting users from harmful content at speed.", "Automated hate speech detection", "Real-time moderation"),
            ("The economic benefits of personalized discovery allow small businesses to reach global audiences more efficiently than ever.", "Small business growth", "Targeted entrepreneurship"),
            ("Digital autonomy is enhanced when users are provided with sophisticated tools to filter and curate their own information environment.", "User-defined filters", "Customizable algorithms")
        ]

        # Select argument based on turn count to ensure variety
        idx = turn_count % len(cautious_args)
        
        if self.stance == "Cautious":
            arg, ex1, ex2 = cautious_args[idx]
            return (
                f"{opponent_summary}{arg} Data suggests that without safety-first guardrails, democratic discourse is vulnerable. "
                f"Example 1: {ex1}. Example 2: {ex2}."
            )
        elif self.stance == "Optimistic":
            arg, ex1, ex2 = optimistic_args[idx]
            return (
                f"{opponent_summary}{arg} Limiting innovation through regulation would only stifle tools that empower voices globally. "
                f"Example 1: {ex1}. Example 2: {ex2}."
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
