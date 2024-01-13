from __future__ import annotations

from enum import IntEnum
from typing import Optional

from krpg.attributes import Attributes


class ItemType(IntEnum):
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

    @staticmethod
    def description(itemtype):
        """Describe the item type"""
        return ITEM_DESCRIPTIONS[itemtype]


ITEM_DESCRIPTIONS = {
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
}


class Item:
    def __init__(self, id: str, name: str, description: str):
        """
        Initialize an Item object.

        Args:
            id (str): The unique identifier of the item.
            name (str): The name of the item.
            description (str): The description of the item.

        Attributes:
            stack (int): The number of items in the stack. Default is 1.
            type (ItemType): The type of the item. Default is ItemType.ITEM.
            attributes (Attributes): The attributes of the item. Default is an empty Attributes object.
            effects (dict[str, int]): The effects of using the item. Default is an empty dictionary.
            sell (int): The sell value of the item. Default is 0.
            cost (int): The cost of the item. Default is 0.
            throwable (bool): Indicates if the item is throwable. Default is True.
        """
        self.id = id
        self.name = name
        self.description = description
        self.stack: int = 1
        self.type: ItemType = ItemType.ITEM
        self.attributes: Attributes = Attributes()
        self.effects: dict[str, int] = {}
        self.sell: int = 0
        self.cost: int = 0
        self.throwable: bool = True

    def set_stack(self, amount):
        """
        Set the number of items in the stack.

        Args:
            amount (int): The number of items in the stack.
        """
        self.stack = amount

    def set_wear(self, type: ItemType, attrib: Attributes):
        """
        Set the type and attributes of the item.

        Args:
            type (ItemType): The type of the item.
            attrib (Attributes): The attributes of the item.
        """
        self.type = type
        self.attributes = attrib

    def set_use(self, action, amount):
        """
        Set the effect of using the item.

        Args:
            action (str): The action performed when using the item.
            amount (int): The amount of the effect.
        """
        self.effects[action] = amount

    def set_cost(self, sell, cost):
        """
        Set the sell value and cost of the item.

        Args:
            sell (int): The sell value of the item.
            cost (int): The cost of the item.
        """
        self.sell = sell
        self.cost = cost

    @property
    def is_wearable(self):
        """
        Check if the item is wearable.

        Returns:
            bool: True if the item is wearable, False otherwise.
        """
        return self.attributes.total != 0

    @property
    def is_usable(self):
        """
        Check if the item is usable.

        Returns:
            bool: True if the item is usable, False otherwise.
        """
        return bool(self.effects)

    def __repr__(self):
        return f"<Item {self.id!r}>"


class Slot:
    def __init__(self, type: ItemType = ItemType.ITEM):
        """
        Initializes a Slot object.

        Args:
            type (ItemType, optional): The type of the slot. Defaults to ItemType.ITEM.
        """
        self.type = type
        self.id: str = ""
        self.amount: int = 0

    def set(self, id: str, amount: int = 1):
        """
        Sets the id and amount of the slot.

        Args:
            id: The id of the item.
            amount (int, optional): The amount of the item. Defaults to 1.

        Returns:
            Slot: The updated Slot object.
        """
        self.id = id
        self.amount = amount
        return self

    def save(self):
        """
        Saves the slot data.

        Returns:
            tuple: A tuple containing the id and amount of the slot, or None if the slot is empty.
        """
        return None if self.empty else (self.id, self.amount)

    def load(self, data):
        """
        Loads the slot data.

        Args:
            data (tuple): A tuple containing the id and amount of the slot, or None if the slot is empty.
        """
        if data is not None:
            self.id = data[0]
            self.amount = data[1]
        else:
            self.clear()

    @property
    def empty(self):
        """
        Checks if the slot is empty.

        Returns:
            bool: True if the slot is empty, False otherwise.
        """
        self.optimize()
        return not self.amount

    def clear(self):
        """
        Clears the slot.
        """
        self.id = ""
        self.amount = 0

    def optimize(self):
        """
        Optimizes the slot by removing unnecessary data.
        """
        if not self.amount:
            self.id = ""
        if not self.id:
            self.amount = 0

    def swap(self, slot: Slot):
        """
        Swaps the contents of two slots.

        Args:
            slot (Slot): The slot to swap with.
        """
        slot.id, self.id = self.id, slot.id
        slot.amount, self.amount = self.amount, slot.amount

    def __repr__(self) -> str:
        """
        Returns a string representation of the Slot object.

        Returns:
            str: A string representation of the Slot object.
        """
        return f"<Slot {self.amount}x{self.id!r}>"


class Inventory:
    def __init__(self, is_carrier: bool = True, size: int = 10):
        """
        Initialize an Inventory object.

        Args:
            is_carrier (bool, optional): Specifies if the inventory is a carrier. Defaults to True.
            size (int, optional): The size of the inventory. Defaults to 10.
        """
        self.is_carrier = is_carrier
        self.size = size

        self.slots: list[Slot] = [Slot(ItemType.ITEM) for _ in range(size)]
        if is_carrier:
            self.slots.extend(
                [
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
                ]
            )

    def save(self):
        """
        Save the inventory.

        Returns:
            list: A list of saved slots.
        """
        return [s.save() for s in self.slots]

    def load(self, data):
        """
        Load the inventory.

        Args:
            data (list): The data to load.
        """
        [self.slots[i].load(d) for i, d in enumerate(data)]

    def __repr__(self):
        """
        Return a string representation of the inventory.

        Returns:
            str: A string representation of the inventory.
        """
        return f"<Inventory {[s.id for s in self.slots]}>"

    def pickup(self, item: Item, amount: int):
        """
        Pick up an item and add it to the inventory.

        Args:
            item (Item): The item to pick up.
            amount (int): The amount of the item to pick up.

        Returns:
            int: The remaining amount of the item that could not be picked up.
        """
        for slot in self.slots:
            if slot.type == ItemType.ITEM:
                if slot.empty:
                    slot_amount = min(item.stack, amount)
                    amount -= slot_amount
                    slot.id = item.id
                    slot.amount = slot_amount
                elif slot.id == item.id:
                    slot_amount = min(item.stack - slot.amount, amount)
                    amount -= slot_amount
                    slot.amount += slot_amount
            if amount == 0:
                break
        return amount

    def get(
        self, item_type: ItemType, inverse: bool = False, only_empty: bool = False
    ) -> list[tuple[int, Slot]]:
        """
        Get slots of a specific item type from the inventory.

        Args:
            item_type (ItemType): The type of item to get slots for.
            inverse (bool, optional): Specifies if the slots should be of a different item type. Defaults to False.
            only_empty (bool, optional): Specifies if only empty slots should be returned. Defaults to False.

        Returns:
            list: A list of tuples containing the index and slot of the matching slots.
        """
        res: list[tuple[int, Slot]] = []
        for i, slot in enumerate(self.slots):
            if not inverse and slot.type == item_type:
                res.append((i, slot))
            elif inverse and slot.type != item_type:
                res.append((i, slot))
        if only_empty:
            res = [(i, slot) for i, slot in res if slot.empty]
        return res

    def count(self, item: Item | str) -> int:
        """
        Count the number of items in the inventory.

        Args:
            item (Item | str): The item to count.

        Returns:
            int: The number of items in the inventory.
        """
        item = item.id if isinstance(item, Item) else item
        return sum(slot.amount for slot in self.slots if slot.id == item)
