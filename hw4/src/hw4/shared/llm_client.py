from __future__ import annotations

import os
from typing import Any

from hw4.shared.gatekeeper import ApiGatekeeper


class LlmClient:
    """OpenAI chat wrapper; all calls go through ApiGatekeeper."""

    def __init__(self, gatekeeper: ApiGatekeeper) -> None:
        self._gatekeeper = gatekeeper
        self._model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def is_configured(self) -> bool:
        key = os.environ.get("OPENAI_API_KEY", "")
        return bool(key) and key != "your_key_here"

    def complete(self, system: str, user: str) -> str:
        if not self.is_configured():
            return ""

        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        def _call() -> Any:
            return client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
            )

        response = self._gatekeeper.execute(_call)
        return response.choices[0].message.content or ""
