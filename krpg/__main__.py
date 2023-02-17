from .game import Game
from .modules.base import BaseModule
from .modules.debug import DebugModule
from .modules.player import PlayerModule

if __name__ == "__main__":
    game = Game()
    game.expand_modules([
        DebugModule(game), 
        BaseModule(game),
        PlayerModule(game)
        ])
    game.main()
