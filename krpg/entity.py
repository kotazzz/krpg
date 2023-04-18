from __future__ import annotations

from krpg.attributes import Attributes
from krpg.inventory import Inventory



class Entity:
    def __init__(self, name):
        self.name = name
        self.attrib = Attributes(1, 1, 1, 1, 1, 1, 1, 10)
        self.inventory = Inventory()
        self.hp = self.attrib.max_hp
        
        self.money = 0

    def save(self):
        return [self.name, self.hp, self.money, self.inventory.save(), *self.attrib.save()]

    def load(self, data):
        self.name, self.hp, self.money, inv, *attrib = data
        self.attrib.update(*attrib)
        self.inventory.load(inv)

    def __repr__(self):
        return f"<Entity name={self.name!r}>"
