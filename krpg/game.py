from __future__ import annotations

import code
import logging
import sys
from itertools import groupby
from typing import Any, Callable, Generator
import zlib

import attr
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from krpg.components import registry, Component
from krpg.commands import CommandManager, command
from krpg.encoder import create_save, load_save
from krpg.engine.builder import build
from krpg.console import KrpgConsole
from krpg.data.consts import ABOUT, LOGO_GAME, __version__
from krpg.actions import Action, ActionCategory, ActionManager, ActionState, action
from krpg.engine.clock import Clock
from krpg.engine.enums import GameState
from krpg.engine.npc import NpcManager
from krpg.engine.player import Player
from krpg.engine.quests import QuestManager
from krpg.engine.random import RandomManager
from krpg.engine.world import World
from krpg.bestiary import BESTIARY
from krpg.engine.executer import Executer, NamedScript, run_scenario
from krpg.events import Event, EventHandler, listener
from krpg.events_middleware import GameEvent, GameMiddleware
from krpg.saves import Savable


@attr.s(auto_attribs=True)
class StateChange(Event):
    new_state: GameState


@attr.s(auto_attribs=True)
class ActionExecuted(GameEvent):
    action: Action


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

        actions = sorted(game.actions.actions, key=get_key)
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
                    game.console.print(
                        "[red b]Выполнение этой команды приведет к завершению игры. Для подтверждения введите exit(1)\nДля возврата в игру используйте Ctrl + D (или Z)[/]"
                    )

            def __repr__(self) -> str:
                return "Команда приведет к закрытию. Используйте exit(1) для подтверждения"

        v = ".".join(map(str, sys.version_info[:3]))
        welcome = f"Python {v}, KRPG {__version__}"
        code.InteractiveConsole(locals={"game": game, "exit": ExitAlt()}).interact(welcome)

    @action("save", "Сохранить игру", ActionCategory.GAME)
    @staticmethod
    def action_save(game: Game) -> None:
        game.console.print("[green]Игра сохранена[/]")
        save_data = game.serialize()
        if game.console.log.level == logging.DEBUG:
            game.console.console.print("Сохраненные данные:", save_data)
        save = create_save(save_data)
        game.console.print("[yellow]Сохраненные данные:[cyan]", save)


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

    def load_bestiary(self, reset: bool = True):  # TODO: is reset really needed?
        if not reset and not BESTIARY.data:
            build(bestiary=BESTIARY, console=self.console)
        else:
            BESTIARY.data.clear()
            build(bestiary=BESTIARY, console=self.console)

    def main(self) -> None:
        self.load_bestiary(False)

        options: dict[str, Callable[..., Any]] = {
            "Начать новую игру": self.new_game,
            "Загрузить сохранение": self.load_game,
            "Перезапустить сценарий": self.load_bestiary,
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
        self.handle_loop(game_loop)

    def load_game(self) -> None:
        self.state = GameState.INIT
        self.console.print("Загрузка игры...")
        try:
            save_data = self.console.session.prompt("Введите данные для загрузки: ")
            if not save_data:
                self.console.print("[red]Ошибка: ввод пуст[/]")
                return
            cleaned = save_data.strip().replace("\n", "").replace(" ", "")

            data = load_save(cleaned)
        except ValueError:
            self.console.print("[red]Ошибка: данные невалидны[/]")
        except zlib.error:
            self.console.print("[red]Ошибка: данные сжаты неверно[/]")
        except KeyboardInterrupt:
            self.console.print("[red]Ошибка: загрузка прервана[/]")
        else:
            game_loop = Game.deserialize(data, self)
            self.state = GameState.PLAY
            self.handle_loop(game_loop)

    def handle_loop(self, loop: Game) -> None:
        # TODO: Add graceful exit
        try:
            loop.play()
        except (KeyboardInterrupt, EOFError):
            self.console.print("Игра завершена")
            self.console.print("[red]История команд: ", self.console.history)
            self.console.print("[red]Ваше сохранение: ", create_save(loop.serialize()))
            self.state = GameState.MENU


class Game(Savable):
    def _pre_init(self) -> None:
        self.console.log.debug("[green b]Loading game")
        self.console.history.clear()
        self.actions = RootActionManager()
        self.events = EventHandler()
        self.events.middlewares.append(GameMiddleware(self))
        self.commands = CommandManager(self.events)

    def __init__(self, game: GameBase) -> None:
        self._game = game
        self._pre_init()
        self.world = World()
        self.npc_manager = NpcManager()
        self.quest_manager = QuestManager()
        self.executer = Executer(self)
        self.player = Player()
        self.clock = Clock()
        self.random = RandomManager()
        self._post_init()
        init = BESTIARY.get_entity_by_id("init", NamedScript)
        if init:
            self.commands.execute(run_scenario(self.executer, init))
        else:
            self.console.log.debug("Init script not found")

    def serialize(self) -> dict[str, Any]:
        # TODO: Use component to find all root items
        data: dict[str, Any] = {
            "world": self.world.serialize(),
            "npc_manager": self.npc_manager.serialize(),
            "quest_manager": self.quest_manager.serialize(),
            "executer": self.executer.serialize(),
            "player": self.player.serialize(),
            "clock": self.clock.serialize(),
            "random": self.random.serialize(),
        }
        return data

    @classmethod
    def deserialize(cls, data: dict[str, Any], game: GameBase) -> Game:
        self = cls.__new__(cls)
        self._game = game
        self._pre_init()

        self.world = World.deserialize(data.get("world", {}))
        self.npc_manager = NpcManager.deserialize(data.get("npc_manager", {}))
        self.quest_manager = QuestManager.deserialize(data.get("quest_manager", {}))
        self.executer = Executer.deserialize(data.get("executer", {}), self)
        self.player = Player.deserialize(data.get("player", {}))
        self.clock = Clock.deserialize(data.get("clock", {}))
        self.random = RandomManager.deserialize(data.get("random", {}))
        self._post_init()
        return self

    def _post_init(self) -> None:
        @listener(Event)
        def debug_event(event: Event):
            self.console.log.debug(f"Event: {event}")

        self.events.subscribe(debug_event)
        for component in registry.components:
            self.register(component)

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
            actions += self.world.current_location.actions

            self.execute_action(actions)
            if self.state == GameState.MENU:
                break

    def execute_action(self, actions: list[Action], prompt: str = "> ", interactive: bool = False) -> Action | None:
        def _name(a: Action):
            state = a.check(self)
            return f"{'red' if state == ActionState.LOCKED else ''}{a.description}"

        actions_dict = {a.name: a for a in actions if (state := a.check(self)) != ActionState.HIDDEN}
        if interactive:
            action = self.console.select(prompt, {_name(a): a for a in actions if (state := a.check(self)) != ActionState.HIDDEN}, True)
        else:
            command = self.console.prompt(prompt, {a.name: a.description for a in actions})
            action = actions_dict.get(command or "")
        if not action:
            return None
        state = action.check(self)
        if state == ActionState.ACTIVE:
            action.callback(self)
            return action
        elif state == ActionState.LOCKED:
            self.console.print("Действие заблокировано")
        return None


def main(debug: bool) -> None:
    game = GameBase()
    game.console.set_debug(debug)
    game.main()
