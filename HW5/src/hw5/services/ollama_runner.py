"""OllamaRunner — RunnerProtocol implementation using a local Ollama server."""

from __future__ import annotations

import logging
import time
from typing import Any

import ollama as _ollama

from hw5.services.ollama_server import OllamaServer
from hw5.services.runner_protocol import InferenceResult
from hw5.shared.config import Config
from hw5.shared.gatekeeper import ApiGatekeeper
from hw5.shared.quant_config import QuantizationConfig

log = logging.getLogger(__name__)


class RunnerError(RuntimeError):
    """Raised when OllamaRunner encounters a load or inference failure."""


def _attr(obj: Any, key: str, default: Any = None) -> Any:
    """Unified attribute/key access for both dict chunks and Pydantic objects."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class OllamaRunner:
    """Runs LLM inference via streaming against a local Ollama HTTP server."""

    def __init__(self, config: Config, gatekeeper: ApiGatekeeper) -> None:
        self._config = config
        self._gatekeeper = gatekeeper
        self._current_tag: str | None = None
        self._current_quant: QuantizationConfig | None = None
        self._server = OllamaServer(config)

    def health_check(self) -> bool:
        """Return True if the Ollama server is reachable."""
        try:
            self._gatekeeper.execute(_ollama.list)
            return True
        except Exception:
            return False

    def load(self, model_id: str, quant: QuantizationConfig) -> None:
        """Resolve and pull the GGUF tag, then mark it as the active model."""
        if not self.health_check():
            raise RunnerError(
                f"Ollama server not reachable at {self._config.ollama_host}"
            )
        tag = self._resolve_tag(model_id, quant)
        log.info("OllamaRunner: pulling %s …", tag)
        try:
            self._gatekeeper.execute(_ollama.pull, tag)
        except Exception as exc:
            raise RunnerError(f"Failed to pull '{tag}': {exc}") from exc
        self._current_tag = tag
        self._current_quant = quant
        log.info("OllamaRunner: loaded %s", tag)

    def infer(self, prompt: str, max_tokens: int = 200) -> InferenceResult:
        """Stream inference from Ollama and return a fully populated InferenceResult."""
        if self._current_tag is None:
            raise RunnerError("No model loaded. Call load() first.")

        t_start = time.perf_counter()
        t_first: float | None = None
        chunks: list[str] = []
        token_count: int = 0

        try:
            stream = self._gatekeeper.execute(
                _ollama.generate,
                model=self._current_tag,
                prompt=prompt,
                stream=True,
                options={"num_predict": max_tokens},
            )
            for chunk in stream:
                if t_first is None:
                    t_first = time.perf_counter() - t_start
                chunks.append(_attr(chunk, "response", ""))
                if _attr(chunk, "done", False):
                    token_count = int(_attr(chunk, "eval_count", 0) or 0)
        except Exception as exc:
            raise RunnerError(f"Inference failed: {exc}") from exc

        t_end = time.perf_counter()
        return InferenceResult(
            output_text="".join(chunks),
            tokens_generated=token_count or len(chunks),
            total_time_s=t_end - t_start,
            first_token_latency_s=t_first or 0.0,
            framework="ollama",
            model_id=self._current_tag,
            quant=str(self._current_quant or ""),
        )

    def unload(self) -> None:
        """Delete the current GGUF from Ollama to free disk/memory."""
        if self._current_tag:
            try:
                self._gatekeeper.execute(_ollama.delete, self._current_tag)
            except Exception as exc:
                log.warning("OllamaRunner: unload failed — %s", exc)
        self._current_tag = None
        self._current_quant = None

    def get_model_info(self) -> dict[str, Any]:
        """Return Ollama metadata for the currently loaded model."""
        if not self._current_tag:
            return {}
        result = self._gatekeeper.execute(_ollama.show, self._current_tag)
        return result if isinstance(result, dict) else vars(result)

    def _resolve_tag(self, model_id: str, quant: QuantizationConfig) -> str:
        """Return model_id unchanged if it is already an Ollama tag; else construct one."""
        if ":" in model_id and "/" not in model_id:
            return model_id
        name = model_id.split("/")[-1].lower()
        return f"{name}:{quant.to_ollama_tag()}"
