from typing import MutableSequence, Sequence
from attr import field
import attr


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
