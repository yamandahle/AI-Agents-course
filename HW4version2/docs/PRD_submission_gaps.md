---
title: PRD — Submission Gap Remediation
version: "1.00"
status: approved
---

# PRD — Submission Gap Remediation (EX04)

## 1. Context

Audit of `HW4version2` against `software_submission_guidelines-V3.pdf` (Dr. Segal Yoram, 2026-03-26)
identified seven gaps. This PRD defines the acceptance criteria for closing each one before submission.

## 2. Gaps and Requirements

### GAP-1: File Size — `generic_fix_applier.py` exceeds 150 lines
**Guideline §3.2:** Every source file ≤ 150 code lines (blank/comment lines excluded).  
**Current state:** `generic_fix_applier.py` = 176 lines.  
**Required:** Extract git-related helpers (`_find_git_root`, `_branch_name`, `_git`, `_export_diff`)
into `src/hw4/shared/git_ops.py`. Both resulting files must be ≤ 150 lines.

### GAP-2: File Size — Two test files exceed 150 lines
**Same guideline applies to test files.**  
**Current state:** `test_generic_fix_applier.py` = 172 lines, `test_crew_runner_v2.py` = 165 lines.  
**Required:** Split each into two files by logical section. All resulting files ≤ 150 lines.
Coverage must remain ≥ 85 % and all tests must pass.

### GAP-3: Missing `notebooks/` folder and analysis notebook
**Guideline §9, §17.5:** A results analysis notebook (Jupyter) is mandatory, covering:
- Token efficiency comparison (naïve vs graph-guided)
- Cost breakdown per model in dollars
- Visualization (bar charts, tables)
- Token savings analysis with interpretation  

**Required:** `notebooks/analysis.ipynb` with ≥ 4 cells: context, token comparison, cost table,
visualisation.

### GAP-4: Missing cost breakdown in dollars
**Guideline §11, §17.5:** Pipeline cost must be tracked in dollars (input tokens, output tokens,
cost per model).  
**Current state:** `results/token_stats.json` only stores estimated token counts and savings %.  
**Required:** Enrich `results/token_stats.json` with `cost_breakdown` table per stage/model
and `total_cost_usd`.

### GAP-5: Missing `config/logging_config.json`
**Guideline §7.3:** Recommended config hierarchy includes `config/logging_config.json`.  
**Required:** Add `config/logging_config.json` with structured logging configuration.

### GAP-6: No version validation at startup
**Guideline §8.1:** "The application must validate that the config version matches at runtime."  
**Current state:** `ConfigManager` loads `setup.json` but never checks `version` against
`src/hw4/shared/version.py::VERSION`.  
**Required:** `ConfigManager.__init__` raises `RuntimeError` if `setup.json["version"] != VERSION`.

### GAP-7: README missing Contribution Guidelines and License sections
**Guideline §2.1:** README must include Contribution Guidelines and License & Credits sections.  
**Current state:** README ends at section 10 with "Config and credits" (informal).  
**Required:** Add formal `## Contributing` and `## License` sections.

## 3. Success Criteria

| GAP | Done When |
|-----|-----------|
| GAP-1 | `generic_fix_applier.py` ≤ 150 lines; `git_ops.py` ≤ 150 lines; tests pass |
| GAP-2 | All test files ≤ 150 lines; `pytest` passes; coverage ≥ 85 % |
| GAP-3 | `notebooks/analysis.ipynb` exists with ≥ 4 cells and matplotlib charts |
| GAP-4 | `token_stats.json` has `cost_breakdown` dict and `total_cost_usd` float |
| GAP-5 | `config/logging_config.json` exists with valid JSON |
| GAP-6 | `ConfigManager` raises `RuntimeError` on version mismatch; test added |
| GAP-7 | README has `## Contributing` and `## License` sections |

## 4. Out of Scope

- Changing the pipeline logic or agent prompts
- Adding new features beyond what is needed for compliance
- Modifying `pyproject.toml` coverage threshold (already ≥ 85 %)
