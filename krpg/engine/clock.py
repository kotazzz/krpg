from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator, Literal

import attr

from krpg.actions import ActionCategory, ActionManager, action
from krpg.commands import command
from krpg.components import component
from krpg.engine.executer import Ctx, Extension, Predicate, add_predicate, executer_command
from krpg.events_middleware import GameEvent
from krpg.saves import Savable

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
    assert minutes > 0, "Must be greater than zero"
    assert minutes < MINUTES_PER_DAY, "Cant skip more, than 1 day"  # TODO: ???
    day = clock.days
    clock.global_minutes += minutes
    yield TimepassEvent(minutes)
    if clock.days > day:
        yield NewdayEvent(clock.days)


@command
def wait_until(clock: Clock, hours: int, minutes: int) -> Generator[TimepassEvent | NewdayEvent, Any, None]:
    total = hours * 60 + minutes
    assert total > 0, "Must be greater than zero"
    assert total < MINUTES_PER_DAY, "Cant skip more, than 1 day"  # TODO: ???
    target_minutes = (hours * 60 + minutes) - clock.today_minutes

    day = clock.days
    clock.global_minutes += target_minutes
    yield TimepassEvent(target_minutes)
    if clock.days > day:
        yield NewdayEvent(clock.days)


@add_predicate
class TimePredicate(Predicate):
    name = "time"

    @staticmethod
    def parse(*args: str) -> tuple[tuple[str, int, int], int]:
        match args:
            case ["after", hh, mm]:
                return (("after", int(hh), int(mm)), 3)
            case ["before", hh, mm]:
                return (("before", int(hh), int(mm)), 3)
            case _:
                raise ValueError(f"Invalid time predicate: {args}")

    @staticmethod
    def eval(game: Game, type: Literal["before", "after"], hh: int, mm: int, *_) -> bool:
        match type:
            case "before":
                return (game.clock.hours, game.clock.minutes) <= (hh, mm)
            case "after":
                return (game.clock.hours, game.clock.minutes) >= (hh, mm)


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
                ctx.game.commands.execute(wait_until(ctx.game.clock, int(hh), int(mm)))
            case _:
                raise ValueError("Invalid wait command")


class Clock(Savable):
    def __init__(self) -> None:
        self.global_minutes: int = 60 * 31  # Day 1, 07:00

    def serialize(self) -> dict[str, Any]:
        return {"global_minutes": self.global_minutes}

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Savable:
        self = cls()
        self.global_minutes = data["global_minutes"]
        return self

    def in_range(self, start: int, end: int) -> bool:
        if start > end:
            return self.in_range(start, 24) or self.in_range(0, end)
        return start <= self.hours < end

    @property
    def days(self) -> int:
        return self.global_minutes // (MINUTES_PER_DAY)

    @property
    def hours(self) -> int:
        return (self.global_minutes % (MINUTES_PER_DAY)) // 60

    @property
    def minutes(self) -> int:
        return (self.global_minutes % (MINUTES_PER_DAY)) % 60

    @property
    def today_minutes(self) -> int:
        return self.global_minutes % (MINUTES_PER_DAY)

    def __repr__(self) -> str:
        return f"<Clock d={self.days} h={self.hours} m={self.minutes} ({self.global_minutes})>"
