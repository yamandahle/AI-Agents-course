---
title: TODO — Generic LLM-driven fix applier
status: in-progress
---

- [ ] 1. Create `src/hw4/services/generic_fix_applier.py`
- [ ] 2. Update `src/hw4/sdk/sdk.py` — apply_fix() uses GenericFixApplier
- [ ] 3. Update `run_pipeline.py` — Stage 3 label/comment only
- [ ] 4. Create `tests/unit/test_generic_fix_applier.py`
- [ ] 5. Run `uv run pytest tests/unit -q --cov=src` — confirm ≥85%
- [ ] 6. Run `uv run ruff check src tests` — confirm 0 errors
- [ ] 7. Reset cookiecutter, rerun full pipeline, confirm PASS verdict
