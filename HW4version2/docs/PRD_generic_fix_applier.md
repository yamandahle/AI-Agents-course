---
title: PRD — Generic LLM-driven fix applier
version: "1.00"
status: approved
---

# Problem

`FixApplierService` (Stage 3) is hardcoded to cookiecutter:

- `self._repo_root = Path(paths["data"]) / "cookiecutter"` — hardcoded repo name
- `apply_main_hub_refactor(self._repo_root)` — pre-written function that edits
  `main.py` and creates `orchestration.py`, regardless of what bug the LLM detected
- `git add cookiecutter/main.py cookiecutter/orchestration.py` — hardcoded filenames

If the pipeline is run on any other Python codebase, Stage 3 either crashes or
applies wrong changes. The LLM already produces a complete fix proposal in
`results/v2_fix_proposal.json` with `target_file`, `new_module_name`, and
`change_description`. Stage 3 should USE that proposal to drive real code changes.

# Solution

Replace `FixApplierService` with `GenericFixApplier` that:

1. Reads `results/v2_fix_proposal.json`
2. Reads the actual target source file from disk
3. Calls the LLM: "here is the file, here is the instruction, produce the
   modified file AND the new module"
4. Parses the LLM response into two file contents
5. Writes both files to disk
6. Auto-detects the git repo root (walks up to find `.git`)
7. Commits the change on a new branch

This works for **any** Python codebase without any hardcoding.

# Success criteria

- Running on cookiecutter produces the same quality refactor
- Running on a completely different repo (e.g. `requests`, `flask`) produces a
  valid, repo-specific fix
- No strings "cookiecutter", "main.py", or "orchestration.py" remain in the fix
  application code

# Files

| File | Action |
|---|---|
| `src/hw4/services/generic_fix_applier.py` | CREATE — LLM-driven generic applier |
| `src/hw4/sdk/sdk.py` | UPDATE — `apply_fix()` uses GenericFixApplier |
| `run_pipeline.py` | UPDATE — Stage 3 reads v2_fix_proposal.json |
| `tests/unit/test_generic_fix_applier.py` | CREATE — unit tests |
| `src/hw4/services/fix_applier.py` | KEEP (used by old v1 path, don't delete) |
| `src/hw4/services/cookiecutter_refactor.py` | KEEP (used by fix_applier v1) |
