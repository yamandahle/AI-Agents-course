# PRD — API Gatekeeper

## Role
The Gatekeeper is the single choke point for ALL external API calls — both
Anthropic LLM calls and Tavily web search calls. Nothing bypasses it.
It exists to enforce budget control, prevent runaway costs, and produce
an auditable token log that feeds the README cost table.

---

## Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| API request | dict | Any agent | model, prompt, max_tokens, call_type (llm/search) |
| Rate limits | dict | rate_limits.json | Requests per minute, max tokens per call, daily budget |
| Env vars | str | os.environ | ANTHROPIC_API_KEY, TAVILY_API_KEY |

---

## Outputs

| Output | Type | Destination | Description |
|--------|------|-------------|-------------|
| API response | str | Calling agent | Raw text response from LLM or search results |
| Token log entry | dict | DebateLogger | input_tokens, output_tokens, model, cost_usd, timestamp |
| Cost table | list[dict] | README / CLI | Aggregated per-model cost breakdown for the full run |
| Queue event | log entry | DebateLogger | Logged when a call is held in FIFO due to rate limit |

---

## Rate Limit Strategy
Limits live exclusively in `config/rate_limits.json` — never in code:
```json
{
  "anthropic": {
    "requests_per_minute": 10,
    "max_tokens_per_call": 1000,
    "daily_budget_usd": 2.00
  },
  "tavily": {
    "requests_per_minute": 5
  }
}
```
When limit is reached: call enters FIFO deque and waits for the next window.
When daily budget is reached: calls are rejected and an error is raised to Father.

---

## Constraints
- Zero direct API calls anywhere in codebase except inside Gatekeeper
- Rate limits are read-only at startup — not modifiable at runtime
- Every call must be logged before it is made (for crash recovery)
- Retry policy: up to 3 retries on HTTP 5xx with exponential backoff (1s, 2s, 4s)
- HTTP 429 (rate limit from provider): treat as FIFO queue trigger, not error
- Gatekeeper must be thread-safe and process-safe (uses multiprocessing.Lock)

---

## Token Cost Model

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|-----------------------|------------------------|
| claude-haiku-4-5 | $0.80 | $4.00 |
| claude-sonnet-4-6 | $3.00 | $15.00 |

Cost is calculated per call and accumulated. Final table printed at debate end.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Per-agent rate limiting | Harder to enforce global budget; agents could each max out their limit |
| Global singleton in memory | Not safe across processes; shared state requires IPC |
| No rate limiting | Fails engineering requirement; risk of unexpected large bills |
| Hard-coded limits in each agent | Violates DRY and zero-hardcoded-values rule |

---

## Success Criteria
- No API call occurs without a corresponding log entry
- Rate limit never exceeded in a run (verified in logs)
- Cost table matches sum of individual call logs (no rounding drift > $0.01)
- FIFO queue correctly delays calls without dropping them
- 85%+ unit test coverage on Gatekeeper class

---

## Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Daily budget exhausted mid-debate | Raise BudgetExceededError; Father logs and halts gracefully |
| FIFO queue grows > 20 items | Log warning; oldest item dropped; alert raised |
| API key missing from environment | Raise ConfigError at startup — fail fast before any debate begins |
| Network timeout on API call | Retry up to 3 times; on 3rd failure raise GatekeeperError |
| Anthropic returns malformed JSON | Log raw response; raise ParseError; calling agent gets empty string |
| Two processes call simultaneously | multiprocessing.Lock ensures only one call executes at a time |
