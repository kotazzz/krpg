from __future__ import annotations

from typing import TYPE_CHECKING

from .entity import Entity

if TYPE_CHECKING:
    from .game import Game


class Bestiary:
    def __init__(self, game: Game):
        self.game = game
        self.entities: dict[str, Entity] = {}
        self.load_scenario()

    def load_scenario(self):
        enemies = self.game.scenario.first("enemies")
        for enemy in enemies.all("enemy"):
            id, n, *ints = enemy.args
            s, d, w, e, m = map(int, ints)
            entity = Entity(self.game, n, s, d, w, e, 0, m)
            self.game.logger.debug(f"Creating {id}: {n}")
            if self.get_entity(id):
                raise Exception(f"id already exists: {id}")
            self.entities[id] = entity

    def get_entity(self, entity_name: Entity | str):
        if isinstance(entity_name, Entity):
            return entity_name
        return self.entities.get(entity_name, None)
