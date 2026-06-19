---
title: TODO — Push test coverage above 85%
version: "1.01"
status: in-progress
---

# TODO — Coverage Gap Fix

Current: 77% (688/896 lines). Target: ≥85% (762 lines). Gap: 74 lines to cover.

## Files at 0% — highest priority

| File | Uncovered lines | Test file to create |
|---|---|---|
| `crewai_tools/tools.py` | 47 | `test_crewai_tools.py` |
| `services/crew_runner_v2.py` | 42 | `test_crew_runner_v2.py` |
| `crewai_agents/agents.py` | 13 | `test_crewai_agents.py` |
| `crewai_tasks/tasks.py` | 8 | `test_crewai_tasks.py` |

## Files with low coverage — second priority

| File | Coverage | Uncovered lines | Action |
|---|---|---|---|
| `shared/gatekeeper.py` | 52% | 27-39, 42-47, 50 | create `test_gatekeeper.py` |
| `services/verify_service.py` | 58% | 39-75, 80, 99-120 | extend `test_verify_service.py` |
| `sdk/sdk.py` | 67% | 38-43, 54-72 | extend `test_sdk.py` |

---

## Task list

- [ ] 1. Create `tests/unit/test_crewai_tools.py`
  - [ ] test_load_graph_metrics_returns_correct_counts
  - [ ] test_load_graph_metrics_empty_graph
  - [ ] test_read_obsidian_files_reads_both_files
  - [ ] test_read_obsidian_files_missing_dir_returns_empty
  - [ ] test_read_source_snippet_returns_content
  - [ ] test_read_source_snippet_file_not_found
  - [ ] test_run_unit_tests_passes
  - [ ] test_run_unit_tests_fails

- [ ] 2. Create `tests/unit/test_crew_runner_v2.py`
  - [ ] test_collect_outputs_reads_json_files
  - [ ] test_collect_outputs_missing_files_returns_empty
  - [ ] test_parse_verdict_missing_file_returns_empty
  - [ ] test_parse_verdict_reads_json
  - [ ] test_run_stops_on_pass_verdict (mock Crew.kickoff)
  - [ ] test_run_retries_on_fail_verdict (mock Crew.kickoff + inject FAIL then PASS)

- [ ] 3. Create `tests/unit/test_crewai_agents.py`
  - [ ] test_build_agents_returns_all_four_keys
  - [ ] test_build_agents_uses_provider_model
  - [ ] test_build_agents_defaults_to_load_provider

- [ ] 4. Create `tests/unit/test_crewai_tasks.py`
  - [ ] test_build_tasks_returns_four_tasks
  - [ ] test_tasks_have_correct_context_chaining

- [ ] 5. Create `tests/unit/test_gatekeeper.py`
  - [ ] test_execute_calls_function_and_returns_result
  - [ ] test_execute_retries_on_failure_then_succeeds
  - [ ] test_execute_raises_after_max_retries
  - [ ] test_wait_if_rate_limited_sleeps_when_full
  - [ ] test_record_call_appends_timestamp

- [ ] 6. Extend `tests/unit/test_verify_service.py` with mocked subprocess
  - [ ] test_run_tests_passes
  - [ ] test_run_tests_fails_returns_false
  - [ ] test_run_ruff_clean
  - [ ] test_run_ruff_dirty

- [ ] 7. Run `uv run pytest tests/unit -q --cov=src` — confirm ≥85%
- [ ] 8. Run `uv run ruff check src tests` — confirm 0 errors
