"""Named experiment cases and config loading for the 3-run vision study."""

from cop_thief.shared.config import load_config

# Three cases: one full 5x5 baseline + two small-grid vision contrasts.
EXPERIMENT_CASES: dict[str, dict] = {
    "exp1_full_5x5": {
        "config_file": "experiments/exp1_full_5x5.json",
        "grid_label": "5x5",
        "hypothesis": "Baseline — balanced play with equal vision (2,2).",
    },
    "exp2_small_blind_cop": {
        "config_file": "experiments/exp2_small_blind_cop.json",
        "grid_label": "3x2",
        "hypothesis": "Blind cop (0,2) — thief should win more often.",
    },
    "exp3_small_full_vision": {
        "config_file": "experiments/exp3_small_full_vision.json",
        "grid_label": "3x2",
        "hypothesis": "Full vision (2,2) on small grid — cop should win more vs Exp 2.",
    },
}


def case_names() -> list[str]:
    """Return experiment case names in run order."""
    return list(EXPERIMENT_CASES.keys())


def load_case_config(case_name: str) -> dict:
    """Load the full config dict for one experiment case."""
    if case_name not in EXPERIMENT_CASES:
        raise KeyError(f"Unknown experiment case: {case_name}")
    filename = EXPERIMENT_CASES[case_name]["config_file"]
    return load_config(filename)
