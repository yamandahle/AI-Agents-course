# TODO — Phase 4: Q-Table Advisor

**Dependency:** Phase 3 complete.  
**PRD:** [PRD_llm_orchestrator.md](PRD_llm_orchestrator.md) §5  
**Status:** [ ] Not started  
**Can run in parallel with:** Phase 5 (GUI)

---

## 1. Trainer (TDD)

- [ ] Write `tests/unit/test_q_table_trainer.py` FIRST (red):
  - `test_q_table_initializes_to_zeros`
  - `test_bellman_update_increases_good_action`
  - `test_bellman_update_decreases_bad_action`
  - `test_epsilon_greedy_explores`
  - `test_epsilon_greedy_exploits`
  - `test_training_saves_npy_file`
- [ ] Implement `src/cop_thief/sdk/q_table/trainer.py` (green):
  - State encoding: `(cop_row, cop_col, thief_row, thief_col)` → int index
  - Epsilon-greedy policy
  - Bellman update
  - Self-play loop for `training_episodes` episodes
  - Save Q-table to `config/q_table.npy`
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 2. Advisor (TDD)

- [ ] Write `tests/unit/test_q_table_advisor.py` FIRST (red):
  - `test_hint_returns_string`
  - `test_hint_is_natural_language_not_coords`
  - `test_hint_matches_best_q_action`
  - `test_hint_empty_when_disabled`
  - `test_loads_npy_file_on_init`
- [ ] Implement `src/cop_thief/sdk/q_table/advisor.py` (green):
  - Load `config/q_table.npy` on init
  - `get_hint(cop_pos, thief_pos) -> str`
  - Maps best action index → natural-language direction string
  - Returns `""` when `q_table.enabled = false`
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 3. Training Run

- [ ] Run training: `uv run python -m cop_thief.sdk.q_table.trainer`
  → `config/q_table.npy` created
- [ ] Add `config/q_table.npy` to `.gitignore`
  (large binary, re-generated on setup)

---

## 4. Integration

- [ ] Set `q_table.enabled = true` in config.json
- [ ] Run full game: `uv run python src/main.py --headless`
  → Verify "Tactical hint" appears in logs each Cop turn
- [ ] Set `q_table.enabled = false`
  → Verify no hint in logs

---

## 5. Performance Check

- [ ] Run 3 games with `q_table.enabled = false` → record cop win count
- [ ] Run 3 games with `q_table.enabled = true` → record cop win count
- [ ] Cop wins with Q-table ≥ cop wins without (document result in PROMPTS.md)

---

## 6. Phase 4 Sign-off

- [ ] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [ ] `uv run ruff check .` → 0 violations
- [ ] Q-table hint correctly injected into LLM prompt
- [ ] All files have docstrings
- [ ] Commit: `git commit -m "ex06: phase 4 — Q-table tactical advisor"`
- [ ] Push to `yamandahle-hw6`
- [ ] Update [TODO.md](TODO.md) phase status to `[x] Done`
