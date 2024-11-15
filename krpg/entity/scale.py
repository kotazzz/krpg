from typing import Any
from attr import field
import attr
from krpg.utils import Nameable


@attr.s(auto_attribs=True)
class Scale(Nameable):
    base_max_value: float = field(
        default=0.0, repr=lambda x: repr("inf" if x == -1 else x)
    )
    bonus: float = 0.0
    _value: float = 0.0

    @property
    def value(self):
        if self.base_max_value != -1:
            return self._value
        return self._value + self.bonus

    @property
    def max_value(self):
        if self.base_max_value != -1:
            return self.base_max_value + self.bonus
        return -1

    def __attrs_post_init__(self):
        self.base_max_value = round(float(self.base_max_value), 2)
        self._value = self.max_value

    @classmethod
    def infinite(cls, *args: Any, **kwargs: Any):
        kwargs["base_max_value"] = -1
        scale = cls(*args, **kwargs)
        scale.reset()
        return scale

    def __iadd__(self, increment: float):
        if self.max_value == -1:
            self._value += increment
        else:
            self._value = min(self.max_value, max(0, self._value + increment))
        self._value = round(float(self._value), 2)
        return self

    def set(self, new_value: float):
        if self.max_value == -1:
            self._value = new_value
        else:
            self._value = min(self.max_value, max(0, new_value))
        self._value = round(float(self._value), 2)

    def reset(self):
        if self.max_value == -1:
            self._value = 0
        else:
            self._value = self.max_value
        self._value = round(float(self._value), 2)

    def set_bonus(self, value: float):
        self.bonus = value
        if self.max_value != -1 and self.value > self.max_value:
            self._value = self.max_value
        self._value = round(float(self._value), 2)
        self.bonus = round(float(self.bonus), 2)
