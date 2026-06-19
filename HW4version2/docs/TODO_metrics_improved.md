---
title: TODO — Fix metrics_improved
version: "1.00"
status: in-progress
---

## Task list

- [ ] 1. Update `tasks.py` — add `graph_summary_task` to verification_task context
- [ ] 2. Update `tasks.py` — rewrite verification_task description (no graph_after.json, use fix proposal)
- [ ] 3. Update `test_crewai_tasks.py` — fix context chain length assertion for verification task
- [ ] 4. Run `uv run pytest tests/unit -q --cov=src` — confirm ≥85% + 0 failures
- [ ] 5. Run `uv run ruff check src tests` — confirm 0 errors
- [ ] 6. Reset cookiecutter to main, delete fix branch
- [ ] 7. Rerun pipeline — confirm verdict changes to PASS
