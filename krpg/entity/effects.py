from __future__ import annotations

import random
from typing import Any, Callable, TypeVar

import attr
from attr import field

from krpg.entity.enums import Attribute, Body, EntityScales, ModifierType, TargetType
from krpg.utils import DEFAULT_DESCRIPTION, Nameable


@attr.s(auto_attribs=True)
class EffectState:
    effect: Effect
    time: int


@attr.s(auto_attribs=True)
class ItemModifier:
    effect: list[Effect]


@attr.s(auto_attribs=True)
class EntityModifier:
    # todo: make programmable modifiers?
    _parts: dict[Body, float] = field(factory=lambda: {}, repr=lambda x: str({i: j for i, j in x.items() if j}))
    _scales: dict[EntityScales, float] = field(factory=lambda: {}, repr=lambda x: str({i: j for i, j in x.items() if j}))
    _attributes: dict[Attribute, float] = field(factory=lambda: {}, repr=lambda x: str({i: j for i, j in x.items() if j}))
    mods: list[tuple[ModifierType, float]] = field(factory=lambda: [])

    TKey = TypeVar("TKey", Attribute, Body, EntityScales)

    @property
    def parts(self) -> dict[Body, float]:
        return self._parts

    @property
    def scales(self) -> dict[EntityScales, float]:
        return self._scales

    @property
    def attributes(self) -> dict[Attribute, float]:
        return self._attributes

    def unpack(self, data: dict[TKey, float]) -> list[float]:
        return list(data.values())

    def pack(self, data: dict[TKey, float], values: list[float]) -> None:
        # for i, (_, v) in enumerate(data.items()):
        #     v.value = values[i]
        for i, (k, _) in enumerate(data.items()):
            data[k] = values[i]

    @staticmethod
    def blur_array(arr: list[float], blur_level: int = 1) -> list[float]:
        result = arr[:]  # Копируем массив
        length = len(arr)

        for i in range(length):
            start = max(i - blur_level, 0)
            end = min(i + blur_level + 1, length)
            # Распределяем значение текущего элемента по соседям
            value_per_neighbor = arr[i] / (end - start)

            for j in range(start, end):
                result[j] += value_per_neighbor

            result[i] -= arr[i]  # Убираем исходное значение

        return result

    @staticmethod
    def copy_element(arr: list[float], pos: int = 0) -> list[float]:
        for i in range(1, len(arr)):
            arr[i] = arr[pos]
        return arr

    @staticmethod
    def swap_with_chance(arr: list[float], chance: int = 50) -> list[float]:
        length = len(arr)

        for i in range(length - 1):
            # todo: use game random
            if random.random() < chance / 100:
                j = random.randint(i + 1, length - 1)
                arr[i], arr[j] = arr[j], arr[i]

        return arr

    def apply_modifiers_to_dict(self, dict_to_modify: dict[TKey, float]) -> None:
        values = self.unpack(dict_to_modify)
        funcs: dict[ModifierType, Callable[[list[float], int], list[float]]] = {
            ModifierType.BLUR: self.blur_array,
            ModifierType.CHAOS: self.swap_with_chance,
            ModifierType.COPY: self.copy_element,
        }
        for mtype, arg in self.mods:
            if mtype in funcs:
                values = funcs[mtype](values, int(arg))
            else:
                raise TypeError
        self.pack(dict_to_modify, values)

    def __attrs_post_init__(self) -> None:
        i: Any
        for i in Body:
            if i not in self._parts:
                self._parts[i] = 0
        for i in EntityScales:
            if i not in self._scales:
                self._scales[i] = 0
        for i in Attribute:
            if i not in self._attributes:
                self._attributes[i] = 0

        self.apply_modifiers_to_dict(self._parts)
        self.apply_modifiers_to_dict(self._scales)
        self.apply_modifiers_to_dict(self._attributes)


@attr.s(auto_attribs=True)
class Effect(Nameable):
    target: TargetType | None = None
    time: int = 0
    interval: int = 0

    modifiers: list[ItemModifier | EntityModifier] = field(factory=lambda: [])

    description: str = DEFAULT_DESCRIPTION

    @property
    def new_instance(self) -> EffectState:
        return EffectState(self, self.time)
