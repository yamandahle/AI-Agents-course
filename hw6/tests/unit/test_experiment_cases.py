"""Unit tests for experiment case definitions."""

import pytest

from cop_thief.experiments.cases import EXPERIMENT_CASES, case_names, load_case_config


def test_all_3_cases_defined():
    assert len(EXPERIMENT_CASES) == 3
    assert case_names() == [
        "exp1_full_5x5",
        "exp2_small_blind_cop",
        "exp3_small_full_vision",
    ]


def test_exp1_uses_vision_radius_2():
    cfg = load_case_config("exp1_full_5x5")
    assert cfg["vision"]["cop_vision_radius"] == 2
    assert cfg["vision"]["thief_vision_radius"] == 2
    assert cfg["grid"]["rows"] == 5


def test_exp2_sets_cop_vision_to_0():
    cfg = load_case_config("exp2_small_blind_cop")
    assert cfg["vision"]["cop_vision_radius"] == 0
    assert cfg["vision"]["thief_vision_radius"] == 2


def test_exp3_small_grid_full_vision():
    cfg = load_case_config("exp3_small_full_vision")
    assert cfg["vision"]["cop_vision_radius"] == 2
    assert cfg["grid"]["rows"] == 3


def test_unknown_case_raises():
    with pytest.raises(KeyError):
        load_case_config("missing_case")
