"""Run the full 4-stage HW4 pipeline."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from hw4.sdk.sdk import HW4SDK  # noqa: E402
from hw4.services.crew_runner_v2 import CrewRunnerV2  # noqa: E402

sdk = HW4SDK()

print(f"\n{'='*60}")
print(f"HW4 SDK v{sdk.config.get('version')} — provider: {os.getenv('LLM_PROVIDER', 'openai')}")
print(f"{'='*60}\n")

# Stage 1 — Grphify
print("── STAGE 1: Grphify scan ──────────────────────────────────")
sdk.run_grphify(backend="claude", project_root=".")
print("✓ graph.json, graph.html, GRAPH_REPORT.md → artifacts/\n")

# Stage 2 — CrewAI agents (v2 with real Gemini LLM)
print("── STAGE 2: CrewAI agents (v2) ────────────────────────────")
runner = CrewRunnerV2(sdk.gatekeeper, sdk.config.get("agents"), sdk.config.get("paths"))
result = runner.run()
print("\n✓ results/v2_graph_summary.json")
print("✓ results/bugs.json")
print("✓ results/fix_proposal.json")
print("✓ results/v2_verification.json\n")

# Stage 3 — Apply fix (LLM-generated, works on any Python codebase)
print("── STAGE 3: Apply fix (LLM-generated) ────────────────────")
fix = sdk.apply_fix()
print(f"✓ branch     : {fix.branch}")
print(f"✓ committed  : {fix.committed}")
print(f"✓ patch      : {fix.patch_path}\n")

# Stage 4 — Verify
print("── STAGE 4: Verify ────────────────────────────────────────")
verify = sdk.verify()
print(f"✓ tests      : {'PASS' if verify.tests_passed else 'FAIL'}")
print(f"✓ coverage   : {verify.coverage_percent}%")
print(f"✓ ruff       : {'PASS' if verify.ruff_clean else 'FAIL'}")
print(f"✓ report     : {verify.report_path}\n")

print("=" * 60)
print("Pipeline complete.")
