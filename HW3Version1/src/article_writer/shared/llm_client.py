"""Unified LLM client — abstracts Anthropic Claude and Google Gemini behind one interface."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from article_writer.shared.tracer import Tracer
from article_writer.shared.metrics_tracker import MetricsTracker

load_dotenv()

_RETRY_DELAYS = [45, 90, 180]  # seconds — for 429 rate-limit errors (free tier is strict)

_COST_PER_1K = {
    "claude-sonnet-4-6": {"input": 0.003, "output": 0.015},
    "claude-haiku-4-5-20251001": {"input": 0.00025, "output": 0.00125},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
    "gemini-2.5-flash": {"input": 0.0001, "output": 0.0004},
    "gemini-2.5-pro": {"input": 0.00125, "output": 0.01},
}

_GOOGLE_DEFAULT_MODEL = "gemini-2.5-flash"


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    cost_usd: float


@dataclass
class _InternalResult:
    text: str
    input_tokens: int
    output_tokens: int


class LLMClient:
    """Thin wrapper over Anthropic and Google Gemini APIs."""

    def __init__(self, provider: str | None = None, model: str | None = None) -> None:
        self.provider = (provider or os.getenv("LLM_PROVIDER", "anthropic")).lower()
        self._tracer = Tracer()
        self._metrics = MetricsTracker()
        if self.provider == "anthropic":
            import anthropic
            self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = model or "claude-sonnet-4-6"
        elif self.provider == "google":
            self.model = model or os.getenv("GEMINI_MODEL", _GOOGLE_DEFAULT_MODEL)
            from google import genai as _genai
            self._google_client = _genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider!r}")

    def complete(
        self,
        system: str,
        user: str,
        step: str = "llm_call",
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ) -> LLMResponse:
        t0 = time.perf_counter()
        resp = self._call_with_retry(system, user, temperature, max_tokens)
        latency_ms = int((time.perf_counter() - t0) * 1000)
        cost = self._estimate_cost(resp)
        self._tracer.log(step=step, model=self.model, provider=self.provider,
                         input=f"SYSTEM:\n{system}\n\nUSER:\n{user}",
                         output=resp.text, input_tokens=resp.input_tokens,
                         output_tokens=resp.output_tokens)
        self._metrics.log(step=step, model=self.model, latency_ms=latency_ms,
                          input_tokens=resp.input_tokens,
                          output_tokens=resp.output_tokens, cost_usd=cost)
        return LLMResponse(text=resp.text, input_tokens=resp.input_tokens,
                           output_tokens=resp.output_tokens, model=self.model,
                           cost_usd=cost)

    def _call_with_retry(self, system: str, user: str,
                         temperature: float, max_tokens: int) -> _InternalResult:
        call_fn = (self._call_anthropic if self.provider == "anthropic"
                   else self._call_google)
        for attempt, delay in enumerate([0] + _RETRY_DELAYS):
            if delay:
                print(f"[llm_client] rate-limited, retrying in {delay}s (attempt {attempt+1})")
                time.sleep(delay)
            try:
                return call_fn(system, user, temperature, max_tokens)
            except Exception as exc:
                err = str(exc)
                is_rate_limit = ("429" in err or "RESOURCE_EXHAUSTED" in err
                                 or "rate" in err.lower())
                if not is_rate_limit or attempt == len(_RETRY_DELAYS):
                    raise
        raise RuntimeError("All retries exhausted")

    def _call_anthropic(self, system: str, user: str,
                        temperature: float, max_tokens: int) -> _InternalResult:
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return _InternalResult(
            text=msg.content[0].text,
            input_tokens=msg.usage.input_tokens,
            output_tokens=msg.usage.output_tokens,
        )

    def _call_google(self, system: str, user: str,
                     temperature: float, max_tokens: int) -> _InternalResult:
        from google.genai import types as _gtypes
        resp = self._google_client.models.generate_content(
            model=self.model,
            contents=user,
            config=_gtypes.GenerateContentConfig(
                system_instruction=system,
                temperature=temperature,
                max_output_tokens=max_tokens,
                # Disable internal thinking so token budget goes to visible output
                thinking_config=_gtypes.ThinkingConfig(thinking_budget=0),
            ),
        )
        meta = resp.usage_metadata
        return _InternalResult(
            text=resp.text or "",
            input_tokens=getattr(meta, "prompt_token_count", 0),
            output_tokens=getattr(meta, "candidates_token_count", 0),
        )

    def _estimate_cost(self, resp: _InternalResult) -> float:
        rates = _COST_PER_1K.get(self.model, {"input": 0.001, "output": 0.004})
        return (resp.input_tokens / 1000 * rates["input"]
                + resp.output_tokens / 1000 * rates["output"])
