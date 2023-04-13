from enum import Enum
from krpg.attributes import Attributes

class ItemType(Enum):
    ITEM = 0
    # шлем нагрудник поножи ботинки перчатки щит оружие кольца амулет
    HELMET = 1
    CHESTPLATE = 2
    LEGGINGS = 3
    BOOTS = 4
    GLOVES = 5
    SHIELD = 6
    WEAPON = 7
    RING = 8
    AMULET = 9

    def description(itemtype):
        """Describe the item type"""
        return {
            ItemType.ITEM: "Предметы",
            ItemType.HELMET: "Шлем",
            ItemType.CHESTPLATE: "Нагрудник",
            ItemType.LEGGINGS: "Поножи",
            ItemType.BOOTS: "Ботинки",
            ItemType.GLOVES: "Перчатки",
            ItemType.SHIELD: "Щит",
            ItemType.WEAPON: "Оружие",
            ItemType.RING: "Кольцо",
            ItemType.AMULET: "Амулет",
        }[itemtype]
        
class Slot:
    def __init__(self, type: ItemType = ItemType.ITEM):
        self.type = type
        self.id = None
        self.amount = 0
    
    def save(self):
        return (self.id, self.amount)
    
    def load(self, data):
        self.id = data[0]
        self.amount = data[1]
    
    @property
    def empty(self):
        self.optimize()
        return not self.amount
    
    def optimize(self):
        if not self.amount:
            self.id = None
        if not self.id:
            self.amount = 0

class Inventory:
    def __init__(self, is_carrier=True, size=10):
        self.is_carrier = is_carrier
        self.size=size
        
        self.slots = [Slot(ItemType.ITEM) for _ in range(size)]
        if is_carrier:
            self.slots.extend([
            Slot(ItemType.HELMET),
            Slot(ItemType.CHESTPLATE),
            Slot(ItemType.LEGGINGS),
            Slot(ItemType.BOOTS),
            Slot(ItemType.GLOVES),
            Slot(ItemType.SHIELD),
            Slot(ItemType.WEAPON),
            Slot(ItemType.RING),
            Slot(ItemType.RING),
            Slot(ItemType.AMULET),
        ])
    def save(self):
        return [s.save() for s in self.slots]
    def load(self, data):
        [self.slots[i].load(d) for i, d in enumerate(data)]
    
    def __repr__(self):
        return f"<Inventory {[s.id for s in self.slots]}>"
        

class Item:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        self.stack = 1
        self.attributes = Attributes()
        self.effects = {}
        self.sell = 0
        self.cost = 10e10
        
    def set_stack(self, amount):
        self.stack = amount
    
    def set_wear(self, slot: ItemType, attrib: Attributes):
        self.attributes = attrib
    
    def set_use(self, action, amount):
        self.effects[action] = amount
    def set_cost(self, sell, cost):
        self.sell = sell
        self.cost = cost
    def __repr__(self):
        return f"<Item {id!r}>"