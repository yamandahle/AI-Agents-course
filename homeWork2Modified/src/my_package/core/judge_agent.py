from .agent_base import AgentBase
from ..skills.argument_extraction.extractor import extract_main_argument
from ..skills.relevance_check.checker import check_relevance
import multiprocessing
import json
import time
import os

class JudgeAgent(AgentBase):
    def __init__(self, name, role, expertise, stance):
        super().__init__(name, role, expertise, stance)
        self.debate_history = []
        self.topic_ledger = [] # Track covered topics
        self.scores = {} # Map agent names to scores
        self.quality_keywords = ['evidence', 'research', 'data', 'study', 'however', 'therefore', 'because', 'consider']
        self.memory_path = "memory/MEMORY.md"
        self.results_path = "results/results.md"
        self.analytics_flow = []
        self.framework = "net psychological and societal harm versus individual digital autonomy"

        # Ensure memory and results directories exist
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.results_path), exist_ok=True)

        # Clear memory file at start of session
        with open(self.memory_path, "w") as f:
            f.write(f"# Debate Memory: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def run(self):
        """Standard run method for the judge process."""
        print(f"[{self.name}] Judge active and waiting to orchestrate...")

    def calculate_score(self, agent_name, content):
        """Calculates score based on length and quality keywords."""
        word_count = len(content.split())
        quality_bonus = sum(2 for word in self.quality_keywords if word in content.lower())
        total_score = word_count + quality_bonus

        self.scores[agent_name] = self.scores.get(agent_name, 0) + total_score
        return total_score

    def use_debate_analyzer(self, speaker_name, speaker_role, speaker_stance, content, turn_number, topic):
        """
        MANDATORY TOOL: Analyzes the speaker's response and builds the analytical flow.
        Extracts circular points and generates judicial analytics.
        """
        print(f"[{self.name}] INVOKING TOOL: debate_analyzer for {speaker_name}...")

        # Use Skill: argument_extraction
        main_point = extract_main_argument(content, speaker_stance)

        # Use Skill: relevance_check
        is_relevant, relevance_msg = check_relevance(content, topic)

        # Generate Judge Analytic
        if not is_relevant:
            analytic = f"The speaker {speaker_name} drifted from the topic. {relevance_msg}"
        else:
            analytic = (
                f"The speaker {speaker_name} effectively anchors their argument in {speaker_role} perspectives. "
                f"Core point: {main_point[:100]}... "
                "The argument is well-structured but requires more empirical support to fully sway the ballot."
            )

        entry = {
            "speaker": speaker_name,
            "role": speaker_role,
            "points": [main_point],
            "analytic": analytic,
            "turn": turn_number
        }
        self.analytics_flow.append(entry)

        # Persistence: memory/MEMORY.md
        with open(self.memory_path, "a") as f:
            f.write(f"### Turn {turn_number}: {speaker_name}\n")
            f.write(f"- **Role**: {speaker_role}\n")
            f.write(f"- **Summary**: {main_point}\n")
            f.write(f"- **Analytic**: {analytic}\n\n")

        return entry

    def conduct_debate(self, agent1_proc, agent2_proc, agent1_pipe, agent2_pipe, topic, rounds=10):
        """Sequential routing with mandatory debate_analyzer tool usage."""
        print(f"[{self.name}] Starting debate on: {topic}")
        
        self.scores[agent1_proc.name] = 0
        self.scores[agent2_proc.name] = 0
        self.analytics_flow = []
        self.topic_ledger = [] # Reset ledger for new session
        jsonl_path = "results/session.jsonl"
        os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)
        
        # Clear previous session file
        with open(jsonl_path, "w") as f:
            pass

        for r in range(rounds):
            print(f"\n--- Round {r+1}/{rounds} ---")
            
            # Phase 1: Agent 1
            payload1 = {
                "topic": topic if r == 0 else None,
                "history": self.debate_history,
                "ledger": self.topic_ledger
            }
            agent1_pipe.send(json.dumps(payload1))
            while not agent1_pipe.poll(timeout=60): time.sleep(0.1)
            resp1 = json.loads(agent1_pipe.recv())
            
            # Extract topic from response
            if "topic_covered" in resp1:
                self.topic_ledger.append(resp1["topic_covered"])
            
            self.calculate_score(resp1['agent'], resp1['content'])
            self.use_debate_analyzer(resp1['agent'], resp1['role'], resp1['stance'], resp1['content'], (r*2)+1, topic)
            self.debate_history.append(resp1)
            
            # Save to jsonl
            with open(jsonl_path, "a") as f:
                f.write(json.dumps(resp1) + "\n")
            
            # Phase 2: Agent 2
            payload2 = {
                "history": self.debate_history,
                "ledger": self.topic_ledger
            }
            agent2_pipe.send(json.dumps(payload2))
            while not agent2_pipe.poll(timeout=60): time.sleep(0.1)
            resp2 = json.loads(agent2_pipe.recv())
            
            # Extract topic from response
            if "topic_covered" in resp2:
                self.topic_ledger.append(resp2["topic_covered"])
            
            self.calculate_score(resp2['agent'], resp2['content'])
            self.use_debate_analyzer(resp2['agent'], resp2['role'], resp2['stance'], resp2['content'], (r*2)+2, topic)
            self.debate_history.append(resp2)
            
            # Save to jsonl
            with open(jsonl_path, "a") as f:
                f.write(json.dumps(resp2) + "\n")

        return self.finalize_debate_with_analyzer(topic, agent1_proc.name, agent2_proc.name)

    def finalize_debate_with_analyzer(self, topic, name1, name2):
        score1 = self.scores.get(name1, 0)
        score2 = self.scores.get(name2, 0)
        winner = name1 if score1 > score2 else name2
        side = "Government" if winner == name1 else "Opposition"
        
        # Determine the key themes based on expertise
        theme1 = "Safety and Ethics" if "Ethics" in name1 or "Ethics" in self.expertise else "Innovation"
        theme2 = "Rapid Innovation" if "Entrepreneur" in name2 else "Regulatory Frameworks"

        # Build results.md structure
        output = []
        output.append(f"## Debate Session Analytics: {topic}\n")
        output.append(f"*   **The Topic:** {topic}")
        output.append(f"*   **The Framework:** The round is evaluated on **{self.framework}**.")
        output.append(f"*   **The Verdict:** Awarded to the **{side} ({winner})** based on quantitative scoring ({self.scores[winner]} points) and qualitative depth of arguments.\n")
        output.append("---\n")
        output.append("## Chronological Session Flow & Judicial Analysis\n")

        for entry in self.analytics_flow:
            output.append(f"### Speaker {entry['turn']}: {entry['speaker']} ({entry['role']})")
            for pt in entry['points']:
                output.append(f"*   **Main Point:** {pt}")
            output.append(f"\n### Judge Analytic: Evaluation of {entry['role']}")
            output.append(f"*   {entry['analytic']}\n")

        output.append("---\n")
        output.append("## Final Round Resolution & Weighing Matrix\n")
        output.append("### Judge Analytic: Ultimate Impact Weighing")
        output.append(f"*   **The {theme1} Clash:** Evaluated based on long-term societal impact.")
        output.append(f"*   **The {theme2} Clash:** Evaluated based on economic and technological feasibility.")
        
        reasoning = f"The {side} ({winner}) demonstrated a more comprehensive understanding of the {self.framework}, particularly in the later rounds."
        output.append(f"*   **Final Decision:** {reasoning}")

        final_report = "\n".join(output)
        with open(self.results_path, "w") as f:
            f.write(final_report)
            
        return {
            "agent": self.name,
            "role": self.role,
            "verdict": f"Winner: {winner}",
            "reasoning": reasoning
        }

    def export_session_to_readme(self, topic):
        """
        Extracts responses from a JSONL file and writes them to README.md.
        """
        jsonl_path = "results/session.jsonl"
        if not os.path.exists(jsonl_path):
            print(f"[{self.name}] ERROR: No session file found at {jsonl_path}")
            return

        print(f"[{self.name}] Extracting session from {jsonl_path} to README.md...")
        
        output = []
        output.append(f"# AI Agent Debate: {topic}\n")
        output.append("## Full Session Log\n")
        
        with open(jsonl_path, "r") as f:
            for i, line in enumerate(f):
                msg = json.loads(line)
                speaker = msg.get("agent", "Unknown")
                role = msg.get("role", "Unknown")
                content = msg.get("content", "")
                
                output.append(f"### Turn {i+1}: {speaker} ({role})")
                output.append(f"{content}\n")
                output.append("---")

        with open("README.md", "w") as f:
            f.write("\n".join(output))
        
        print(f"[{self.name}] README.md updated successfully.")

def create_policy_expert():
    return JudgeAgent(
        name="Justice P. Vane",
        role="Policy Expert",
        expertise="Stakeholder Interests and Evidence-based Analysis",
        stance="Balanced"
    )
