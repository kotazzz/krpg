from .game import Game
from .modules import base, test

if __name__ == '__main__':
    game = Game()
    base.load(game)
    test.load(game)
    game.main()