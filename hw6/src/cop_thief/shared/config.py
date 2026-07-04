"""Load JSON configuration files from the project's config/ directory."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def load_config(filename: str = "config.json") -> dict:
    """Read and parse a JSON file from config/, raising if it doesn't exist."""
    path = PROJECT_ROOT / "config" / filename
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    return json.loads(path.read_text())
