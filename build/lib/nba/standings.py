"""
Tabulate the current conference standings.
"""

from tabulate import tabulate

# ANSI escape codes for text formatting
BOLD = "\033[1m"
END = "\033[0m"
RED = "\033[91m"
GREEN = "\033[32m"


def _build_conference_table(standings, conference: str) -> str:
    """Build a formatted table string for one conference."""
    data = []
    rank = 1

    for result_set in standings["resultSets"]:
        if result_set["name"] == "Standings":
            for team in result_set["rowSet"]:
                if team[5] != conference:
                    continue
                wins = team[12]
                losses = team[13]
                win_pct = team[14]
                streak = team[35]

                strk_color = (
                    f"{RED}{streak}{END}"
                    if int(streak) < 0
                    else f"{GREEN}{streak}{END}"
                )

                data.append(
                    [
                        f"{rank}",
                        team[4],
                        f"{wins}-{losses}",
                        f"{win_pct:.3f}",
                        team[37],
                        strk_color,
                        team[19],
                        team[17],
                        team[18],
                    ]
                )
                rank += 1

    headers = ["Rank", "Team", "W-L", "PCT", "GB", "STRK", "L10", "HOME", "AWAY"]
    label = "Eastern" if conference == "East" else "Western"
    return f"{BOLD}{label} Conference Standings:{END}\n" + tabulate(
        data, headers=headers, tablefmt="grid"
    )


def get_east_standings_table(standings) -> str:
    """Returns the Eastern Conference standings as a formatted string."""
    return _build_conference_table(standings, "East")


def get_west_standings_table(standings) -> str:
    """Returns the Western Conference standings as a formatted string."""
    return _build_conference_table(standings, "West")


def get_standings_tables(standings) -> str:
    """
    Builds and returns both conference standings as a formatted string.

    Args:
            standings (dict): Team standings data.

    Returns:
            str: Formatted standings string with ANSI color codes for both conferences.
    """
    return (
        get_east_standings_table(standings)
        + "\n\n"
        + get_west_standings_table(standings)
    )


def build_standings(standings) -> None:
    """
    Prints team standings in two separate tables.

    Args:
            standings (dict): Team standings data.
    """
    print(get_standings_tables(standings))
