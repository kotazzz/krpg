from __future__ import annotations

from ..game import Game
from ..module import Module
from ..scenario import parse


class DebugModule(Module):
    name = "debug"
    version = "0"
    requires = ["base>=0.1"]

    def __init__(self, game: Game):
        super().__init__()
        self.game = game

    def init(self):
        self.game.logger.debug(
            f"Modules: {' '.join(f'{m.name}-{m.version}' for m in self.game.modules)}"
        )

    def on_event(self, event, *args, **kwargs):
        self.game.logger.debug(f"New event: {event} {args} {kwargs}")
