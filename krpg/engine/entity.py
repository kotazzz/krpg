from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game

from krpg.engine.attributes import Attributes
from krpg.engine.inventory import Inventory, ItemType


class Entity:
    def __init__(self, game: Game, name):
        """
        Initialize an Entity object.

        Args:
            game (Game): The game object.
            name (str): The name of the entity.
        """
        self.game = game

        self.name = name
        self.attributes = Attributes(1, 1, 1, 1, 1, 1, 1, 10, self)
        self.inventory = Inventory()
        self.hp: float = self.max_hp

        self.money = 0

    def save(self):
        """
        Save the entity's data.

        Returns:
            list: A list containing the entity's name, hp, money, inventory data, and attribute data.
        """
        return [
            self.name,
            self.hp,
            self.money,
            self.inventory.save(),
            *self.attributes.save(),
        ]

    def load(self, data: list):
        """
        Load the entity's data.

        Args:
            data (list): A list containing the entity's name, hp, money, inventory data, and attribute data.
        """
        self.name = data[0]
        self.hp = float(data[1])
        self.money = data[2]
        inv: list = data[3]
        attrib: list = data[4:]
        self.attributes.update(
            strength=attrib[0],
            wisdom=attrib[1],
            endurance=attrib[2],
            agility=attrib[3],
            intelligence=attrib[4],
            charisma=attrib[5],
            perception=attrib[6],
            free=attrib[7],
            replace=True,
        )
        self.inventory.load(inv)

    def __repr__(self):
        """
        Return a string representation of the entity.

        Returns:
            str: A string representation of the entity.
        """
        return f"<Entity name={self.name!r}>"

    def calculate(self, attribute: str):
        """
        Calculate the value of a specific attribute for the entity.

        Args:
            attribute (str): The name of the attribute.

        Returns:
            int: The calculated value of the attribute.
        """
        result: int = getattr(self.attributes, attribute)
        for _, slot in self.inventory.get(ItemType.ITEM, True):
            if not slot.empty:
                item = self.game.bestiary.get_item(slot.id)
                result += getattr(item.attributes, attribute)
        return result

    @property
    def strength(self):
        """
        The strength attribute of the entity.

        Returns:
            int: The strength attribute value.
        """
        return self.calculate("strength")

    @property
    def wisdom(self):
        """
        The wisdom attribute of the entity.

        Returns:
            int: The wisdom attribute value.
        """
        return self.calculate("wisdom")

    @property
    def endurance(self):
        """
        The endurance attribute of the entity.

        Returns:
            int: The endurance attribute value.
        """
        return self.calculate("endurance")

    @property
    def agility(self):
        """
        The agility attribute of the entity.

        Returns:
            int: The agility attribute value.
        """
        return self.calculate("agility")

    @property
    def intelligence(self):
        """
        The intelligence attribute of the entity.

        Returns:
            int: The intelligence attribute value.
        """
        return self.calculate("intelligence")

    @property
    def charisma(self):
        """
        The charisma attribute of the entity.

        Returns:
            int: The charisma attribute value.
        """
        return self.calculate("charisma")

    @property
    def perception(self):
        """
        The perception attribute of the entity.

        Returns:
            int: The perception attribute value.
        """
        return self.calculate("perception")

    @property
    def attack(self):
        """
        The attack attribute of the entity.

        Returns:
            float: The attack attribute value.
        """
        return (self.strength * 2) + (self.agility * 0.5) + (self.intelligence * 0.25)

    @property
    def defense(self):
        """
        The defense attribute of the entity.

        Returns:
            float: The defense attribute value.
        """
        return (self.endurance * 2) + (self.wisdom * 0.5) + (self.intelligence * 0.25)

    @property
    def parry_chance(self):
        """
        The parry chance attribute of the entity.

        Returns:
            float: The parry chance attribute value.
        """
        return (self.agility * 0.1) + (self.perception * 0.05)

    @property
    def crit_chance(self):
        """
        The crit chance attribute of the entity.

        Returns:
            float: The crit chance attribute value.
        """
        return (self.intelligence * 0.1) + (self.perception * 0.05)

    @property
    def max_hp(self):
        """
        The maximum HP attribute of the entity.

        Returns:
            int: The maximum HP attribute value.
        """
        return (
            (self.endurance * 3)
            + (self.strength * 2)
            + (self.wisdom * 0.5)
            + (self.intelligence * 0.25)
        )
