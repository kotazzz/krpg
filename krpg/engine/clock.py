from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator

import attr

from krpg.actions import ActionCategory, ActionManager, action
from krpg.command import command
from krpg.engine.executer import Extension, executer_command
from krpg.events import Event

if TYPE_CHECKING:
    from krpg.game import Game


@attr.s(auto_attribs=True)
class TimepassEvent(Event):
    minutes: int


@attr.s(auto_attribs=True)
class NewdayEvent(Event):
    day: int


@command
def wait(
    clock: Clock, minutes: int
) -> Generator[TimepassEvent | NewdayEvent, Any, None]:
    assert minutes, "Must be number"
    assert minutes > 0, "Must be greater than zero"
    assert minutes < 24 * 60, "Cant skip more, than 1 day"  # TODO: ???
    day = clock.days
    clock.global_minutes += minutes
    yield TimepassEvent(minutes)
    if clock.days > day:
        yield NewdayEvent(clock.days)


class ClockCommands(ActionManager):
    @action("time", "Узнать, сколько время", ActionCategory.INFO)
    @staticmethod
    def time(game: Game) -> None:
        c = game.clock
        game.console.print(
            f"[green]Время: День [yellow]{c.days}[green], [yellow]{c.hours:0>2}:{c.minutes:0>2}[/]"
        )


class ClockExtension(Extension):
    @executer_command("pass")
    @staticmethod
    def passtime(game: Game, minutes: str) -> None:
        assert minutes.isdigit()
        game.commands.execute(wait(int(minutes)))


class Clock:
    def __init__(self, game: Game) -> None:  # TODO: restruct
        self.global_minutes: int = 60 * 31  # Day 1, 07:00

    def in_range(self, start: int, end: int) -> bool:
        if start > end:
            return self.in_range(start, 24) or self.in_range(0, end)
        return start <= self.hours < end

    @property
    def days(self) -> int:
        return self.global_minutes // (24 * 60)

    @property
    def hours(self) -> int:
        return (self.global_minutes % (24 * 60)) // 60

    @property
    def minutes(self) -> int:
        return (self.global_minutes % (24 * 60)) % 60

    def __repr__(self) -> str:
        return f"<Clock d={self.days} h={self.hours} m={self.minutes} ({self.global_minutes})>"
