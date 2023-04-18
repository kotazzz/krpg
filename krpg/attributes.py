from __future__ import annotations

class Attributes:

    def __init__(self,
                 strength = 0,
wisdom = 0,
endurance = 0,
agility = 0,
intelligence = 0,
charisma = 0,
perception = 0,
free = 0,
                 ):
        self.strength = strength  # Сила
        self.wisdom = wisdom  # Мудрость
        self.endurance = endurance  # Выносливость
        self.agility = agility  # Ловкость
        self.intelligence = intelligence  # Интеллект
        self.charisma = charisma  # Харизма
        self.perception = perception  # Восприятие

        self.free = free

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

    @property
    def max_hp(self):
        return self.endurance * 10
    @property
    def attack(self):
        return self.strength * 10
    @property
    def defense(self):
        return self.agility * 10