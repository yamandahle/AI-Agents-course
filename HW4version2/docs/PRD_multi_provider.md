---
title: PRD — Multi-Provider LLM Support
version: "1.01"
status: draft
---

# PRD — Provider-Agnostic LLM Client

## 1. Problem

The project hard-codes OpenAI as the only LLM provider. Every class that
touches an LLM (`LlmClient`, `CrewRunnerV2`, `crewai_agents/agents.py`, `sdk.py`)
reads `OPENAI_API_KEY` and `OPENAI_MODEL`. Running with Gemini or Anthropic
requires touching multiple files, and the rate-limit config only has an
`"openai"` key.

## 2. Goal

A single env var (`LLM_PROVIDER`) selects the active provider.
All LLM-touching code reads that var; nothing else changes in the call sites.

## 3. Supported Providers

| Provider   | Env var for key      | LiteLLM model prefix | Example model                      |
|------------|----------------------|----------------------|------------------------------------|
| openai     | `OPENAI_API_KEY`     | (none)               | `gpt-4o-mini`                      |
| gemini     | `GEMINI_API_KEY`     | `gemini/`            | `gemini/gemini-2.0-flash`          |
| anthropic  | `ANTHROPIC_API_KEY`  | `anthropic/`         | `anthropic/claude-haiku-4-5-20251001` |

## 4. Design

All three providers are accessed through **LiteLLM**, which is already a
CrewAI transitive dependency. LiteLLM uses a unified `completion()` API and
routes based on the model string prefix.

A new shared helper `ProviderConfig` (in `shared/provider.py`) centralises
the mapping: given `LLM_PROVIDER`, it returns the correct key env-var name,
the model string, and the rate-limit config key. Every caller imports
`ProviderConfig` instead of reading `OPENAI_*` directly.

## 5. Affected Files

| File | Change |
|------|--------|
| `src/hw4/shared/provider.py` | **new** — `ProviderConfig` dataclass + `load_provider()` factory |
| `src/hw4/shared/llm_client.py` | replace OpenAI import with LiteLLM; read from `ProviderConfig` |
| `src/hw4/services/crew_runner_v2.py` | read model + key from `ProviderConfig` |
| `src/hw4/crewai_agents/agents.py` | accept `ProviderConfig` instead of raw model/key strings |
| `src/hw4/sdk/sdk.py` | pass provider name to `get_rate_limit()` from `ProviderConfig` |
| `config/rate_limits.json` | add `"gemini"` and `"anthropic"` service blocks |
| `.env-example` | show all three provider key options + `LLM_PROVIDER` var |

## 6. `.env` contract

Only one provider block is active at a time:

```
LLM_PROVIDER=gemini          # openai | gemini | anthropic

# --- fill in only the block that matches LLM_PROVIDER ---
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini

GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-2.0-flash

ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=anthropic/claude-haiku-4-5-20251001
```

## 7. Success Criteria

- Setting `LLM_PROVIDER=gemini` (+ `GEMINI_API_KEY`) runs the full pipeline
  with no code changes
- Setting `LLM_PROVIDER=anthropic` works the same way
- `LLM_PROVIDER=openai` is the default and keeps existing behaviour
- `LlmClient.is_configured()` returns `False` if the active provider's key
  is missing or equals `"your_key_here"`
- All 29 existing unit tests still pass
- Zero Ruff errors
- Each new/changed file stays ≤ 150 lines

## 8. Out of Scope

- Mixing providers in a single run
- Per-agent provider selection
- Token counting / cost tracking per provider
