from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game
    
from krpg.attributes import Attributes
from krpg.inventory import Inventory, ItemType


class Entity:
    def __init__(self, game: Game, name):
        self.game = game
        
        self.name = name
        self.attributes = Attributes(1, 1, 1, 1, 1, 1, 1, 10, holder=self)
        self.inventory = Inventory()
        self.hp = self.max_hp

        self.money = 0

    def save(self):
        return [
            self.name,
            self.hp,
            self.money,
            self.inventory.save(),
            *self.attributes.save(),
        ]

    def load(self, data):
        self.name, self.hp, self.money, inv, *attrib = data
        self.attributes.update(*attrib, set=True)
        self.inventory.load(inv)

    def __repr__(self):
        return f"<Entity name={self.name!r}>"

    
    def calculate(self, attribute: str):
        result: int = getattr(self.attributes, attribute)
        for i, slot in self.inventory.get(ItemType.ITEM, True):
            if not slot.empty:
                item = self.game.bestiary.get_item(slot.id)
                result += getattr(item.attributes, attribute)
        return result
    
    @property
    def strength(self):
        return self.calculate("strength")
    @property
    def wisdom(self):
        return self.calculate("wisdom")
    @property
    def endurance(self):
        return self.calculate("endurance")
    @property
    def agility(self):
        return self.calculate("agility")
    @property
    def intelligence(self):
        return self.calculate("intelligence")
    @property
    def charisma(self):
        return self.calculate("charisma")
    @property
    def perception(self):
        return self.calculate("perception")
    
    @property
    def attack(self):
        return (self.strength * 2) + (self.agility * 0.5) + (self.intelligence * 0.25)

    @property
    def defense(self):
        return (self.endurance * 2) + (self.wisdom * 0.5) + (self.intelligence * 0.25)

    @property
    def parry_chance(self):
        return (self.agility * 0.1) + (self.perception * 0.05)

    @property
    def crit_chance(self):
        return (self.intelligence * 0.1) + (self.perception * 0.05)

    @property
    def max_hp(self):
        return (self.endurance * 3) + (self.strength * 2) + (self.wisdom * 0.5) + (self.intelligence * 0.25)