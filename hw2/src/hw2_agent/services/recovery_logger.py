from pathlib import Path
from ..config import load_config

def update_recovery_checkpoint(speaker: str, speech_type: str, message: str) -> None:
    """
    Maintains a brief, agent-optimized markdown checkpoint for session recovery.
    Captures the essence of each turn to allow a replacement process to quickly 
    re-orient itself.
    """
    config = load_config()
    log_dir = Path(config["fifo_logging"]["log_directory"])
    log_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = log_dir / "agent_checkpoint.md"
    
    # Ensure file exists with header
    if not checkpoint_path.exists():
        checkpoint_path.write_text("# 🔄 Agent Recovery Checkpoint\n\nThis file provides a concise state-of-play for agent re-initialization.\n\n---\n", encoding="utf-8")

    # Generate a brief summary (first 300 characters of the response)
    # This acts as a 'memory anchor' for the agent.
    brief_summary = message[:300].replace("\n", " ").strip()
    if len(message) > 300:
        brief_summary += "..."

    with open(checkpoint_path, "a", encoding="utf-8") as f:
        f.write(f"### Turn Summary: {speaker}\n")
        f.write(f"- **Role/Stage**: {speech_type}\n")
        f.write(f"- **Key Argument**: {brief_summary}\n\n---\n")

def load_recovery_checkpoint() -> str:
    """
    Reads the recovery checkpoint file. Replacement agents can use this 
    to understand the debate's progression without parsing the full history.
    """
    config = load_config()
    log_dir = Path(config["fifo_logging"]["log_directory"])
    checkpoint_path = log_dir / "agent_checkpoint.md"
    
    if checkpoint_path.exists():
        return checkpoint_path.read_text(encoding="utf-8")
    return "No recovery checkpoint found. Initializing fresh session."
