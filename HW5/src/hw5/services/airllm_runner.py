"""AirLLMRunner — RunnerProtocol implementation using AirLLM layer streaming."""

from __future__ import annotations

import logging
import time
from typing import Any

from transformers import AutoTokenizer as _AutoTokenizer

from hw5.services.airllm_types import (
    _SUPPORTED_COMPRESSIONS,
    RunnerError,
    UnsupportedQuantError,
    _airllm_version,
    _cuda_available,
)
from hw5.services.runner_protocol import InferenceResult
from hw5.shared.config import Config
from hw5.shared.gatekeeper import ApiGatekeeper
from hw5.shared.quant_config import QuantizationConfig

log = logging.getLogger(__name__)

try:
    from airllm import AutoModel as _AirLLMAuto

    _AIRLLM_AVAILABLE = True
except ImportError:
    _AirLLMAuto = None  # type: ignore[assignment]
    _AIRLLM_AVAILABLE = False


class AirLLMRunner:
    """Runs LLM inference via AirLLM's layer-by-layer disk-streaming approach."""

    def __init__(self, config: Config, gatekeeper: ApiGatekeeper) -> None:
        self._config = config
        self._gatekeeper = gatekeeper
        self._model: Any = None
        self._tokenizer: Any = None
        self._model_id: str | None = None
        self._quant: QuantizationConfig | None = None

    def health_check(self) -> bool:
        return _AIRLLM_AVAILABLE

    def load(self, model_id: str, quant: QuantizationConfig) -> None:
        """Download and initialise the AirLLM model for layer-streaming inference."""
        compression = self._resolve_compression(quant)
        log.info("AirLLM: loading %s with %s compression", model_id, compression)
        t0 = time.perf_counter()
        try:
            self._model = self._gatekeeper.execute(
                _AirLLMAuto.from_pretrained,
                model_id,
                compression=compression,
            )
            self._tokenizer = self._gatekeeper.execute(
                _AutoTokenizer.from_pretrained,
                model_id,
            )
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
        except Exception as exc:
            self._model = None
            self._tokenizer = None
            raise RunnerError(f"AirLLM load failed for '{model_id}': {exc}") from exc
        self._model_id = model_id
        self._quant = quant
        log.info("AirLLM: loaded %s in %.1fs", model_id, time.perf_counter() - t0)

    def infer(self, prompt: str, max_tokens: int = 200) -> InferenceResult:
        """Run generation and return a populated InferenceResult."""
        if self._model is None:
            raise RunnerError("No model loaded. Call load() first.")
        tok = self._load_tokenizer()
        input_ids = tok(prompt, return_tensors="pt").input_ids
        prompt_len = int(input_ids.shape[1])
        t_start = time.perf_counter()
        try:
            output = self._gatekeeper.execute(
                self._model.generate,
                input_ids,
                max_new_tokens=max_tokens,
                use_cache=False,
            )
        except Exception as exc:
            raise RunnerError(f"AirLLM inference failed: {exc}") from exc
        t_end = time.perf_counter()
        new_ids = output[0][prompt_len:]
        output_text = tok.decode(new_ids, skip_special_tokens=True)
        return InferenceResult(
            output_text=output_text,
            tokens_generated=int(len(new_ids)),
            total_time_s=t_end - t_start,
            first_token_latency_s=0.0,
            framework="airllm",
            model_id=self._model_id or "",
            quant=str(self._quant or ""),
            prompt_token_count=prompt_len,
            metadata={
                "cpu_only": not _cuda_available(),
                "airllm_version": _airllm_version(),
            },
        )

    def unload(self) -> None:
        """Delete the model from RAM and free GPU cache if applicable."""
        if self._model is not None:
            del self._model
            self._model = None
            try:
                import torch

                torch.cuda.empty_cache()
            except Exception:
                pass
        import gc

        gc.collect()  # noqa: E702
        self._tokenizer = None
        self._model_id = None
        self._quant = None
        log.info("AirLLM: unloaded model, freed GPU cache")

    def count_prompt_tokens(self, prompt: str) -> int:
        """Return the number of tokens the tokenizer produces for prompt."""
        tok = self._load_tokenizer()
        return int(tok(prompt, return_tensors="pt").input_ids.shape[1])

    def _load_tokenizer(self) -> Any:
        if self._tokenizer is None:
            if not self._model_id:
                raise RunnerError("No model_id set; call load() first.")
            self._tokenizer = _AutoTokenizer.from_pretrained(self._model_id)
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
        return self._tokenizer

    def _resolve_compression(self, quant: QuantizationConfig) -> str:
        label = str(quant)
        compression = quant.to_airllm_param()
        if compression not in _SUPPORTED_COMPRESSIONS:
            raise UnsupportedQuantError(
                f"{label} maps to '{compression}' which AirLLM does not support. "
                f"Supported: {sorted(_SUPPORTED_COMPRESSIONS)}"
            )
        log.info("AirLLM: using compression=%s", compression)
        return compression
