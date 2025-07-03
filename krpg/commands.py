from __future__ import annotations

from typing import Any, Callable, Generator

import attr
from krpg.events import Event, EventHandler


type EventGenerator = Generator[Event, Any, Any]
type Pt = Any


@attr.s(auto_attribs=True)
class Command[**P]:
    callback: Callable[P, EventGenerator]
    args: tuple[Any, ...] = attr.ib(factory=tuple)
    kwargs: dict[str, Any] = attr.ib(factory=lambda: {})

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Command[P]:
        self.args = args
        self.kwargs = kwargs
        return self


def command[**P](callback: Callable[P, EventGenerator]) -> Command[P]:
    return Command(callback=callback)


class CommandManager:
    def __init__(self, event_handler: EventHandler) -> None:
        self.event_handler = event_handler

    def execute(self, command: Command[...]) -> Any | None:
        a, k = command.args, command.kwargs
        gen = command.callback(*a, **k)
        for event in gen:
            self.event_handler.publish(event)
        try:
            next(gen)
        except StopIteration as e:
            return e.value
        return None
