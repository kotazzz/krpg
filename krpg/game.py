from __future__ import annotations
from typing import Any, Callable
from rich.console import Group
from rich.align import Align
from rich.panel import Panel
from krpg.builder import Builder
from krpg.console import KrpgConsole
from krpg.data.consts import ABOUT, LOGO_GAME
from krpg.engine.actions import ActionManager, action
from krpg.engine.enums import GameState
from krpg.executer import Executer
from rich.text import Text


class RootActionManager(ActionManager):
    @action("exit")
    @staticmethod
    def action_exit(game: Game) -> None:
        game.state = GameState.MENU

    @action("test")
    @staticmethod
    def action_test(game: Game) -> None:
        game.console.print("Test action")


class Game:
    def __init__(self) -> None:
        self.console = KrpgConsole()
        self.state = GameState.MENU
        self.actions = RootActionManager()
        self.executer = Executer(self)
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


def main() -> None:
    game = Game()
    game.main()
