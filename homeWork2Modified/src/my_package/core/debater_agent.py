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
            "REBUTTAL FIRST POLICY: You MUST spend the first 50% of your response directly criticizing the specific point "
            "made by your opponent in their immediate previous turn. Do not introduce your new point until this is complete.\n"
            "MEMORY LEDGER: Check the 'ledger' in your input. You are STRICTLY FORBIDDEN from bringing up topics or "
            "using examples listed in the ledger. You must advance the debate with a new argument or angle.\n"
            "NO VERBATIM: Summarize the opponent's points or reference their key terminology. Never quote verbatim.\n"
            "TONE: Polite, respectful, and professional.\n"
            "FORMAT: Conversational and natural. Avoid rigid prefixes. Ensure your response is substantial.\n"
            "[INSTRUCTION]: Formulate your response. Include the tag [TOPIC: your_new_topic] at the end of your response."
        )

        while True:
            if pipe.poll():
                raw_input = pipe.recv()
                if raw_input == "STOP":
                    break
                
                try:
                    data = json.loads(raw_input)
                    history = data.get("history", [])
                    ledger = data.get("ledger", [])
                    # topic = data.get("topic") # Initial topic if needed
                except:
                    history = []
                    ledger = []

                print(f"[{self.name}] Generating response based on stance: {self.stance}...")
                
                # Logic to formulate the response
                content = self.generate_stance_content(history, ledger)
                
                # Extract the topic tag
                topic_covered = "General"
                if "[TOPIC:" in content:
                    parts = content.split("[TOPIC:")
                    content = parts[0].strip()
                    topic_covered = parts[1].split("]")[0].strip()

                response = {
                    "agent": self.name,
                    "role": self.role,
                    "stance": self.stance,
                    "content": content,
                    "topic_covered": topic_covered
                }
                pipe.send(json.dumps(response))
            time.sleep(0.1)

    def generate_stance_content(self, history, ledger):
        # Determine turn count
        turn_count = len([msg for msg in history if msg.get('agent') == self.name])
        
        # 1. Rebuttal (50%)
        rebuttal = ""
        if history:
            last_msg = history[-1]
            last_content = last_msg.get('content', '')
            # Simulate rebuttal by referencing their core claim and offering a counter-perspective
            rebuttal = (
                f"While you emphasize the importance of {last_msg.get('topic_covered', 'the current discourse')}, "
                "this perspective fails to account for the systemic externalities that arise when short-term gains "
                "are prioritized over long-term stability. Your argument assumes a degree of market efficiency "
                "that simply doesn't exist in the current technological landscape. "
            )

        # 2. New Argument (50%) - Check ledger
        cautious_args = [
            ("algorithmic risks", "The systemic risks inherent in algorithmic amplification necessitate immediate implementation of robust regulatory frameworks.", "The rise of echo chambers in 2021", "Documented algorithmic bias"),
            ("data privacy", "Data privacy concerns are paramount as predictive models often ingest sensitive user data without explicit informed consent.", "Data harvesting scandals", "Unauthorized profiling"),
            ("mental health", "The psychological impact of engagement-optimized feeds contributes significantly to the erosion of mental well-being in youth.", "Increased anxiety rates", "Addictive UI patterns"),
            ("algorithmic opacity", "Algorithmic opacity prevents independent audits, making it impossible to verify if platforms are adhering to safety standards.", "Black-box decision making", "Lack of transparency reports"),
            ("tech monopolies", "The concentration of power in a few tech giants undermines the decentralized nature of democratic discourse.", "Market monopolies", "Censorship concerns")
        ]

        optimistic_args = [
            ("innovation engines", "Market-driven innovation is the primary engine for improving information accessibility and democratic engagement.", "Open platforms enabling grassroots movements", "Real-time translation tools"),
            ("education access", "Algorithms can effectively surface high-quality educational content, democratizing access to specialized knowledge.", "AI-driven tutoring", "Personalized learning paths"),
            ("moderation tools", "AI-enhanced moderation tools are essential for scaling safety measures and protecting users from harmful content at speed.", "Automated hate speech detection", "Real-time moderation"),
            ("economic discovery", "The economic benefits of personalized discovery allow small businesses to reach global audiences more efficiently than ever.", "Small business growth", "Targeted entrepreneurship"),
            ("digital curation", "Digital autonomy is enhanced when users are provided with sophisticated tools to filter and curate their own information environment.", "User-defined filters", "Customizable algorithms")
        ]

        available_args = []
        if self.stance == "Cautious":
            available_args = [a for a in cautious_args if a[0] not in ledger]
        else:
            available_args = [a for a in optimistic_args if a[0] not in ledger]

        if not available_args:
            available_args = [cautious_args[0]] if self.stance == "Cautious" else [optimistic_args[0]]

        topic_key, arg, ex1, ex2 = available_args[0]
        
        new_point = (
            f"Moving forward, we must consider that {arg} For instance, {ex1} and {ex2} demonstrate "
            "why this approach is vital for the future of democratic discourse."
        )

        return f"{rebuttal}{new_point} [TOPIC: {topic_key}]"

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
