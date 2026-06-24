"""ModelRegistry — loads models.json and provides hookable model lookup."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from huggingface_hub import snapshot_download

from hw5.services.model_entry import ModelEntry
from hw5.shared.gatekeeper import ApiGatekeeper

log = logging.getLogger(__name__)

_HOOK_MARKER = "<HOOK"


class RegistryError(ValueError):
    """Raised when the model registry config is invalid or incomplete."""


class DownloadError(RuntimeError):
    """Raised when a HuggingFace model download fails."""


class ModelRegistry:
    """Loads and queries the model registry from config/models.json."""

    def __init__(self, gatekeeper: ApiGatekeeper) -> None:
        self._gatekeeper = gatekeeper
        self._models: dict[str, ModelEntry] = {}

    def load_config(self, path: str) -> None:
        """Parse models.json, populate the registry, and validate all entries."""
        try:
            data: dict[str, Any] = json.loads(Path(path).read_text())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RegistryError(f"Cannot load models config from {path}: {e}") from e

        raw_models: list[dict[str, Any]] = data.get("models", [])
        if not raw_models:
            raise RegistryError(f"No models defined in {path}")

        self._models = {}
        for raw in raw_models:
            entry = ModelEntry.from_dict(raw)
            self._models[entry.name] = entry

        self.validate()
        log.info("ModelRegistry: loaded %d model(s)", len(self._models))

    def validate(self) -> None:
        """Raise RegistryError if any entry still contains a HOOK placeholder."""
        for entry in self._models.values():
            if _HOOK_MARKER in entry.hf_repo_id:
                raise RegistryError(
                    f"Model '{entry.name}' still has a HOOK placeholder in hf_repo_id. "
                    f"Edit config/models.json and replace it with a real HuggingFace repo ID."
                )
            if _HOOK_MARKER in entry.ollama_tag:
                raise RegistryError(
                    f"Model '{entry.name}' still has a HOOK placeholder in ollama_tag."
                )

    def get_model(self, name: str) -> ModelEntry:
        """Return the ModelEntry for the given name, or raise KeyError."""
        if name not in self._models:
            raise KeyError(
                f"Model '{name}' not found in registry. "
                f"Available: {sorted(self._models)}"
            )
        return self._models[name]

    def list_models(self) -> list[ModelEntry]:
        """Return all registered models, sorted by name."""
        return [self._models[k] for k in sorted(self._models)]

    def list_names(self) -> list[str]:
        """Return all registered model names, sorted alphabetically."""
        return sorted(self._models)

    def filter_by_framework(self, framework: str) -> list[ModelEntry]:
        """Return models compatible with the given framework ('ollama' or 'airllm')."""
        if framework == "ollama":
            return [m for m in self.list_models() if m.ollama_compatible]
        if framework == "airllm":
            return [m for m in self.list_models() if m.airllm_compatible]
        return []

    @property
    def count(self) -> int:
        """Number of models currently loaded in the registry."""
        return len(self._models)

    def check_local(self, entry: ModelEntry) -> bool:
        """Return True if the model cache directory exists and is non-empty."""
        cache = Path(entry.local_cache)
        return cache.exists() and any(cache.iterdir())

    def ensure_downloaded(self, entry: ModelEntry, dry_run: bool = False) -> None:
        """Download model weights from HuggingFace if not already cached."""
        if dry_run:
            log.info(
                "DRY RUN: would download %s → %s", entry.hf_repo_id, entry.local_cache
            )
            return
        if self.check_local(entry):
            log.info("Model '%s' already cached at %s", entry.name, entry.local_cache)
            return
        log.info("Downloading '%s' from %s …", entry.name, entry.hf_repo_id)
        try:
            self._gatekeeper.execute(
                snapshot_download,
                repo_id=entry.hf_repo_id,
                cache_dir=entry.local_cache,
                token=os.getenv("HF_TOKEN"),
            )
        except Exception as e:
            raise DownloadError(f"Failed to download '{entry.hf_repo_id}': {e}") from e
        log.info("Downloaded '%s' successfully → %s", entry.name, entry.local_cache)
