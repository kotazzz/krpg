from __future__ import annotations
from krpg.builder import Builder
from krpg.console import KrpgConsole
from krpg.data.consts import LOGO_GAME
from krpg.engine.actions import ActionManager, action
from krpg.engine.enums import GameState
from krpg.executer import Executer


class RootActionManager(ActionManager):
    @action("exit")
    @staticmethod
    def action_exit(game: Game):
        game.state = GameState.MENU

    @action("test")
    @staticmethod
    def action_test(game: Game):
        game.console.print("Test action")


class Game:
    def __init__(self) -> None:
        self.console = KrpgConsole()
        self.state = GameState.MENU
        self.actions = RootActionManager()
        self.executer = Executer(self)
        self.builder = Builder(self)

    def main(self):
        options = {
            "Начать новую игру": self.new_game,
            "Выйти": exit,
        }
        self.console.print(LOGO_GAME)
        while True:
            choice = self.console.menu("[red]Добро пожаловать[/]", options)
            if not choice:
                break
            choice()

    def init_game(self):
        self.builder.build()

    def new_game(self):
        self.state = GameState.INIT
        self.init_game()
        self.state = GameState.PLAY
        try:
            self.play()
        except KeyboardInterrupt:
            self.console.print("Игра завершена")

    def play(self):
        while True:
            actions = self.actions.actions
            command = self.console.prompt(
                "> ", {n: a.description for n, a in actions.items()}
            )
            if command in actions:
                actions[command].callback(self)
            if self.state == GameState.MENU:
                break


def main():
    game = Game()
    game.main()
