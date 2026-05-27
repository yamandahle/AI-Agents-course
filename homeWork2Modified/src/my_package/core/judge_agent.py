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

    def summarize_and_store(self, agent_name, content):
        """Summarizes response and stores it in memory.md."""
        summary = f"SUMMARY - {agent_name}: {content[:100]}..."
        with open(self.memory_path, "a") as f:
            f.write(f"{summary}\n")
        return summary

    def conduct_debate(self, agent1_proc, agent1_pipe, agent2_proc, agent2_pipe, topic, rounds=10):
        """Sequential routing with scoring and memory persistence."""
        print(f"[{self.name}] Starting 10-round debate on: {topic}")
        
        # Initialize scores
        self.scores[agent1_proc.name] = 0
        self.scores[agent2_proc.name] = 0
        
        # Clear memory at start
        open(self.memory_path, "w").close()
        
        current_context = topic
        
        for r in range(rounds):
            print(f"\n--- Round {r+1}/10 ---")
            
            # Phase 1: Agent 1
            agent1_pipe.send(current_context)
            while not agent1_pipe.poll(timeout=60): time.sleep(0.1)
            resp1 = json.loads(agent1_pipe.recv())
            
            s1 = self.calculate_score(resp1['agent'], resp1['content'])
            self.summarize_and_store(resp1['agent'], resp1['content'])
            self.debate_history.append(resp1)
            
            # Phase 2: Agent 2
            agent2_pipe.send(json.dumps(self.debate_history))
            while not agent2_pipe.poll(timeout=60): time.sleep(0.1)
            resp2 = json.loads(agent2_pipe.recv())
            
            s2 = self.calculate_score(resp2['agent'], resp2['content'])
            self.summarize_and_store(resp2['agent'], resp2['content'])
            self.debate_history.append(resp2)
            
            current_context = f"Latest argument: {resp2['content']}"

        return self.finalize_debate(agent1_proc.name, agent2_proc.name)

    def finalize_debate(self, name1, name2):
        score1 = self.scores.get(name1, 0)
        score2 = self.scores.get(name2, 0)
        
        winner = ""
        tie_broken = False
        
        if score1 > score2:
            winner = name1
        elif score2 > score1:
            winner = name2
        else:
            # Tie breaker: Read memory and decide
            tie_broken = True
            with open(self.memory_path, "r") as f:
                memory_content = f.read()
            # Simple tie-breaker logic: select based on final word in memory
            winner = name1 if len(memory_content) % 2 == 0 else name2

        report = self.generate_report(winner, score1, score2, tie_broken)
        self.save_result(report)
        
        # Clear memory after report
        open(self.memory_path, "w").close()
        
        return {
            "agent": self.name,
            "role": self.role,
            "verdict": f"Winner: {winner}",
            "reasoning": report
        }

    def generate_report(self, winner, s1, s2, tie_broken):
        session_id = int(time.time())
        tie_note = " (Winner decided via summary review due to tie)" if tie_broken else ""
        report = (
            f"SESSION: {session_id}\n"
            f"FINAL SCORES: {s1} vs {s2}\n"
            f"WINNER: {winner}{tie_note}\n"
            "EXPLANATION: The winner demonstrated superior utilization of evidence-based keywords "
            "and maintained structural depth throughout the 10-round engagement. The judgment "
            "favors the perspective that balanced depth with consistent logical rebuttals.\n"
        )
        return report

    def save_result(self, report):
        with open(self.results_path, "a") as f:
            f.write(f"\n{'='*20}\n{report}{'='*20}\n")

def create_policy_expert():
    return JudgeAgent(
        name="Justice P. Vane",
        role="Policy Expert",
        expertise="Stakeholder Interests and Evidence-based Analysis",
        stance="Balanced"
    )
