from src.my_package.core.judge_agent import create_policy_expert
from src.my_package.core.debater_agent import create_ethics_researcher, create_tech_entrepreneur
from src.my_package.ui.terminal_menu import start_menu
import multiprocessing
import sys

FIXED_TOPIC = "Do social media algorithms do more harm to democratic discourse than good?"

def run_system():
    while True:
        choice = start_menu()
        
        if choice == "1":
            print(f"\nInitializing Debate: {FIXED_TOPIC}\n")
            
            # Create agents
            judge = create_policy_expert()
            ethicist = create_ethics_researcher()
            entrepreneur = create_tech_entrepreneur()
            
            # Setup IPC
            parent_conn1, child_conn1 = multiprocessing.Pipe()
            parent_conn2, child_conn2 = multiprocessing.Pipe()
            
            # Start Debater Processes
            p1 = multiprocessing.Process(target=ethicist.run, args=(child_conn1,), name=ethicist.name)
            p2 = multiprocessing.Process(target=entrepreneur.run, args=(child_conn2,), name=entrepreneur.name)
            
            p1.start()
            p2.start()
            
            try:
                # Judge orchestrates (runs in main process for UI feedback)
                verdict = judge.conduct_debate(
                    p1, parent_conn1, 
                    p2, parent_conn2, 
                    topic=FIXED_TOPIC
                )
                
                print("\n=== FINAL JUDGMENT ===")
                print(f"Judge: {verdict['agent']}")
                print(f"Role: {verdict['role']}")
                print(f"Verdict: {verdict['verdict']}")
                print(f"Reasoning: {verdict['reasoning']}")
                print("======================\n")
                
            finally:
                # Cleanup
                parent_conn1.send("STOP")
                parent_conn2.send("STOP")
                p1.join(timeout=5)
                p2.join(timeout=5)
                if p1.is_alive(): p1.terminate()
                if p2.is_alive(): p2.terminate()
                
        elif choice == "3":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    run_system()
