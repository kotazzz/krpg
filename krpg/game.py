from __future__ import annotations

import code
import logging
import sys
from itertools import groupby
from typing import Any, Callable

from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from krpg.engine.builder import Builder
from krpg.console import KrpgConsole
from krpg.data.consts import ABOUT, LOGO_GAME, __version__
from krpg.actions import Action, ActionCategory, ActionManager, action
from krpg.engine.enums import GameState
from krpg.engine.quests import QuestManager
from krpg.engine.world import World
from krpg.entity.bestiary import Bestiary
from krpg.engine.executer import Executer, Extension


class RootActionManager(ActionManager):
    @action("exit", "Выйти из игры", ActionCategory.GAME)
    @staticmethod
    def action_exit(game: Game) -> None:
        game.state = GameState.MENU

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


class Game:
    actions: RootActionManager
    executer: Executer
    bestiary: Bestiary
    world: World
    quest_manager: QuestManager
    builder: Builder

    def __init__(self) -> None:
        self.console = KrpgConsole()
        self.state = GameState.MENU

    def add_extension(self, extension: Extension) -> None:
        self.executer.extensions.append(extension)
        self.console.log.debug(f"Added extension {extension}")

    def add_action_manager(self, manager: ActionManager) -> None:
        self.actions.submanagers.append(manager)
        self.console.log.debug(f"Added action manager {manager}")

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
            choice = self.console.menu("Добро пожаловать", options)
            if not choice:
                break
            choice()

    def init_game(self) -> None:
        self.actions = RootActionManager()
        self.executer = Executer(self)
        self.bestiary = Bestiary()
        self.world = World()
        self.quest_manager = QuestManager(self)
        self.builder = Builder(self)
        self.console.log.debug(self.world)
        self.builder.build()

    def new_game(self) -> None:
        self.state = GameState.INIT
        self.init_game()
        self.state = GameState.PLAY
        try:
            self.play()
        except (KeyboardInterrupt, EOFError):
            self.console.print("Игра завершена")
            self.state = GameState.MENU

    def play(self) -> None:
        while True:
            actions = self.actions.actions
            command = self.console.prompt("> ", {n: a.description for n, a in actions.items()})
            if command in actions:
                actions[command].callback(self)
            if self.state == GameState.MENU:
                break


def main(debug: bool) -> None:
    game = Game()
    game.console.set_debug(debug)
    game.main()
