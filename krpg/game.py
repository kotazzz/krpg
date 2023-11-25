from __future__ import annotations
import glob
import os

import random
import time
from typing import Literal
import zlib
from datetime import datetime
from hashlib import sha512
from itertools import groupby
from textwrap import wrap

import msgpack
from rich.live import Live
from rich.spinner import SPINNERS, Spinner

import krpg.game
from krpg.actions import ActionManager, action
from krpg.battle import BattleManager
from krpg.bestiary import Bestiary
from krpg.builder import Builder
from krpg.clock import Clock
from krpg.console import KrpgConsole
from krpg.data.info import BRAND_COLORS, TIMESHIFT, __version__, ABOUT_TEXT, FAQ
from krpg.data.splashes import SPLASHES
from krpg.diary import Diary
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
from enum import Enum


class GameState(Enum):
    NONE = 0
    PLAYING = 1
    EXIT = 2
    DEAD = 3


class Game:
    savers: dict[str, set[callable, callable]] = {}

    def __init__(self, debug_mode: bool = False):
        self.version = __version__
        self.state = GameState.NONE
        self.console = KrpgConsole()
        self.log = self.console.log
        self.set_debug(debug_mode)
        self.main()

    def set_debug(self, value: bool):
        self.debug = value
        self.console.setlevel(0 if self.debug else 30)

    def main(self):
        while True:
            try:
                self.main_menu()
            except Exception as e:
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
        if not self.debug:
            spinner = random.choice(list(SPINNERS.keys()))
            spin_size = len(SPINNERS[spinner]["frames"][0]) + 1
            spin = Spinner(spinner, text="test", style="green")
            _reserve = self.console.log.debug
            lines = []

            def func(t, **_):
                nonlocal lines
                lines.append(t)
                lines = lines[-3:]
                spin.update(text=f"\n{' '*spin_size}".join(lines))
                time.sleep(random.random() / 10)

            self.console.log.debug = func
            with Live(spin, refresh_per_second=20) as live:
                self.new_game_init()
                func("Завершение инициализации...")
                func("Подготовка...")
                func("⭐ Игра загружена")
            self.console.log.debug = _reserve
        else:
            self.new_game_init()

    def new_game_init(self):
        self.start_time = self.save_time = self.timestamp()

        def init(obj: object) -> object:
            self.log.debug(f"Init [green]{obj.__class__.__name__}[/]: {obj}")
            return obj

        self.scenario: Scenario = init(Scenario())
        game_path = os.path.dirname(krpg.game.__file__)
        content_path = os.path.join(game_path, "content")
        # list files in krpg/content/**/*.krpg
        for filename in glob.glob(os.path.join(content_path, "**", "*.krpg"), recursive=True):
            self.scenario.add_section(filename, content_path)
            self.log.debug(f"Loaded scenario {filename}: {self.scenario}")
        
        self.actions: ActionManager = init(ActionManager(self))
        self.events: EventHandler = init(EventHandler(self))
        self.encoder: Encoder = init(Encoder())
        self.random: RandomManager = init(RandomManager(self))
        self.settings: Settings = init(Settings(self))
        self.executer: Executer = init(Executer(self))
        self.player: Player = init(Player(self))
        self.diary: Diary = init(Diary(self))
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
                c.print(f"[green]Введите имя:[/]")
                self.player.name = c.prompt(2)
                c.print(f"[green]Введите сид мира (или оставьте пустым):[/]")
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
                init = self.scenario.first("init")
                self.executer.create_block(init).run()
                self.world.set()
                self.world.current.locked = False
                self.events.dispatch(Events.STATE_CHANGE, state=GameState.PLAYING)

            elif select == "load":
                self.new_game()
                self.events.dispatch(Events.LOAD)
            elif select == "credits":
                self.action_credits.callback(self)
            elif select == "exit":
                exit()

    def playing(self):

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
        return int(time.time()) - TIMESHIFT

    def add_actions(self, obj: object):
        self.log.debug(
            f"  [yellow3]Add submanager [yellow]{obj.__class__.__name__}", stacklevel=2
        )
        self.actions.submanagers.append(obj)

    def add_saver(self, name: str, save: callable, load: callable):
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
        self.events.dispatch(Events.STATE_CHANGE, GameState.DEAD)

    def on_state_change(self, state: GameState):
        old = self.state
        self.state = state
        if old != GameState.PLAYING and state == GameState.PLAYING:
            self.playing()

    def on_save(self):
        self.save_time = self.timestamp()
        data = {name: funcs[0]() for name, funcs in self.savers.items()}
        self.log.debug(f"Data: {data}")
        data = [
            i[1] for i in sorted(data.items(), key=lambda item: item[0])
        ]  # EXPEREMENTAL
        bdata = msgpack.packb(data)
        zdata = zlib.compress(bdata, level=9)
        select = self.console.menu(5, list(self.encoder.abc.keys()))
        encoded = self.encoder.encode(zdata, type=select)
        self.log.debug(f"Data: {data}")
        self.log.debug(f"BinData ({len(bdata)}): {bdata.hex()}")
        self.log.debug(
            f"Zipped from {len(bdata)} to {len(zdata)}, string: {len(encoded)}"
        )
        self.console.print(
            f"[green]Код сохранения: [yellow]{list(self.encoder.abc.keys()).index(select)}{encoded}[/]"
        )

    def on_load(self):
        while True:
            self.console.print("[green]Введите код сохранения (e - выход):")
            encoded = self.console.prompt(2, raw=True)
            try:
                if encoded == "e":
                    break
                # TODO: Move to encoder
                select, encoded = encoded[0], encoded[1:]
                select = list(self.encoder.abc.keys())[int(select)]
                zdata = self.encoder.decode(encoded, type=select)
                bdata = zlib.decompress(zdata)
                data = msgpack.unpackb(bdata)

                funcs = dict(
                    sorted(self.savers.items(), key=lambda item: item[0])
                ).values()  # EXPEREMENTAL
                for i, (save, load) in enumerate(funcs):
                    load(data[i])
                # for name, funcs in self.savers.items():
                #     funcs[1](data[name])
            except Exception as e:
                self.console.print(f"[red]Ошибка при загрузке игры: {e}[/]")
                if self.debug:
                    self.log.exception(e)
            else:
                self.console.print("[green]Игра загружена[/]")
                self.events.dispatch(Events.STATE_CHANGE, state=GameState.PLAYING)
                return

    def on_event(self, event, *args, **kwargs):
        self.log.debug(f"[b yellow]{event}[/] {args} {kwargs}")

    def on_command(self, command):
        actions = self.actions.get_actions()
        cmds = {cmd.name: cmd for cmd in actions}
        if command in cmds:
            cmds[command].callback(self)
            self.clock.wait(cmds[command].time)
        else:
            self.console.print(f"[red]Неизвестная команда {command}[/]")
            self.console.print(f"[green]Доступные команды: {' '.join(cmds.keys())}[/]")

    def show_logo(self):
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
    def action_history(game: Game):
        c = game.console
        c.print(f"[green]История команд: [red]{' '.join(c.get_history())}")

    @action("help", "Показать команды", "Игра")
    def action_help(game: Game):
        actions = sorted(game.actions.get_actions(), key=lambda x: x.category)
        cmdcat = groupby(actions, key=lambda x: x.category)
        for cat, cmds in cmdcat:
            game.console.print(f"[b red]{cat}")
            for cmd in cmds:
                game.console.print(f" [green]{cmd.name}[/] - {cmd.description}")

    @action("about", "Авторы, благодарности и об игре", "Игра")
    def action_credits(game: Game):
        game.show_logo()
        game.console.print(ABOUT_TEXT)

    @action("info", "Об текущей игре", "Игра")
    def action_about(game: Game):
        datefmt = lambda ts: datetime.fromtimestamp(ts + TIMESHIFT).strftime(
            "%d.%m.%Y %H:%M"
        )
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
    def action_guide(game: Game):
        while True:
            game.console.print("[bold green]Гайды и справка[/]")
            game.console.print("[green]Выберите секцию (e - Выход)[/]")
            select = game.console.menu(2, list(FAQ.items()), "e", lambda x: x[0])
            if not select:
                return
            else:
                text = wrap(select[1], replace_whitespace=False)
                game.console.print("\n".join(text))

    @action("exit", "Выйти из игры", "Игра")
    def action_exit(game: Game):
        game.state = GameState.EXIT

    @action("save", "Сохранить игру", "Игра")
    def action_save(game: Game):
        game.events.dispatch(Events.SAVE)

    @action("load", "Загрузить игру", "Игра")
    def action_load(game: Game):
        game.events.dispatch(Events.LOAD)

    def __repr__(self) -> Literal['<Game>']:
        return "<Game>"
