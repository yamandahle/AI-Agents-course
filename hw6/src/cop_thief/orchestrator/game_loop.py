"""Drives a full game: sub-games run via MCP tool calls and LLM decisions."""

import logging
from contextlib import AsyncExitStack
from typing import Callable

from fastmcp.exceptions import ToolError

from cop_thief.gui.game_state import GameState
from cop_thief.orchestrator.action_parser import parse_response
from cop_thief.orchestrator.fallback import (
    get_q_hint,
    random_starts,
    random_valid_action,
)
from cop_thief.orchestrator.live_state import build_game_state
from cop_thief.orchestrator.prompt_builder import build_system_prompt, build_user_prompt
from cop_thief.orchestrator.turn_io import call_llm, dispatch_action
from cop_thief.sdk.game_engine.game_session import GameResult, TooManyCrashesError
from cop_thief.sdk.game_engine.sub_game import SubGame, SubGameResult
from cop_thief.sdk.q_table.advisor import QTableAdvisor

logger = logging.getLogger(__name__)


class GameLoop:
    """Runs config['game']['num_games'] sub-games via MCP + LLM, with retries."""

    def __init__(
        self, config: dict, sub_game: SubGame, cop_client, thief_client, gatekeeper,
        advisor: QTableAdvisor | None = None,
    ):
        self._config = config
        self._sub_game = sub_game
        self._clients = {"cop": cop_client, "thief": thief_client}
        self._gatekeeper = gatekeeper
        self._max_retries = config["llm"]["max_retries"]
        self._advisor = advisor
        self._totals = {"cop": 0, "thief": 0}
        self._last_messages = {"cop": "", "thief": ""}

    async def run(
        self,
        on_complete: Callable[[GameResult], None] | None = None,
        on_turn: Callable[[GameState], None] | None = None,
    ) -> GameResult:
        """Run all valid sub-games and return the aggregated GameResult.

        Connects both agents' MCP clients once at the start and closes them once
        at the end (even on crash) -- a single connection is reused for every
        tool call across the whole game instead of reconnecting per call.
        """
        async with AsyncExitStack() as stack:
            for client in self._clients.values():
                await client.connect()
                stack.push_async_callback(client.close)

            num_games = self._config["game"]["num_games"]
            max_attempts = num_games * 5
            results: list[SubGameResult] = []
            valid = 0
            while valid < num_games and len(results) < max_attempts:
                result = await self._run_one_sub_game(len(results) + 1, on_turn)
                results.append(result)
                if not result.crashed:
                    valid += 1
                    self._totals["cop"] += result.cop_score
                    self._totals["thief"] += result.thief_score
            if valid < num_games:
                raise TooManyCrashesError(
                    f"Only {valid}/{num_games} valid sub-games "
                    f"after {len(results)} attempts."
                )
            valid_results = [r for r in results if not r.crashed]
            game_result = GameResult(sub_games=valid_results, totals=dict(self._totals))
            if on_complete:
                on_complete(game_result)
            return game_result

    async def _run_one_sub_game(
        self, sub_game_number: int, on_turn: Callable[[GameState], None] | None
    ) -> SubGameResult:
        """Run one sub-game to completion; return a crashed result on any error."""
        cop_start, thief_start = random_starts(self._config)
        self._sub_game.reset(cop_start, thief_start)
        try:
            while not self._sub_game.is_terminal():
                await self._take_turn("thief", sub_game_number, on_turn)
                await self._take_turn("cop", sub_game_number, on_turn)
            return self._sub_game.get_result()
        except Exception as exc:
            logger.warning("sub-game crashed: %s: %s", type(exc).__name__, exc)
            return SubGameResult(
                winner="none", cop_score=0, thief_score=0,
                moves_played=self._sub_game.move_counter,
                barriers_placed=0, crashed=True,
            )

    async def _take_turn(
        self,
        agent_id: str,
        sub_game_number: int,
        on_turn: Callable[[GameState], None] | None,
    ) -> None:
        """Observe, decide, message, and act for one agent's turn — all via MCP.

        Retries cover both unparseable responses and server-rejected actions
        (e.g. out of bounds); the final fallback is checked against the real
        board so it can never itself be rejected.
        """
        client = self._clients[agent_id]
        obs = await client.get_observation()
        system_prompt = build_system_prompt(agent_id, self._config)
        q_hint = get_q_hint(self._sub_game, self._advisor, agent_id)
        user_prompt = build_user_prompt(obs, agent_id, self._config, q_hint=q_hint)
        max_chars = self._config["communication"]["max_message_chars"]

        model = self._config["llm"]["model"]
        for attempt in range(1, self._max_retries + 1):
            text = await call_llm(self._gatekeeper, model, system_prompt, user_prompt)
            message, action = parse_response(text)
            if action is None:
                logger.warning(
                    "Unparseable LLM response for %s (attempt %d/%d): %r",
                    agent_id, attempt, self._max_retries, text,
                )
                continue
            try:
                await dispatch_action(client, action, message[:max_chars])
                self._after_turn(
                    agent_id, message[:max_chars], sub_game_number, on_turn
                )
                return
            except ToolError as exc:
                logger.warning(
                    "Rejected action for %s (attempt %d/%d): %s",
                    agent_id, attempt, self._max_retries, exc,
                )

        action = random_valid_action(self._sub_game, agent_id)
        logger.warning(
            "All retries failed for %s; using fallback action %s", agent_id, action
        )
        await dispatch_action(client, action, "")
        self._after_turn(agent_id, "", sub_game_number, on_turn)

    def _after_turn(
        self,
        agent_id: str,
        message: str,
        sub_game_number: int,
        on_turn: Callable[[GameState], None] | None,
    ) -> None:
        """Record the sent message and push a GameState snapshot to the GUI."""
        self._last_messages[agent_id] = message
        if on_turn is None:
            return
        on_turn(build_game_state(
            self._sub_game, sub_game_number, self._totals, self._last_messages, agent_id
        ))
