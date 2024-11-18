from __future__ import annotations
from typing import Any
from attr import field
import attr
from krpg.utils import Nameable, add, get_by_id


@attr.s(auto_attribs=True)
class Bestiary:
    data: list[Any] = field(factory=list)

    def add(self, entity: Nameable) -> None:
        add(self.data, entity)

    def get_entity_by_id[T: type](self, entity_id: str, expected: T) -> T | None:
        obj = get_by_id(self.data, entity_id)
        if not obj:
            return None

        assert isinstance(obj, expected)
        return obj
