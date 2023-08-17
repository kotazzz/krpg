from __future__ import annotations
from typing import TYPE_CHECKING
from krpg.entity import Entity

if TYPE_CHECKING:
    from krpg.game import Game
    from krpg.attributes import Attributes
from krpg.inventory import Item


class Meta:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        attributes: Attributes,
        money: int = 0,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.attributes = attributes
        self.money = money


class Bestiary:
    def __init__(self, game: Game):
        self.game = game
        self.entities: list[Meta] = []
        self.items: list[Item] = []

    def get_item(self, id: str | Item):
        if isinstance(id, Item):
            return id
        for item in self.items:
            if item.id == id:
                return item
        raise Exception(f"Item {id} not found")

    def get_entity(self, id: str):
        for meta in self.entities:
            if meta.id == id:
                return self.create_monster(meta)
        raise Exception(f"Monster {id} not found")

    def create_monster(self, meta: Meta):
        entity = Entity(self.game, meta.name)
        entity.money = meta.money
        entity.attributes.load(meta.attributes.save())
        return entity

    def __repr__(self):
        return f"<Bestiary e={len(self.entities)} i={len(self.items)}"
