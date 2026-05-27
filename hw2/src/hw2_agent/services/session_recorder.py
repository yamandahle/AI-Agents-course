import json
from pathlib import Path
from ..config import load_config

def _get_log_paths() -> tuple[Path, Path]:
    """Helper to retrieve and prepare verified storage file paths from configuration."""
    config = load_config()
    log_dir = Path(config["fifo_logging"]["log_directory"])
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Dual-Track Storage Engine (JSONL Database + Human Markdown Transcript)
    return log_dir / "session_history.jsonl", log_dir / "debate_summary.md"

def initialize_or_restore_session() -> list[dict]:
    """
    Lane 1: Agent Initialization
    Restores past state messages if a crash occurs, or initializes a clean slate.
    """
    jsonl_path, md_path = _get_log_paths()
    history = []
    
    if jsonl_path.exists():
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line.strip()))
        return history

    # Setup pristine file layouts if booting for the first time
    config = load_config()
    md_path.write_text(f"# 🏆 Live Debate Transcript\n**Topic**: {config['debate_constraints']['topic']}\n\n---\n", encoding="utf-8")
    return history

def persist_session_message(speaker: str, message: str, search_queries: list = None) -> None:
    """
    Lane 2 & 3: Message Addition & Agent Invocation/Sync State
    Saves a message state change directly into the database layers.
    """
    jsonl_path, md_path = _get_log_paths()
    
    # 1. State on Disk: Append to programmatic JSONL Database entry row
    data_packet = {
        "speaker": speaker,
        "search_queries": search_queries or [],
        "message": message
    }
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data_packet) + "\n")
        
    # 2. Human Visually Readable: Append clean layout formatting to the MD log
    with open(md_path, "a", encoding="utf-8") as f:
        f.write(f"### 🎙️ Speaker: {speaker}\n")
        if search_queries:
            f.write(f"* **Live Search Citations**: `{search_queries}`\n")
        f.write(f" \n> {message}\n\n---\n")

def store_redacted_message(speaker: str, original_message: str, reason: str) -> None:
    """
    Lane 4: Message Redaction
    Stores context-engineered safety modifications or truncated tokens.
    """
    jsonl_path, _ = _get_log_paths()
    redaction_packet = {
        "speaker": speaker,
        "status": "REDACTED",
        "reason": reason,
        "censored_content_stub": original_message[:100] + "... [Truncated by System Manager]"
    }
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(redaction_packet) + "\n")
