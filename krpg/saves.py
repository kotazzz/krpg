from __future__ import annotations

from typing import Any, Protocol, Self, runtime_checkable


@runtime_checkable
class Serializable(Protocol):
    def serialize(self) -> Any: ...

    @classmethod
    def deserialize(cls, data: Any, *args: Any, **kwargs: Any) -> Self: ...
