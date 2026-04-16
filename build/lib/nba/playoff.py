"""
Fetches and formats the NBA playoff picture.
"""

import json

from tabulate import tabulate
from nba_api.stats.endpoints.playoffpicture import PlayoffPicture

BOLD = "\033[1m"
END = "\033[0m"
RED = "\033[91m"
GREEN = "\033[32m"
YELLOW = "\033[33m"


def fetch_playoff_picture() -> dict:
    endpoint = PlayoffPicture()
    return json.loads(endpoint.get_json())


def _clinch_status(row: list, idx: dict) -> str:
    """Return a color-coded status string from clinch/elimination columns."""
    def val(col):
        return row[idx[col]] if col in idx else None

    if val("CLINCHED_CONFERENCE"):
        return f"{BOLD}{GREEN}z-Clinched Conf{END}"
    if val("CLINCHED_DIVISION") or val("CLINCHED_PLAYOFFS"):
        return f"{GREEN}x-Clinched{END}"
    if val("Clinched_Play_In"):
        return f"{YELLOW}pi-Play-In{END}"
    if val("ELIMINATED_PLAYOFFS"):
        return f"{RED}e-Eliminated{END}"
    return ""


def _build_conference_table(result_sets: list, name: str) -> str:
    """Build a formatted playoff standings table for one conference."""
    rs = next((r for r in result_sets if r["name"] == name), None)
    if rs is None or not rs["rowSet"]:
        return "No data available."

    headers = rs["headers"]
    rows = rs["rowSet"]
    idx = {h: i for i, h in enumerate(headers)}

    def get(row, col, default=""):
        return row[idx[col]] if col in idx else default

    table_data = []
    for row in rows:
        wins = get(row, "WINS")
        losses = get(row, "LOSSES")
        pct = get(row, "PCT")
        pct_str = f"{float(pct):.3f}" if pct not in ("", None) else ""
        table_data.append([
            get(row, "RANK"),
            get(row, "TEAM"),
            f"{wins}-{losses}",
            pct_str,
            get(row, "GB"),
            get(row, "HOME"),
            get(row, "AWAY"),
            get(row, "CONF"),
            _clinch_status(row, idx),
        ])

    display_headers = ["#", "Team", "W-L", "PCT", "GB", "HOME", "AWAY", "CONF", "Status"]
    conf_label = "Eastern" if "East" in name else "Western"
    title = f"{BOLD}{conf_label} Conference Playoff Picture:{END}"
    return title + "\n" + tabulate(table_data, headers=display_headers, tablefmt="grid")


def get_west_playoff_table(data: dict) -> str:
    return _build_conference_table(data["resultSets"], "WestConfStandings")


def get_east_playoff_table(data: dict) -> str:
    return _build_conference_table(data["resultSets"], "EastConfStandings")
