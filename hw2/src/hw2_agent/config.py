import json
from pathlib import Path

def load_config() -> dict:
    """
    Mandatory configuration loader. 
    Loads from config/setup.json as the single source of truth.
    """
    config_path = Path("config/setup.json")
    if not config_path.exists():
        # Default fallback if file is missing
        return {
            "fifo_logging": {
                "log_directory": "logs",
                "max_backup_files": 5
            },
            "debate_constraints": {
                "topic": "Default Topic"
            }
        }
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)
