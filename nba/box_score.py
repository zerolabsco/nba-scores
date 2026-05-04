"""
Fetches and formats live box scores for individual games.
"""

import json

from tabulate import tabulate
from nba_api.live.nba.endpoints.boxscore import BoxScore

BOLD = "\033[1m"
END = "\033[0m"

_HEADERS = [
    "Player",
    "Pos",
    "Min",
    "Pts",
    "Reb",
    "Ast",
    "Stl",
    "Blk",
    "TO",
    "FG",
    "3P",
    "FT",
    "+/-",
]


def fetch_box_score(game_id: str) -> dict:
    endpoint = BoxScore(game_id=game_id)
    return json.loads(endpoint.get_json())


def _parse_minutes(raw: str) -> str:
    """Convert 'PT35M24.00S' → '35:24'."""
    if not raw:
        return "0:00"
    try:
        raw = raw.replace("PT", "").replace("S", "")
        mins, secs = raw.split("M")
        return f"{int(mins)}:{int(float(secs)):02d}"
    except Exception:
        return raw


def _player_rows(players: list) -> list:
    rows = []
    for p in players:
        if p.get("status") == "INACTIVE":
            continue
        s = p.get("statistics", {})
        rows.append(
            [
                p.get("name", ""),
                p.get("position", ""),
                _parse_minutes(s.get("minutes", "")),
                s.get("points", 0),
                s.get("reboundsTotal", 0),
                s.get("assists", 0),
                s.get("steals", 0),
                s.get("blocks", 0),
                s.get("turnovers", 0),
                f"{s.get('fieldGoalsMade', 0)}/{s.get('fieldGoalsAttempted', 0)}",
                f"{s.get('threePointersMade', 0)}/{s.get('threePointersAttempted', 0)}",
                f"{s.get('freeThrowsMade', 0)}/{s.get('freeThrowsAttempted', 0)}",
                s.get("plusMinusPoints", 0),
            ]
        )
    return rows


def get_box_score_tables(data: dict) -> tuple:
    """Return (home_table_str, away_table_str)."""
    game = data["game"]
    home = game["homeTeam"]
    away = game["awayTeam"]

    home_rows = _player_rows(home.get("players", []))
    away_rows = _player_rows(away.get("players", []))

    home_table = (
        f"{BOLD}{home['teamCity']} {home['teamName']} ({home['score']}){END}\n"
        + tabulate(home_rows, headers=_HEADERS, tablefmt="grid")
    )
    away_table = (
        f"{BOLD}{away['teamCity']} {away['teamName']} ({away['score']}){END}\n"
        + tabulate(away_rows, headers=_HEADERS, tablefmt="grid")
    )
    return home_table, away_table
