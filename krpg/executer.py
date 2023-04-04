from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from krpg.scenario import Command

if TYPE_CHECKING:
    from krpg.game import Game


def executer_command(name):
    def wrapper(callback):
        return ExecuterCommand(name, callback)

    return wrapper


class ExecuterCommand:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback


class Base:
    @executer_command("print")
    def builtin_print(game: Game, *args, **kwargs):
        args = [ast.literal_eval('"""' + arg + '"""') for arg in args]
        newkwargs = {}
        argtypes = {"min": float}

        for name, func in argtypes.items():
            if name in kwargs:
                newkwargs[name] = func(kwargs[name])
        text = eval(
            f"f'''{' '.join(args)}'''", {"game": game, "env": game.executer.env}
        )
        game.console.print(text, **newkwargs)

    @executer_command("exec")
    def builtin_exec(game: Game, code):
        exec(code, {"game": game, "env": game.executer.env})

    @executer_command("set")
    def builtin_exec(game: Game, name, expr):
        env = game.executer.env
        env[name] = eval(expr, {"game": game, "env": env})


class Executer:
    def __init__(self, game: Game):
        self.game = game
        self.extensions: list[object] = [Base()]
        self.env = {}
        game.add_saver("env", self.save, self.load)

    def save(self):
        return self.env

    def load(self, data):
        self.env = data

    def get_executer_additions(self, obj):
        cmds: dict[str, ExecuterCommand] = []
        for i in dir(obj):
            attr = getattr(obj, i)
            if isinstance(attr, ExecuterCommand):
                cmds[attr.name] = attr
        return cmds

    def add_extension(self, ext: object):
        self.game.log.debug(f"Added ExecuterExtension {ext}")
        self.extensions.append(ext)

    def get_all_commands(self):
        commands = {}
        for ext in self.extensions:
            commands |= self.get_executer_additions(ext)
        return commands

    def execute(self, command: Command):
        commands = self.get_all_commands()
        if command.name in commands:
            self.game.log.debug(f"Executing {command.name} ")
            commands[command.name](self.game, *command.args, **command.kwargs)
        else:
            raise Exception(f"Unknown command: {command.name}")

    def __repr__(self):
        return (
            f"<Executer ext={len(self.extensions)} cmd={len(self.get_all_commands())}"
        )
