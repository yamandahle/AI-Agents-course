"""Drives a full game: sub-games run via MCP tool calls and LLM decisions."""

import logging
import random
from typing import Callable

from fastmcp.exceptions import ToolError

from cop_thief.orchestrator.action_parser import parse_response
from cop_thief.orchestrator.prompt_builder import build_system_prompt, build_user_prompt
from cop_thief.sdk.game_engine.board import Action, Direction
from cop_thief.sdk.game_engine.game_session import GameResult, TooManyCrashesError
from cop_thief.sdk.game_engine.sub_game import SubGame, SubGameResult

logger = logging.getLogger(__name__)


class GameLoop:
    """Runs config['game']['num_games'] sub-games via MCP + LLM, with retries."""

    def __init__(
        self, config: dict, sub_game: SubGame, cop_client, thief_client, gatekeeper
    ):
        self._config = config
        self._sub_game = sub_game
        self._clients = {"cop": cop_client, "thief": thief_client}
        self._gatekeeper = gatekeeper
        self._max_retries = config["llm"]["max_retries"]

    async def run(
        self, on_complete: Callable[[GameResult], None] | None = None
    ) -> GameResult:
        """Run all valid sub-games and return the aggregated GameResult."""
        num_games = self._config["game"]["num_games"]
        max_attempts = num_games * 5
        results: list[SubGameResult] = []
        valid = 0
        while valid < num_games and len(results) < max_attempts:
            result = await self._run_one_sub_game()
            results.append(result)
            if not result.crashed:
                valid += 1
        if valid < num_games:
            raise TooManyCrashesError(
                f"Only {valid}/{num_games} valid sub-games "
                f"after {len(results)} attempts."
            )
        valid_results = [r for r in results if not r.crashed]
        totals = {
            "cop": sum(r.cop_score for r in valid_results),
            "thief": sum(r.thief_score for r in valid_results),
        }
        game_result = GameResult(sub_games=valid_results, totals=totals)
        if on_complete:
            on_complete(game_result)
        return game_result

    async def _run_one_sub_game(self) -> SubGameResult:
        """Run one sub-game to completion; return a crashed result on any error."""
        cop_start, thief_start = self._random_starts()
        self._sub_game.reset(cop_start, thief_start)
        try:
            while not self._sub_game.is_terminal():
                await self._take_turn("thief")
                await self._take_turn("cop")
            return self._sub_game.get_result()
        except Exception as exc:
            logger.warning("sub-game crashed: %s: %s", type(exc).__name__, exc)
            return SubGameResult(
                winner="none", cop_score=0, thief_score=0,
                moves_played=self._sub_game.move_counter,
                barriers_placed=0, crashed=True,
            )

    async def _take_turn(self, agent_id: str) -> None:
        """Observe, decide, message, and act for one agent's turn — all via MCP.

        Retries cover both an unparseable LLM response and a syntactically
        valid action later rejected by the server (e.g. out of bounds) —
        both are "the LLM didn't produce a usable move" from the loop's
        point of view. Only after every retry fails do we fall back to a
        move verified against the real board state, so the fallback itself
        can never be rejected and crash the sub-game.
        """
        client = self._clients[agent_id]
        obs = await client.get_observation()
        system_prompt = build_system_prompt(agent_id, self._config)
        user_prompt = build_user_prompt(obs, agent_id, self._config)
        max_chars = self._config["communication"]["max_message_chars"]

        for attempt in range(1, self._max_retries + 1):
            text = await self._call_llm(system_prompt, user_prompt)
            message, action = parse_response(text)
            if action is None:
                logger.warning(
                    "Unparseable LLM response for %s (attempt %d/%d): %r",
                    agent_id, attempt, self._max_retries, text,
                )
                continue
            try:
                await self._dispatch(client, action, message[:max_chars])
                return
            except ToolError as exc:
                logger.warning(
                    "Rejected action for %s (attempt %d/%d): %s",
                    agent_id, attempt, self._max_retries, exc,
                )

        action = self._random_valid_action(agent_id)
        logger.warning(
            "All retries failed for %s; using fallback action %s", agent_id, action
        )
        await self._dispatch(client, action, "")

    async def _dispatch(self, client, action: Action, message: str) -> None:
        """Send the message, then apply the move or barrier, via MCP tool calls."""
        await client.send_message(message)
        if action.direction is None:
            await client.place_barrier()
        else:
            await client.make_move(action.direction.name)

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """POST the prompt pair to the LLM via ApiGatekeeper; return raw text."""
        payload = {
            "model": self._config["llm"]["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        result = await self._gatekeeper.call("/api/chat", payload)
        return result["message"]["content"]

    def _random_valid_action(self, agent_id: str) -> Action:
        """Pick a random action verified legal against the real board right now.

        Checked directly against the game engine SDK (not via MCP) so this
        fallback can never itself be rejected by the server.
        """
        board = self._sub_game.board
        choices: list = [d for d in Direction if board.is_valid_move(agent_id, d)]
        if agent_id == "cop" and board.barriers_remaining > 0:
            choices.append(None)
        return Action(direction=random.choice(choices or [Direction.N]))

    def _random_starts(self) -> tuple:
        """Return random distinct (cop_start, thief_start) positions from config."""
        rows, cols = self._config["grid"]["rows"], self._config["grid"]["cols"]
        all_cells = [(r, c) for r in range(rows) for c in range(cols)]
        return tuple(random.sample(all_cells, 2))
