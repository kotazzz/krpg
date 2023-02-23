
from __future__ import annotations

from typing import TYPE_CHECKING

from .core.actions import action, ActionManager
from .core.entity import Entity

if TYPE_CHECKING:
    from .game import Game  


class Player(ActionManager):

    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.e = Entity("Игрок", 0, 0, 0, 0, 4, 100)
        game.savers["player"] = (self.save, self.load)
        game.expand_actions(self)

    def save(self):
        return self.e.save()

    def load(self, data):
        self.e.load(data)          

    @action("me", "Информация о себе", "Игрок")    
    def me(game: Game):
        p = game.player
        s, d, w, e = p.e.s, p.e.d, p.e.w, p.e.e
        print("sdwe: ", s, d, w, e)