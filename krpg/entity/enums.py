from __future__ import annotations
from enum import Enum, auto
from typing import Any, Self


class NamedEnum(Enum):
    def __repr__(self) -> str:
        return repr(self.name)

    def serialize(self) -> str:
        if isinstance(self.value, tuple):
            return self.value[0]  # type: ignore
        return self.value

    @classmethod
    def deserialize(cls, data: Any, *args: Any, **kwargs: Any) -> Self:
        if isinstance(data, str):
            for item in cls:
                if item.value[0] == data:
                    return item
        raise ValueError(f"Unknown {cls.__name__}: {data}")


class SlotType(NamedEnum):
    HELMET = ("helmet", "Шлем")
    ARMOR = ("armor", "Броня")
    TROUSERS = ("trousers", "Брюки")
    BOOTS = ("boots", "Ботинки")
    SHIELD = ("shield", "Щит")
    WEAPON = ("weapon", "Оружие")
    RING = ("ring", "Кольцо")
    AMULET = ("amulet", "Амулет")
    ITEM = ("item", "Предмет")


class Attribute(NamedEnum):
    STRENGTH = ("strength", "Сила")
    PERCEPTION = ("perception", "Восприятие")
    ENDURANCE = ("endurance", "Выносливость")
    CHARISMA = ("charisma", "Харизма")
    AGILITY = ("agility", "Ловкость")
    INTELLIGENSE = ("intelligense", "Интеллект")
    WISDOM = ("wisdom", "Мудрость")


class Body(NamedEnum):
    HEAD = ("head", "Голова")
    NECK = ("neck", "Шея")
    CHEST = ("chest", "Грудь")
    BODY = ("body", "Тело")
    LEFT_HAND = ("left_hand", "Левая рука")
    RIGHT_HAND = ("right_hand", "Правая рука")
    LEFT_LEG = ("left_leg", "Левая нога")
    RIGHT_LEG = ("right_leg", "Правая нога")


class EntityScales(NamedEnum):
    MP = ("mp", "Mана", Attribute.WISDOM, "🔮")
    EXHAUSTION = ("exhaustion", "Истощение", Attribute.PERCEPTION, "💤")
    ENERGY = ("energy", "Энергия", Attribute.AGILITY, "⚡")
    HUNGER = ("hunger", "Голод", Attribute.STRENGTH, "🍖")
    THIRST = ("thirst", "Жажда", Attribute.ENDURANCE, "💧")


class ItemTag(Enum):
    ARROW = auto()


class TargetType(Enum):
    ENTITY = auto()
    SELF = auto()
    ITEM = auto()


class ModifierType(Enum):
    BLUR = auto()
    CHAOS = auto()
    COPY = auto()
