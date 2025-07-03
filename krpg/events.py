from __future__ import annotations

from abc import ABC, abstractmethod
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


def listener(event: EventType) -> Callable[..., Listener]:
    def decorator(callback: Callback) -> Listener:
        return Listener(event, callback)

    return decorator


class Middleware(ABC):
    @abstractmethod
    def process(self, event: Event) -> None:
        raise NotImplementedError("Subclasses must implement this method.")


class EventHandler:
    def __init__(self, *lookup: object) -> None:
        self.middlewares: list[Middleware] = []
        self.listeners: dict[EventType, list[Listener]] = defaultdict(list)
        for obj in lookup:
            self.lookup(obj)

    def add_middleware(self, mw: Middleware):
        self.middlewares.append(mw)

    def subscribe(self, callback: Listener) -> None:
        if callback not in self.listeners[callback.event]:
            self.listeners[callback.event].append(callback)

    def lookup(self, obj: object) -> None:
        for attrib in dir(obj):
            item = getattr(obj, attrib)
            if isinstance(item, Listener):
                self.subscribe(item)

    def publish(self, event: Event) -> None:
        for mw in self.middlewares:
            mw.process(event)

        for listener in self.listeners[type(event)]:
            listener.callback(event)

        for listener in self.listeners[Event]:
            listener.callback(event)

    def __repr__(self) -> str:
        return f"<EventHandler listeners={len(self.listeners)}>"
