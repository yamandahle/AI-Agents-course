"""Terminal menu handlers and live display for the AI Debate System."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from debate.sdk.runner import DebateRunner

_TOPIC = "Is remote work better than working from the office?"
_CONFIG_DIR = "config"
_runner = DebateRunner(config_dir=_CONFIG_DIR)
_state: dict[str, Any] = {"pro_searches": 0, "con_searches": 0, "round_tokens": []}


def show_header() -> None:
    print("\n========================================")
    print("   AI DEBATE SYSTEM — HW2")
    print("   Remote Work vs Office Work")
    print("========================================")
    print("1. Start new debate")
    print("2. View last debate transcript")
    print("3. View cost report")
    print("4. View logs")
    print("5. Exit")
    print("========================================")


def _on_event(event: str, data: dict[str, Any]) -> None:
    """Live callback fired by FatherAgent during the debate."""
    if event == "round_start":
        print(f"\n=== PING {data['round']}/{data['total']} ===")
    elif event == "pro_searching":
        _state["pro_searches"] += 1
        print("  \U0001f50d PRO searching web for evidence...")
    elif event == "pro_argument":
        print(f"  PRO: {data['content'][:110]}...")
    elif event == "father_validate":
        print("  FATHER: validating JSON... ✓")
    elif event == "father_check":
        result_str = "CLEAR" if data["ok"] else "⚠ INTERVENING"
        print(f"  FATHER: checking {data['check']}... {result_str}")
    elif event == "father_route":
        print(f"  FATHER: routing to {data['to'].upper()}...")
    elif event == "con_searching":
        _state["con_searches"] += 1
        print("  \U0001f50d CON searching web for evidence...")
    elif event == "con_argument":
        print(f"  CON: {data['content'][:110]}...")
    elif event == "intervention":
        print("  ⚠ FATHER INTERVENES: Stay in your role. You must disagree.")
    elif event == "context_update":
        _state["round_tokens"].append(data["total"])
        print(f"  [Context: ~{data['total']} tokens used]")
    elif event == "context_compact":
        print("  ⚙ FATHER: Summarizing history to save tokens...")
        print(f"  [Context compacted: saved ~{data['saved']} tokens]")
    elif event == "verdict":
        _print_verdict(data["result"])


def _print_verdict(result: Any) -> None:
    print("\n======= FINAL VERDICT =======")
    winner_pct = result.pro_score if result.winner == "pro" else result.con_score
    loser_pct = 100.0 - winner_pct
    searches = _state["pro_searches"] + _state["con_searches"]
    print(f"WINNER: {result.winner.upper()} — Score: {winner_pct:.0f}% vs {loser_pct:.0f}%")
    print(f"Total interventions:  {result.total_interventions}")
    print(f"Total tokens used:    {result.context_tokens}")
    print(f"Total web searches:   {searches}")
    print("==============================")


def handle_start_debate() -> None:
    setup = json.loads(Path(f"{_CONFIG_DIR}/setup.json").read_text(encoding="utf-8"))
    skills = setup["debate"].get("skills_path", "src/debate/skills/")
    print("\nStarting debate... Topic: Remote Work vs Office")
    print(f"PRO agent loading skill:    {skills}pro_skill.md")
    print(f"CON agent loading skill:    {skills}con_skill.md")
    print(f"FATHER loading skill:       {skills}father_skill.md")
    _state["pro_searches"] = 0
    _state["con_searches"] = 0
    _state["round_tokens"] = []
    _runner.run(_TOPIC, on_event=_on_event)


def handle_view_transcript() -> None:
    result = _runner.get_last_result()
    if result is None:
        print("\nNo debate has been run yet. Use option 1 first.")
        return
    print(f"\n--- TRANSCRIPT ({result.rounds_completed} rounds) ---")
    for msg in result.transcript:
        print(f"\n[Round {msg.round}] {msg.sender.upper()}:")
        print(f"  {msg.content[:250]}")
    _print_verdict(result)


def handle_cost_report() -> None:
    entries = _runner.get_cost_breakdown()
    if not entries:
        print("\nNo cost data yet. Run a debate first (option 1).")
        return
    total_in = sum(e["input_tokens"] for e in entries)
    total_out = sum(e["output_tokens"] for e in entries)
    total_cost = sum(e["cost_usd"] for e in entries)
    hdr = f"{'Agent':<8} {'Model':<18} {'Input':>8} {'Output':>8} {'Cost($)':>10}"
    print(f"\n{hdr}")
    print("-" * len(hdr))
    for e in entries:
        ag = e.get("agent", "?")
        print(f"{ag:<8} {e['model']:<18} {e['input_tokens']:>8} {e['output_tokens']:>8} {e['cost_usd']:>10.4f}")
    print("-" * len(hdr))
    print(f"{'TOTAL':<27} {total_in:>8} {total_out:>8} {total_cost:>10.4f}")
    if _state["round_tokens"]:
        print("\nContext window growth:")
        for i, tokens in enumerate(_state["round_tokens"], 1):
            print(f"  Ping {i:>2}: ~{tokens} tokens")


def handle_view_logs() -> None:
    entries = _runner.get_recent_logs(20)
    if not entries:
        print("\nNo log entries yet. Run a debate first (option 1).")
        return
    print("\n--- LAST 20 LOG ENTRIES ---")
    print(f"{'Timestamp':<20} {'Agent':>8} {'Event':<22} Data")
    print("-" * 75)
    for e in entries:
        ts = e.get("timestamp", "")[:19].replace("T", " ")
        print(f"{ts:<20} {e.get('agent', '?'):>8} {e.get('event', '?'):<22} {e.get('data', {})}")
