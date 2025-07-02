from __future__ import annotations

import code
import logging
import sys
from itertools import groupby
from typing import Any, Callable, Generator

import attr
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from krpg.components import registry, Component
from krpg.commands import CommandManager, command
from krpg.engine.builder import build
from krpg.console import KrpgConsole
from krpg.data.consts import ABOUT, LOGO_GAME, __version__
from krpg.actions import Action, ActionCategory, ActionManager, action
from krpg.engine.clock import Clock
from krpg.engine.enums import GameState
from krpg.engine.player import Player
from krpg.engine.quests import QuestManager
from krpg.engine.world import World
from krpg.entity.bestiary import Bestiary
from krpg.engine.executer import Executer
from krpg.events import Event, EventHandler, listener
from krpg.events_middleware import GameMiddleware


@attr.s(auto_attribs=True)
class StateChange(Event):
    new_state: GameState


@command
def set_state(game: Game, state: GameState) -> Generator[Event, Any, None]:
    game.set_state(state)
    yield StateChange(state)


class RootActionManager(ActionManager):
    @action("exit", "Выйти из игры", ActionCategory.GAME)
    @staticmethod
    def action_exit(game: Game) -> None:
        game.commands.execute(set_state(game, GameState.MENU))

    @action("history", "История команд", ActionCategory.GAME)
    @staticmethod
    def action_history(game: Game) -> None:
        c = game.console
        c.print(f"[green]История команд: [red]{' '.join(c.get_history())}")

    @action("help", "Показать команды", ActionCategory.GAME)
    @staticmethod
    def action_help(game: Game) -> None:
        def get_key(act: Action) -> ActionCategory | str:
            return act.category

        actions = sorted(game.actions.actions.values(), key=get_key)
        cmdcat = groupby(actions, key=get_key)
        for cat, cmds in cmdcat:
            game.console.print(f"[b red]{cat}")
            for cmd in cmds:
                game.console.print(f" [green]{cmd.name}[/] - {cmd.description}")

    @action("debug", "Исполнение команды", ActionCategory.DEBUG)
    @staticmethod
    def action_debug(game: Game) -> None:
        if game.console.log.level != logging.DEBUG:
            game.console.print("Режим отладки отключен, команда не доступна")
            return

        class ExitAlt:
            def __call__(self, confirm: int = 0) -> None:
                if confirm == 1:
                    raise SystemExit
                else:
                    game.console.print("[red b]Выполнение этой команды приведет к завершению игры. Для подтверждения введите exit(1)\nДля возврата в игру используйте Ctrl + D (или Z)[/]")

            def __repr__(self) -> str:
                return "Команда приведет к закрытию. Используйте exit(1) для подтверждения"

        v = ".".join(map(str, sys.version_info[:3]))
        welcome = f"Python {v}, KRPG {__version__}"
        code.InteractiveConsole(locals={"game": game, "exit": ExitAlt()}).interact(welcome)


class GameBase:
    def __init__(self) -> None:
        self.state = GameState.MENU
        self.console = KrpgConsole()

    def show_logo(self) -> None:
        centered_logo = Align(LOGO_GAME, align="center")
        centered_about = Align(Text(ABOUT, justify="center", style="green"), align="center", width=80)
        pad = "\n" * 3
        self.console.print(
            Panel(
                Group(pad, centered_logo, centered_about, pad),
                title="Добро пожаловать в KRPG",
            )
        )

    def main(self) -> None:
        options: dict[str, Callable[..., Any]] = {
            "Начать новую игру": self.new_game,
            "Выйти": exit,
        }
        self.show_logo()
        while True:
            choice = self.console.interactive_select("Добро пожаловать", options)
            if not choice:
                return
            choice()

    def new_game(self) -> None:
        self.state = GameState.INIT
        game_loop = Game(self)
        self.state = GameState.PLAY
        try:
            game_loop.play()
        except (KeyboardInterrupt, EOFError):
            self.console.print("Игра завершена")
            self.state = GameState.MENU


class Game:
    def __init__(self, game: GameBase) -> None:
        self._game = game
        self.console.log.debug("[green b]Loading game")
        self.console.history.clear()

        self.actions = RootActionManager()

        self.events = EventHandler()
        self.events.middlewares.append(GameMiddleware(self))
        self.commands = CommandManager(self.events)

        self.bestiary = Bestiary()
        self.world = World()
        self.quest_manager = QuestManager()
        self.executer = Executer(self)
        self.player = Player()
        self.clock = Clock()

        @listener(Event)
        def debug_event(event: Event):
            self.console.log.debug(f"Event: {event}")

        self.events.subscribe(debug_event)

        for component in registry.components:
            self.register(component)

        build(self)

    def set_state(self, state: GameState):
        self._game.state = state

    @property
    def state(self) -> GameState:
        return self._game.state

    @property
    def console(self) -> KrpgConsole:
        return self._game.console

    def register(self, component: Component) -> None:
        # TODO: rewrite to match?
        if isinstance(component, type):
            item = component()
            if isinstance(item, ActionManager):
                self.actions.submanagers.append(item)
                self.console.log.debug(f"Added action manager {item}")
            else:
                self.executer.extensions.append(item)
                self.console.log.debug(f"Added extension {item}")
        else:
            self.events.subscribe(component)
            self.console.log.debug(f"Added event subscribe {component}")

    def play(self) -> None:
        while True:
            actions = self.actions.actions
            actions |= {a.name: a for a in self.world.current_location.actions}
            command = self.console.prompt("> ", {n: a.description for n, a in actions.items()})
            if command and command in actions:
                actions[command].callback(self)
            if self.state == GameState.MENU:
                break


def main(debug: bool) -> None:
    game = GameBase()
    game.console.set_debug(debug)
    game.main()
