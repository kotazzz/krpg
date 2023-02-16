from .game import Game
from .modules.base import BaseModule
from .modules.debug import DebugModule

if __name__ == "__main__":
    game = Game()
    game.expand_modules([DebugModule(game), BaseModule(game)])
    game.main()
