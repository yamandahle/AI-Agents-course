"""Terminal menu handlers and live display for the AI Debate System."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

from debate.sdk.runner import DebateRunner

_TOPIC = "Is remote work better than working from the office?"
_WIDTH = 80  # wrap width for argument text


def _wrap(text: str, indent: str = "  ") -> str:
    """Wrap text to terminal width with a consistent left indent."""
    return textwrap.fill(text, width=_WIDTH, initial_indent=indent, subsequent_indent=indent)
_CONFIG_DIR = "config"
_runner = DebateRunner(config_dir=_CONFIG_DIR)
_state: dict[str, Any] = {"pro_searches": 0, "con_searches": 0, "round_tokens": []}


def show_header() -> None:
    print("\n========================================")
    print("   AI DEBATE SYSTEM - HW2")
    print(f"   {_TOPIC}")
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
        print("  [SEARCH] PRO searching web for evidence...")
    elif event == "pro_argument":
        print(_wrap(f"PRO: {data['content']}"))
    elif event == "father_validate":
        print("  FATHER: validating JSON... OK")
    elif event == "father_check":
        result_str = "CLEAR" if data["ok"] else "VIOLATION FOUND"
        print(f"  FATHER: checking {data['check']}... {result_str}")
    elif event == "father_route":
        print(f"  FATHER: routing to {data['to'].upper()}...")
    elif event == "con_searching":
        _state["con_searches"] += 1
        print("  [SEARCH] CON searching web for evidence...")
    elif event == "con_argument":
        print(_wrap(f"CON: {data['content']}"))
    elif event == "father_coaching":
        agent = data["agent"].upper()
        print(f"  [COACH -> {agent}] {data['message']}")
    elif event == "round_result":
        rnd = data["round"]
        w = data["winner"].upper()
        reason = data["reason"]
        pw = data["pro_rounds_won"]
        cw = data["con_rounds_won"]
        print(f"  FATHER: Round {rnd} -> {w} ({reason})  |  Score: PRO {pw} - CON {cw}")
    elif event == "intervention":
        print("  !! FATHER INTERVENES: Stay in your role. You must disagree.")
    elif event == "context_update":
        _state["round_tokens"].append(data["total"])
        print(f"  [Context: ~{data['total']} tokens used]")
    elif event == "context_compact":
        print("  [COMPACT] FATHER: Summarizing history to save tokens...")
        print(f"  [Context compacted: saved ~{data['saved']} tokens]")
        summary = data.get("summary", "")
        if summary and summary != "(summary unavailable)":
            print(_wrap(f"SUMMARY: {summary}"))
    elif event == "verdict":
        _print_verdict(data["result"])


def _print_verdict(result: Any) -> None:
    print("\n======= FINAL VERDICT =======")
    winner_pct = result.pro_score if result.winner == "pro" else result.con_score
    loser_pct = 100.0 - winner_pct
    searches = _state["pro_searches"] + _state["con_searches"]
    compactions = getattr(result, "total_compactions", 0)
    print(f"WINNER: {result.winner.upper()} - Score: {winner_pct:.0f}% vs {loser_pct:.0f}%")
    print(f"Role violations fixed: {result.total_interventions}")
    print(f"History compactions:   {compactions}")
    print(f"Total tokens used:     {result.context_tokens}")
    print(f"Total web searches:    {searches}")

    pb, cb = result.pro_breakdown, result.con_breakdown
    if pb and cb:
        print("\n--- HOW THE FATHER DECIDED ---")
        col = 16
        print(f"{'Category':<26} {'PRO':>{col}} {'CON':>{col}}")
        print("-" * (26 + col * 2 + 2))
        print(f"{'Argument strength':<26} {pb.strength:>{col}.1f} {cb.strength:>{col}.1f}")
        print(f"{'Evidence quality':<26} {pb.evidence:>{col}.1f} {cb.evidence:>{col}.1f}")
        print(f"{'Persuasiveness':<26} {pb.persuasion:>{col}.1f} {cb.persuasion:>{col}.1f}")
        print(f"{'New concepts  (+2 each)':<26} {pb.concept_bonus:>{col}.1f} {cb.concept_bonus:>{col}.1f}")
        print(f"{'Contradictions (-2 each)':<26} {-pb.contradiction_penalty:>{col}.1f} {-cb.contradiction_penalty:>{col}.1f}")
        print("-" * (26 + col * 2 + 2))
        print(f"{'Raw score':<26} {pb.total:>{col}.1f} {cb.total:>{col}.1f}")
        print(f"{'Unique concepts introduced':<26} {pb.concepts_introduced:>{col}} {cb.concepts_introduced:>{col}}")
        print(f"{'Self-contradictions found':<26} {pb.contradictions_found:>{col}} {cb.contradictions_found:>{col}}")
    print("==============================")


def handle_start_debate() -> None:
    setup = json.loads(Path(f"{_CONFIG_DIR}/setup.json").read_text(encoding="utf-8"))
    skills = setup["debate"].get("skills_path", "src/debate/skills/")
    print(f"\nStarting debate... Topic: {_TOPIC}")
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
        print(_wrap(msg.content))
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
