from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game

from enum import Enum


class ItemType(Enum):
    ITEM = 0
    HELMET = 1  # Шлем
    CHESTPLATE = 2  # Нагрудник
    LEGGINGS = 3  # Поножи
    BOOTS = 4  # Ботинки
    GLOVES = 5  # Перчатки
    SHIELD = 6  # Щит
    WEAPON = 7  # Оружие
    RING = 8  # Кольца
    AMULET = 9  # Амулет

    def description(itemtype):
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


class Item:
    def __init__(self, type: ItemType, id: str, name: str, description: str):
        self.type = type
        self.id = id
        self.name = name
        self.description = description

        self.max_stack = 1
        self.usable = False

        self.use_sdwe = (0, 0, 0, 0)
        self.use_heal = 0
        self.use_mana = 0

        self.wear_sdwe = (0, 0, 0, 0)

    @property
    def wearable(self):
        if self.type != ItemType.ITEM:
            return True
        return False

    def setup_use(self, s, d, w, e, hp, mp):
        self.usable = True
        self.use_sdwe = (s, d, w, e)
        self.use_heal = hp
        self.use_mana = mp

    def setup_wear(self, *sdwe):
        if not self.wearable:
            raise Exception(f"Cannot setup wear for ITEM {self.id} {self.name!r}")
        self.wear_sdwe = sdwe


class Slot:
    def __init__(self, game: Game, itemtype: ItemType):
        self.game = game
        self.itemtype = itemtype
        self.item: Item = None
        self.count = 0

    def save(self):
        if self.empty:
            return None
        else:
            return self.item.id, self.count

    def load(self, data):
        if data == None:
            self.item = None
            self.empty
        else:
            self.item = self.game.bestiary.get_item(data[0])
            self.count = data[1]

    def swap(self, other: Slot):
        self.item, other.item = other.item, self.item
        self.count, other.count = other.count, self.count

    @property
    def empty(self):
        if self.item == None:
            self.count = 0
        return self.count == 0 or self.item == None

    def __repr__(self) -> str:
        return f"<Slot {self.itemtype.name} {self.item} {self.count}>"


class Inventory:
    def __init__(self, game: Game):
        self.game = game
        self.slots = [Slot(game, ItemType.ITEM)] * 10 + [
            Slot(game, ItemType.HELMET),
            Slot(game, ItemType.CHESTPLATE),
            Slot(game, ItemType.LEGGINGS),
            Slot(game, ItemType.BOOTS),
            Slot(game, ItemType.GLOVES),
            Slot(game, ItemType.SHIELD),
            Slot(game, ItemType.WEAPON),
            Slot(game, ItemType.RING),
            Slot(game, ItemType.RING),
            Slot(game, ItemType.AMULET),
            Slot(game, ItemType.AMULET),
        ]

    def give(self, item: Item | str):
        pass

    def save(self):
        return [slot.save() for slot in self.slots]

    def load(self, data):
        for i, slot in enumerate(data):
            self.slots[i].load(slot)
