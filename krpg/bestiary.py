from __future__ import annotations

from typing import Any

import attr
from attr import field

from krpg.utils import Nameable, add, get_by_id


@attr.s(auto_attribs=True)
class Bestiary:
    data: list[Any] = field(factory=lambda: [])

    def add(self, entity: Nameable) -> None:
        add(self.data, entity)

    def get_entity_by_id[T](self, entity_id: str, expected: type[T]) -> T | None:
        obj = get_by_id(self.data, entity_id)
        if not obj:
            return None

        assert isinstance(obj, expected)
        return obj

    def strict_get_entity_by_id[T](self, entity_id: str, expected: type[T]) -> T:
        obj = self.get_entity_by_id(entity_id, expected)
        if not obj:
            raise ValueError(f"Entity {entity_id} not found")
        return obj

    def get_all[T](self, expected: type[T]) -> list[T]:
        return [obj for obj in self.data if isinstance(obj, expected)]


BESTIARY = Bestiary()
