"""
Fetches and formats the NBA playoff bracket.
"""

import json
from collections import defaultdict
from typing import Optional

from nba_api.stats.endpoints.commonplayoffseries import CommonPlayoffSeries
from nba_api.stats.endpoints.leaguegamelog import LeagueGameLog
from nba_api.stats.static import teams

BOLD = "\033[1m"
END = "\033[0m"
GREEN = "\033[32m"

ROUND_LABELS = {
    1: "First Round",
    2: "Conference Semifinals",
    3: "Conference Finals",
    4: "NBA Finals",
}


def fetch_bracket() -> dict:
    """
    Fetch playoff series and completed playoff games.

    CommonPlayoffSeries provides the bracket's scheduled series and games. The
    playoff game log is used to compute each series record from completed games.
    """
    series_endpoint = CommonPlayoffSeries()
    game_log_endpoint = LeagueGameLog(season_type_all_star="Playoffs")
    return {
        "series": json.loads(series_endpoint.get_json()),
        "game_log": json.loads(game_log_endpoint.get_json()),
    }


def get_bracket_table(data: dict) -> str:
    """Return a formatted playoff bracket."""
    result_sets = data["series"]["resultSets"]
    series_set = next((r for r in result_sets if r["name"] == "PlayoffSeries"), None)
    if series_set is None or not series_set["rowSet"]:
        return "No playoff bracket data available."

    headers = series_set["headers"]
    idx = {header: i for i, header in enumerate(headers)}
    team_map = _team_map()
    series_games = _group_series(series_set["rowSet"], idx)
    series_wins = _series_wins(data["game_log"], series_games)
    summaries = _series_summaries(team_map, series_games, series_wins)

    return "\n".join(
        [
            _center(f"{BOLD}NBA Playoff Bracket{END}", 74),
            "",
            _render_conference("Western", summaries),
            "",
            _render_finals(summaries),
            "",
            _render_conference("Eastern", summaries),
        ]
    )


def _team_map() -> dict:
    return {
        team["id"]: {
            "abbr": team["abbreviation"],
            "name": f"{team['city']} {team['nickname']}",
        }
        for team in teams.get_teams()
    }


def _group_series(rows: list, idx: dict) -> dict:
    series_games = defaultdict(list)
    for row in rows:
        series_id = row[idx["SERIES_ID"]]
        series_games[series_id].append(
            {
                "game_id": row[idx["GAME_ID"]],
                "game_num": row[idx["GAME_NUM"]],
                "home_team_id": row[idx["HOME_TEAM_ID"]],
                "visitor_team_id": row[idx["VISITOR_TEAM_ID"]],
            }
        )

    return {
        series_id: sorted(games, key=lambda game: game["game_num"])
        for series_id, games in series_games.items()
    }


def _series_wins(game_log: dict, series_games: dict) -> dict:
    game_to_series = {
        game["game_id"]: series_id
        for series_id, games in series_games.items()
        for game in games
    }
    wins = defaultdict(lambda: defaultdict(int))

    for series_id in series_games:
        wins[series_id]["completed_games"] = set()

    result_set = game_log["resultSets"][0]
    idx = {header: i for i, header in enumerate(result_set["headers"])}
    for row in result_set["rowSet"]:
        game_id = row[idx["GAME_ID"]]
        series_id = game_to_series.get(game_id)
        if series_id is None or row[idx["WL"]] != "W":
            continue

        team_id = row[idx["TEAM_ID"]]
        wins[series_id][team_id] += 1
        wins[series_id]["completed_games"].add(game_id)

    return wins


def _series_summaries(team_map: dict, series_games: dict, series_wins: dict) -> dict:
    summaries = {}
    for series_id, games in series_games.items():
        first_game = games[0]
        home_id = first_game["home_team_id"]
        visitor_id = first_game["visitor_team_id"]
        wins = series_wins[series_id]
        home_wins = wins.get(home_id, 0)
        visitor_wins = wins.get(visitor_id, 0)

        summaries[series_id] = {
            "conference": _conference(series_id),
            "round": _round_number(series_id),
            "slot": _series_slot(series_id),
            "home_id": home_id,
            "visitor_id": visitor_id,
            "home_abbr": _abbr(team_map, home_id),
            "visitor_abbr": _abbr(team_map, visitor_id),
            "home_wins": home_wins,
            "visitor_wins": visitor_wins,
            "winner": _winner(team_map, home_id, visitor_id, home_wins, visitor_wins),
        }
    return summaries


def _render_conference(conference: str, summaries: dict) -> str:
    first_round = _conference_round(summaries, conference, 1)
    semifinals = _conference_round(summaries, conference, 2)
    finals = _conference_round(summaries, conference, 3)
    final = finals[0] if finals else None

    lines = [
        f"{BOLD}{conference.upper()} CONFERENCE{END}",
        "First Round                 Semifinals                 Conference Finals",
    ]

    lines.extend(
        [
            f"{_series_box(_slot(first_round, 0), 24)} ┐",
            f"{_blank(24)} ├── {_series_box(_slot(semifinals, 0), 24)} ┐",
            f"{_series_box(_slot(first_round, 1), 24)} ┘   {_blank(24)} │",
            f"{_blank(24)}     {_blank(24)} ├── {_series_box(final, 24)}",
            f"{_series_box(_slot(first_round, 2), 24)} ┐   {_blank(24)} │",
            f"{_blank(24)} ├── {_series_box(_slot(semifinals, 1), 24)} ┘",
            f"{_series_box(_slot(first_round, 3), 24)} ┘",
        ]
    )

    return "\n".join(lines)


def _render_finals(summaries: dict) -> str:
    finals = [summary for summary in summaries.values() if summary["round"] == 4]
    final = finals[0] if finals else None

    lines = [
        f"{BOLD}NBA FINALS{END}",
        "West Champion              East Champion",
        f"{_series_box(final, 24)}",
    ]
    if final is None:
        lines.append("Winner TBD")
    elif final["winner"]:
        lines.append(f"{GREEN}{final['winner']} wins the Finals{END}")
    return "\n".join(lines)


def _conference_round(summaries: dict, conference: str, round_number: int) -> list:
    return sorted(
        [
            summary
            for summary in summaries.values()
            if summary["conference"] == conference[:4]
            and summary["round"] == round_number
        ],
        key=lambda summary: summary["slot"],
    )


def _slot(items: list, idx: int) -> Optional[dict]:
    return items[idx] if idx < len(items) else None


def _series_box(summary: Optional[dict], width: int) -> str:
    if summary is None:
        return _blank(width, "TBD")

    visitor = _team_line(
        summary["visitor_abbr"],
        summary["visitor_wins"],
        summary["winner"] == summary["visitor_abbr"],
    )
    home = _team_line(
        summary["home_abbr"],
        summary["home_wins"],
        summary["winner"] == summary["home_abbr"],
    )
    return f"{visitor} / {home}".ljust(width)


def _team_line(abbr: str, wins: int, won_series: bool) -> str:
    label = f"{abbr} {wins}"
    if won_series:
        return f"{label}*"
    return label


def _winner(
    team_map: dict,
    home_id: int,
    visitor_id: int,
    home_wins: int,
    visitor_wins: int,
) -> str:
    if home_wins >= 4:
        return _abbr(team_map, home_id)
    if visitor_wins >= 4:
        return _abbr(team_map, visitor_id)
    return ""


def _blank(width: int, text: str = "") -> str:
    return text.ljust(width)


def _center(text: str, width: int) -> str:
    return text.center(width)


def _round_number(series_id: str) -> int:
    try:
        return int(series_id[-3:-1])
    except ValueError:
        return 0


def _series_slot(series_id: str) -> int:
    try:
        return int(series_id[-1])
    except ValueError:
        return 0


def _conference(series_id: str) -> str:
    round_number = _round_number(series_id)
    slot = _series_slot(series_id)

    if round_number == 4:
        return "NBA"
    if round_number == 3:
        return "East" if slot == 0 else "West"
    if round_number == 2:
        return "East" if slot <= 1 else "West"
    if round_number == 1:
        return "East" if slot <= 3 else "West"
    return ""


def _abbr(team_map: dict, team_id: int) -> str:
    return team_map.get(team_id, {}).get("abbr", str(team_id))
