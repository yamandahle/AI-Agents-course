# PROMPTS — Decision Log (EX06)

This file logs all significant prompts and decisions made during development.
It is a graded requirement — update it after every meaningful decision.

---

## 2026-07-03 — Documentation Phase

**Decision:** Use Approach 3 (hybrid/local) for LLM architecture.  
**Reason:** No external exposure needed during development; swap to cloud via config.

**Decision:** Q-table as optional tactical advisor (injected into LLM prompt).  
**Reason:** Assignment recommends it (Section 8); keeps LLM as final decision-maker.

**Decision:** tkinter for GUI framework.  
**Reason:** Zero extra dependency (stdlib); sufficient for 5×5 grid display.

**Decision:** Q-table state = (cop_row, cop_col, thief_row, thief_col) only — no barriers.  
**Reason:** Keeps state space at 625 entries; barriers change per sub-game making Q-table unstable if included.

**Decision:** 7 experiment cases (A–G) covering vision radius, Q-table on/off, thief deception, initial placement.  
**Reason:** Shows diverse outcome scenarios required by assignment originality section.

---

<!-- Add new entries below as development progresses -->
