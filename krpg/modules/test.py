from __future__ import annotations

from ..game import Game
from ..module import Module
from ..scenario import parse
from ..commands import CommandEngine


class TestModule(Module):
    requires = ["BaseModule"]
    
    def __init__(self, game: Game):
        
        super().__init__(game)
    
    def main(self):
        print(self.game.base)
        print("Hello, test module!")
        print(self.game.modules)
        
    

def load(game: Game):
    game.add_module(TestModule(game))