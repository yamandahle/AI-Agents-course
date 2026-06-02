"""Entry point for the AI Debate System terminal interface."""

from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from menu import (
    handle_cost_report,
    handle_start_debate,
    handle_view_logs,
    handle_view_transcript,
    show_header,
)


def main() -> None:
    handlers = {
        "1": handle_start_debate,
        "2": handle_view_transcript,
        "3": handle_cost_report,
        "4": handle_view_logs,
    }
    while True:
        show_header()
        choice = input("Select option (1-5): ").strip()
        if choice == "5":
            print("\nGoodbye!")
            break
        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            print("\nInvalid option. Please enter 1-5.")
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
