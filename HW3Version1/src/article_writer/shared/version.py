"""Version tracking — reads from config/setup.json, never hardcoded."""
from __future__ import annotations

import json
from pathlib import Path

from article_writer.shared.constants import CONFIG_DIR, VERSION_FALLBACK


def get_version() -> str:
    """Return the current project version string (e.g. '1.00')."""
    config_path = Path(CONFIG_DIR) / "setup.json"
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        return str(data.get("version", VERSION_FALLBACK))
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return VERSION_FALLBACK
