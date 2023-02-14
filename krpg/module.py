from __future__ import annotations
class Module:
    requires = []
    
    def __init__(self, game):
        from .game import Game
        game: Game
        self.game = game
        self._commands = {}
    
    def main(self):
        raise NotImplementedError
    
    def load(self):
        self.main()
    
    def __repr__(self):
        return f"<Module {self.__class__.__name__}>"