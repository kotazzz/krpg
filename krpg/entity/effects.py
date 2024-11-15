from __future__ import annotations
from enum import Enum
import random
from typing import Any, Callable

from attr import field
import attr

from krpg.entity.enums import Attribute, Body, EntityScales, ModifierType, TargetType
from krpg.utils import DEFAULT_DESCRIPTION, Nameable


@attr.s(auto_attribs=True)
class Effect(Nameable):
    target: TargetType | None = None
    time: int = 0
    interval: int = 0

    modifiers: list[ItemModifier | EntityModifier] = field(factory=list)

    description: str = DEFAULT_DESCRIPTION

    @property
    def new_instance(self) -> EffectState:
        return EffectState(self, self.time)


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
    _parts: dict[Body, int] = field(
        factory=lambda: {}, repr=lambda x: str({i: j for i, j in x.items() if j})
    )
    _scales: dict[EntityScales, int] = field(
        factory=lambda: {}, repr=lambda x: str({i: j for i, j in x.items() if j})
    )
    _attributes: dict[Attribute, int] = field(
        factory=lambda: {}, repr=lambda x: str({i: j for i, j in x.items() if j})
    )
    mods: list[tuple[ModifierType, int]] = field(factory=list)

    @property
    def parts(self):
        return self._parts

    @property
    def scales(self):
        return self._scales

    @property
    def attributes(self):
        return self._attributes

    def unpack(self, data: dict[Enum, int | float]):
        return list(data.values())

    def pack(self, data: dict[Enum, float], values: list[float]):
        # for i, (_, v) in enumerate(data.items()):
        #     v.value = values[i]
        for i, (k, _) in enumerate(data.items()):
            data[k] = values[i]

    @staticmethod
    def blur_array(arr: list[int | float], blur_level: int = 1) -> list[int | float]:
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
    def copy_element(arr: list[int | float], pos: int = 0) -> list[int | float]:
        for i in range(1, len(arr)):
            arr[i] = arr[pos]
        return arr

    @staticmethod
    def swap_with_chance(arr: list[int | float], chance: int = 50) -> list[int | float]:
        length = len(arr)

        for i in range(length - 1):
            # todo: use game random
            if random.random() < chance / 100:
                j = random.randint(i + 1, length - 1)
                arr[i], arr[j] = arr[j], arr[i]

        return arr

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

        t: Any
        for t in [self._parts, self._scales, self._attributes]:
            values = self.unpack(t)
            # TODO: slice this long type hint
            funcs: dict[
                ModifierType, Callable[[list[int | float], int], list[int | float]]
            ] = {
                ModifierType.BLUR: self.blur_array,
                ModifierType.CHAOS: self.swap_with_chance,
                ModifierType.COPY: self.copy_element,
            }
            for mtype, arg in self.mods:
                if mtype in funcs:
                    values = funcs[mtype](values, arg)
                else:
                    raise TypeError
            self.pack(t, values)
