"""Provider-agnostic LLM configuration.

Set LLM_PROVIDER=openai|gemini|anthropic in .env.
Each provider reads its own key env var and model env var.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

_PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "openai": {
        "key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "default_model": "gpt-4o-mini",
        "rate_limit_key": "openai",
    },
    "gemini": {
        "key_env": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "default_model": "gemini/gemini-2.5-flash",
        "rate_limit_key": "gemini",
    },
    "anthropic": {
        "key_env": "ANTHROPIC_API_KEY",
        "model_env": "ANTHROPIC_MODEL",
        "default_model": "anthropic/claude-haiku-4-5-20251001",
        "rate_limit_key": "anthropic",
    },
}


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    api_key: str
    model: str
    rate_limit_key: str

    def is_configured(self) -> bool:
        return bool(self.api_key) and self.api_key != "your_key_here"


def load_provider() -> ProviderConfig:
    """Read LLM_PROVIDER from env and return the matching ProviderConfig.

    Raises ValueError for unknown provider names.
    Defaults to 'openai' when LLM_PROVIDER is not set.
    """
    name = os.environ.get("LLM_PROVIDER", "openai").lower().strip()
    if name not in _PROVIDER_DEFAULTS:
        known = ", ".join(_PROVIDER_DEFAULTS)
        raise ValueError(
            f"Unknown LLM_PROVIDER='{name}'. Must be one of: {known}. "
            "Check your .env file."
        )
    cfg = _PROVIDER_DEFAULTS[name]
    api_key = os.environ.get(cfg["key_env"], "")
    model = os.environ.get(cfg["model_env"], cfg["default_model"])
    return ProviderConfig(
        name=name,
        api_key=api_key,
        model=model,
        rate_limit_key=cfg["rate_limit_key"],
    )
