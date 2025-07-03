from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

import attr

from krpg.events import Event, Middleware


if TYPE_CHECKING:
    from krpg.game import Game


@runtime_checkable
class HasGame(Protocol):
    game: Game = attr.ib(init=False)


class GameEvent(Event, HasGame):
    pass


@attr.s(auto_attribs=True)
class GameMiddleware(Middleware):
    game: Game

    def process(self, event: Event) -> None:
        if isinstance(event, HasGame):
            event.game = self.game
