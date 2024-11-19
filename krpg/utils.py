from typing import Callable, MutableSequence, Sequence

import attr
from attr import field

DEFAULT_DESCRIPTION = field(default="Нет описания", repr=False)


@attr.s(auto_attribs=True)
class Nameable:
    id: str
    name: str = field(repr=False)
    description: str = DEFAULT_DESCRIPTION


def get_by_id[T: Nameable](collection: Sequence[T], item: str | T) -> T | None:
    item = item.id if isinstance(item, Nameable) else item
    return next((obj for obj in collection if obj.id == item), None)


def add[T: Nameable](collection: MutableSequence[T], obj: T) -> None:
    if get_by_id(collection, obj.id):
        raise ValueError(f"exists: {obj.id}")
    collection.append(obj)


def validate_select(start: int, end: int) -> Callable[[str], bool]:
    def validator(value: str) -> bool:
        try:
            res = int(value)
            return start <= res <= end
        except ValueError:
            return False

    return validator
