from __future__ import annotations

from typing import Any, Callable, Iterator

import attr
from krpg.events import Event, EventHandler


type CommandCallback = Callable[..., Iterator[Event]]


@attr.s(auto_attribs=True)
class Command:
    callback: CommandCallback
    args: tuple[Any, ...] = attr.ib(factory=tuple)
    kwargs: dict[str, Any] = attr.ib(factory=dict)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.args = args
        self.kwargs = kwargs
        return self


class CommandManager:
    def __init__(self, event_handler: EventHandler) -> None:
        self.event_handler = event_handler

    def execute(self, command: Command) -> Any | None:
        a, k = command.args, command.kwargs
        gen = command.callback(*a, **k)
        for event in gen:
            self.event_handler.publish(event)
        try:
            next(gen)
        except StopIteration as e:
            return e.value
        return None


def command(callback: CommandCallback) -> Command:
    return Command(callback=callback)
