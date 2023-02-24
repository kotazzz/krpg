
from __future__ import annotations

from typing import TYPE_CHECKING

from .core.actions import action, ActionManager
from .entity import Entity

if TYPE_CHECKING:
    from .game import Game  


class Player(ActionManager):

    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.entity = Entity(game, "Игрок", 0, 0, 0, 0, 4, 100)
        game.savers["player"] = (self.save, self.load)
        game.expand_actions(self)

    def save(self):
        return self.entity.save()

    def load(self, data):
        self.entity.load(data)          

    @action("me", "Информация о себе", "Игрок")    
    def me(game: Game):
        p = game.player
        s, d, w, e = p.entity.strength, p.entity.dexterity, p.entity.wisdom, p.entity.endurance
        print("sdwe: ", s, d, w, e)