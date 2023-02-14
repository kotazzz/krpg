from __future__ import annotations

from ..game import Game
from ..module import Module
from ..scenario import parse
from ..commands import CommandEngine


class BaseModule(Module):
    requires = []
    
    def __init__(self, game: Game):
        
        super().__init__(game)
        self.parse = parse
        self.engine = CommandEngine()
        self.game = game
        
        self.engine.register("test")(self.test)
        self.game.base = self
    
    def main(self):
        print("Hello, base module!")
        print(self.game.modules)
        
    def test(self, *args):  
        pass
    

def load(game: Game):
    game.add_module(BaseModule(game))