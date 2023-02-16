from __future__ import annotations
from .resolver import DependObject


class Module(DependObject):
    def __init__(self):
        self._commands = {}

    def init(self):
        raise NotImplementedError

    def __repr__(self):
        return f"<Module {self.__class__.__name__}>"
