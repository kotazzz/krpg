from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from .core.scenario import Command

if TYPE_CHECKING:
    from .game import Game  


class Executer:
    def __init__(self, game: Game):
        self.game = game
        self.commands: dict[str, callable] = {}

        for name in filter(lambda x: x.startswith("builtin_"), dir(self)):
            func = getattr(self, name)
            self.commands[name[8:]] = func

    def add(self, name: str, callback: callable):
        self.commands[name] = callback

    def execute(self, command: Command):
        if command.name in self.commands:
            self.commands[command.name](*command.args, **command.kwargs)
        else:
            raise Exception(f"Unknown command: {command.name}")

    def builtin_print(self, *args, **kwargs):
        args = [ast.literal_eval('"' + arg + '"') for arg in args]
        newkwargs = {}
        argtypes = {"min": float}
        for name, func in argtypes.items():
            if name in kwargs:
                newkwargs[name] = func(kwargs[name])
        self.game.console.print(*args, **newkwargs)
