"""Unit tests for prompt_builder — TDD red phase."""

from cop_thief.orchestrator.prompt_builder import build_system_prompt, build_user_prompt

CONFIG = {
    "grid": {"rows": 5, "cols": 5},
    "game": {"max_moves": 25, "max_barriers": 5},
}


def _obs(
    own_position=(2, 2), opponent_pos=None, barriers=None, move_counter=3, msg=None
):
    return {
        "own_position": own_position,
        "barriers": barriers or [],
        "move_counter": move_counter,
        "opponent_pos": opponent_pos,
        "last_message": msg,
    }


# ── system prompt ────────────────────────────────────────────────────────────

def test_system_prompt_contains_agent_role():
    prompt = build_system_prompt("cop", CONFIG)
    assert "cop" in prompt.lower()


def test_cop_prompt_mentions_barrier_option():
    prompt = build_system_prompt("cop", CONFIG)
    assert "barrier" in prompt.lower()


def test_thief_prompt_has_no_barrier_mention():
    prompt = build_system_prompt("thief", CONFIG)
    assert "barrier" not in prompt.lower()


# ── user prompt ───────────────────────────────────────────────────────────────

def test_user_prompt_contains_own_position():
    prompt = build_user_prompt(_obs(own_position=(1, 4)), "cop", CONFIG)
    assert "row 1" in prompt and "col 4" in prompt


def test_user_prompt_contains_move_counter():
    prompt = build_user_prompt(_obs(move_counter=7), "cop", CONFIG)
    assert "7" in prompt and "25" in prompt


def test_user_prompt_hides_opponent_when_null():
    prompt = build_user_prompt(_obs(opponent_pos=None), "cop", CONFIG)
    assert "unknown" in prompt.lower()


def test_user_prompt_shows_opponent_when_visible():
    obs = _obs(own_position=(2, 2), opponent_pos=(1, 3))
    prompt = build_user_prompt(obs, "cop", CONFIG)
    assert "unknown" not in prompt.lower()
    assert "away" in prompt.lower()


def test_q_hint_included_when_enabled():
    prompt = build_user_prompt(_obs(), "cop", CONFIG, q_hint="Move north.")
    assert "Move north." in prompt


def test_q_hint_absent_when_disabled():
    prompt = build_user_prompt(_obs(), "cop", CONFIG, q_hint=None)
    assert "Tactical hint" not in prompt


def test_user_prompt_lists_barriers_when_present():
    prompt = build_user_prompt(_obs(barriers=[(1, 1), (2, 3)]), "cop", CONFIG)
    assert "(1,1)" in prompt and "(2,3)" in prompt
