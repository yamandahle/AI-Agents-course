---
title: PLAN — Multi-Provider LLM Support
version: "1.01"
status: draft
---

# Implementation Plan — Provider-Agnostic LLM Client

## Approach

Use LiteLLM (already bundled as a CrewAI dependency) as the single adapter
for all three providers. A new `ProviderConfig` dataclass centralises the
provider→key-var→model-string mapping so every caller has one import, not
scattered `os.getenv("OPENAI_*")` calls.

## Step 1 — Add `shared/provider.py` (new file)

```python
# src/hw4/shared/provider.py
@dataclass
class ProviderConfig:
    name: str          # "openai" | "gemini" | "anthropic"
    api_key: str       # value read from env
    model: str         # LiteLLM model string
    rate_limit_key: str  # key into rate_limits.json

def load_provider() -> ProviderConfig:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    ...  # map provider → env vars → ProviderConfig
```

`load_provider()` raises `ValueError` with a clear message if `LLM_PROVIDER`
is set to an unknown value.

## Step 2 — Update `shared/llm_client.py`

- Remove `from openai import OpenAI`
- Import `litellm` and `load_provider`
- `is_configured()` checks `provider.api_key` is set and not placeholder
- `complete()` calls `litellm.completion(model=..., api_key=..., messages=...)`
- All calls still go through `self._gatekeeper.execute(...)`

## Step 3 — Update `services/crew_runner_v2.py`

- Replace the two `os.environ.get("OPENAI_*")` lines with `load_provider()`
- Pass `provider.model` and `provider.api_key` to `build_agents()`

## Step 4 — Update `crewai_agents/agents.py`

- Change signature from `build_agents(model, api_key)` to
  `build_agents(provider: ProviderConfig)`
- `LLM(model=provider.model, api_key=provider.api_key, temperature=0.2)`

## Step 5 — Update `sdk/sdk.py`

- Change `self.config.get_rate_limit("openai")` to
  `self.config.get_rate_limit(load_provider().rate_limit_key)`

## Step 6 — Update `config/rate_limits.json`

Add `"gemini"` and `"anthropic"` blocks alongside the existing `"openai"` block.

Gemini free-tier: 15 RPM.
Anthropic tier-1: 50 RPM.

```json
{
  "services": {
    "openai":     { "requests_per_minute": 30, ... },
    "gemini":     { "requests_per_minute": 15, "requests_per_hour": 500,
                    "concurrent_max": 3, "retry_after_seconds": 30, "max_retries": 3 },
    "anthropic":  { "requests_per_minute": 50, "requests_per_hour": 1000,
                    "concurrent_max": 5, "retry_after_seconds": 30, "max_retries": 3 }
  }
}
```

## Step 7 — Update `.env-example`

Show all three provider blocks with `LLM_PROVIDER` at the top.

## Step 8 — Update unit tests

- `test_llm_client.py`: mock `litellm.completion` instead of `OpenAI`
- `test_config.py`: add gemini/anthropic rate-limit lookup tests
- Any test that patches `OPENAI_API_KEY` switches to `GEMINI_API_KEY` or
  uses `LLM_PROVIDER` parametrisation

## File order (do in this sequence to avoid broken imports)

1. `shared/provider.py` (no deps on other hw4 modules)
2. `config/rate_limits.json`
3. `.env-example`
4. `shared/llm_client.py`
5. `sdk/sdk.py`
6. `services/crew_runner_v2.py`
7. `crewai_agents/agents.py`
8. Tests

## Validation

```bash
uv run pytest tests/unit -q          # all 29 pass
uv run ruff check src tests          # zero errors
# smoke test with real key:
LLM_PROVIDER=gemini GEMINI_API_KEY=<key> uv run python -c "
from hw4.shared.provider import load_provider
from hw4.shared.llm_client import LlmClient
from hw4.shared.gatekeeper import ApiGatekeeper, RateLimitConfig
p = load_provider()
g = ApiGatekeeper(config=RateLimitConfig(15,500,3,30,3))
c = LlmClient(g)
print(c.complete('You are helpful.', 'Say hello in one word.'))
"
```
