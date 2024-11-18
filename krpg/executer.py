from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import attr

from krpg.engine.actions import Action, ActionCategory
from krpg.parser import Command, Section
from krpg.utils import Nameable

if TYPE_CHECKING:
    from krpg.game import Game


type Enviroment = dict[str, Any]
type ExecuterCommandCallback = Callable[..., None]


def executer_command(name: str) -> Callable[..., ExecuterCommand]:
    def wrapper(callback: ExecuterCommandCallback) -> ExecuterCommand:
        return ExecuterCommand(name, callback)

    return wrapper


class ExecuterCommand:
    def __init__(self, name: str, callback: ExecuterCommandCallback) -> None:
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
    def builtin_print(ctx: Ctx, *args: str) -> None:
        game = ctx.game
        text = " ".join(args)
        game.console.print("[blue]" + game.executer.process_text(text))

    @executer_command("$")
    @staticmethod
    def builtin_exec(ctx: Ctx, *code: str) -> None:
        exec_str = " ".join(code)
        env = ctx.executer.env | {"game": ctx.game, "env": ctx.executer.env}
        exec(exec_str, env)  # noqa

    @executer_command("set")
    @staticmethod
    def builtin_set(ctx: Ctx, name: str, expr: str) -> None:
        game = ctx.game
        game.executer.env[name] = ctx.executer.evaluate(expr)  # noqa

    @executer_command("say")
    @staticmethod
    def builtin_say(ctx: Ctx, *args: str) -> None:
        game = ctx.game
        text = " ".join(args)
        game.console.print("[green]" + game.executer.process_text(text))


@attr.s(auto_attribs=True)
class Ctx:
    game: Game
    executer: Executer
    locals: Enviroment = {}


@attr.s(auto_attribs=True)
class Script:
    executer: Executer
    section: Section
    position = 0
    env: Enviroment = {}

    def run(self) -> None:
        while True:
            if self.position >= len(self.section.children):
                break
            command = self.section.children[self.position]
            self.executer.execute(command, self.env)
            self.position += 1


@attr.s(auto_attribs=True)
class Scenario(Nameable):
    script: Script | None = None


class Executer:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.extensions: list[Extension] = [Base()]
        self.env: Enviroment = {}

    def process_text(self, text: str) -> str:
        t = self.evaluate(f"f'''{text}'''")
        assert isinstance(t, str)
        return t  # noqa

    def evaluate(self, text: str) -> Any:
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

    def execute(self, command: Command | Section, locals: Enviroment) -> None:
        game = self.game
        ctx = Ctx(game, self, locals)
        cmds = self.get_commands()
        if command.name in cmds:
            if isinstance(command, Section):
                cmds[command.name].callback(ctx, *command.args, children=command.children)
            else:
                cmds[command.name].callback(ctx, *command.args)
            return
        raise ValueError(f"Command {command.name} not found")

    def run(self, section: Section) -> None:
        script = Script(self, section)
        script.run()

    def create_scenario(self, section: Section) -> Scenario:
        if not section.name:
            raise ValueError("Scenario name is required")
        return Scenario(
            id=section.name,
            name=section.name,
            script=Script(self, section),
        )

    def create_action(self, section: Section) -> Action:
        script = Script(self, section)
        assert len(section.args) == 2, f"Expected 2 arguments, got {len(section.args)}"
        name, desc = section.args
        return Action(name=name, description=desc, category=ActionCategory.OTHER, callback=script.run)
