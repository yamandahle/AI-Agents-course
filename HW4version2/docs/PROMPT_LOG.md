---
title: Prompt Engineering Log
version: "1.00"
status: complete
---

# Prompt Engineering Log

Log of significant AI interactions during EX04. Required by submission guidelines V3.

---

### 2026-06-17 — Stage: Grphify

- **Goal:** Build the first code graph for cookiecutter (package only).
- **Context given:** `data/cookiecutter/cookiecutter/` (18 Python files).
- **Prompt:** Run Grphify extract on the package with Claude backend; save outputs to `artifacts/`.
- **Output quality:** good — 269 nodes, 504 edges, 15 communities.
- **Tokens (approx):** input ~20,000 / output ~3,000 (Grphify semantic pass).
- **Iteration:** Switched from full-repo scan (1264 nodes) to package-only for a focused graph.

---

### 2026-06-17 — Stage: Agents (Graph Reader)

- **Goal:** Summarize the graph without reading all source files.
- **Context given:** `artifacts/graph.json`, `obsidian/hot.md`, `obsidian/index.md` (first 2000 chars each).
- **Prompt:** (automatic) Load metrics + top 10 hubs + hot/index excerpts → `GraphSummary`.
- **Output quality:** good — ~645 estimated tokens vs ~23,537 naive.
- **Tokens (approx):** input ~600 / output ~50.
- **Iteration:** Capped excerpts at 2000 chars in `config/setup.json`.

---

### 2026-06-18 — Stage: Agents (Bug Detector)

- **Goal:** Find architectural risks from graph structure.
- **Context given:** Graph with hub degree threshold = 10; top hubs from summary.
- **Prompt:** `Top hubs: [...]. Detected nodes: cookiecutter(), prompt.py, ... In one sentence each, explain the architectural risk.`
- **Output quality:** good — 5 HUB bugs in `results/bugs.json`.
- **Tokens (approx):** input ~400 / output ~150.
- **Iteration:** Rule-based detection first; LLM enriches explanations only.

---

### 2026-06-18 — Stage: Agents (Fix Proposer)

- **Goal:** Propose a minimal refactor for the top hub bug.
- **Context given:** HUB on `cookiecutter()` in `main.py`; hot excerpt; first 800 chars of `main.py`.
- **Prompt:** `Bug: HUB on cookiecutter(). Hot context: [...]. Code snippet: [...]` + system: `Propose a minimal architectural refactor.`
- **Output quality:** good — extract to `orchestration.py`, thin `main.py` facade.
- **Tokens (approx):** input ~500 / output ~100.
- **Iteration:** Template fallback if LLM unavailable; chosen fix saved to `results/fix_proposal.json`.

---

### 2026-06-19 — Stage: Agents (BugsInPy cross-check)

- **Goal:** Check if graph-hot files match known BugsInPy cookiecutter bugs.
- **Context given:** `config/bugsinpy_cookiecutter.json`, graph top hubs, GitHub raw buggy commits.
- **Prompt:** (automatic) Compare `generate.py`, `hooks.py`, `prompt.py`, `exceptions.py` against BugsInPy catalog.
- **Output quality:** good — 4/4 `CONFIRMED_HISTORICAL`, all `graph_hub_match: true`.
- **Tokens (approx):** input ~200 / output ~100 (GitHub fetch, no LLM).
- **Iteration:** Shallow clone lacks history; fetch buggy commits from GitHub raw.

---

### 2026-06-19 — Stage: Fix

- **Goal:** Apply the hub refactor on cookiecutter clone.
- **Context given:** `results/fix_proposal.json`, templates in `src/hw4/resources/`.
- **Prompt:** (code) Apply `orchestration.py` + thin `main.py` via `FixApplierService`.
- **Output quality:** good — patch in `results/fix_diff.patch`, branch `fix/hub-cookiecutter`.
- **Tokens (approx):** N/A (deterministic refactor).
- **Iteration:** None.

---

### 2026-06-19 — Stage: Verify

- **Goal:** Prove the fix works with new graph metrics and tests.
- **Context given:** Baseline `artifacts/graph.json`, fixed package in `data/cookiecutter/`.
- **Prompt:** (automatic) `graphify update` with `GRAPHIFY_OUT=artifacts/graphify-out`; compare metrics; run pytest + ruff.
- **Output quality:** good — `improved: true`, 29 tests pass, coverage ~86%.
- **Tokens (approx):** N/A (update is AST-only, no LLM).
- **Iteration:** Moved `graphify-out` from clone to `artifacts/graphify-out/` for cleaner layout.

---

### 2026-06-19 — Stage: README & docs

- **Goal:** Write final submission README in simple language.
- **Context given:** All `results/*.json`, `reports/verification.md`, screenshots in `assets/`.
- **Prompt:** Structure: goal → why cookiecutter → how it works → results → proof → summary.
- **Output quality:** good — `README.md` complete.
- **Tokens (approx):** input ~3,000 / output ~2,000 (Cursor assistant).
- **Iteration:** Separated “fixed” (architectural HUB) from “validated” (BugsInPy match).
