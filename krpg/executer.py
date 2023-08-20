from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from krpg.scenario import Command, Section, Multiline

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
        env = game.executer.env | {"game": game, "env": game.executer.env}
        args = [ast.literal_eval('"""' + arg + '"""') for arg in args]
        # newkwargs = {}
        # argtypes = {"min": float}
        # for name, func in argtypes.items():
        #    if name in kwargs:
        #        newkwargs[name] = func(kwargs[name])
        text = eval(f"f'''{' '.join(args)}'''", env)
        # game.console.print(text, **newkwargs)
        game.console.print(text)

    @executer_command("$")
    def builtin_exec(game: Game, code: str):
        env = game.executer.env | {"game": game, "env": game.executer.env}
        exec(code, env)

    @executer_command("set")
    def builtin_set(game: Game, name: str, expr: str):
        env = game.executer.env | {"game": game, "env": game.executer.env}
        game.executer.env[name] = eval(expr, env)

    @executer_command("if")
    def builtin_if(game: Game, expr: str, block: Block):
        env = game.executer.env | {"game": game, "env": game.executer.env}
        if eval(expr, env):
            block.run()


class Block:
    def __init__(self, executer: Executer, section: Section, parent=None):
        self.pos = 0
        self.state = "stop"
        self.section = section
        self.code: list[Command | Section | Multiline] = section.children
        self.executer = executer
        self.execute = self.executer.create_execute([self])
        self.parent = parent

        @executer_command("print_block")  # TODO: Goto
        def print_block_command(game: Game):
            game.console.print(self)

        self.print_block_command = print_block_command

    def run(self, from_start: bool = True):
        if not self.code:
            return
        if from_start:
            self.pos = 0
        self.state = "run"
        while self.state == "run":
            pos = self.pos
            self.execute(self.code[self.pos])
            if pos == self.pos:  # if execute dont changed pos
                self.pos += 1
            if self.pos >= len(self.code):
                break
        self.state = "stop"


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
        cmds: dict[str, ExecuterCommand] = {}
        for i in dir(obj):
            attr = getattr(obj, i)
            if isinstance(attr, ExecuterCommand):
                cmds[attr.name] = attr
        return cmds

    def add_extension(self, ext: object):
        self.game.log.debug(f"  [yellow3]Added ExecuterExtension [yellow]{ext.__class__.__name__}", stacklevel=2)
        self.extensions.append(ext)

    def get_all_commands(self) -> dict[str, ExecuterCommand]:
        commands: dict[str, ExecuterCommand] = {}
        for ext in self.extensions:
            commands |= self.get_executer_additions(ext)
        return commands

    def create_execute(self, extensions: list[object]):
        """
        Creates new execute method, that works same, but before
        run it extends extension list and after returns it back
        """

        def execute(command: Command):
            ext = self.extensions
            self.extensions += extensions
            self.execute(command)
            self.extensions = ext

        return execute

    def execute(self, command: Command | Section):
        """
        Executes command by name, passing game, args, kwargs
        and "block" kwarg if command have {}
        """
        commands = self.get_all_commands()
        if command.name in commands:
            self.game.log.debug(f"Executing {command.name} ")
            if isinstance(command, Section):
                kwargs = {"block": self.create_block(command)}
            else:
                kwargs = command.kwargs
            commands[command.name].callback(self.game, *command.args, **kwargs)
        else:
            raise Exception(f"Unknown command: {command.name}")

    def create_block(self, section: Section):
        block = Block(self, section)
        return block

    def __repr__(self):
        return (
            f"<Executer ext={len(self.extensions)} cmd={len(self.get_all_commands())}>"
        )
