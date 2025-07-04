from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Savable(Protocol):
    def serialize(self) -> Any: ...

    @classmethod
    def deserialize(cls, data: Any, *args: Any, **kwargs: Any) -> Savable: ...
