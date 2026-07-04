"""Builds the JSON-only game report sent by the Gmail sender."""

from cop_thief.sdk.game_engine.game_session import GameResult
from cop_thief.sdk.game_engine.sub_game import SubGameResult


class ReportBuilder:
    """Turns a GameResult + config into the JSON report dict (PRD schema)."""

    @staticmethod
    def build(game_result: GameResult, config: dict) -> dict:
        """Return the report dict, excluding any crashed sub-games."""
        reporting = config["reporting"]
        mcp = config["mcp"]
        sub_games = [
            ReportBuilder._sub_game_entry(i + 1, sg)
            for i, sg in enumerate(game_result.sub_games)
            if not sg.crashed
        ]
        return {
            "group_name": reporting["group_name"],
            "students": reporting["students"],
            "github_repo": reporting["github_repo"],
            "cop_mcp_url": f"http://127.0.0.1:{mcp['cop_port']}",
            "thief_mcp_url": f"http://127.0.0.1:{mcp['thief_port']}",
            "timezone": reporting["timezone"],
            "sub_games": sub_games,
            "totals": game_result.totals,
        }

    @staticmethod
    def _sub_game_entry(number: int, sg: SubGameResult) -> dict:
        """Build one sub-game's report entry, extracting messages from turns."""
        return {
            "sub_game_number": number,
            "winner": sg.winner,
            "moves_played": sg.moves_played,
            "cop_score": sg.cop_score,
            "thief_score": sg.thief_score,
            "barriers_placed": sg.barriers_placed,
            "cop_messages": [
                t["cop_message"] for t in sg.turns if t.get("cop_message")
            ],
            "thief_messages": [
                t["thief_message"] for t in sg.turns if t.get("thief_message")
            ],
        }
