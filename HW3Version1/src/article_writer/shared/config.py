"""Configuration loader — reads setup.json and rate_limits.json with singleton caching."""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    temperature: float
    model: str = "claude-sonnet-4-6"
    anthropic_model: str = "claude-sonnet-4-6"
    gemini_model: str = "gemini-2.5-flash"


@dataclass(frozen=True)
class ResearchConfig:
    search_backend: str
    fallback_backend: str
    batch_size: int
    max_batches: int
    min_confidence: str


@dataclass(frozen=True)
class WritingConfig:
    max_evaluator_iterations: int
    score_threshold: float
    target_pages: int
    review_iterations: int = 3


@dataclass(frozen=True)
class LaTeXConfig:
    compiler: str
    compile_passes: int


@dataclass(frozen=True)
class AppConfig:
    version: str
    llm: LLMConfig
    research: ResearchConfig
    writing: WritingConfig
    latex: LaTeXConfig


@lru_cache(maxsize=1)
def load_config(config_path: str = "config/setup.json") -> AppConfig:
    """Load and parse setup.json into AppConfig. Cached — reads once per process."""
    raw = json.loads(Path(config_path).read_text(encoding="utf-8"))
    return AppConfig(
        version=raw["version"],
        llm=LLMConfig(**raw["llm"]),
        research=ResearchConfig(**raw["research"]),
        writing=WritingConfig(**raw["writing"]),
        latex=LaTeXConfig(**raw["latex"]),
    )


@lru_cache(maxsize=1)
def load_rate_limits(config_path: str = "config/rate_limits.json") -> dict:
    """Load rate_limits.json services dict. Cached — reads once per process."""
    raw = json.loads(Path(config_path).read_text(encoding="utf-8"))
    return raw["rate_limits"]["services"]
