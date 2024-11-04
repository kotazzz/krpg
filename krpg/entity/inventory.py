from __future__ import annotations

import attr
from attr import field

from krpg.entity.effects import Effect
from krpg.entity.enums import ItemTag, SlotType
from krpg.entity.skills import SkillState, SkillTree
from krpg.entity.utils import DEFAULT_DESCRIPTION, Nameable


@attr.s(auto_attribs=True)
class Inventory:
    slots: list[Slot] = field(factory=list)

    @classmethod
    def basic(cls):
        return cls(
            [
                Slot(type=slot_type)
                for slot_type in (
                    SlotType.HELMET,
                    SlotType.ARMOR,
                    SlotType.TROUSERS,
                    SlotType.BOOTS,
                    SlotType.SHIELD,
                    SlotType.WEAPON,
                    SlotType.RING,
                    SlotType.RING,
                    SlotType.AMULET,
                    SlotType.AMULET,
                )
            ]
            + [Slot(type=SlotType.ITEM) for _ in range(18)]
        )

    @property
    def actionable(self):
        actions = []
        for slot in self.slots:
            if slot.type != SlotType.ITEM and not slot.empty:
                if not slot.item.wear_skill:
                    continue
                actions.extend(slot.item.wear_skill.learned)
            elif not slot.empty and slot.use_skills:
                actions.extend(slot.use_skills)
        return actions

    @property
    def effects(self):
        effects: list[Effect] = []
        for slot in self.slots:
            if slot.type != SlotType.ITEM and not slot.empty:
                effects.extend(slot.item.effects)
        return [effect.new_instance for effect in effects]

    def get_slot(self, type: SlotType):
        if not self.slots:
            raise ValueError("No slots")
        return [s for s in self.slots if s.type == type]

    def get_free_slot(self, filter: Item = None):
        for slot in self.get_slot(SlotType.ITEM):
            if filter and slot.item == filter and not slot.full:
                return slot
            elif slot.empty:
                return slot

    def find(self, item: str | Item):
        # TODO: tag search
        item = item if isinstance(item, str) else item.id
        for slot in self.slots:
            if not slot.empty and slot.item.id == item:
                return slot

    def equip(self, slot: Slot):
        if slot.type != SlotType.ITEM:
            free = self.get_free_slot()
            if free:
                free.swap(slot)
                return True
            else:
                return False

        slots = self.get_slot(slot.item.slot_type)
        for s in slots:
            if s.empty:
                s.swap(slot)
                break
        else:
            slots[0].swap(slot)
        return True

    def pickup(self, item: Item, count: int):
        while count:
            slot = self.get_free_slot(item)
            if not slot:
                return count
            count = slot.fill(item, count)

    def ipickup(self, item: Item, count: int = 1):
        x = self.pickup(item, count)
        if x:
            raise ValueError(f"Cant insert {x} x {item.id}")
        return self


@attr.s(auto_attribs=True)
class Slot:
    type: SlotType = SlotType.ITEM
    item: Item | None = attr.field(default=None, repr=lambda x: x and repr(x.id))
    count: int = 0

    def fill(self, item: Item, count: int):
        if not self.item:
            self.item = item
        if item != self.item:
            raise ValueError(f"Cant insert {item.id} into slot with {self.item.id}")
        available = min(item.stack, count + self.count)
        count -= available - self.count
        self.count = available
        return count

    @property
    def full(self):
        return self.count == self.item.stack

    @property
    def empty(self):
        if self.count == 0:
            self.item = None
            return True
        if self.item is None:
            self.count = 0
            return True
        return False

    def swap(self, slot: Slot):
        self.item, slot.item = (slot.item, self.item)
        self.count, slot.count = (slot.count, self.count)

    @property
    def use_skills(self):
        skills = self.item.use_skills
        for skill in skills:
            skill.use_slot = self
        return skills


@attr.s(auto_attribs=True)
class Item(Nameable):
    slot_type: SlotType = SlotType.ITEM

    description: str = DEFAULT_DESCRIPTION
    use_skills: list[SkillState] = field(factory=list)
    wear_skill: SkillTree = None
    effects: list[Effect] = field(factory=list)

    buy_cost: int = -1
    sell_cost: int = -1
    stack: int = 1
    tags: list[ItemTag] = field(factory=list)
