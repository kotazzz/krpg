"""
Main game file. Run game with `python -m krpg` command
"""

from __future__ import annotations

import glob
import os
import random
import sys
import time
import zlib
from datetime import datetime
from enum import Enum
from hashlib import sha512
from itertools import groupby
from textwrap import wrap
from typing import Any, Callable, Literal

import msgpack  # type: ignore
from rich._spinners import SPINNERS
from rich.live import Live
from rich.spinner import Spinner

from krpg.actions import ActionManager, action
from krpg.battle import BattleManager
from krpg.bestiary import Bestiary
from krpg.builder import Builder
from krpg.clock import Clock
from krpg.console import KrpgConsole
from krpg.data.info import __version__  # noqa: BLK100
from krpg.data.info import ABOUT_TEXT, BRAND_COLORS, FAQ, TIMESHIFT
from krpg.data.splashes import SPLASHES
from krpg.diary import DiaryManager
from krpg.encoder import Encoder
from krpg.events import EventHandler, Events
from krpg.executer import Executer
from krpg.npc import NpcManager
from krpg.player import Player
from krpg.presenter import Presenter
from krpg.quests import QuestManager
from krpg.random import RandomManager
from krpg.scenario import Scenario
from krpg.settings import Settings
from krpg.stats import StatsManager
from krpg.world import World


class GameState(Enum):
    """Game states"""

    NONE = 0
    PLAYING = 1
    EXIT = 2
    DEAD = 3


class Game:
    """Main game class. Run game with `python -m krpg` command"""

    savers: dict[str, tuple[Callable, Callable]] = {}
    actions: ActionManager
    events: EventHandler
    encoder: Encoder
    random: RandomManager
    settings: Settings
    executer: Executer
    player: Player
    diary: DiaryManager
    presenter: Presenter
    battle_manager: BattleManager
    bestiary: Bestiary
    stats: StatsManager
    clock: Clock
    npc_manager: NpcManager
    world: World
    quest_manager: QuestManager
    builder: Builder
    start_time: int
    save_time: int
    scenario: Scenario

    def __init__(self, debug_mode: bool = False):
        self.version = __version__
        self.state = GameState.NONE
        self.console = KrpgConsole()
        self.log = self.console.log
        self.set_debug(debug_mode)
        self.main()

    def set_debug(self, value: bool):
        """Set debug mode

        Parameters
        ----------
        value : bool
            Debug mode. If True, debug messages will be displayed
        """
        self.debug = value
        self.console.setlevel(0 if self.debug else 30)

    def main(self):
        """Main game loop"""
        while True:
            try:
                self.main_menu()
            except Exception as e:  # noqa: PLW718
                self.log.exception(e)
                try:
                    if not self.console.confirm("[red]Перезапустить? (y/n): [/]"):
                        break
                except KeyboardInterrupt:
                    break
            except KeyboardInterrupt:
                break

        c = self.console
        c.print(f"[green]История команд: [red]{' '.join(c.get_history())}")
        c.print("[red b]Пока!")

    def new_game(self):
        """New game init wrapper. Show spinner if debug is False"""
        if not self.debug:
            spinner = random.choice(list(SPINNERS.keys()))
            spin_size = len(SPINNERS[spinner]["frames"][0]) + 1
            spin = Spinner(spinner, text="test", style="green")
            _reserve = self.console.log.debug

            lines = []

            def func(msg, *_, **__):
                nonlocal lines
                lines.append(msg)
                lines = lines[-3:]
                spin.update(text=f"\n{' ' * spin_size}".join(lines))
                time.sleep(random.random() / 10)

            self.console.log.debug = func
            with Live(spin, refresh_per_second=20) as _:  # type: ignore
                self.new_game_init()
                func("Завершение инициализации...")
                func("Подготовка...")
                func("⭐ Игра загружена")
            self.console.log.debug = _reserve
        else:
            self.new_game_init()

    def new_game_init(self) -> None:
        """New game init function. Called from `new_game` method"""
        self.start_time = self.save_time = self.timestamp()

        def init(obj: Any) -> Any:
            self.log.debug(f"Init [green]{obj.__class__.__name__}[/]: {obj}")
            return obj

        self.scenario: Scenario = init(Scenario())
        game_path = os.path.dirname(__file__)
        content_path = os.path.join(game_path, "content")
        # list files in krpg/content/**/*.krpg
        for filename in glob.glob(
            os.path.join(content_path, "**", "*.krpg"), recursive=True
        ):
            self.scenario.add_section(filename, content_path)
            self.log.debug(f"Loaded scenario {filename}")

        self.actions: ActionManager = init(ActionManager(self))
        self.events: EventHandler = init(EventHandler(self))
        self.encoder: Encoder = init(Encoder())
        self.random: RandomManager = init(RandomManager(self))
        self.settings: Settings = init(Settings(self))
        self.executer: Executer = init(Executer(self))
        self.player: Player = init(Player(self))
        self.diary: DiaryManager = init(DiaryManager(self))
        self.presenter: Presenter = init(Presenter(self))
        self.battle_manager: BattleManager = init(BattleManager(self))
        self.bestiary: Bestiary = init(Bestiary(self))
        self.stats: StatsManager = init(StatsManager(self))
        self.clock: Clock = init(Clock(self))
        self.npc_manager: NpcManager = init(NpcManager(self))
        self.world: World = init(World(self))
        self.quest_manager: QuestManager = init(QuestManager(self))
        self.builder: Builder = init(Builder(self))

    def main_menu(self):
        """Main menu loop"""
        c = self.console

        self.console.print(random.choice(BRAND_COLORS) + random.choice(SPLASHES))
        self.show_logo()
        self.console.set_bar(
            f"[magenta]K[/][red]-[/][blue]R[/][yellow]P[/][green]G[/] {random.choice(BRAND_COLORS)}{self.version}[/]"
        )
        while self.state != GameState.PLAYING:
            menu = {
                "start": "Начать новую игру",
                "load": "Загрузить сохранение",
                "credits": "Авторы игры",
                "exit": "Выйти",
            }
            select = self.console.menu(
                5,
                list(menu.keys()),
                view=lambda k: f"{menu[k]}",
                title="[green b]Игровое меню",
            )

            if select == "start":
                self.new_game()
                c.print(
                    "Задать имя персонажу можно [red]только один раз[/]!\n"
                    "  [blue]help[/] - Показать список команд\n"
                    "  [blue]guide[/] - Справка и помощь, как начать\n"
                )
                c.print("[green]Введите имя:[/]")
                self.player.name = c.prompt(2)
                c.print("[green]Введите сид мира (или оставьте пустым):[/]")
                src = c.prompt(2, allow_empty=True)
                if src:
                    seed = (
                        int(src)
                        if src.isnumeric()
                        else (
                            int(
                                int.from_bytes(sha512(src.encode()).digest(), "big")
                                ** 0.1
                            )
                        )
                    )
                    self.log.debug(f"New seed: {seed} from {src!r}")
                    self.random.set_seed(seed)
                else:
                    self.log.debug(f"Using by default: {self.random.seed}")
                init = self.scenario.first_section("init")
                self.executer.create_block(init).run()
                self.world.set_default()
                self.events.dispatch(Events.STATE_CHANGE, state=GameState.PLAYING)

            elif select == "load":
                self.new_game()
                self.events.dispatch(Events.LOAD)
            elif select == "credits":
                self.action_credits.callback(self)
            elif select == "exit":
                sys.exit()

    def playing(self):
        """Playing loop"""
        try:
            while self.state == GameState.PLAYING:
                self.console.set_bar(f"[yellow]{self.player.name}[/]")
                actions = self.actions.get_actions()
                cmds_data = {cmd.name: cmd.description for cmd in actions}
                cmd = self.console.prompt(1, cmds_data)
                self.events.dispatch(Events.COMMAND, command=cmd)
        except KeyboardInterrupt:
            self.console.print("[red]Выход из игры[/]")
            self.state = GameState.NONE

    def timestamp(self):
        """
        Get current timestamp converted by shift constant
        """
        return int(time.time()) - TIMESHIFT

    def add_actions(self, obj: object):
        """Add actions from object

        Parameters
        ----------
        obj : object
            Object with actions
        """
        self.log.debug(
            f"  [yellow3]Add submanager [yellow]{obj.__class__.__name__}", stacklevel=2
        )
        self.actions.submanagers.append(obj)

    def add_saver(self, name: str, save: Callable, load: Callable):
        """Add saver

        Parameters
        ----------
        name : str
            name of saver
        save : Callable
            save function, called when game saving
        load : Callable
            load function, called when game loading
        """

        def add_message(func, message):
            def deco(*args, **kwargs):
                self.log.debug(message)
                return func(*args, **kwargs)

            return deco

        self.log.debug(f"  [yellow3]Add Savers {name!r}", stacklevel=2)
        self.savers[name] = (
            add_message(save, f"Saving {name}"),
            add_message(load, f"Loading {name}"),
        )

    def on_dead(self):
        """Called when player dead"""
        self.events.dispatch(Events.STATE_CHANGE, GameState.DEAD)

    def on_state_change(self, state: GameState):
        """Called when game state changed

        Parameters
        ----------
        state : GameState
            New game state
        """
        old = self.state
        self.state = state
        if old != GameState.PLAYING and state == GameState.PLAYING:
            self.playing()

    def on_save(self):
        """Called when game saving

        Raises
        ------
        TypeError
            When msgpack.packb return not bytes
        """
        self.save_time = self.timestamp()
        data = {name: funcs[0]() for name, funcs in self.savers.items()}
        self.log.debug(f"Data: {data}")
        data = [
            i[1] for i in sorted(data.items(), key=lambda item: item[0])
        ]  # EXPEREMENTAL
        bdata = msgpack.packb(data)
        if not isinstance(bdata, bytes):
            raise TypeError(f"msgpack.packb return {type(bdata)}")
        zdata = zlib.compress(bdata, level=9)
        select = self.console.menu(5, list(self.encoder.abc.keys()))
        encoded = self.encoder.encode(zdata, select)
        self.log.debug(f"Data: {data}")
        self.log.debug(f"BinData ({len(bdata)}): {bdata.hex()}")
        self.log.debug(
            f"Zipped from {len(bdata)} to {len(zdata)}, string: {len(encoded)}"
        )
        self.console.print(
            f"[green]Код сохранения: [yellow]{list(self.encoder.abc.keys()).index(select)}{encoded}[/]"
        )

    def on_load(self):
        """Called when game loading"""
        while True:
            self.console.print("[green]Введите код сохранения (e - выход):")
            encoded = self.console.prompt(2, raw=True)
            try:
                if encoded == "e":
                    break
                # TODO: Move to encoder
                select, encoded = encoded[0], encoded[1:]
                select = list(self.encoder.abc.keys())[int(select)]
                zdata = self.encoder.decode(encoded, select)
                bdata = zlib.decompress(zdata)
                data = msgpack.unpackb(bdata)

                funcs = dict(
                    sorted(self.savers.items(), key=lambda item: item[0])
                ).values()  # EXPEREMENTAL
                for i, (_, load) in enumerate(funcs):
                    load(data[i])
                # for name, funcs in self.savers.items():
                #     funcs[1](data[name])
            except Exception as e:  # noqa: PLW718
                self.console.print(f"[red]Ошибка при загрузке игры: {e}[/]")
                if self.debug:
                    self.log.exception(e)
            else:
                self.console.print("[green]Игра загружена[/]")
                self.events.dispatch(Events.STATE_CHANGE, state=GameState.PLAYING)
                return

    def on_event(self, event: Events, *args, **kwargs):
        """Logs all events

        Parameters
        ----------
        event : Events
            Event
        """
        self.log.debug(f"[b yellow]{event}[/] {args} {kwargs}")

    def on_command(self, command: str):
        """Called when command entered

        Parameters
        ----------
        command : str
            Command name
        """
        actions = self.actions.get_actions()
        cmds = {cmd.name: cmd for cmd in actions}
        if command in cmds:
            cmds[command].callback(self)
        else:
            self.console.print(f"[red]Неизвестная команда {command}[/]")
            self.console.print(f"[green]Доступные команды: {' '.join(cmds.keys())}[/]")

    def show_logo(self):
        """Show game logo"""
        self.console.print(
            (
                "{0}╭───╮ ╭─╮{1}       {2}╭──────╮  {3}╭───────╮{4}╭───────╮\n"
                "{0}│   │ │ │{1}       {2}│   ╭─╮│  {3}│       │{4}│       │\n"
                "{0}│   ╰─╯ │{1}╭────╮ {2}│   │ ││  {3}│   ╭─╮ │{4}│   ╭───╯\n"
                "{0}│     ╭─╯{1}╰────╯ {2}│   ╰─╯╰─╮{3}│   ╰─╯ │{4}│   │╭──╮\n"
                "{0}│     ╰─╮{1}       {2}│   ╭──╮ │{3}│   ╭───╯{4}│   ││  │\n"
                "{0}│   ╭─╮ │{1}       {2}│   │  │ │{3}│   │    {4}│   ╰╯  │\n"
                "{0}╰───╯ ╰─╯{1}       {2}╰───╯  ╰─╯{3}╰───╯    {4}╰───────╯\n".format(
                    *BRAND_COLORS
                )
            )
        )
        self.console.print(
            "[magenta]K[/][red]-[/][blue]R[/][yellow]P[/][green]G[/] - Вас ждет увлекательное путешествие по миру, \n"
            "где Вы будете сражаться с монстрами, выполнять квесты и становиться\n"
            "все сильнее и сильнее. Сможете ли Вы стать настоящим героем?\n"
        )

    @action("history", "История команд", "Игра")
    @staticmethod
    def action_history(game: Game):
        """Show command history

        Parameters
        ----------
        game : Game
            Game instance
        """
        c = game.console
        c.print(f"[green]История команд: [red]{' '.join(c.get_history())}")

    @action("help", "Показать команды", "Игра")
    @staticmethod
    def action_help(game: Game):
        """Show commands

        Parameters
        ----------
        game : Game
            Game instance
        """
        actions = sorted(game.actions.get_actions(), key=lambda x: x.category)
        cmdcat = groupby(actions, key=lambda x: x.category)
        for cat, cmds in cmdcat:
            game.console.print(f"[b red]{cat}")
            for cmd in cmds:
                game.console.print(f" [green]{cmd.name}[/] - {cmd.description}")

    @action("about", "Авторы, благодарности и об игре", "Игра")
    @staticmethod
    def action_credits(game: Game):
        """Show credits

        Parameters
        ----------
        game : Game
            Game instance
        """
        game.show_logo()
        game.console.print(ABOUT_TEXT)

    @action("info", "Об текущей игре", "Игра")
    @staticmethod
    def action_about(game: Game):
        """Show game info

        Parameters
        ----------
        game : Game
            Game instance
        """

        def datefmt(ts):
            return datetime.fromtimestamp(ts + TIMESHIFT).strftime("%d.%m.%Y %H:%M")

        game.console.print(
            f"--- [blue]KRPG[/] by [green]KOTAZ[/] ---\n"
            f"[b green]Подробнее:       [/][magenta]credits[/]\n"
            f"[green  ]Версия:          [/][yellow]{game.version}[/]\n"
            f"[green  ]Игрок:           [/][yellow]{game.player.name}[/]\n"
            f"[green  ]Дата начала:     [/][yellow]{datefmt(game.start_time)}[/]\n"
            f"[green  ]Дата сохранения: [/][yellow]{datefmt(game.save_time)}[/]\n"
            f"[green  ]Сид:             [/][yellow]{game.random.seed}[/]\n"
        )

    @action("guide", "Игровая справка", "Игра")
    @staticmethod
    def action_guide(game: Game):
        """Show game guide

        Parameters
        ----------
        game : Game
            Game instance
        """
        while True:
            game.console.print("[bold green]Гайды и справка[/]")
            game.console.print("[green]Выберите секцию (e - Выход)[/]")
            select = game.console.menu(2, list(FAQ.items()), "e", lambda x: x[0])
            if not select:
                return
            text = wrap(select[1], replace_whitespace=False)
            game.console.print("\n".join(text))

    @action("exit", "Выйти из игры", "Игра")
    @staticmethod
    def action_exit(game: Game):
        """Exit from game

        Parameters
        ----------
        game : Game
            Game instance
        """
        game.state = GameState.EXIT

    @action("save", "Сохранить игру", "Игра")
    @staticmethod
    def action_save(game: Game):
        """Save game

        Parameters
        ----------
        game : Game
            Game instance
        """
        game.events.dispatch(Events.SAVE)

    @action("load", "Загрузить игру", "Игра")
    @staticmethod
    def action_load(game: Game):
        """Load game

        Parameters
        ----------
        game : Game
            Game instance
        """
        game.events.dispatch(Events.LOAD)

    def __repr__(self) -> Literal["<Game>"]:
        return "<Game>"
