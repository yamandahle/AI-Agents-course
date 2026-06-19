"""Provider-agnostic LLM wrapper via LiteLLM; all calls go through ApiGatekeeper."""

from __future__ import annotations

import litellm

from hw4.shared.gatekeeper import ApiGatekeeper
from hw4.shared.provider import ProviderConfig, load_provider

litellm.drop_params = True


class LlmClient:
    """Thin wrapper around LiteLLM that routes to OpenAI, Gemini, or Anthropic.

    The active provider is selected by LLM_PROVIDER in .env.
    Falls back to a no-op (returns "") when no API key is configured,
    so the pipeline runs without an LLM key (pure Python mode).
    """

    def __init__(self, gatekeeper: ApiGatekeeper) -> None:
        self._gatekeeper = gatekeeper
        self._provider: ProviderConfig = load_provider()

    def is_configured(self) -> bool:
        return self._provider.is_configured()

    def complete(self, system: str, user: str) -> str:
        if not self.is_configured():
            return ""

        def _call() -> str:
            response = litellm.completion(
                model=self._provider.model,
                api_key=self._provider.api_key,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content or ""

        return self._gatekeeper.execute(_call)
