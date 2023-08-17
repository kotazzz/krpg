from __future__ import annotations
from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from krpg.entity import Entity



class Attributes:
    def __init__(
        self,
        strength: int=0,
        wisdom: int=0,
        endurance: int=0,
        agility: int=0,
        intelligence: int=0,
        charisma: int=0,
        perception: int=0,
        free: int=0,
        holder: Entity = None,
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
    def total(self):
        return sum(self.save()) - self.free

    def save(self) -> list:
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

    def load(self, data: list):
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
        set: bool = False,
    ):
        def action(a, b, set):
            if not b:
                return a
            if set:
                return b
            return a + b

        self.strength = action(self.strength, strength, set)
        self.wisdom = action(self.wisdom, wisdom, set)
        self.endurance = action(self.endurance, endurance, set)
        self.agility = action(self.agility, agility, set)
        self.intelligence = action(self.intelligence, intelligence, set)
        self.charisma = action(self.charisma, charisma, set)
        self.perception = action(self.perception, perception, set)
        self.free = action(self.free, free, set)

    