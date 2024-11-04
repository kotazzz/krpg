from enum import Enum, auto


class NamedEnum(Enum):
    def __repr__(self):
        return repr(self.name)


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
