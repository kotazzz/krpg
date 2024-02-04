from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game

from krpg.actions import action
from krpg.events import Events
from krpg.executer import executer_command


class Clock:
    def __init__(self, game: Game):
        self.global_minutes: int = 60 * 31  # Day 1, 07:00
        self.game = game
        self.game.add_saver("clock", self.save, self.load)
        self.game.executer.add_extension(self)
        self.game.add_actions(self)

    def save(self) -> int:
        """Save the clock state.

        Returns
        -------
        int
            The global minutes.
        """
        return self.global_minutes

    def load(self, data: int):
        """Load the clock state.

        Parameters
        ----------
        data : int
            The global minutes.
        """
        self.global_minutes = data

    def wait(self, minutes):
        """Wait for a specified number of minutes.

        Parameters
        ----------
        minutes : int
            The number of minutes to wait.
        """
        if not minutes:
            return
        day = self.days
        self.global_minutes += minutes
        self.game.events.dispatch(Events.TIMEPASS, minutes=minutes)
        if self.days > day:
            self.game.events.dispatch(Events.NEWDAY, day=self.days)

    def in_range(self, start: int, end: int) -> bool:
        """Check if the current time is in the specified range.

        Parameters
        ----------
        start : int
            The start of the range.
        end : int
            The end of the range.

        Returns
        -------
        bool
            Whether the current time is in the specified range.
        """
        if start > end:
            return self.in_range(start, 24) or self.in_range(0, end)
        return start <= self.hours < end

    @property
    def days(self):
        """Days"""
        return self.global_minutes // (24 * 60)

    @property
    def hours(self):
        """Hours"""
        return (self.global_minutes % (24 * 60)) // 60

    @property
    def minutes(self):
        """Minutes"""
        return (self.global_minutes % (24 * 60)) % 60

    def __repr__(self):
        return f"<Clock d={self.days} h={self.hours} m={self.minutes} ({self.global_minutes})>"

    @executer_command("pass")
    @staticmethod
    def passtime(game: Game, minutes: str):
        """Pass the specified number of minutes.

        Parameters
        ----------
        game : Game
            The game instance.
        minutes : str
            The number of minutes to pass.
        """
        game.clock.wait(int(minutes))

    @action("time", "Узнать, сколько время", "Информация")
    @staticmethod
    def time(game: Game):
        """Print the current time.

        Parameters
        ----------
        game : Game
            The game instance.
        """
        c = game.clock
        game.console.print(
            f"[green]Время: День [yellow]{c.days}[green], [yellow]{c.hours:0>2}:{c.minutes:0>2}[/]"
        )
