from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator

import attr

from krpg.actions import ActionCategory, ActionManager, action
from krpg.commands import command
from krpg.components import component
from krpg.engine.executer import Ctx, Extension, executer_command
from krpg.events_middleware import GameEvent

if TYPE_CHECKING:
    from krpg.game import Game


@attr.s(auto_attribs=True)
class TimepassEvent(GameEvent):
    minutes: int


@attr.s(auto_attribs=True)
class NewdayEvent(GameEvent):
    day: int


MINUTES_PER_DAY = 24 * 60

@command
def wait(clock: Clock, minutes: int) -> Generator[TimepassEvent | NewdayEvent, Any, None]:
    assert minutes, "Must be number"
    assert minutes > 0, "Must be greater than zero"
    assert minutes < MINUTES_PER_DAY, "Cant skip more, than 1 day"  # TODO: ???
    day = clock.days
    clock.global_minutes += minutes
    yield TimepassEvent(minutes)
    if clock.days > day:
        yield NewdayEvent(clock.days)


@component
class ClockCommands(ActionManager):
    @action("time", "Узнать, сколько время", ActionCategory.INFO)
    @staticmethod
    def time(game: Game) -> None:
        c = game.clock
        game.console.print(f"[green]Время: День [yellow]{c.days}[green], [yellow]{c.hours:0>2}:{c.minutes:0>2}[/]")


@component
class ClockExtension(Extension):
    @executer_command("pass")
    @staticmethod
    def passtime(ctx: Ctx, minutes: str) -> None:
        assert minutes.isdigit()
        ctx.game.commands.execute(wait(ctx.game.clock, int(minutes)))

    @executer_command("wait")
    @staticmethod
    def wait(ctx: Ctx, *args: str) -> None:
        match args:
            case [minutes]:
                minutes = ctx.executer.evaluate(minutes)
                ctx.game.commands.execute(wait(ctx.game.clock, int(minutes)))
            case ["until", hh, mm]:
                hh = ctx.executer.evaluate(hh)
                mm = ctx.executer.evaluate(mm)
                ctx.game.commands.execute(wait(ctx.game.clock, (int(hh) * 60 + int(mm)) - ctx.game.clock.global_minutes))
            case _:
                raise ValueError("Invalid wait command")

class Clock:
    def __init__(self) -> None:
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
