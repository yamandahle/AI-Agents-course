"""Decision-support helpers for GameLoop: Q-table hints, safe fallback moves."""

import random

from cop_thief.sdk.game_engine.board import Action, Direction
from cop_thief.sdk.game_engine.sub_game import SubGame
from cop_thief.sdk.q_table.advisor import QTableAdvisor


def get_q_hint(
    sub_game: SubGame, advisor: QTableAdvisor | None, agent_id: str
) -> str | None:
    """Return the Cop's tactical hint from ground-truth positions, or None.

    Uses true positions (not the agent's own fog-of-war observation) -- the
    advisor is a strategic-assist layer, not part of the agent's senses,
    matching the PRD's get_hint(cop_pos, thief_pos) signature.
    """
    if agent_id != "cop" or advisor is None:
        return None
    board = sub_game.board
    hint = advisor.get_hint(board.get_agent_pos("cop"), board.get_agent_pos("thief"))
    return hint or None


def random_valid_action(sub_game: SubGame, agent_id: str) -> Action:
    """Pick a random action verified legal against the real board right now.

    Checked directly against the game engine SDK (not via MCP) so this
    fallback can never itself be rejected by the server.
    """
    board = sub_game.board
    choices: list = [d for d in Direction if board.is_valid_move(agent_id, d)]
    if agent_id == "cop" and board.barriers_remaining > 0:
        choices.append(None)
    return Action(direction=random.choice(choices or [Direction.N]))


def random_starts(config: dict) -> tuple:
    """Return random distinct (cop_start, thief_start) positions from config."""
    rows, cols = config["grid"]["rows"], config["grid"]["cols"]
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]
    return tuple(random.sample(all_cells, 2))
