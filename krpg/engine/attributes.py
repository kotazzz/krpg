"""
The attributes module contains the Attributes class, which represents the attributes of an entity in a role-playing game.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from krpg.engine.entity import Entity


class Attributes:
    """
    Represents the attributes of an entity in a role-playing game.

    Attributes:
    - strength (int): The strength attribute of the entity.
    - wisdom (int): The wisdom attribute of the entity.
    - endurance (int): The endurance attribute of the entity.
    - agility (int): The agility attribute of the entity.
    - intelligence (int): The intelligence attribute of the entity.
    - charisma (int): The charisma attribute of the entity.
    - perception (int): The perception attribute of the entity.
    - free (int): The number of free attribute points available.
    - holder (Entity): The entity that holds these attributes.

    Methods:
    - total(): Calculates the total attribute points.
    - save(): Returns a list of attribute values.
    - load(data: list): Loads attribute values from a list.
    - update(): Updates attribute values based on provided arguments.
    """

    def __init__(
        self,
        strength: int = 0,
        wisdom: int = 0,
        endurance: int = 0,
        agility: int = 0,
        intelligence: int = 0,
        charisma: int = 0,
        perception: int = 0,
        free: int = 0,
        holder: Optional[Entity] = None,
    ):
        self.strength = strength  # Сила
        self.wisdom = wisdom  # Мудрость
        self.endurance = endurance  # Выносливость
        self.agility = agility  # Ловкость
        self.intelligence = intelligence  # Интеллект
        self.charisma = charisma  # Харизма
        self.perception = perception  # Восприятие

        self.free = free

        self.holder = holder

    @property
    def total(self) -> int:
        """The total number of attribute points

        Returns
        -------
        int
            The total number of attribute points
        """
        return sum(self.save()) - self.free

    def save(self) -> list[int]:
        """Returns a list of attribute values.

        Returns
        -------
        list[int]
            A list of attribute values
        """
        return [
            self.strength,
            self.wisdom,
            self.endurance,
            self.agility,
            self.intelligence,
            self.charisma,
            self.perception,
            self.free,
        ]

    def load(self, data: list[int]) -> None:
        """Loads attribute values from a list

        Parameters
        ----------
        data : list[int]
            A list of attribute values
        """
        self.strength = data[0]
        self.wisdom = data[1]
        self.endurance = data[2]
        self.agility = data[3]
        self.intelligence = data[4]
        self.charisma = data[5]
        self.perception = data[6]
        self.free = data[7]

    def update(
        self,
        strength: int | None = None,
        wisdom: int | None = None,
        endurance: int | None = None,
        agility: int | None = None,
        intelligence: int | None = None,
        charisma: int | None = None,
        perception: int | None = None,
        free: int | None = None,
        replace: bool = False,
    ):
        """
        Update the attributes of the character.

        Args:
            strength (int | None): The new value for strength attribute. Defaults to None.
            wisdom (int | None): The new value for wisdom attribute. Defaults to None.
            endurance (int | None): The new value for endurance attribute. Defaults to None.
            agility (int | None): The new value for agility attribute. Defaults to None.
            intelligence (int | None): The new value for intelligence attribute. Defaults to None.
            charisma (int | None): The new value for charisma attribute. Defaults to None.
            perception (int | None): The new value for perception attribute. Defaults to None.
            free (int | None): The new value for free attribute. Defaults to None.
            set (bool): If True, the attribute will be set to the new value. If False, the new value will be added to the current value. Defaults to False.
        """

        def action(a, b, replace):
            if not b:
                return a
            if replace:
                return b
            return a + b

        self.strength = action(self.strength, strength, replace)
        self.wisdom = action(self.wisdom, wisdom, replace)
        self.endurance = action(self.endurance, endurance, replace)
        self.agility = action(self.agility, agility, replace)
        self.intelligence = action(self.intelligence, intelligence, replace)
        self.charisma = action(self.charisma, charisma, replace)
        self.perception = action(self.perception, perception, replace)
        self.free = action(self.free, free, replace)
