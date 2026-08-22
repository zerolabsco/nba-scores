"""
This script uses argparse to parse command line arguments.

It imports the required modules and sets up a parser with basic options for demonstration purposes.
"""

import argparse

from nba import fetch_data, scores, standings


def nba() -> None:
    """
    Parse command-line arguments and display either scoreboard or standings.
    """
    parser = argparse.ArgumentParser(description="NBA Scoreboard and Standings")
    parser.add_argument(
        "--scores", "-sc", action="store_true", help="Display the scoreboard"
    )
    parser.add_argument(
        "--standings", "-st", action="store_true", help="Display the standings"
    )
    parser.add_argument("--tui", action="store_true", help="Launch the interactive TUI")
    parser.add_argument(
        "--refresh",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Auto-refresh interval in TUI mode (default: 60, minimum: 10)",
    )
    args = parser.parse_args()

    if args.tui:
        from nba.tui.app import NBAApp

        initial_tab = "standings" if args.standings else "scores"
        refresh_interval = max(args.refresh, 10)
        NBAApp(initial_tab=initial_tab, refresh_interval=refresh_interval).run()
        return

    # Legacy static mode
    games, ranks = fetch_data.fetch_data()

    if args.scores:
        scores.build_scoreboard(games, ranks)
    elif args.standings:
        standings.build_standings(ranks)
    else:
        print(
            "Please specify --scores or --standings (or use --tui for interactive mode)"
        )
