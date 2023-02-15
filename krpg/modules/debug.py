from __future__ import annotations

from ..game import Game
from ..module import Module
from ..scenario import parse


class DebugModule(Module):
    requires = ["BaseModule"]
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
    
    def main(self):
        self.game.logger.debug(f"Modules: {' '.join(m.__class__.__name__ for m in self.game.modules)}")
        
    def on_event(self, event, *args, **kwargs):
        self.game.logger.debug(f"New event: {event} {args} {kwargs}")
        
    