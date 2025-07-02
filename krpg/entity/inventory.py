from __future__ import annotations

from typing import Any, Generator, Self

import attr
from attr import field

from krpg.commands import command
from krpg.components import component
from krpg.engine.executer import Ctx, Extension, executer_command
from krpg.entity.effects import Effect, EffectState
from krpg.entity.enums import ItemTag, SlotType
from krpg.entity.skills import SkillState, SkillTree
from krpg.events_middleware import GameEvent
from krpg.utils import DEFAULT_DESCRIPTION, Nameable


@attr.s(auto_attribs=True)
class EquipEvent(GameEvent):
    slot: Slot
    item: Item


@attr.s(auto_attribs=True)
class UnequipEvent(GameEvent):
    slot: Slot
    item: Item


@attr.s(auto_attribs=True)
class PickupEvent(GameEvent):
    item: Item
    count: int


@attr.s(auto_attribs=True)
class DropEvent(GameEvent):
    slot: Slot
    count: int


@command
def equip(inventory: Inventory, slot: Slot) -> Generator[EquipEvent | UnequipEvent, Any, None]:
    assert slot.item
    item = slot.item
    res = inventory.equip(slot)
    if res is True:
        yield UnequipEvent(slot, item)
    elif res is False:
        yield EquipEvent(slot, item)


@command
def pickup(inventory: Inventory, item: Item, count: int) -> Generator[PickupEvent, Any, int | None]:
    left = inventory.pickup(item, count)
    yield PickupEvent(item, count)
    return left


@command
def drop(slot: Slot, count: int) -> Generator[DropEvent, Any, tuple[Item | None, int]]:
    assert not slot.empty
    assert slot.count >= count, f"Count must be less or equal of content ({slot.count} >= {count})"
    dropped = (slot.item, count)
    # TODO: place item to world
    slot.count -= count
    yield DropEvent(slot, count)
    return dropped

@component
class InventoryCommands(Extension):
    @executer_command("pickup")
    @staticmethod
    def pickup(ctx: Ctx,item_id: str):
        item = ctx.game.bestiary.get_entity_by_id(item_id, Item)
        if not item:
            raise ValueError(f"Item with ID {item_id} not found")
        remain = ctx.game.commands.execute(pickup(ctx.game.player.entity.inventory, item, 1)) # TODO: property inventory to player
        if remain:
            # ctx.game.console.print(f"[yellow]Не удалось получить все предметы. [green]{remain}[/]x[green]{item.name}[/] остались лежать тут[/]")
            # TODO: implement world item placing
            ctx.game.console.print(f"[yellow]Не удалось получить все предметы. [green]{remain}[/]x[green]{item.name}[/] были утеряны[/]")




@attr.s(auto_attribs=True)
class Slot:
    type: SlotType = SlotType.ITEM
    item: Item | None = attr.field(default=None, repr=lambda x: x and repr(x.id))
    count: int = 0

    def fill(self, item: Item, count: int) -> int:
        if not self.item:
            self.item = item
        if item != self.item:
            raise ValueError(f"Cant insert {item.id} into slot with {self.item.id}")
        available = min(item.stack, count + self.count)
        count -= available - self.count
        self.count = available
        return count

    @property
    def full(self) -> bool:
        if self.empty:
            raise Exception("Slot is empty")
        assert self.item is not None
        return self.count == self.item.stack

    @property
    def empty(self) -> bool:
        if self.count == 0:
            self.item = None
            return True
        if self.item is None:
            self.count = 0
            return True
        return False

    def swap(self, slot: Slot) -> None:
        self.item, slot.item = (slot.item, self.item)
        self.count, slot.count = (slot.count, self.count)

    @property
    def use_skills(self) -> list[SkillState]:
        assert self.item is not None
        skills = self.item.use_skills
        for skill in skills:
            skill.use_slot = self
        return skills


@attr.s(auto_attribs=True)
class Inventory:
    slots: list[Slot] = field(factory=lambda: [])

    @classmethod
    def basic(cls) -> Self:
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
    def actionable(self) -> list[SkillState]:
        actions: list[SkillState] = []
        for slot in self.slots:
            if slot.type != SlotType.ITEM and not slot.empty:
                assert slot.item is not None
                if not slot.item.wear_skill:
                    continue
                actions.extend(slot.item.wear_skill.learned)
            elif not slot.empty and slot.use_skills:
                actions.extend(slot.use_skills)
        return actions

    @property
    def effects(self) -> list[EffectState]:
        effects: list[Effect] = []
        for slot in self.slots:
            if slot.type != SlotType.ITEM and not slot.empty:
                assert slot.item is not None
                effects.extend(slot.item.effects)
        return [effect.new_instance for effect in effects]

    def get_slot(self, type: SlotType) -> list[Slot]:
        if not self.slots:
            raise ValueError("No slots")
        return [s for s in self.slots if s.type == type]

    def get_free_slot(self, filter: Item | None = None) -> Slot | None:
        for slot in self.get_slot(SlotType.ITEM):
            if filter and slot.item == filter and not slot.full:
                return slot
            elif slot.empty:
                return slot
        return None

    def find(self, item: str | Item) -> Slot | None:
        # TODO: tag search
        item = item if isinstance(item, str) else item.id
        for slot in self.slots:
            assert slot.item is not None
            if not slot.empty and slot.item.id == item:
                return slot
        return None

    def equip(self, slot: Slot) -> bool | None:
        if slot.type != SlotType.ITEM:
            free = self.get_free_slot()
            if free:
                free.swap(slot)
                return True
            else:
                return None
        assert slot.item is not None
        slots = self.get_slot(slot.item.slot_type)
        for s in slots:
            if s.empty:
                s.swap(slot)
                break
        else:
            slots[0].swap(slot)
        return False

    def pickup(self, item: Item, count: int) -> int | None:
        while count:
            slot = self.get_free_slot(item)
            if not slot:
                return count
            count = slot.fill(item, count)
        return None

    def ipickup(self, item: Item, count: int = 1) -> Self:
        x = self.pickup(item, count)
        if x:
            raise ValueError(f"Cant insert {x} x {item.id}")
        return self


@attr.s(auto_attribs=True)
class Item(Nameable):
    slot_type: SlotType = SlotType.ITEM

    description: str = DEFAULT_DESCRIPTION
    use_skills: list[SkillState] = field(factory=lambda: [])
    wear_skill: SkillTree | None = None
    effects: list[Effect] = field(factory=lambda: [])

    buy_cost: int = -1
    sell_cost: int = -1
    stack: int = 1
    tags: list[ItemTag] = field(factory=lambda: [])
