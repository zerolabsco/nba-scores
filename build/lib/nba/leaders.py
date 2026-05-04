"""
Fetches and formats NBA statistical leaders.
"""

import json

from tabulate import tabulate
from nba_api.stats.endpoints.leagueleaders import LeagueLeaders

BOLD = "\033[1m"
END = "\033[0m"

# Ordered list of (api_abbreviation, display_label)
CATEGORIES = [
    ("PTS", "Points"),
    ("REB", "Rebounds"),
    ("AST", "Assists"),
    ("STL", "Steals"),
    ("BLK", "Blocks"),
    ("EFF", "Efficiency"),
    ("FG_PCT", "FG%"),
    ("FT_PCT", "FT%"),
    ("FG3_PCT", "3P%"),
]

# Extra columns to show alongside RANK, PLAYER, TEAM, GP for each category
_EXTRA_COLS = {
    "PTS": ["PTS", "FGM", "FGA", "FG_PCT", "FTM", "FTA", "FT_PCT"],
    "REB": ["REB", "OREB", "DREB", "GP"],
    "AST": ["AST", "TOV", "AST_TOV", "GP"],
    "STL": ["STL", "TOV", "GP"],
    "BLK": ["BLK", "PF", "GP"],
    "EFF": ["EFF", "PTS", "REB", "AST", "GP"],
    "FG_PCT": ["FG_PCT", "FGM", "FGA", "PTS"],
    "FT_PCT": ["FT_PCT", "FTM", "FTA", "PTS"],
    "FG3_PCT": ["FG3_PCT", "FG3M", "FG3A", "PTS"],
}

_DISPLAY_NAMES = {
    "FG_PCT": "FG%",
    "FT_PCT": "FT%",
    "FG3_PCT": "3P%",
    "FG3M": "3PM",
    "FG3A": "3PA",
    "AST_TOV": "AST/TO",
}


def fetch_leaders(category: str = "PTS") -> dict:
    endpoint = LeagueLeaders(
        stat_category_abbreviation=category,
        season_type_all_star="Regular Season",
    )
    return json.loads(endpoint.get_json())


def get_leaders_table(data: dict, category: str = "PTS") -> str:
    result = data["resultSet"]
    headers = result["headers"]
    rows = result["rowSet"]

    base = ["RANK", "PLAYER", "TEAM", "GP"]
    extra = [c for c in _EXTRA_COLS.get(category, [category]) if c not in base]
    wanted = base + extra

    idx = {h: i for i, h in enumerate(headers)}
    table_data = [[row[idx[col]] for col in wanted if col in idx] for row in rows[:25]]
    display_headers = [_DISPLAY_NAMES.get(c, c) for c in wanted if c in idx]

    cat_label = dict(CATEGORIES).get(category, category)
    title = f"{BOLD}League Leaders — {cat_label}{END}"
    return title + "\n" + tabulate(table_data, headers=display_headers, tablefmt="grid")
