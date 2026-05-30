# PLAN — System Architecture

## Architecture Layers
```
External CLI  →  SDK (sdk.py)  →  Domain (agents, gatekeeper)  →  Infrastructure (config, logger, watchdog)
```
No business logic in CLI. All orchestration lives in FatherAgent. SDK is the only public interface.

---

## OOP Class Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    BaseAgent  (ABC)                       │
│  config: ConfigManager   gatekeeper: ApiGatekeeper        │
│  logger: DebateLogger                                     │
│  ──────────────────────────────────────────────────────  │
│  + respond(msg: DebateMessage) -> DebateMessage           │
│  + build_system_prompt() -> str          [abstract]       │
│  + get_skill() -> str                    [abstract]       │
└────────────────────────┬─────────────────────────────────┘
              inherits   │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ FatherAgent │   │  ProAgent   │   │  ConAgent   │
│ round: int  │   │ skill=stats │   │ skill=psych │
│ scores: dict│   ├─────────────┤   ├─────────────┤
├─────────────┤   │+ argue()    │   │+ argue()    │
│+orchestrate()   │+ search()   │   │+ search()   │
│+ judge()    │   └─────────────┘   └─────────────┘
│+ intervene()│
│+ route()    │
└─────────────┘

┌──────────────────────────┐    ┌────────────────────────┐
│      ApiGatekeeper       │    │     ConfigManager       │
│  _rate_limits: dict      │    │  _config: dict          │
│  _queue: deque           │    ├────────────────────────┤
│  _token_log: list[dict]  │    │+ get(key, default)->Any │
├──────────────────────────┤    │+ load_all() -> None     │
│+ call(prompt,model) ->str│    └────────────────────────┘
│+ log_tokens(in,out)->None│
│+ check_limit() -> bool   │    ┌────────────────────────┐
│+ get_cost_table() -> list│    │     DebateLogger        │
└──────────────────────────┘    │  _log_dir: Path         │
                                │  _line_count: int       │
┌──────────────────────────┐    ├────────────────────────┤
│         Watchdog         │    │+ log(msg, level)->None  │
│  _procs: list[Process]   │    │+ rotate() -> None       │
│  _restart_count: int     │    └────────────────────────┘
├──────────────────────────┤
│+ monitor() -> None       │    ┌────────────────────────┐
│+ restart(proc) -> None   │    │    DebateMessage        │
│+ keepalive() -> None     │    │    (dataclass)          │
└──────────────────────────┘    │  round: int            │
                                │  sender: str           │
  ApiGatekeeper ◄── used by ──► │  recipient: str        │
  BaseAgent, all subclasses     │  type: str             │
  ConfigManager ◄── used by ──► │  content: str          │
  all classes                   │  word_count: int       │
  DebateLogger ◄── used by ───► │  sources: list[str]    │
  all classes                   │  timestamp: str        │
                                └────────────────────────┘
```

---

## IPC Design — Multiprocessing Queues

```
  FatherProcess
      │   ▲           father_to_pro ──► ProProcess
      │   │           pro_to_father ◄── ProProcess
      │   │
      │   │           father_to_con ──► ConProcess
      │   │           con_to_father ◄── ConProcess
      ▼   │
  Watchdog monitors all 3 processes; restarts any that die
```
- 4 queues total; Pro and Con never share a queue
- Father polls both child queues in sequence each round
- Watchdog runs in a 5th daemon process with keepalive pings

---

## Context Window Management

```
WCn = WCn-1 + Qn + Rn + An

  WCn   = total accumulated tokens after round n
  Qn    = Father's routing prompt tokens at round n  (~100)
  Rn    = Child response tokens at round n           (~200)
  An    = web search snippets + intervention tokens  (~150)

Round 1:  WC1 =    0 + 100 + 200 + 150 =   450
Round 5:  WC5 = 1800 + 100 + 200 + 150 = 2250
Round 10: WC10= 4050 + 100 + 200 + 150 = 4500  (well within 200k limit)
```
Father strategy: pass full history to child each round (safe at these sizes).
If token count exceeds threshold from config, Father summarizes rounds 1..(n-3).

---

## JSON Message Schema

```json
{
  "round":      1,
  "sender":     "pro | con | father",
  "recipient":  "pro | con | father",
  "type":       "argument | counter | intervention | verdict",
  "content":    "...",
  "word_count": 142,
  "sources":    ["https://..."],
  "timestamp":  "2026-05-30T22:00:00Z"
}
```
Verdict adds: `{ "winner": "pro", "pro_score": 7, "con_score": 5, "justification": "..." }`

---

## File Structure

```
hw2/
  src/debate/
    sdk/sdk.py              ← single public entry point
    agents/base_agent.py    ← ABC with shared logic
    agents/father_agent.py
    agents/pro_agent.py
    agents/con_agent.py
    shared/gatekeeper.py
    shared/config.py
    shared/version.py
    shared/logger.py
    watchdog.py
  tests/unit/
    test_gatekeeper.py
    test_logger.py
    test_agents.py
  tests/integration/
    test_debate_flow.py
  config/
    setup.json
    rate_limits.json
    logging_config.json
  docs/
  .env-example  .gitignore  pyproject.toml  README.md
```

---

## Design Decisions

**Multiprocessing over threading** — Python's GIL prevents true parallelism in threads.
Separate processes give each agent isolated memory and allow Watchdog to restart
one agent without killing the others. Thread crash = full program crash.

**JSON over pickle/protobuf** — Human-readable for debugging, no dependencies,
native Python support, trivially logged, and validates against schema without extra libs.
