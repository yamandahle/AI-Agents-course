"""Generate results/sample_debate.txt from a mocked 10-round debate (no API keys)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from unittest.mock import MagicMock  # noqa: E402

from debate.agents.con_agent import ConAgent  # noqa: E402
from debate.agents.father_agent import FatherAgent  # noqa: E402
from debate.agents.pro_agent import ProAgent  # noqa: E402
from debate.shared.gatekeeper import ApiGatekeeper  # noqa: E402
from debate.shared.logger import DebateLogger  # noqa: E402
from menu_handlers import print_verdict, wrap  # noqa: E402

_TOPIC = "Is remote work better than working from the office?"

_LLM_RESPONSES = [
    "Remote work eliminates daily commuting and open-plan interruptions. Stanford research "
    "reports roughly 13% higher productivity for structured remote setups, with lower "
    "turnover when autonomy is paired with clear goals.",
    "Office work preserves spontaneous collaboration and mentorship. Microsoft's studies show "
    "remote networks become siloed; junior staff lose informal coaching that only happens "
    "in person.",
    "PRO rebuttal round 2: hybrid policies fail when they are vague. Firms with documented "
    "async norms outperform ad-hoc remote teams on delivery metrics.",
    "CON rebuttal round 2: coordination cost rises when meetings span time zones. Evening "
    "calls increase and decisions slow without shared physical context.",
    "PRO round 3: global hiring widens talent pools; office-only hiring cannot access "
    "specialists in other regions without relocation cost.",
    "CON round 3: culture erodes when teams never share space; trust and accountability "
    "suffer when conflict is handled only over chat.",
    "PRO round 4: real-estate savings fund better tools and training; the office tax is "
    "not free productivity.",
    "CON round 4: innovation often starts at whiteboards; scheduled video calls rarely "
    "replace hallway problem-solving.",
    "PRO round 5: carbon and time costs of commuting are measurable; remote reduces both "
    "without lowering output when managed well.",
    "CON round 5: presenteeism in offices rewards visibility over outcomes; still, remote "
    "requires stronger managers — many firms are not ready.",
    "PRO round 6: Fortune 100 best employers overwhelmingly offer flexible work because "
    "retention and satisfaction data support it.",
    "CON round 6: forced return-to-office mandates triggered attrition at major tech firms; "
    "that proves policy matters more than location alone.",
    "PRO round 7: async documentation creates institutional memory; meetings evaporate.",
    "CON round 7: duplication and misalignment rise when channels multiply without norms.",
    "PRO round 8: BLS sector analyses show no uniform remote productivity collapse when "
    "controls are applied carefully.",
    "CON round 8: self-selection and concurrent tech investment confound aggregate stats.",
    "PRO round 9: employee well-being and accessibility improve when commute barriers drop.",
    "CON round 9: isolation harms mental health for many roles; offices provide belonging.",
    "PRO round 10 closing: on balance, designed remote work wins on measurable output, "
    "cost, and talent access.",
    "CON round 10 closing: on balance, office-centric work wins on culture, coaching, and "
    "fast coordination for complex teams.",
]

_LOG_CFG = {"log_dir": "logs", "max_files": 3, "max_lines_per_file": 100, "level": "INFO"}
_RATE_LIMITS = {
    "anthropic": {
        "requests_per_minute": 1000,
        "max_tokens_per_call": 500,
        "daily_budget_usd": 100.0,
        "retry_attempts": 1,
        "retry_backoff_seconds": [0],
        "model_costs": {"claude-haiku-4-5": {"input_per_million": 0.80, "output_per_million": 4.00}},
    },
    "tavily": {"max_results_per_search": 3},
}


class _Cfg:
    setup = {
        "debate": {
            "model": "claude-haiku-4-5",
            "timeout_seconds": 10.0,
            "word_limit": 150,
            "rounds": 10,
            "max_restarts": 3,
            "watchdog_interval_seconds": 2,
            "context_summarize_after_round": 3,
            "token_estimate_multiplier": 1.3,
            "skills_path": "src/debate/skills/",
        }
    }
    rate_limits = _RATE_LIMITS


def _mock_client() -> MagicMock:
    count = [0]

    def _create(**_: object) -> MagicMock:
        text = _LLM_RESPONSES[count[0] % len(_LLM_RESPONSES)]
        count[0] += 1
        resp = MagicMock()
        resp.content = [MagicMock(text=text)]
        resp.usage.input_tokens = 120
        resp.usage.output_tokens = max(40, len(text.split()))
        return resp

    client = MagicMock()
    client.messages.create.side_effect = _create
    return client


def _capture_verdict(result: object, lines: list[str]) -> None:
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        print_verdict(result)
    lines.extend(buf.getvalue().splitlines())


def main() -> None:
    client = _mock_client()
    logger = DebateLogger(_LOG_CFG, log_dir=ROOT / "logs" / "_sample_gen")
    gk = ApiGatekeeper(_RATE_LIMITS, client, logger)
    cfg = _Cfg()
    pro = ProAgent(role="pro", config_manager=cfg, gatekeeper=gk, logger=logger, tavily=None)
    con = ConAgent(role="con", config_manager=cfg, gatekeeper=gk, logger=logger, tavily=None)
    father = FatherAgent(role="father", config_manager=cfg, gatekeeper=gk, logger=logger)

    result = father.run_debate(_TOPIC, pro, con)

    lines: list[str] = [
        "AI DEBATE SYSTEM — Sample Run (mocked LLM, structure matches production)",
        f"Topic: {_TOPIC}",
        f"Rounds completed: {result.rounds_completed}",
        "Generated by: uv run python scripts/generate_sample_debate.py",
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
        label = msg.sender.upper()
        lines.append(wrap(f"{label}: {msg.content}"))
        lines.append(f"  ({msg.word_count} words)")

    lines.extend(["", "=" * 60, "FINAL VERDICT", "=" * 60])
    _capture_verdict(result, lines)

    entries = gk.get_cost_table()
    total_in = sum(e["input_tokens"] for e in entries)
    total_out = sum(e["output_tokens"] for e in entries)
    total_cost = sum(e["cost_usd"] for e in entries)
    lines.extend(
        [
            "",
            "=" * 60,
            "COST SUMMARY (this mocked run)",
            "=" * 60,
            f"API calls: {len(entries)}",
            f"Input tokens:  {total_in}",
            f"Output tokens: {total_out}",
            f"Total cost:    ${total_cost:.4f}",
            "",
            "Note: A real 10-round run with live APIs typically costs ~$0.25 (Haiku).",
            "See README Cost Analysis for a measured production log.",
        ]
    )

    out_path = ROOT / "results" / "sample_debate.txt"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
