"""CLI entry point: load config, start both MCP servers, run one full game."""

import argparse
import asyncio
import json
import logging
import os

from dotenv import load_dotenv

import cop_thief.mcp.cop_server as cop_server
import cop_thief.mcp.thief_server as thief_server
from cop_thief.api_gatekeeper import ApiGatekeeper
from cop_thief.gmail.auth import GmailAuth
from cop_thief.gmail.report_builder import ReportBuilder
from cop_thief.gmail.sender import GmailSender
from cop_thief.gui.app import GuiApp
from cop_thief.mcp.tools import GameContext
from cop_thief.orchestrator.game_loop import GameLoop
from cop_thief.orchestrator.mcp_client import build_client
from cop_thief.sdk.game_engine.sub_game import SubGame
from cop_thief.sdk.q_table.advisor import QTableAdvisor
from cop_thief.shared.config import PROJECT_ROOT, load_config

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI flags for the game runner."""
    parser = argparse.ArgumentParser(description="Cop & Thief: dual AI agents via MCP")
    parser.add_argument(
        "--config", default="config.json",
        help="Config file under config/ (default: config.json)",
    )
    parser.add_argument(
        "--gui", action="store_true", help="Show the live GUI (Phase 5)"
    )
    parser.add_argument("--headless", action="store_true", help="Run with no UI")
    parser.add_argument("--case", default=None, help="Named experiment case (Phase 7)")
    return parser.parse_args(argv)


def _build_sub_game(config: dict) -> SubGame:
    """Create the shared SubGame instance from config values."""
    return SubGame(
        rows=config["grid"]["rows"], cols=config["grid"]["cols"],
        max_moves=config["game"]["max_moves"],
        max_barriers=config["game"]["max_barriers"],
        cop_vision_radius=config["vision"]["cop_vision_radius"],
        thief_vision_radius=config["vision"]["thief_vision_radius"],
        scoring=config["scoring"],
    )


async def _send_report(result, config: dict, gatekeeper: ApiGatekeeper) -> None:
    """Build and send the Gmail report; log (don't crash) on failure.

    A failed report send shouldn't hide a successful game run, so failures
    are logged rather than propagated.
    """
    report = ReportBuilder.build(result, config)
    gmail_auth = GmailAuth(
        config["gmail"]["credentials_file"], config["gmail"]["token_file"]
    )
    sender = GmailSender(gmail_auth, gatekeeper)
    try:
        await sender.send(report, config)
    except Exception as exc:
        logger.error("Failed to send Gmail report: %s", exc)


async def run_game(config: dict) -> dict:
    """Start both MCP servers and the orchestrator, then run one full game."""
    auth_token = os.environ.get("MCP_AUTH_TOKEN", "dev-token")
    sub_game = _build_sub_game(config)
    store: dict = {"cop": None, "thief": None}
    max_chars = config["communication"]["max_message_chars"]
    cop_server.set_context(GameContext(sub_game, "cop", store, max_chars, auth_token))
    thief_server.set_context(
        GameContext(sub_game, "thief", store, max_chars, auth_token)
    )

    cop_task = asyncio.create_task(cop_server.mcp.run_async(
        transport="streamable-http", host="127.0.0.1", port=config["mcp"]["cop_port"],
    ))
    thief_task = asyncio.create_task(thief_server.mcp.run_async(
        transport="streamable-http", host="127.0.0.1", port=config["mcp"]["thief_port"],
    ))
    await asyncio.sleep(0.5)  # let both servers finish binding before clients connect

    advisor = QTableAdvisor(
        config["q_table"]["enabled"], str(PROJECT_ROOT / "config" / "q_table.npy"),
        config["grid"]["rows"], config["grid"]["cols"],
    )
    gui = GuiApp(
        config,
        case_name=config.get("experiments", {}).get("name", "default"),
    )
    if config["gui"]["enabled"]:
        gui.run_in_background()
    try:
        gatekeeper = ApiGatekeeper(config["llm"], load_config("rate_limits.json"))
        cop_client = build_client("cop", config, auth_token=auth_token)
        thief_client = build_client("thief", config, auth_token=auth_token)
        loop = GameLoop(
            config, sub_game, cop_client, thief_client, gatekeeper, advisor=advisor
        )
        result = await loop.run(
            on_complete=lambda r: logger.info("Game finished: %s", r.totals),
            on_turn=gui.update,
        )
        if config.get("gmail", {}).get("enabled", True):
            await _send_report(result, config, gatekeeper)
        else:
            logger.info("Gmail disabled in config; skipping report email.")
        return result.to_dict()
    finally:
        gui.close()
        cop_task.cancel()
        thief_task.cancel()
        await asyncio.gather(cop_task, thief_task, return_exceptions=True)


def _save_result(result: dict, config: dict) -> None:
    """Write the game result JSON under results/<experiment_name>/."""
    name = config.get("experiments", {}).get("name")
    if not name:
        return
    out_dir = PROJECT_ROOT / "results" / name
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info("Saved result to %s", out_dir / "result.json")


def main(argv: list[str] | None = None) -> None:
    """CLI entry point: parse flags, load config, and run one full game."""
    load_dotenv()
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    if args.case:
        logger.warning("--case is not implemented yet (Phase 7); ignoring.")

    config = load_config(args.config)
    if args.gui:
        config["gui"]["enabled"] = True
    if args.headless:
        config["gui"]["enabled"] = False

    result = asyncio.run(run_game(config))
    _save_result(result, config)
    print(result)


if __name__ == "__main__":
    main()
