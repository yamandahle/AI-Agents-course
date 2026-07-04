"""Observation engine: builds each agent's fog-of-war view of the board."""

from dataclasses import dataclass

from cop_thief.sdk.game_engine.board import GameBoard


@dataclass
class Observation:
    """What one agent can see at a given turn."""

    agent_id: str
    own_position: tuple[int, int]
    barriers: list[tuple[int, int]]
    move_counter: int
    opponent_pos: tuple[int, int] | None  # None when outside vision radius
    last_message: str | None


class ObservationEngine:
    """Builds per-agent observations applying the fog-of-war rule."""

    def __init__(
        self,
        cop_vision_radius: int,
        thief_vision_radius: int,
    ) -> None:
        """Store per-agent vision radii from config."""
        self._radii = {
            "cop": cop_vision_radius,
            "thief": thief_vision_radius,
        }

    def get_observation(
        self,
        agent_id: str,
        board: GameBoard,
        move_counter: int,
        last_message: str | None = None,
    ) -> Observation:
        """Build and return the observation for agent_id."""
        opponent_id = "thief" if agent_id == "cop" else "cop"
        own_pos = board.get_agent_pos(agent_id)
        opponent_pos = board.get_agent_pos(opponent_id)

        vision_radius = self._radii[agent_id]
        visible = board.chebyshev(own_pos, opponent_pos) <= vision_radius

        return Observation(
            agent_id=agent_id,
            own_position=own_pos,
            barriers=board.get_all_barriers(),
            move_counter=move_counter,
            opponent_pos=opponent_pos if visible else None,
            last_message=last_message,
        )
