---
title: TODO — Multi-Provider LLM Support
version: "1.01"
status: in-progress
---

# TODO — Provider-Agnostic LLM Client

Legend: `[x]` done · `[ ]` to do

---

## Step 1 — New file: `shared/provider.py`
- [x] Create `ProviderConfig` dataclass (name, api_key, model, rate_limit_key)
- [x] Implement `load_provider()` — reads `LLM_PROVIDER` env var, maps to config
- [x] Support values: `openai`, `gemini`, `anthropic`
- [x] Raise `ValueError` with clear message for unknown provider
- [x] Default to `openai` when `LLM_PROVIDER` is not set

## Step 2 — Update `shared/llm_client.py`
- [x] Remove `from openai import OpenAI` and all `OPENAI_*` env reads
- [x] Import `litellm` and `load_provider`
- [x] `is_configured()` — checks active provider key is set and not placeholder
- [x] `complete()` — calls `litellm.completion(model, api_key, messages)`
- [x] All calls still wrapped in `self._gatekeeper.execute(...)`
- [x] File stays ≤ 150 lines

## Step 3 — Update `services/crew_runner_v2.py`
- [x] Replace `os.environ.get("OPENAI_MODEL")` / `"OPENAI_API_KEY"` with `load_provider()`
- [x] Pass `ProviderConfig` to `build_agents()`
- [x] File stays ≤ 150 lines

## Step 4 — Update `crewai_agents/agents.py`
- [x] Change `build_agents(model, api_key)` → `build_agents(provider: ProviderConfig)`
- [x] `LLM(model=provider.model, api_key=provider.api_key, temperature=0.2)`
- [x] File stays ≤ 150 lines

## Step 5 — Update `sdk/sdk.py`
- [x] Change `get_rate_limit("openai")` → `get_rate_limit(load_provider().rate_limit_key)`
- [x] File stays ≤ 150 lines

## Step 6 — Update `config/rate_limits.json`
- [x] Add `"gemini"` block (15 RPM, 500 RPH, 3 concurrent, 30s retry, 3 retries)
- [x] Add `"anthropic"` block (50 RPM, 1000 RPH, 5 concurrent, 30s retry, 3 retries)
- [x] Keep existing `"openai"` block unchanged

## Step 7 — Update `.env-example`
- [x] Add `LLM_PROVIDER=openai` at the top with comment
- [x] Add all three provider key + model blocks with comments
- [x] Make clear only one block is needed at a time

## Step 8 — Update unit tests
- [x] `test_llm_client.py` — mock `litellm.completion` instead of `openai.OpenAI`
- [x] `test_llm_client.py` — test `is_configured()` for each provider
- [x] `test_config.py` — add rate-limit lookup for `gemini` and `anthropic`
- [x] Add `test_provider.py` — test `load_provider()` for all three values + unknown raises

## Step 9 — Verify
- [x] `uv run pytest tests/unit -q` — all 29 tests pass (+ new provider tests)
- [x] `uv run ruff check src tests` — zero errors
- [x] Smoke test: `LLM_PROVIDER=gemini GEMINI_API_KEY=<key>` — real call returns text
- [x] Git commit: `feat: provider-agnostic LLM client — openai, gemini, anthropic`
