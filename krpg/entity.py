class Attributes:
    def __init__(self):
        self.strength = 0 # Сила
        self.wisdom = 0 # Мудрость
        self.endurance = 0 # Выносливость
        self.agility = 0 # Ловкость
        self.intelligence = 0 # Интеллект
        self.charisma = 0 # Харизма
        self.perception = 0 # Восприятие
        
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
            self.free
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
        set: bool = True
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

    def calc_hp(self):
        return self.endurance * 10 
    

class Location:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.env = {}
        self.actions = []
    
    def save(self):
        return self.env
    def load(self, data):
        self.env = data

class Bestiary:
    def __init__(self):
        self.entities = []
        self.items = []

class World:
    def __init__(self):
        self.locations = []
        self.roads = []
    
    def add(self, location: Location):
        self.locations.append(location)
    
    def get(self, *names: list[str | Location]):
        res = []
        for name in names:
            if isinstance(name, str):
                for loc in self.locations:
                    if loc.name == name:
                        res.append(loc)
                        break
            elif isinstance(name, Location):
                res.append(loc)
        if len(res) != len(names):
            raise Exception(f"{res} != {names}")
        if len(res) == 1:
            return res[0]
        return res
        
    def get_road(self, loc: str | Location):
        loc = self.get(loc)
        res = []
        for a, b in self.roads:
            if a is loc:
                res.append(b)
            if b is loc:
                res.append(a)
        return res
        
    def road(self, loc1: str | Location, loc2: str | Location):
        loc1, loc2 = self.get(loc1, loc2)
        if loc2 in self.get_road(loc1):
            raise Exception(f'Road from {loc1} to {loc2} already exist')
        self.roads.append((loc1, loc2))
        
class Entity:
    def __init__(self, name):
        self.name = name
        self.attrib = Attributes()
        
    def save(self):
        return [self.name, *self.attrib.save()]
    def load(self, data):
        self.name, attrib = data
        self.attrib.update(*attrib)

class Builder:
    def __init__(self, game):
        pass
