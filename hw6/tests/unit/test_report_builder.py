"""Unit tests for ReportBuilder — TDD red phase."""

import json

from cop_thief.gmail.report_builder import ReportBuilder
from cop_thief.sdk.game_engine.game_session import GameResult
from cop_thief.sdk.game_engine.sub_game import SubGameResult

CONFIG = {
    "mcp": {"cop_port": 8001, "thief_port": 8002},
    "reporting": {
        "group_name": "Team-Alpha",
        "students": ["Yaman Dahle", "Nagham"],
        "github_repo": "https://github.com/yamandahle/AI-Agents-course",
        "timezone": "Asia/Jerusalem",
    },
}


def _sub_game(winner="cop", crashed=False, turn_num=1):
    return SubGameResult(
        winner=winner,
        cop_score=20 if winner == "cop" else 5,
        thief_score=5 if winner == "cop" else 10,
        moves_played=3,
        barriers_placed=1,
        turns=[
            {
                "turn": turn_num, "thief_move": "N", "thief_message": "Going north!",
                "cop_move": "S", "cop_message": "I see you.",
            },
        ],
        crashed=crashed,
    )


def test_report_has_all_required_fields():
    result = GameResult(sub_games=[_sub_game()], totals={"cop": 20, "thief": 5})
    report = ReportBuilder.build(result, CONFIG)
    required = {
        "group_name", "students", "github_repo", "cop_mcp_url",
        "thief_mcp_url", "timezone", "sub_games", "totals",
    }
    assert required.issubset(report.keys())


def test_report_body_is_valid_json():
    result = GameResult(sub_games=[_sub_game()], totals={"cop": 20, "thief": 5})
    report = ReportBuilder.build(result, CONFIG)
    json.dumps(report)  # must not raise


def test_report_excludes_crashed_sub_games():
    result = GameResult(
        sub_games=[_sub_game(), _sub_game(crashed=True)],
        totals={"cop": 20, "thief": 5},
    )
    report = ReportBuilder.build(result, CONFIG)
    assert len(report["sub_games"]) == 1
    assert all(not sg.get("crashed") for sg in report["sub_games"])


def test_report_totals_match_sub_game_scores():
    result = GameResult(sub_games=[_sub_game()], totals={"cop": 20, "thief": 5})
    report = ReportBuilder.build(result, CONFIG)
    assert report["totals"] == {"cop": 20, "thief": 5}


def test_report_contains_student_names():
    result = GameResult(sub_games=[_sub_game()], totals={"cop": 20, "thief": 5})
    report = ReportBuilder.build(result, CONFIG)
    assert report["students"] == ["Yaman Dahle", "Nagham"]


def test_report_contains_github_repo():
    result = GameResult(sub_games=[_sub_game()], totals={"cop": 20, "thief": 5})
    report = ReportBuilder.build(result, CONFIG)
    assert report["github_repo"] == "https://github.com/yamandahle/AI-Agents-course"


def test_report_extracts_messages_per_sub_game():
    result = GameResult(sub_games=[_sub_game()], totals={"cop": 20, "thief": 5})
    report = ReportBuilder.build(result, CONFIG)
    sg = report["sub_games"][0]
    assert sg["cop_messages"] == ["I see you."]
    assert sg["thief_messages"] == ["Going north!"]
