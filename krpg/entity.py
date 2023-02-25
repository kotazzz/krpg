from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game

from krpg.inventory import Inventory


class Entity:
    def __init__(
        self,
        game: Game,
        name: str,
        s: int,
        d: int,
        w: int,
        e: int,
        f: int,
        money: int,
    ):
        self.game = game
        self.name = name
        self.strength = s  # strength
        self.dexterity = d  # dexterity
        self.wisdom = w  # wisdom
        self.endurance = e  # endurance
        self.free_points = f
        self.money = money
        self.hp = self.max_hp
        self.mp = self.max_mp

        self.inventory = Inventory(self.game)

    def save(self):
        return [
            self.name,
            self.strength,
            self.dexterity,
            self.wisdom,
            self.endurance,
            self.free_points,
            self.money,
            self.hp,
            self.mp,
            self.inventory.save(),
        ]

    def load(self, data):
        self.name = data[0]
        self.strength = data[1]
        self.dexterity = data[2]
        self.wisdom = data[3]
        self.endurance = data[4]
        self.free_points = data[5]
        self.money = data[6]
        self.hp = data[7]
        self.mp = data[8]
        self.inventory.load(data[9])

    def upgrade(self, s: int = 0, d: int = 0, w: int = 0, e: int = 0):

        self.strength += s
        self.dexterity += d
        self.wisdom += w
        self.endurance += e
        self.game.eh.dispatch("upgrade", entity=self, s=s, d=d, w=w, e=e)

    def damage(self, hp):
        if hp > 0:
            self.game.eh.dispatch("damage", entity=self, amount=hp)
            self.hp = max(0, min(self.max_hp, self.hp - hp))
        elif hp < 0:
            self.heal(-hp)

    def heal(self, hp):
        if hp > 0:
            self.game.eh.dispatch("damage", entity=self, amount=hp)
            self.hp = max(0, min(self.max_hp, self.hp + hp))
        elif hp < 0:
            self.damage(-hp)

    @property
    def attack(self):
        s, d, w, e, = (
            self.strength,
            self.dexterity,
            self.wisdom,
            self.endurance,
        )
        return s * 2 + 1

    @property
    def defense(self):
        s, d, w, e, = (
            self.strength,
            self.dexterity,
            self.wisdom,
            self.endurance,
        )
        return d * 2 + 0.5

    @property
    def max_hp(self):
        s, d, w, e, = (
            self.strength,
            self.dexterity,
            self.wisdom,
            self.endurance,
        )
        return w * 10 + 5

    @property
    def max_mp(self):
        s, d, w, e, = (
            self.strength,
            self.dexterity,
            self.wisdom,
            self.endurance,
        )
        return e * 10 + 10

    def __repr__(self):
        name, s, d, w, e, = (
            self.name,
            self.strength,
            self.dexterity,
            self.wisdom,
            self.endurance,
        )
        return f"<Entity {name=} {s=} {d=} {w=} {e=}>"
