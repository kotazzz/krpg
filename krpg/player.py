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
        game.add_saver("player", self.save, self.load)
        game.expand_actions(self)

    def save(self):
        return self.entity.save()

    def load(self, data):
        self.entity.load(data)

    @action("me", "Информация о себе", "Игрок")
    def me(game: Game):
        game.presenter.presense(game.player.entity)

    def __repr__(self):
        return self.entity.__repr__()
