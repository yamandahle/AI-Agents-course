# TODO — Phase 4: Q-Table Advisor

**Dependency:** Phase 3 complete.  
**PRD:** [PRD_llm_orchestrator.md](PRD_llm_orchestrator.md) §5  
**Status:** [~] Trainer + Advisor done; Integration/Performance Check blocked on Phase 3
**Can run in parallel with:** Phase 5 (GUI)

**Note:** Built in parallel with Phase 3 (not sequentially after it, as this file
originally assumed) — see [nagham-hw6 branch, `HW6/docs/PROMPTS.md`] for that decision.
Sections 4 and 5 below need the orchestrator (Phase 3) to exist for real, so they're
done via a standalone proxy check instead (see section 5).

---

## 1. Trainer (TDD) -- DONE

- [x] Write `tests/unit/test_q_table_trainer.py` FIRST (red):
  - `test_q_table_initializes_to_zeros`
  - `test_bellman_update_increases_good_action`
  - `test_bellman_update_decreases_bad_action`
  - `test_epsilon_greedy_explores`
  - `test_epsilon_greedy_exploits`
  - `test_training_saves_npy_file`
  - plus 2 extra regression tests added for a real bug found during training (see below)
- [x] Implement `src/cop_thief/sdk/q_table/trainer.py` (green):
  - State encoding: `(cop_row, cop_col, thief_row, thief_col)` → int index (factored
    into a shared `sdk/q_table/encoding.py` module, reused by the advisor)
  - Epsilon-greedy policy, masked to the Cop's *currently legal* actions only
  - Bellman update
  - Self-play loop for `training_episodes` episodes (Thief = random valid move;
    the real Thief agent doesn't exist until Phase 3)
  - Save Q-table to `config/q_table.npy`
- [x] Refactor — 147 code lines, under the 150 cap
- [x] `uv run ruff check` → 0 violations

**Bug found + fixed during the real training run:** with an unmasked epsilon-greedy
policy, the Cop can wall itself into a corner with its own barriers (as few as 3
barriers seals a corner cell) — the base game engine has no stalemate rule for this,
so the naive approach either crashed with `InvalidMoveError` or (my first, wrong fix)
silently pretended all 9 actions were legal, which still crashed. Fixed by masking
action selection to only the Cop's currently-valid moves, and having `_cop_step()`
return `False` to end the episode cleanly if that set is ever empty. Covered by
`test_cop_step_returns_false_when_boxed_in` and
`test_run_episode_stops_cleanly_when_cop_boxed_in`.

---

## 2. Advisor (TDD) -- DONE

- [x] Write `tests/unit/test_q_table_advisor.py` FIRST (red):
  - `test_hint_returns_string`
  - `test_hint_is_natural_language_not_coords`
  - `test_hint_matches_best_q_action`
  - `test_hint_empty_when_disabled`
  - `test_loads_npy_file_on_init`
- [x] Implement `src/cop_thief/sdk/q_table/advisor.py` (green):
  - Load `config/q_table.npy` on init
  - `get_hint(cop_pos, thief_pos) -> str`
  - Maps best action index → natural-language direction string
  - Returns `""` when `q_table.enabled = false`
- [x] Refactor — 33 code lines
- [x] `uv run ruff check` → 0 violations

---

## 3. Training Run -- DONE

- [x] Run training: `uv run python -m cop_thief.sdk.q_table.trainer`
  → `config/q_table.npy` created (10,000 episodes, ~2s)
- [x] `config/q_table.npy` already in `.gitignore` (was added earlier alongside the
  original CLAUDE.md/doc suite)

---

## 4. Integration -- BLOCKED on Phase 3

- [ ] Set `q_table.enabled = true` in config.json
- [ ] Run full game: `uv run python src/main.py --headless`
  → Verify "Tactical hint" appears in logs each Cop turn
- [ ] Set `q_table.enabled = false`
  → Verify no hint in logs

Can't do this yet — `src/main.py` / the orchestrator don't exist until Phase 3 lands.
Revisit once Phase 3 merges.

---

## 5. Performance Check -- proxy done, real check blocked on Phase 3

- [ ] Run 3 games with `q_table.enabled = false` → record cop win count (needs Phase 3)
- [ ] Run 3 games with `q_table.enabled = true` → record cop win count (needs Phase 3)
- [x] **Proxy check** (SDK-level only, no orchestrator): 200 self-play games with a
  uniform-random Cop vs. 200 with a greedy-over-trained-Q-table Cop (both vs. a random
  Thief) — cop win rate 62.0% (random) vs. 98.5% (Q-table). Documented in
  `docs/PROMPTS.md`. Real check with the LLM-driven Cop still needs Phase 3.

---

## 6. Phase 4 Sign-off

- [x] `uv run pytest tests/ --cov` → all green (99 passed), coverage 95.02%
- [x] `uv run ruff check .` → 0 violations
- [ ] Q-table hint correctly injected into LLM prompt — blocked on Phase 3's prompt
  builder existing; `QTableAdvisor.get_hint()` is ready to be called from it
- [x] All files have docstrings
- [ ] Commit: `git commit -m "ex06: phase 4 — Q-table tactical advisor"`
- [ ] Push to `yamandahle-hw6` — opened as a PR from the `nagham-hw6` side instead
- [ ] Update [TODO.md](TODO.md) phase status to `[x] Done` (partially — see note there)
