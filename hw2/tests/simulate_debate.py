import os
import shutil
from pathlib import Path
from src.hw2_agent.orchestrator import DebateOrchestrator

def simulate():
    # 1. Enable Mocking
    os.environ["MOCK_LLM"] = "true"
    
    # 2. Clean up old logs to start a fresh session
    log_dir = Path("logs")
    jsonl_path = log_dir / "session_history.jsonl"
    md_path = log_dir / "debate_summary.md"
    
    if jsonl_path.exists():
        os.remove(jsonl_path)
    if md_path.exists():
        os.remove(md_path)
        
    print("Starting debate simulation (MOCKED)...")
    
    # 3. Initialize and start the debate
    orchestrator = DebateOrchestrator()
    orchestrator.start_debate()
    
    # 4. Save the report to firstArgument.md
    if md_path.exists():
        shutil.copy(md_path, "firstArgument.md")
        print(f"Simulation complete. Report saved to firstArgument.md")
    else:
        print("Error: Debate summary not found.")

if __name__ == "__main__":
    simulate()
