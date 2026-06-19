---
title: PLAN — Generic LLM-driven fix applier
version: "1.00"
---

# Step 1 — Create GenericFixApplier

`src/hw4/services/generic_fix_applier.py`

Key design:
- Constructor: `__init__(llm_client, gatekeeper, paths)`
- `apply_from_proposal(proposal_path=None) -> FixResult`
  1. Load proposal from `results/v2_fix_proposal.json`
  2. Resolve `target_file` to absolute path
  3. Read target file content
  4. Call `_generate_fix(content, filename, new_module_name, description)`
  5. Write modified file + new module to disk
  6. `_find_git_root(target)` — walk parent dirs until `.git` found
  7. `git checkout -b <branch>`, `git add <files>`, `git commit`
  8. Export diff to `results/fix_diff.patch`
  9. Return `FixResult`

LLM prompt uses two hard delimiters so parsing is reliable:
```
===MODIFIED_FILE===
<content>
===NEW_MODULE===
<content>
```

`_parse_response` splits on those delimiters; raises `ValueError` if missing so
caller can surface a clean error rather than silently writing empty files.

# Step 2 — Update sdk.py

Replace `apply_fix()` body: import `GenericFixApplier` and `LlmClient`,
construct and call `apply_from_proposal()`.

# Step 3 — Update run_pipeline.py

Stage 3 comment updated to reflect it is now LLM-driven and generic.
No import changes needed (calls `sdk.apply_fix()`).

# Step 4 — Write tests

`tests/unit/test_generic_fix_applier.py`
- `test_parse_response_valid` — delimiters present, correct split
- `test_parse_response_missing_delimiter_raises` — ValueError
- `test_find_git_root_finds_dotgit` — tmp_path with .git
- `test_find_git_root_raises_when_none` — no .git in ancestry
- `test_branch_name_slugifies_node` — special chars → hyphens
- `test_apply_from_proposal_writes_files_and_commits` — full mock
