"""Handler functions for the AI Debate System menu."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

from debate.sdk.runner import DebateRunner

_WIDTH = 80
_CONFIG_DIR = "config"
_TOPIC = "Is remote work better than working from the office?"


def wrap(text: str, indent: str = "  ") -> str:
    return textwrap.fill(text, width=_WIDTH, initial_indent=indent, subsequent_indent=indent)


def make_runner() -> DebateRunner:
    return DebateRunner(config_dir=_CONFIG_DIR)


def print_verdict(result: Any) -> None:
    print("\n======= FINAL VERDICT =======")
    winner_pct = result.pro_score if result.winner == "pro" else result.con_score
    print(f"WINNER: {result.winner.upper()} - Score: {winner_pct:.0f}% vs {100.0 - winner_pct:.0f}%")
    print(f"Role violations fixed: {result.total_interventions}")
    print(f"History compactions:   {getattr(result, 'total_compactions', 0)}")
    print(f"Total tokens used:     {result.context_tokens}")
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
        print(f"{'Raw score (display only)':<26} {pb.total:>{col}.1f} {cb.total:>{col}.1f}")
        print(f"{'Unique concepts introduced':<26} {pb.concepts_introduced:>{col}} {cb.concepts_introduced:>{col}}")
        print(f"{'Self-contradictions found':<26} {pb.contradictions_found:>{col}} {cb.contradictions_found:>{col}}")
    reasoning = getattr(result, "verdict_reasoning", "")
    if reasoning:
        print(f"\nFATHER'S REASONING:\n{wrap(reasoning)}")
    print("==============================")


def handle_start_debate(runner: DebateRunner, state: dict[str, Any], on_event: Any) -> None:
    setup = json.loads(Path(f"{_CONFIG_DIR}/setup.json").read_text(encoding="utf-8"))
    skills = setup["debate"].get("skills_path", "src/debate/skills/")
    print(f"\nStarting debate... Topic: {_TOPIC}")
    print(f"PRO agent loading skill:    {skills}pro_skill.md")
    print(f"CON agent loading skill:    {skills}con_skill.md")
    print(f"FATHER loading skill:       {skills}father_skill.md")
    state["pro_searches"] = 0
    state["con_searches"] = 0
    state["round_tokens"] = []
    runner.run(_TOPIC, on_event=on_event)


def handle_view_transcript(runner: DebateRunner) -> None:
    result = runner.get_last_result()
    if result is None:
        print("\nNo debate has been run yet. Use option 1 first.")
        return
    print(f"\n--- TRANSCRIPT ({result.rounds_completed} rounds) ---")
    for msg in result.transcript:
        print(f"\n[Round {msg.round}] {msg.sender.upper()}:")
        print(wrap(msg.content))
    print_verdict(result)


def handle_cost_report(runner: DebateRunner, state: dict[str, Any]) -> None:
    entries = runner.get_cost_breakdown()
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
        print(f"{e.get('agent','?'):<8} {e['model']:<18} {e['input_tokens']:>8} {e['output_tokens']:>8} {e['cost_usd']:>10.4f}")
    print("-" * len(hdr))
    print(f"{'TOTAL':<27} {total_in:>8} {total_out:>8} {total_cost:>10.4f}")
    if state["round_tokens"]:
        print("\nContext window growth:")
        for i, tokens in enumerate(state["round_tokens"], 1):
            print(f"  Ping {i:>2}: ~{tokens} tokens")


def handle_view_logs(runner: DebateRunner) -> None:
    entries = runner.get_recent_logs(20)
    if not entries:
        print("\nNo log entries yet. Run a debate first (option 1).")
        return
    print("\n--- LAST 20 LOG ENTRIES ---")
    print(f"{'Timestamp':<20} {'Agent':>8} {'Event':<22} Data")
    print("-" * 75)
    for e in entries:
        ts = e.get("timestamp", "")[:19].replace("T", " ")
        print(f"{ts:<20} {e.get('agent', '?'):>8} {e.get('event', '?'):<22} {e.get('data', {})}")
