from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from krpg.parser import Command, Section

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


class Extension:
    def get_commands(self) -> dict[str, ExecuterCommand]:
        commands: dict[str, ExecuterCommand] = {}
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, ExecuterCommand):
                if attr.name in commands:
                    raise ValueError(f"Command with name {attr.name} already exists")
                commands[attr.name] = attr
        return commands


class Base(Extension):
    @executer_command("print")
    @staticmethod
    def builtin_print(ctx: Ctx, *args):
        game = ctx.game
        """Builtin print"""
        text = " ".join(args)
        game.console.print("[blue]" + game.executer.process_text(text))

    @executer_command("$")
    @staticmethod
    def builtin_exec(ctx: Ctx, *code: str):
        game = ctx.game
        """Builtin exec"""
        exec_str = " ".join(code)
        env = game.executer.env | {"game": game, "env": game.executer.env}
        exec(exec_str, env)  # noqa

    @executer_command("set")
    @staticmethod
    def builtin_set(ctx: Ctx, name: str, expr: str):
        game = ctx.game
        """Builtin set"""
        env = game.executer.env | {"game": game, "env": game.executer.env}
        game.executer.env[name] = eval(expr, env)  # noqa


@attr.s(auto_attribs=True)
class Ctx:
    game: Game
    executer: Executer


class Executer:
    def __init__(self, game: Game):
        self.game = game
        self.extensions: list[Extension] = [Base()]
        self.env: dict[str, Any] = {}

    def process_text(self, text):
        return self.evaluate(f"f'''{text}'''")  # noqa

    def evaluate(self, text: str):
        game = self.game
        env = game.executer.env | {"game": game, "env": game.executer.env}
        # Scenario allowed to use python code
        return eval(text, env)  # noqa

    def get_commands(self) -> dict[str, ExecuterCommand]:
        commands: dict[str, ExecuterCommand] = {}
        for extension in self.extensions:
            for name, command in extension.get_commands().items():
                if name in commands:
                    raise ValueError(f"Command with name {name} already exists")
                commands[name] = command
        return commands

    def execute(self, command: Command | Section):
        game = self.game
        ctx = Ctx(game, self)
        cmds = self.get_commands()
        if command.name in cmds:
            if isinstance(command, Section):
                cmds[command.name].callback(
                    ctx, *command.args, children=command.children
                )
            else:
                cmds[command.name].callback(ctx, *command.args)

    def run(self, section: Section | Command):
        if isinstance(section, Section):
            for child in section.children:
                self.execute(child)
        else:
            self.execute(section)
