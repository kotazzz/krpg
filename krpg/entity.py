from __future__ import annotations
from typing import TYPE_CHECKING


class Attributes:
    def __init__(self):
        self.strength = 0  # Сила
        self.wisdom = 0  # Мудрость
        self.endurance = 0  # Выносливость
        self.agility = 0  # Ловкость
        self.intelligence = 0  # Интеллект
        self.charisma = 0  # Харизма
        self.perception = 0  # Восприятие

        self.free = 0

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
        set: bool = True,
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

    @property
    def max_hp(self):
        return self.endurance * 10


class Entity:
    def __init__(self, name):
        self.name = name
        self.attrib = Attributes()
        self.hp = self.attrib.max_hp

    def save(self):
        return [self.name, self.hp, *self.attrib.save()]

    def load(self, data):
        self.name, self.hp, *attrib = data
        self.attrib.update(*attrib)

    def __repr__(self):
        return f"<Entity name={self.name!r}>"
