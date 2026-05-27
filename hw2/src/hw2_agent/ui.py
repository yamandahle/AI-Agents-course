import questionary
import json
from pathlib import Path
from .orchestrator import DebateOrchestrator
from .services.analytics import display_full_analytics_report

CONFIG_PATH = Path("config/setup.json")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def main_menu():
    while True:
        config = load_config()
        choice = questionary.select(
            "Welcome to the AI Debate Platform",
            choices=[
                "Start Debate",
                "Set Topic",
                "Adjust Turn Limits",
                "View Analytics",
                "Exit"
            ]
        ).ask()

        if choice == "Start Debate":
            orchestrator = DebateOrchestrator()
            orchestrator.start_debate()
            
            print("\n" + "="*50)
            print("DEBATE SUMMARY (Last 20 lines):")
            print("="*50)
            summary_path = Path("logs/debate_summary.md")
            if summary_path.exists():
                with open(summary_path, "r") as f:
                    lines = f.readlines()
                    last_lines = lines[-20:]
                    for line in last_lines:
                        print(line.rstrip())
            print("="*50)
            input("\nPress Enter to return to menu...")
        
        elif choice == "Set Topic":
            new_topic = questionary.text("Enter new debate topic:", default=config["debate_constraints"]["topic"]).ask()
            if new_topic:
                config["debate_constraints"]["topic"] = new_topic
                save_config(config)
        
        elif choice == "Adjust Turn Limits":
            new_limit = questionary.text("Enter turn limit (per side):", default=str(config["debate_constraints"].get("max_turns", 10))).ask()
            if new_limit.isdigit():
                if "debate_constraints" not in config: config["debate_constraints"] = {}
                config["debate_constraints"]["max_turns"] = int(new_limit)
                save_config(config)

        elif choice == "View Analytics":
            display_full_analytics_report()
            input("\nPress Enter to return to menu...")

        elif choice == "Exit":
            break

if __name__ == "__main__":
    main_menu()
