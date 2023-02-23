

class Entity:
    def __init__(self,
     name: str,
     s: int,
     d: int,
     w: int,
     e: int,
     f: int,
     money: int,
     ):
        self.name = name
        self.s = s # strength
        self.d = d # dexterity
        self.w = w # wisdom
        self.e = e # endurance
        self.f = f
        self.money = money
        self.current_health = self.max_health
        self.current_mana     = self.max_mana
        
    @property
    def attack(self):
        s, d, w, e,  = self.s, self.d, self.w, self.e
        return ((s**1.5) * 2.8) + ((d**1.5) * 1.5) + ((w**0.8) * 1.2) + ((e**0.5) * 0.5) + (((s*d)**1.2) / ((w+1)**0.8)) + 25
        
    @property
    def defense(self):
        s, d, w, e,  = self.s, self.d, self.w, self.e
        return ((d**1.5) * 2.8) + ((s**1.5) * 1.5) + ((w**0.5) * 0.5) + ((e**0.8) * 1.2) + (((d*e)**1.2) / ((s+1)**0.8)) + 25
        
    @property
    def max_health(self):
        s, d, w, e,  = self.s, self.d, self.w, self.e
        return ((e**2.2) * 11) + ((s**1.8) * 1.8) + ((d**0.5) * 0.6) + ((w**0.3) * 0.3) + (((s*e)**1.5) / ((d+1)**0.8)) + 100
        
        
    @property
    def max_mana(self):
        s, d, w, e,  = self.s, self.d, self.w, self.e
        return ((w**2.2) * 8) + ((d**1.8) * 1.8) + ((s**0.5) * 0.6) + ((e**0.3) * 0.3) + (((w*d)**1.5) / ((s+1)**0.8)) + 80
        
    
    def save(self):
        return [
            self.name,
            self.s,
            self.d,
            self.w,
            self.e,
            self.f,
            self.money,
            self.current_health,
            self.current_mana,
        ]

    def load(self, data):
        self.name = data[0]
        self.s = data[1]
        self.d = data[2]
        self.w = data[3]
        self.e = data[4]
        self.f = data[5]
        self.money = data[6]
        self.current_health = data[7]
        self.current_mana     = data[8]

    def __repr__(self):
        s, d, w, e,  = self.s, self.d, self.w, self.e
        return f"<Entity {s=} {d=} {w=} {e=}>"