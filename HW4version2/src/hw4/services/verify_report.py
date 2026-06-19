from __future__ import annotations

from typing import Any


def render_verification_report(
    proposal: dict,
    comparison: dict[str, Any],
    tests_passed: bool,
    coverage: float,
    ruff_clean: bool,
) -> str:
    """Render a Markdown verification report from the fix proposal and metrics comparison."""
    bug = proposal.get("bug", {})
    hub = comparison["main_cookiecutter_hub_degree"]
    tests = "PASS" if tests_passed else "FAIL"
    ruff = "PASS" if ruff_clean else "FAIL"
    return f"""# Verification Report — EX04

## Bug fixed

- **Type:** {bug.get("bug_type", "HUB")}
- **Node:** `{bug.get("node_name", "cookiecutter()")}`
- **File:** `{proposal.get("target_file", "main.py")}`
- **Change:** {proposal.get("change_description", "")}

## Graph metrics (before vs after)

| Metric | Before | After |
|--------|--------|-------|
| Nodes | {comparison["node_count"]["before"]} | {comparison["node_count"]["after"]} |
| Edges | {comparison["edge_count"]["before"]} | {comparison["edge_count"]["after"]} |
| Communities | {comparison["community_count"]["before"]} | {comparison["community_count"]["after"]} |
| Bridges | {comparison["bridge_count"]["before"]} | {comparison["bridge_count"]["after"]} |
| `main_cookiecutter` hub degree | {hub["before"]} | {hub["after"]} |
| Orchestration hub sum (after) | — | {comparison["orchestration_hub_sum_after"]} |

## Quality checks

| Check | Result |
|-------|--------|
| Unit tests | {tests} |
| Coverage | {coverage:.1f}% |
| Ruff | {ruff} |

## Conclusion

Logic moved from `main.py` into `orchestration.py`. The entry function still
coordinates the pipeline, so its graph degree can stay high or rise slightly.
The fix distributes responsibilities into smaller orchestration nodes instead
of one monolithic implementation block.
"""
