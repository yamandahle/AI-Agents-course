# Hot zone — architecture investigation

Top nodes by degree (package-only graph). I start bug research here.

| Rank | Node | Edges | File | Risk |
|------|------|-------|------|------|
| 1 | `UndefinedVariableInTemplate` | 21 | exceptions.py | Exception hub |
| 2 | `CookiecutterException` | 20 | exceptions.py | Base exception hub |
| 3 | `cookiecutter()` | 16 | main.py | SPOF / orchestrator |
| 4 | `generate_files()` | 14 | generate.py | Overloaded hub |
| 5 | `prompt_for_config()` | 12 | prompt.py | Prompt hub |
| 6 | `Context` | 11 | generate.py | Shared data object |
| 7 | `Parameter` | 11 | prompt.py | Prompt model |

## Primary suspect

**`cookiecutter()` in `main.py`** — central orchestrator. Many modules depend on it.

## Secondary suspect

**`generate_files()` in `generate.py`** — high fan-in from generation workflow.

## Links

- [[index.md]]
- [[GRAPH_REPORT.md]]
