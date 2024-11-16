from __future__ import annotations
from collections import defaultdict
from typing import Callable

import attr

type EventType = type[Event]
type Callback = Callable[[Event], None]


@attr.s(auto_attribs=True)
class Listener:
    event: EventType
    callback: Callback


class Event:
    pass


def listen(event: EventType) -> Callable[..., Listener]:
    def decorator(callback: Callback) -> Listener:
        return Listener(event, callback)

    return decorator


class EventHandler:
    def __init__(self, *lookup: object) -> None:
        self.listeners: dict[EventType, list[Listener]] = defaultdict(list)
        for obj in lookup:
            self.lookup(obj)

    def listen(self, event: EventType, callback: Listener) -> None:
        if callback not in self.listeners[event]:
            self.listeners[event].append(callback)

    def lookup(self, obj: object):
        for attrib in dir(obj):
            item = getattr(obj, attrib)
            if isinstance(item, Listener):
                self.listen(item.event, item)

    def dispatch(self, event: Event) -> None:
        for listener in self.listeners[type(event)]:
            listener.callback(event)

        for listener in self.listeners[Event]:
            listener.callback(event)

    def __repr__(self):
        return f"<EventHandler listeners={len(self.listeners)}>"
