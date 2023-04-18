from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game
from krpg.inventory import Item


class Bestiary:
    def __init__(self, game: Game):
        self.entities: list = [] # TODO: Edit list -> list[??]
        self.items: list[Item] = []
        
    def get_item(self, id: str | Item):
        if isinstance(id, Item):
            return id
        for item in self.items:
            if item.id == id:
                return item
        raise Exception(f'Item {id} not found')

    def __repr__(self):
        return f"<Bestiary e={len(self.entities)} i={len(self.items)}"