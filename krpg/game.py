from __future__ import annotations
from itertools import groupby
from typing import Any, Callable
from rich.console import Group
from rich.align import Align
from rich.panel import Panel
from krpg.builder import Builder
from krpg.console import KrpgConsole
from krpg.data.consts import ABOUT, LOGO_GAME
from krpg.engine.actions import Action, ActionCategory, ActionManager, action
from krpg.engine.enums import GameState
from krpg.engine.world import World
from krpg.entity.bestiary import Bestiary
from krpg.executer import Executer
from rich.text import Text


class RootActionManager(ActionManager):
    @action("exit", "Выйти из игры", "Игра")
    @staticmethod
    def action_exit(game: Game) -> None:
        game.state = GameState.MENU

    @action("history", "История команд", "Игра")
    @staticmethod
    def action_history(game: Game) -> None:
        c = game.console
        c.print(f"[green]История команд: [red]{' '.join(c.get_history())}")

    @action("help", "Показать команды", "Игра")
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


class Game:
    def __init__(self) -> None:
        self.console = KrpgConsole()
        self.state = GameState.MENU
        self.actions = RootActionManager()
        self.executer = Executer(self)
        self.bestiary = Bestiary()
        self.world = World()
        self.builder = Builder(self)

    def show_logo(self) -> None:
        centered_logo = Align(LOGO_GAME, align="center")
        centered_about = Align(
            Text(ABOUT, justify="center", style="green"), align="center", width=80
        )
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
        self.builder.build()

    def new_game(self) -> None:
        self.state = GameState.INIT
        self.init_game()
        self.state = GameState.PLAY
        try:
            self.play()
        except KeyboardInterrupt:
            self.console.print("Игра завершена")

    def play(self) -> None:
        while True:
            actions = self.actions.actions
            command = self.console.prompt(
                "> ", {n: a.description for n, a in actions.items()}
            )
            if command in actions:
                actions[command].callback(self)
            if self.state == GameState.MENU:
                break


def main(debug: bool) -> None:
    game = Game()
    game.console.set_debug(debug)
    game.main()
