# PLAN — System Architecture

Full architecture document (C4, IPC, JSON schema, ADRs): see  
[`../../docs/PLAN.md`](../../docs/PLAN.md).

## Summary (Stage 3 implementation)

```
CLI (main.py / menu.py)
         │
         ▼
   DebateSDK (sdk.py)  ← single entry point for all business logic
         │
         ▼
 DebateOrchestrator (multiprocessing + Watchdog)
         │
         ▼
 FatherAgent → ProAgent / ConAgent
         │
         ▼
 ApiGatekeeper → Anthropic API
 DebateLogger  → JSON rotating logs
```

- No business logic in CLI handlers beyond display formatting.
- All external API calls go through `ApiGatekeeper`.
- Config loaded via `ConfigManager` with version `1.00` validation.
