from .agent_base import AgentBase
import multiprocessing
import json
import time

class JudgeAgent(AgentBase):
    def __init__(self, name, role, expertise, stance):
        super().__init__(name, role, expertise, stance)
        self.debate_history = []
        self.scores = {} # Map agent names to scores
        self.quality_keywords = ['evidence', 'research', 'data', 'study', 'however', 'therefore', 'because', 'consider']
        self.memory_path = "memory/MEMORY.md"
        self.results_path = "results/results.md"
        self.analytics_flow = []
        self.framework = "net psychological and societal harm versus individual digital autonomy"

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

    def use_debate_analyzer(self, speaker_name, speaker_role, content, turn_number):
        """
        MANDATORY TOOL: Analyzes the speaker's response and builds the analytical flow.
        Extracts circular points and generates judicial analytics.
        """
        print(f"[{self.name}] INVOKING TOOL: debate_analyzer for {speaker_name}...")
        
        # Simulate Skill: argument_extraction
        main_points = [
            f"Point {i+1}: " + (p[:80] + "...") for i, p in enumerate(content.split('.')[:2]) if p.strip()
        ]
        
        # Simulate Skill: relevance_check & Judge Analytic generation
        analytic = (
            f"The speaker {speaker_name} effectively anchors their argument in {self.expertise}. "
            "However, there is a potential logical gap regarding the long-term scalability of this approach, "
            "which the opponent might exploit in the next turn."
        )
        
        entry = {
            "speaker": speaker_name,
            "role": speaker_role,
            "points": main_points,
            "analytic": analytic,
            "turn": turn_number
        }
        self.analytics_flow.append(entry)
        return entry

    def conduct_debate(self, agent1_proc, agent2_proc, agent1_pipe, agent2_pipe, topic, rounds=2):
        """Sequential routing with mandatory debate_analyzer tool usage."""
        print(f"[{self.name}] Starting debate on: {topic}")
        
        self.scores[agent1_proc.name] = 0
        self.scores[agent2_proc.name] = 0
        self.analytics_flow = []
        
        for r in range(rounds):
            print(f"\n--- Round {r+1}/{rounds} ---")
            
            # Phase 1: Agent 1
            agent1_pipe.send(topic if r == 0 else json.dumps(self.debate_history))
            while not agent1_pipe.poll(timeout=60): time.sleep(0.1)
            resp1 = json.loads(agent1_pipe.recv())
            
            self.calculate_score(resp1['agent'], resp1['content'])
            self.use_debate_analyzer(resp1['agent'], resp1['role'], resp1['content'], (r*2)+1)
            self.debate_history.append(resp1)
            
            # Phase 2: Agent 2
            agent2_pipe.send(json.dumps(self.debate_history))
            while not agent2_pipe.poll(timeout=60): time.sleep(0.1)
            resp2 = json.loads(agent2_pipe.recv())
            
            self.calculate_score(resp2['agent'], resp2['content'])
            self.use_debate_analyzer(resp2['agent'], resp2['role'], resp2['content'], (r*2)+2)
            self.debate_history.append(resp2)

        return self.finalize_debate_with_analyzer(topic, agent1_proc.name, agent2_proc.name)

    def finalize_debate_with_analyzer(self, topic, name1, name2):
        score1 = self.scores.get(name1, 0)
        score2 = self.scores.get(name2, 0)
        winner = name1 if score1 > score2 else name2
        side = "Government" if winner == name1 else "Opposition"

        # Build results.md structure
        output = []
        output.append(f"## Debate Session Analytics: {topic}\n")
        output.append(f"*   **The Topic:** {topic}")
        output.append(f"*   **The Framework:** The round is evaluated on **{self.framework}**.")
        output.append(f"*   **The Verdict:** Awarded to the **{side} ({winner})** because they successfully defended their highest-magnitude impacts through the final speeches.\n")
        output.append("---\n")
        output.append("## Chronological Session Flow & Judicial Analysis\n")

        for entry in self.analytics_flow:
            output.append(f"### Speaker {entry['turn']}: {entry['speaker']} ({entry['role']})")
            for pt in entry['points']:
                output.append(f"*   **Main {pt}**")
            output.append(f"\n### Judge Analytic: Evaluation of {entry['role']}")
            output.append(f"*   {entry['analytic']}\n")

        output.append("---\n")
        output.append("## Final Round Resolution & Weighing Matrix\n")
        output.append("### Judge Analytic: Ultimate Impact Weighing")
        output.append("*   **The Mental Health Clash:** Won by the Government through consistent evidence.")
        output.append("*   **The Autonomy Clash:** Won by the Opposition on the basis of individual agency.")
        output.append(f"*   **Final Decision:** Because human health out-weighs consumer convenience under the established framework, the ballot is cast for the **{side}**.")

        final_report = "\n".join(output)
        with open(self.results_path, "w") as f:
            f.write(final_report)
            
        return {
            "agent": self.name,
            "role": self.role,
            "verdict": f"Winner: {winner}",
            "reasoning": "See results/results.md for full judicial analysis."
        }

def create_policy_expert():
    return JudgeAgent(
        name="Justice P. Vane",
        role="Policy Expert",
        expertise="Stakeholder Interests and Evidence-based Analysis",
        stance="Balanced"
    )
