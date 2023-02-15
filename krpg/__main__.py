from .game import Game
from .modules.base import BaseModule
from .modules.debug import DebugModule

if __name__ == '__main__':
    game = Game()
    game.expand_modules([BaseModule(game), DebugModule(game)])
    game.main()