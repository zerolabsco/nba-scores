"""
Textual TUI application for NBA scores and standings.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane

from nba import fetch_data
from nba import bracket as bracket_mod
from nba import leaders as leaders_mod
from nba import playoff as playoff_mod
from nba import box_score as box_score_mod
from nba.scores import get_scoreboard_table
from nba.standings import get_east_standings_table, get_west_standings_table
from nba.tui.widgets import CountdownBar, ScoresWidget


class NBAApp(App):
    """Live NBA scores and standings TUI with auto-refresh."""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "show_scores", "Scores"),
        ("t", "show_standings", "Standings"),
        ("l", "show_leaders", "Leaders"),
        ("p", "show_playoff", "Playoff"),
        ("k", "show_bracket", "Bracket"),
        ("b", "show_boxscore", "Box Score"),
        ("r", "refresh_now", "Refresh"),
        ("comma", "prev_category", "◀ Cat"),
        ("full_stop", "next_category", "Cat ▶"),
    ]

    TITLE = "NBA Scores"

    def __init__(self, initial_tab: str = "scores", refresh_interval: int = 60) -> None:
        super().__init__()
        self.initial_tab = initial_tab
        self.refresh_interval = refresh_interval
        self._games: dict | None = None
        self._ranks: dict | None = None
        self._leaders_data: dict | None = None
        self._leaders_cat_idx: int = 0
        self._playoff_data: dict | None = None
        self._bracket_data: dict | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial=self.initial_tab):
            with TabPane("Scores", id="scores"):
                yield ScoresWidget("Loading...", id="scores-content")
            with TabPane("Standings", id="standings"):
                with Horizontal(id="standings-container"):
                    yield Static("Loading...", id="west-content")
                    yield Static("Loading...", id="east-content")
            with TabPane("Leaders", id="leaders"):
                yield Static("Loading...", id="leaders-content")
            with TabPane("Playoff", id="playoff"):
                with Horizontal(id="playoff-container"):
                    yield Static("Loading...", id="playoff-west-content")
                    yield Static("Loading...", id="playoff-east-content")
            with TabPane("Bracket", id="bracket"):
                yield Static("Loading...", id="bracket-content")
            with TabPane("Box Score", id="boxscore"):
                with Horizontal(id="boxscore-container"):
                    yield Static(
                        "Press 1–9 to load a game from the Scores tab.",
                        id="home-content",
                    )
                    yield Static("", id="away-content")
        yield CountdownBar(self.refresh_interval, id="countdown")
        yield Footer()

    async def on_mount(self) -> None:
        await self._do_refresh()
        self.set_interval(self.refresh_interval, self._do_refresh)

    # ------------------------------------------------------------------ #
    # Refresh logic                                                        #
    # ------------------------------------------------------------------ #

    async def _do_refresh(self) -> None:
        """Fetch scores, standings, leaders, playoff picture, and bracket in parallel."""
        loop = asyncio.get_event_loop()
        cat = leaders_mod.CATEGORIES[self._leaders_cat_idx][0]

        results = await asyncio.gather(
            loop.run_in_executor(None, fetch_data.fetch_data),
            loop.run_in_executor(None, lambda: leaders_mod.fetch_leaders(cat)),
            loop.run_in_executor(None, playoff_mod.fetch_playoff_picture),
            loop.run_in_executor(None, bracket_mod.fetch_bracket),
            return_exceptions=True,
        )

        games_ranks, leaders_data, playoff_data, bracket_data = results

        if not isinstance(games_ranks, Exception):
            self._games, self._ranks = games_ranks
        if not isinstance(leaders_data, Exception):
            self._leaders_data = leaders_data
        if not isinstance(playoff_data, Exception):
            self._playoff_data = playoff_data
        if not isinstance(bracket_data, Exception):
            self._bracket_data = bracket_data

        self._update_widgets()
        self.query_one(CountdownBar).reset(self.refresh_interval)

    def _update_widgets(self) -> None:
        if self._games and self._ranks:
            self.query_one(ScoresWidget).update(
                Text.from_ansi(get_scoreboard_table(self._games, self._ranks))
            )
            self.query_one("#west-content", Static).update(
                Text.from_ansi(get_west_standings_table(self._ranks))
            )
            self.query_one("#east-content", Static).update(
                Text.from_ansi(get_east_standings_table(self._ranks))
            )

        if self._leaders_data:
            cat = leaders_mod.CATEGORIES[self._leaders_cat_idx][0]
            self.query_one("#leaders-content", Static).update(
                Text.from_ansi(leaders_mod.get_leaders_table(self._leaders_data, cat))
            )

        if self._playoff_data:
            self.query_one("#playoff-west-content", Static).update(
                Text.from_ansi(playoff_mod.get_west_playoff_table(self._playoff_data))
            )
            self.query_one("#playoff-east-content", Static).update(
                Text.from_ansi(playoff_mod.get_east_playoff_table(self._playoff_data))
            )

        if self._bracket_data:
            self.query_one("#bracket-content", Static).update(
                Text.from_ansi(bracket_mod.get_bracket_table(self._bracket_data))
            )

    # ------------------------------------------------------------------ #
    # Key handlers                                                         #
    # ------------------------------------------------------------------ #

    def on_key(self, event) -> None:
        """Handle 1–9 to select a game for the box score tab."""
        char = event.character
        if char and char.isdigit() and char != "0":
            asyncio.create_task(self._load_box_score(int(char) - 1))

    # ------------------------------------------------------------------ #
    # Actions                                                              #
    # ------------------------------------------------------------------ #

    async def action_refresh_now(self) -> None:
        await self._do_refresh()

    def action_show_scores(self) -> None:
        self.query_one(TabbedContent).active = "scores"

    def action_show_standings(self) -> None:
        self.query_one(TabbedContent).active = "standings"

    def action_show_leaders(self) -> None:
        self.query_one(TabbedContent).active = "leaders"

    def action_show_playoff(self) -> None:
        self.query_one(TabbedContent).active = "playoff"

    def action_show_bracket(self) -> None:
        self.query_one(TabbedContent).active = "bracket"

    def action_show_boxscore(self) -> None:
        self.query_one(TabbedContent).active = "boxscore"

    async def action_prev_category(self) -> None:
        self._leaders_cat_idx = (self._leaders_cat_idx - 1) % len(
            leaders_mod.CATEGORIES
        )
        await self._refresh_leaders()

    async def action_next_category(self) -> None:
        self._leaders_cat_idx = (self._leaders_cat_idx + 1) % len(
            leaders_mod.CATEGORIES
        )
        await self._refresh_leaders()

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    async def _refresh_leaders(self) -> None:
        cat, label = leaders_mod.CATEGORIES[self._leaders_cat_idx]
        self.query_one("#leaders-content", Static).update(f"Loading {label} leaders...")
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(
                None, lambda: leaders_mod.fetch_leaders(cat)
            )
            self._leaders_data = data
            self.query_one("#leaders-content", Static).update(
                Text.from_ansi(leaders_mod.get_leaders_table(data, cat))
            )
        except Exception as exc:
            self.query_one("#leaders-content", Static).update(
                f"Error loading leaders: {exc}"
            )

    async def _load_box_score(self, game_idx: int) -> None:
        if not self._games:
            return
        games = self._games["scoreboard"]["games"]
        if game_idx >= len(games):
            return

        game = games[game_idx]
        game_id = game["gameId"]
        home = game["homeTeam"]["teamName"]
        away = game["awayTeam"]["teamName"]

        self.query_one("#home-content", Static).update(
            f"Loading box score: {away} @ {home}..."
        )
        self.query_one("#away-content", Static).update("")
        self.query_one(TabbedContent).active = "boxscore"

        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(
                None, lambda: box_score_mod.fetch_box_score(game_id)
            )
            home_table, away_table = box_score_mod.get_box_score_tables(data)
            self.query_one("#home-content", Static).update(Text.from_ansi(home_table))
            self.query_one("#away-content", Static).update(Text.from_ansi(away_table))
        except Exception as exc:
            self.query_one("#home-content", Static).update(
                f"Error loading box score: {exc}"
            )
            self.query_one("#away-content", Static).update("")
