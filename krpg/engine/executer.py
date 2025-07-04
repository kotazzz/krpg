from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generator, Protocol

import attr

from krpg.actions import Action, ActionCategory
from krpg.commands import command
from krpg.events_middleware import GameEvent
from krpg.parser import Command, Section
from krpg.saves import Savable
from krpg.utils import Nameable

if TYPE_CHECKING:
    from krpg.game import Game


type Enviroment = dict[str, Any]


class ExecuterCommandCallback(Protocol):
    # FIXME: Any to str | children
    def __call__(self, ctx: Ctx, *args: Any, **kwargs: Any) -> None | int: ...


class Parse(Protocol):
    def __call__(self, *args: str) -> tuple[Any, int]: ...


class Eval(Protocol):
    def __call__(self, game: Game, *args: Any) -> bool: ...


class Predicate(Protocol):
    name: str
    parse: Parse
    eval: Eval

    def __repr__(self) -> str:
        return f"<Predicate {self.name}>"


predicates: dict[str, Predicate] = {}


def add_predicate(obj: type[Predicate]) -> Predicate:
    item = obj()
    predicates[item.name] = item
    return item


@attr.s(auto_attribs=True)
class ScenarioRun(GameEvent):
    scenario: NamedScript


@command
def run_scenario(executer: Executer, scenario: NamedScript) -> Generator[ScenarioRun, Any, None]:
    yield ScenarioRun(scenario)
    scenario.script.run(executer)


def executer_command(name: str) -> Callable[[ExecuterCommandCallback], ExecuterCommand]:
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

    def __repr__(self) -> str:
        return f"<Extension {self.__class__.__name__}>"


@add_predicate
class ValuePredicate(Predicate):
    name = "value"

    @staticmethod
    def parse(*args: str) -> tuple[tuple[str], int]:
        if args:
            return (args[0],), 1
        raise ValueError("No value provided")

    @staticmethod
    def eval(game: Game, key: str, *_) -> bool:
        return game.executer.env.get(key) is not None


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
        if len(args) > 1:
            id, *text = args
            speech = " ".join(text)
            if id == "you":
                name = f"[white b]{game.player.entity.name}[/][cyan]"
            else:
                npc = game.npc_manager.npcs[id]
                assert npc, f"Where is {id} npc?"
                name = npc.display
            game.console.print(f"{name}[green]:[/] {speech}")
        else:
            speech = " ".join(args)
            game.console.print("[green]" + game.executer.process_text(speech))

    @executer_command("if")
    @staticmethod
    def builtin_if(ctx: Ctx, expr: str, children: list[Command | Section]) -> None | int:
        res = ctx.executer.evaluate(expr)
        if res:
            return ctx.executer.run(Section(children=children))

    @executer_command("return")
    @staticmethod
    def builtin_return(ctx: Ctx):
        return 0

    @executer_command("require")
    @staticmethod
    def builtin_require(
        ctx: Ctx,
        name: str,
        *args: str,
        children: list[Command | Section] | None = None,
    ) -> None | int:
        if name not in predicates:
            raise ValueError(f"Unknown require predicate: {name}")
        parsed, _ = predicates[name].parse(*args)  # TODO: move logic out
        if not predicates[name].eval(ctx.game, *parsed):
            if children:
                ctx.executer.run(Section(children=children))
            return 0


@attr.s(auto_attribs=True)
class Ctx:
    game: Game
    executer: Executer
    locals: Enviroment = {}


@attr.s(auto_attribs=True)
class Script:
    section: Section
    position = 0
    env: Enviroment = {}

    def run(self, executer: Executer) -> None | int:
        self.position = 0
        while True:
            if self.position >= len(self.section.children):
                break
            command = self.section.children[self.position]
            returned = executer.execute(command, self.env)
            self.position += 1
            if returned is not None:
                return returned


@attr.s(auto_attribs=True)
class NamedScript(Nameable):
    script: Script = attr.ib(default=None)

    @property
    def as_action(self) -> Action:
        return Action(self.name, self.description, ActionCategory.ACTION, lambda g: self.script.run(g.executer))  #


def generate_named_script(
    section: Section,
    force_id: str | None = None,
    force_name: str | None = None,
    force_description: str | None = None,
) -> NamedScript:
    match section.name, section.args:
        case None, _:
            raise ValueError("Scenario name is required")
        case id, []:
            id = force_id or id
            name = force_name or id
            description = force_description or id
        case id, [name]:
            id = force_id or id
            name = force_name or name
            description = force_description or name
        case id, [name, description]:
            id = force_id or id
            name = force_name or name
            description = force_description or description
        case _:
            raise Exception("Invalid scenario definition")

    return NamedScript(
        id=id,
        name=name,
        description=description,
        script=Script(section),
    )


class Executer(Savable):
    def __init__(self, game: Game) -> None:
        self.game = game
        self.extensions: list[Extension] = [Base()]
        self.env: Enviroment = {}

    def clear_env(self) -> None:
        for key in list(self.env.keys()):
            if key.startswith("_"):
                del self.env[key]

    def serialize(self) -> dict[str, Any]:
        self.clear_env()
        return self.env

    @classmethod
    def deserialize(cls, data: dict[str, Any], game: Game) -> Savable:
        self = cls(game)
        self.env = data
        return self

    def process_text(self, text: str) -> str:
        t = self.evaluate(f"f'''{text}'''")
        assert isinstance(t, str)
        return t  # noqa

    def evaluate(self, text: str) -> Any:
        env = self.env | {"game": self.game, "env": self.env}
        # Scenario allowed to use python code
        return eval(text, env)  # noqa

    def get_commands(self) -> dict[str, ExecuterCommand]:
        commands: dict[str, ExecuterCommand] = {}
        for extension in self.extensions:
            for name, cmd in extension.get_commands().items():
                if name in commands:
                    raise ValueError(f"Command with name {name} already exists")
                commands[name] = cmd
        return commands

    def execute(self, command: Command | Section, locals: Enviroment) -> None | int:
        game = self.game
        ctx = Ctx(game, self, locals)
        cmds = self.get_commands()
        if command.name in cmds:
            if isinstance(command, Section):
                return cmds[command.name].callback(ctx, *command.args, children=command.children)
            else:
                return cmds[command.name].callback(ctx, *command.args)
        raise ValueError(f"Command {command.name} not found")

    def run(self, section: Section) -> None | int:
        script = Script(section)
        return script.run(self)

    def __str__(self) -> str:
        return "<Executer>"
