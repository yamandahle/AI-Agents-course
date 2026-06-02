"""Terminal menu and live-event display for the AI Debate System."""

from __future__ import annotations

from typing import Any

from menu_handlers import (
    _TOPIC,
    make_runner,
    print_verdict,
    truncate_display,
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
        print(f"\n{'=' * 40}")
        print(f"  ROUND {data['round']} of {data['total']}")
        print(f"{'=' * 40}")
    elif event == "pro_searching":
        _state["pro_searches"] += 1
        print("  [PRO] Searching web for evidence...")
    elif event == "pro_argument":
        print(wrap(f"PRO: {data['content']}"))
    elif event == "father_check" and not data.get("ok"):
        print(f"  [FATHER] Rule check failed: {data['check']}")
    elif event == "father_route":
        print(f"  [FATHER] Turn -> {data['to'].upper()}")
    elif event == "con_searching":
        _state["con_searches"] += 1
        print("  [CON] Searching web for evidence...")
    elif event == "con_argument":
        print(wrap(f"CON: {data['content']}"))
    elif event == "father_coaching":
        print(f"  [COACH -> {data['agent'].upper()}] {data['message']}")
    elif event == "round_result":
        pw, cw = data["pro_rounds_won"], data["con_rounds_won"]
        print(
            f"  [ROUND {data['round']}] Winner: {data['winner'].upper()} "
            f"({data['reason']})  |  Running tally PRO {pw} - CON {cw}"
        )
        print(f"  {'-' * 38}")
    elif event == "intervention":
        print("  !! [FATHER] Intervention: stay in role — do not agree.")
    elif event == "context_update":
        _state["round_tokens"].append(data["total"])
        print(f"  [Context] ~{data['total']} tokens in history")
    elif event == "context_compact":
        saved = data.get("saved", 0)
        print(f"  [FATHER] History compacted (~{saved} tokens saved).")
        summary = data.get("summary", "")
        if summary and summary != "(summary unavailable)":
            short = truncate_display(summary)
            print(wrap(f"Summary (short): {short}"))
            print("  (Full summary is in logs/ — menu option 4)")
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
