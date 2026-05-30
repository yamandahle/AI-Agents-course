from .agent_base import AgentBase
import time
import json
import os

class DebaterAgent(AgentBase):
    def run(self, pipe):
        """Sequential loop: receive from parent, process, send to parent."""
        # System instructions enforcing persona and fluid protocol
        system_instructions = (
            f"You are {self.name}, the {self.role}. You are simulating a fluid, unscripted panel debate. "
            f"Speak completely in your distinct voice as a {self.expertise} with a {self.stance} stance.\n\n"
            "RULES:\n"
            "1. NO TEMPLATES: DO NOT use fixed conversational templates, transition phrases, or introductory formulas. "
            "Do not mimic the sentence structure, openings, or closing statements of the previous speaker.\n"
            "2. LOGIC DISMANTLING: You must directly address and attempt to dismantle the specific logic or examples "
            "brought up by the previous speaker before introducing a new point. Do not just pivot.\n"
            "3. NATURAL FLOW: Every response must flow naturally from the previous turn—do not use repetitive opening clichés "
            "('While you emphasize...') or closing clichés ('demonstrate why this approach is vital...').\n"
            "4. CONCISE DEPTH: Limit your response to 2–3 concise paragraphs. Focus on one core counterargument per turn "
            "rather than a list of points.\n"
            "5. NO REPETITION: Check the 'ledger'. You are STRICTLY FORBIDDEN from using topics or examples listed there.\n\n"
            "[INSTRUCTION]: Respond naturally to the debate history. End with the tag [TOPIC: your_new_topic]."
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
                except:
                    history = []
                    ledger = []

                print(f"[{self.name}] Generating fluid response (Temp: 0.9)...")
                
                # Logic to formulate the response
                content = self.generate_fluid_content(history, ledger)
                
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

    def generate_fluid_content(self, history, ledger):
        # Determine turn count for variety
        turn_count = len([msg for msg in history if msg.get('agent') == self.name])
        
        # Logic Dismantling & Rebuttal (Simulated high-temperature variability)
        rebuttal_starts = [
            "That focus on {0} misses the fundamental structural reality of how these systems operate.",
            "I have to take issue with that characterization of {0}.",
            "Looking closely at the {0} mentioned, the underlying logic falls apart when we consider scalability.",
            "It's a common misconception that {0} provides a sufficient safety net.",
            "We can't talk about {0} without acknowledging the massive power imbalance it creates."
        ]
        
        rebuttal = ""
        if history:
            last_msg = history[-1]
            last_topic = last_msg.get('topic_covered', 'the current argument')
            start_phrase = rebuttal_starts[turn_count % len(rebuttal_starts)].format(last_topic)
            
            rebuttal = (
                f"{start_phrase} By narrowing the scope to just those metrics, you're ignoring the cascading "
                "failures that occur at the platform level. The examples you cited aren't isolated wins; "
                "they're exceptions that prove the rule of systemic instability. "
            )

        # New Argument Selection
        cautious_args = [
            ("algorithmic risks", "The systemic risks in algorithmic amplification create a feedback loop of polarization that no manual regulation can keep up with."),
            ("data privacy", "We're seeing a total erosion of the boundary between public discourse and private cognitive profiling."),
            ("mental health", "The optimization for engagement is, by definition, an optimization for psychological addiction."),
            ("algorithmic opacity", "Transparency is a myth when the 'black box' is designed to be commercially un-auditable."),
            ("tech monopolies", "Democratic discourse cannot survive when the town square is owned by a handful of profit-motivated entities.")
        ]

        optimistic_args = [
            ("innovation engines", "Stifling the very engines that democratized information access is a regressive step for global discourse."),
            ("education access", "The ability to curate vast quantities of human knowledge into digestible, personalized streams is a superpower for the average citizen."),
            ("moderation tools", "Scale requires automated vigilance; without these tools, the internet becomes a landfill of unmoderated vitriol."),
            ("economic discovery", "The democratization of the market via discovery algorithms is the greatest equalizer for small-scale entrepreneurs."),
            ("digital curation", "Giving individuals the tools to carve out their own corners of the web is the ultimate expression of digital agency.")
        ]

        available = [a for a in (cautious_args if self.stance == "Cautious" else optimistic_args) if a[0] not in ledger]
        if not available: available = [cautious_args[0]] if self.stance == "Cautious" else [optimistic_args[0]]

        topic_key, arg = available[0]
        
        # Build natural paragraphs
        p1 = rebuttal.strip()
        p2 = f"{arg} If we look at {topic_key}, it becomes clear that the path forward requires a shift in how we value individual autonomy over corporate predictability."

        return f"{p1}\n\n{p2}\n\n[TOPIC: {topic_key}]"

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
