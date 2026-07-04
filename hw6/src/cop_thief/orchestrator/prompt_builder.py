"""Build the system and user prompts sent to the LLM each turn."""

WIN_CONDITION = {
    "cop": "you land exactly on the thief's cell",
    "thief": "you survive all moves without being caught",
}
GOAL = {
    "cop": "catch the thief by landing on their exact cell",
    "thief": "survive without being caught for the full sub-game",
}


def build_system_prompt(agent_id: str, config: dict) -> str:
    """Build the once-per-sub-game system prompt for the given agent."""
    rows, cols = config["grid"]["rows"], config["grid"]["cols"]
    lines = [
        f"You are the {agent_id} agent in a pursuit game on a {rows}x{cols} grid.",
        f"Your goal: {GOAL[agent_id]}.",
        "",
        "Rules:",
        "- You move one cell per turn in 8 directions: N, NE, E, SE, S, SW, W, NW.",
    ]
    if agent_id == "cop":
        max_barriers = config["game"]["max_barriers"]
        lines.append(
            "- You may place a barrier on your current cell instead of moving "
            f"(max {max_barriers} per sub-game)."
        )
    lines += [
        f"- You win if: {WIN_CONDITION[agent_id]}.",
        "- You MUST first send a natural-language message to your opponent, "
        "then declare your action.",
        "",
        "Communication: Your message may be truthful, vague, or deceptive. "
        "Never reveal raw coordinates. Speak naturally.",
    ]
    return "\n".join(lines)


def _describe_opponent(own_pos: tuple, opponent_pos: tuple | None) -> str:
    """Describe the opponent's rough direction/distance, or 'unknown' if hidden."""
    if opponent_pos is None:
        return "position unknown"
    dr, dc = opponent_pos[0] - own_pos[0], opponent_pos[1] - own_pos[1]
    ns = "N" if dr < 0 else ("S" if dr > 0 else "")
    ew = "E" if dc > 0 else ("W" if dc < 0 else "")
    direction = (ns + ew) or "your cell"
    distance = max(abs(dr), abs(dc))
    return f"at approximately {direction}, {distance} cell(s) away"


def _describe_barriers(barriers: list) -> str:
    """Describe placed barriers in plain text, or 'none' if empty."""
    if not barriers:
        return "none placed yet"
    return ", ".join(f"({r},{c})" for r, c in barriers)


def build_user_prompt(
    observation: dict, agent_id: str, config: dict, q_hint: str | None = None
) -> str:
    """Build the per-turn user prompt from the current fog-of-war observation."""
    r, c = observation["own_position"]
    max_moves = config["game"]["max_moves"]
    opponent_desc = _describe_opponent(
        observation["own_position"], observation["opponent_pos"]
    )
    barrier_desc = _describe_barriers(observation["barriers"])
    lines = [
        "Current observation:",
        f"- Your position: row {r}, col {c}",
        f"- Move number: {observation['move_counter']} of {max_moves}",
        f"- Barriers on board: {barrier_desc}",
        f"- Opponent: {opponent_desc}",
        f"- Opponent's last message: \"{observation['last_message'] or ''}\"",
    ]
    if q_hint:
        lines.append(f"- Tactical hint: {q_hint}")
    actions = "N, NE, E, SE, S, SW, W, NW" + (", BARRIER" if agent_id == "cop" else "")
    lines += [
        "",
        "Respond in this exact format:",
        "MESSAGE: <your natural-language message to opponent>",
        f"ACTION: <one of: {actions}>",
    ]
    return "\n".join(lines)
