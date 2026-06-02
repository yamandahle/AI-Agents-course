"""Terminal menu and live-event display for the AI Debate System."""

from __future__ import annotations

from typing import Any

from menu_handlers import (
    _TOPIC,
    make_runner,
    print_verdict,
    wrap,
)
from menu_handlers import (
    handle_cost_report as _cost_impl,
)
from menu_handlers import (
    handle_start_debate as _start_impl,
)
from menu_handlers import (
    handle_view_logs as _logs_impl,
)
from menu_handlers import (
    handle_view_transcript as _transcript_impl,
)

_runner = make_runner()
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
    if event == "round_start":
        print(f"\n=== PING {data['round']}/{data['total']} ===")
    elif event == "pro_searching":
        _state["pro_searches"] += 1
        print("  [SEARCH] PRO searching web for evidence...")
    elif event == "pro_argument":
        print(wrap(f"PRO: {data['content']}"))
    elif event == "father_validate":
        print("  FATHER: validating JSON... OK")
    elif event == "father_check":
        print(f"  FATHER: checking {data['check']}... {'CLEAR' if data['ok'] else 'VIOLATION FOUND'}")
    elif event == "father_route":
        print(f"  FATHER: routing to {data['to'].upper()}...")
    elif event == "con_searching":
        _state["con_searches"] += 1
        print("  [SEARCH] CON searching web for evidence...")
    elif event == "con_argument":
        print(wrap(f"CON: {data['content']}"))
    elif event == "father_coaching":
        print(f"  [COACH -> {data['agent'].upper()}] {data['message']}")
    elif event == "round_result":
        pw, cw = data["pro_rounds_won"], data["con_rounds_won"]
        print(f"  FATHER: Round {data['round']} -> {data['winner'].upper()} ({data['reason']})  |  Score: PRO {pw} - CON {cw}")
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
            print(wrap(f"SUMMARY: {summary}"))
    elif event == "verdict":
        searches = _state["pro_searches"] + _state["con_searches"]
        print(f"Total web searches:    {searches}")
        print_verdict(data["result"])


def handle_start_debate() -> None:
    _start_impl(_runner, _state, _on_event)


def handle_view_transcript() -> None:
    _transcript_impl(_runner)


def handle_cost_report() -> None:
    _cost_impl(_runner, _state)


def handle_view_logs() -> None:
    _logs_impl(_runner)
