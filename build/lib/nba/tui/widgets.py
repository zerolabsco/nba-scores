"""
Custom Textual widgets for the NBA scores TUI.
"""

from textual.reactive import reactive
from textual.widgets import Static


class ScoresWidget(Static):
    """Displays the NBA scoreboard as a scrollable ANSI-formatted table."""


class StandingsWidget(Static):
    """Displays the NBA standings as a scrollable ANSI-formatted table."""


class CountdownBar(Static):
    """
    Docked status bar that counts down to the next auto-refresh.

    Maintains its own 1-second ticker and re-renders via a reactive attribute.
    """

    seconds: reactive[int] = reactive(60)

    def __init__(self, interval: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self._interval = interval
        self.seconds = interval

    def on_mount(self) -> None:
        self.set_interval(1, self._tick)

    def _tick(self) -> None:
        if self.seconds > 0:
            self.seconds -= 1

    def watch_seconds(self, value: int) -> None:
        if value <= 0:
            self.update("Refreshing...")
        else:
            self.update(
                f"Next refresh in {value}s  |  "
                "\\[1-9] Box Score  |  \\[</>] Leaders Cat  |  \\[r] Refresh  |  \\[q] Quit"
            )

    def reset(self, interval: int) -> None:
        """Reset the countdown to the given interval."""
        self._interval = interval
        self.seconds = interval
