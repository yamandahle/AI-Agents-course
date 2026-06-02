"""Handler functions for the AI Debate System menu."""

from __future__ import annotations

import io
import textwrap
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

from debate.sdk.runner import DebateRunner
from debate.shared.config import ConfigManager

_WIDTH = 80
_CONFIG_DIR = "config"
_TOPIC = "Is remote work better than working from the office?"
_SUMMARY_DISPLAY_MAX = 400
_LOG_DATA_MAX = 72


def wrap(text: str, indent: str = "  ") -> str:
    return textwrap.fill(text, width=_WIDTH, initial_indent=indent, subsequent_indent=indent)


def truncate_display(text: str, max_chars: int = _SUMMARY_DISPLAY_MAX) -> str:
    """Shorten long text for terminal / screenshots (full text stays in logs)."""
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    cut = cleaned[: max_chars - 3].rsplit(" ", 1)[0]
    return f"{cut}..."


def format_log_data(data: object) -> str:
    """Compact one-line summary for log viewer (avoid huge dict dumps)."""
    if not isinstance(data, dict):
        return str(data)[:_LOG_DATA_MAX]
    parts: list[str] = []
    for key, value in data.items():
        if key == "summary" and isinstance(value, str):
            value = truncate_display(value, 60)
        text = f"{key}={value}"
        if len(text) > 36:
            text = f"{key}=..."
        parts.append(text)
    line = " ".join(parts)
    return line if len(line) <= _LOG_DATA_MAX else line[: _LOG_DATA_MAX - 3] + "..."


def make_runner() -> DebateRunner:
    return DebateRunner(config_dir=_CONFIG_DIR)


def export_debate_to_file(
    result: Any,
    cost_entries: list[dict[str, Any]],
    path: str = "results/sample_debate.txt",
) -> Path:
    """Write transcript + verdict + cost summary for README / GitHub."""
    lines: list[str] = [
        "AI DEBATE SYSTEM — Saved run output",
        f"Topic: {_TOPIC}",
        f"Rounds completed: {result.rounds_completed}",
        "",
        "=" * 60,
        "DEBATE TRANSCRIPT",
        "=" * 60,
    ]
    debate_round = 0
    for msg in result.transcript:
        if msg.sender == "pro":
            debate_round += 1
            lines.extend(["", f"--- ROUND {debate_round} of {result.rounds_completed} ---", ""])
        lines.append(wrap(f"{msg.sender.upper()}: {msg.content}"))
        lines.append(f"  ({msg.word_count} words)")

    lines.extend(["", "=" * 60, "FINAL VERDICT", "=" * 60])
    buf = io.StringIO()
    with redirect_stdout(buf):
        print_verdict(result)
    lines.extend(buf.getvalue().splitlines())

    if cost_entries:
        total_in = sum(e["input_tokens"] for e in cost_entries)
        total_out = sum(e["output_tokens"] for e in cost_entries)
        total_cost = sum(e["cost_usd"] for e in cost_entries)
        lines.extend(
            [
                "",
                "=" * 60,
                "COST SUMMARY (Gatekeeper)",
                "=" * 60,
                f"API calls:     {len(cost_entries)}",
                f"Input tokens:  {total_in}",
                f"Output tokens: {total_out}",
                f"Total cost:    ${total_cost:.4f}",
            ]
        )

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


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
    setup = ConfigManager(_CONFIG_DIR).setup
    skills = setup["debate"].get("skills_path", "src/debate/skills/")
    rounds = setup["debate"].get("rounds", 10)
    print(f"\nStarting debate ({rounds} rounds)...")
    print(f"Topic: {_TOPIC}")
    print(f"Skills: {skills}pro_skill.md, con_skill.md, father_skill.md")
    print("Live output below — scroll for verdict, or use menu 2–4 after.\n")
    state["pro_searches"] = 0
    state["con_searches"] = 0
    state["round_tokens"] = []
    runner.run(_TOPIC, on_event=on_event)
    result = runner.get_last_result()
    if result is not None:
        out = export_debate_to_file(result, runner.get_cost_breakdown())
        print(f"\n[SAVED] Full transcript + verdict -> {out}")


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
    print("\n--- LAST 20 LOG ENTRIES (most recent session) ---")
    print(f"{'Timestamp':<20} {'Agent':>8} {'Event':<18} Details")
    print("-" * 80)
    for e in entries:
        ts = e.get("timestamp", "")[:19].replace("T", " ")
        print(
            f"{ts:<20} {e.get('agent', '?'):>8} {e.get('event', '?'):<18} "
            f"{format_log_data(e.get('data', {}))}"
        )
