"""Returns a configured CrewAI LLM object based on LLM_PROVIDER env var."""
from __future__ import annotations

import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()


def get_crewai_llm() -> LLM:
    """Return a CrewAI-compatible LLM using the configured provider."""
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    if provider == "google":
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        return LLM(model=f"gemini/{model}", api_key=os.getenv("GEMINI_API_KEY"))
    # default: anthropic
    model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    return LLM(model=f"anthropic/{model}", api_key=os.getenv("ANTHROPIC_API_KEY"))
