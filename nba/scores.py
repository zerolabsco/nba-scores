"""
Tabulates a scoreboard for today's games.
"""

from tabulate import tabulate

# ANSI escape codes for text formatting
BOLD = "\033[1m"
END = "\033[0m"
RED = "\033[91m"
GREEN = "\033[32m"


# Function to get team record from standings
def get_team_record(team_name, standings) -> str:
    """
    Retrieves a team's win-loss record from the standings data.

    Args:
            team_name (str): Name of the team.
            standings (dict): Team standings data.

    Returns:
            record (str): Team's win-loss record in 'W-L' format. Defaults to 'N/A'.
    """
    for result_set in standings["resultSets"]:
        if result_set["name"] == "Standings":
            for team in result_set["rowSet"]:
                if team[4] == team_name:
                    return f"{team[12]}-{team[13]}"
    return "N/A"


def get_scoreboard_table(games, standings) -> str:
    """
    Builds and returns the current day's games as a formatted table string.

    Args:
            games (dict): JSON parsed games data.
            standings (dict): Team standings data.

    Returns:
            str: Formatted table string with ANSI color codes.
    """
    scoreboard_data = games["scoreboard"]
    game_list = scoreboard_data["games"]

    if not game_list:
        return "No games scheduled today."

    # Prepare the table data
    table_data = []
    for game in game_list:
        home_team = game["homeTeam"]["teamName"]
        away_team = game["awayTeam"]["teamName"]
        game_status = game["gameStatusText"]
        home_score = game["homeTeam"]["score"]
        away_score = game["awayTeam"]["score"]

        home_record = get_team_record(home_team, standings)
        away_record = get_team_record(away_team, standings)

        # Determine the winning team
        if home_score > away_score:
            home_team_bold = f"{BOLD}{GREEN}{home_team} ({home_record}){END}{END}"
            away_team_bold = f"{away_team} ({away_record}){END}"
            home_score_bold = f"{BOLD}{GREEN}{home_score}{END}{END}"
            away_score_bold = f"{away_score}{END}"
        elif away_score > home_score:
            home_team_bold = f"{home_team} ({home_record}){END}"
            away_team_bold = f"{BOLD}{GREEN}{away_team} ({away_record}){END}{END}"
            home_score_bold = f"{home_score}{END}"
            away_score_bold = f"{BOLD}{GREEN}{away_score}{END}{END}"
        else:
            home_team_bold = f"{home_team} ({home_record})"
            away_team_bold = f"{away_team} ({away_record})"
            home_score_bold = f"{home_score}"
            away_score_bold = f"{away_score}"

        # Determine games still in progress
        if game_status != "Final":
            game_status = f"{RED}{game_status}{END}"

        table_data.append(
            [
                f"{home_team_bold}\n{away_team_bold}",
                f"{home_score_bold}\n{away_score_bold}",
                f"{BOLD}{game_status}{END}",
            ]
        )

    # Define the table headers
    headers = ["Team", "Score", "Game Status"]

    return tabulate(table_data, headers=headers, tablefmt="grid")


def build_scoreboard(games, standings) -> None:
    """
    Prints the current day's games in a table format.

    Args:
            games (dict): JSON parsed games data.
            standings (dict): Team standings data.
    """
    print(get_scoreboard_table(games, standings))
