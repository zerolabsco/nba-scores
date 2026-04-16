"""
Fetches data for use in other modules.
"""

import json
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import leaguestandings


def fetch_data() -> tuple:
    """
    Fetches live NBA scoreboard data and standings from the NBA API.

    Returns:
            games (dict): JSON parsed games data.
            standings (dict): JSON parsed team standings data.
    """
    # Get today's scoreboard data
    games_endpoint = scoreboard.ScoreBoard()
    games_json = games_endpoint.get_json()

    # Get league standings
    standings_endpoint = leaguestandings.LeagueStandings()
    standings_json = standings_endpoint.get_json()

    # Parse the JSON strings into Python dictionaries
    games = json.loads(games_json)
    standings = json.loads(standings_json)

    return games, standings
