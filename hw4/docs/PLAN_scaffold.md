---
title: PLAN — Setup Stage
version: "1.00"
status: draft
---

# Setup Stage Plan

## Goal
Create the full folder structure, initialize uv, configure tools, and write
skeleton files. No logic yet — just the project skeleton.

## Steps

### 1. Initialize uv
Run from inside the `hw4/` folder:
```
uv init .
```
- Project name: `hw4`, layout: `src/hw4/`
- Creates: `pyproject.toml`, `uv.lock`, `.python-version`

### 2. Folder Structure
```
hw4/
├── src/hw4/
│   ├── __init__.py
│   ├── sdk/sdk.py
│   ├── services/
│   ├── agents/
│   │   ├── graph_reader.py        ← Agent 1 (own file)
│   │   ├── bug_detector_agent.py  ← Agent 2 (own file)
│   │   ├── fix_proposer.py        ← Agent 3 (own file)
│   │   └── verifier.py            ← Agent 4 (own file)
│   ├── models/
│   └── shared/
│       ├── gatekeeper.py
│       ├── config.py
│       └── version.py
├── tests/unit/
├── tests/integration/
├── tests/conftest.py
├── config/
│   ├── setup.json
│   └── rate_limits.json
├── data/
├── results/
├── artifacts/
├── obsidian/
├── reports/
├── assets/
├── .env-example
└── .gitignore
```

### 3. `shared/version.py`
```python
VERSION = "1.00"
```

### 4. `config/setup.json`
```json
{
  "version": "1.00",
  "project": "hw4-ex04",
  "agents": {
    "top_n_nodes": 20,
    "max_prompt_tokens": 2000,
    "hub_degree_threshold": 10
  },
  "paths": {
    "artifacts": "artifacts/",
    "results": "results/",
    "obsidian": "obsidian/",
    "data": "data/",
    "reports": "reports/"
  }
}
```

### 5. `config/rate_limits.json`
```json
{
  "version": "1.00",
  "services": {
    "openai": {
      "requests_per_minute": 30,
      "requests_per_hour": 500,
      "concurrent_max": 5,
      "retry_after_seconds": 30,
      "max_retries": 3
    },
    "github": {
      "requests_per_minute": 10,
      "requests_per_hour": 100,
      "concurrent_max": 2,
      "retry_after_seconds": 60,
      "max_retries": 3
    }
  }
}
```

### 6. `pyproject.toml` — dependencies + tools
Dependencies: `crewai`, `networkx`, `python-dotenv`
Dev: `pytest`, `pytest-cov`, `ruff`

```toml
[tool.ruff]
line-length = 100
target-version = "py310"
[tool.ruff.lint]
select = ["E","F","W","I","N","UP","B","C4","SIM"]
ignore = ["E501"]

[tool.coverage.run]
source = ["src"]
omit = ["src/main.py", "*/tests/*"]
[tool.coverage.report]
fail_under = 85
```

### 7. `.env-example`
```
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 8. `.gitignore`
Standard Python + `.env` + uv artifacts + `data/thefuck/`

### 9. Skeleton stubs
- `sdk/sdk.py` — `HW4SDK` class, all methods as `pass`
- `shared/gatekeeper.py` — `ApiGatekeeper` class, all methods as `pass`
- Each agent file — one class, `pass` body

## Done Checklist
- [ ] `uv run python -c "import hw4"` works
- [ ] `uv run ruff check src/` → zero errors
- [ ] All folders exist
- [ ] `VERSION = "1.00"` in `shared/version.py`
- [ ] `"version": "1.00"` in both config files

## Git Commit
```
feat: init hw4 project setup v1.00
```

## Next
`PLAN_grphify.md` — clone thefuck and run Grphify
