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
        """
        Represents the metadata of a creature in the bestiary.

        Args:
            id (str): The unique identifier of the creature.
            name (str): The name of the creature.
            description (str): The description of the creature.
            attributes (Attributes): The attributes of the creature.
            money (int, optional): The amount of money the creature possesses. Defaults to 0.
        """
        self.id = id
        self.name = name
        self.description = description
        self.attributes = attributes
        self.money = money


class Bestiary:
    """
    The Bestiary class represents a collection of entities and items in a game.

    Attributes:
        game (Game): The game instance associated with the bestiary.
        entities (list[Meta]): The list of entities in the bestiary.
        items (list[Item]): The list of items in the bestiary.
    """

    def __init__(self, game: Game):
        self.game = game
        self.entities: list[Meta] = []
        self.items: list[Item] = []

    def get_item(self, id: str | Item):
        """
        Get an item from the bestiary based on its ID or directly by passing the item object.

        Args:
            id (str | Item): The ID of the item or the item object itself.

        Returns:
            Item: The item object.

        Raises:
            Exception: If the item with the specified ID is not found.
        """
        if isinstance(id, Item):
            return id
        for item in self.items:
            if item.id == id:
                return item
        raise Exception(f"Item {id} not found")

    def get_entity(self, id: str):
        """
        Get an entity from the bestiary based on its ID.

        Args:
            id (str): The ID of the entity.

        Returns:
            Entity: The created entity object.

        Raises:
            Exception: If the entity with the specified ID is not found.
        """
        for meta in self.entities:
            if meta.id == id:
                return self.create_monster(meta)
        raise Exception(f"Monster {id} not found")

    def create_monster(self, meta: Meta):
        """
        Create a monster entity based on the provided meta data.

        Args:
            meta (Meta): The meta data of the monster.

        Returns:
            Entity: The created monster entity.
        """
        entity = Entity(self.game, meta.name)
        entity.money = meta.money
        entity.attributes.load(meta.attributes.save())
        return entity

    def __repr__(self):
        return f"<Bestiary e={len(self.entities)} i={len(self.items)}"
