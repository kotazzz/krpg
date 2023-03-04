from __future__ import annotations

import zlib

import msgpack

from krpg.battle import BattleManager
from krpg.bestiary import Bestiary
from krpg.clock import Clock
from krpg.core.actions import ActionManager, action
from krpg.core.console import Console
from krpg.core.encoder import Encoder
from krpg.core.events import EventHandler
from krpg.core.logger import Logger
from krpg.core.scenario import parse
from krpg.executer import Executer
from krpg.player import Player
from krpg.presenter import Presenter
from krpg.world import World

DEBUG = True
__version__ = "8A"


class Game(ActionManager):
    def __init__(self):
        ActionManager.__init__(self)
        self.eh = EventHandler()
        for attr in filter(lambda x: x.startswith("on_"), dir(self)):
            cb = getattr(self, attr)
            self.eh.listen(attr[3:], cb)

        self.scenario = parse(open("scenario.krpg").read())
        self.savers: dict[str, tuple[callable, callable]] = {}
        self.running = True

        self.console = Console()
        self.encoder = Encoder()
        self.logger = Logger(file=False, level=DEBUG * 5)

        self.executer = Executer(self)
        self.clock = Clock(self)
        self.presenter = Presenter(self)
        self.player = Player(self)
        self.world = World(self)
        self.bestiary = Bestiary(self)
        self.battle = BattleManager(self)

    def expand_actions(self, actionmanager: ActionManager):
        self.logger.debug(f"Added ActionManager {actionmanager}")
        return super().expand_actions(actionmanager)

    def add_saver(self, name: str, save: callable, load: callable):
        def add_message(func, message):
            def deco(*args, **kwargs):
                self.logger.debug(message)
                return func(*args, **kwargs)

            return deco

        self.logger.debug(f"Added Savers {name!r}")
        self.savers[name] = (
            add_message(save, f"Saving {name}"),
            add_message(load, f"Loading {name}"),
        )

    def on_save(self, game: Game):
        data = {name: funcs[0]() for name, funcs in self.savers.items()}

        bdata = msgpack.packb(data)
        zdata = zlib.compress(bdata, level=9)
        encoded = game.encoder.encode(zdata, type=0)
        game.logger.debug(f"Data: {data}")
        game.console.print(f"[green]Код сохранения: [yellow]{encoded}[/]")

    def on_load(self, game: Game, failcb=None, successcb=None):
        while True:
            game.console.print("[green]Введите код сохранения (e - выход): [yellow]")
            encoded = input()
            game.console.print("[/]")
            try:
                if encoded == "e":
                    break
                zdata = game.encoder.decode(encoded, type=0)
                bdata = zlib.decompress(zdata)
                data = msgpack.unpackb(bdata)
                for name, funcs in self.savers.items():
                    funcs[1](data[name])
            except Exception as e:
                game.console.print(f"[red]Ошибка при загрузке игры: {e}[/]")
            else:
                game.console.print("[green]Игра загружена[/]")
                if successcb:
                    successcb()
                    game.eh.dispatch("load_done")
                return

        if failcb:
            failcb()

    def on_new_game(self):
        self.console.print("[green]Введите имя:[/]")
        # self.player.name = self.console.prompt(2)
        self.console.prompt(2)

        sec = self.scenario.first("init")
        for cmd in sec.children:
            self.executer.execute(cmd)

    def on_event(self, event, *args, **kwargs):
        self.logger.debug(f"{event} {args} {kwargs}")

    def on_post_init(self):
        c = self.console
        while self.running:
            cmd = c.prompt()
            self.eh.dispatch("command", command=cmd)

    def on_command(self, command):
        cmds = self.get_all_actions()
        if command in cmds:
            cmds[command].callback(self)
        else:
            self.console.print(f"[red]Неизвестная команда {command}[/]")
            self.console.print(f"[green]Доступные команды: {' '.join(cmds.keys())}[/]")

    def on_player_death(self):
        self.eh.dispatch("exit")

    def on_exit(self):
        self.running = False

    def main(self):
        c = self.console

        self.logger.debug(f"Version: {__version__}")
        self.logger.debug(f"Version: {__version__}")
        self.logger.debug(f"Executer: {self.executer}")
        self.logger.debug(f"Clock: {self.clock}")
        self.logger.debug(f"Player: {self.player}")
        self.logger.debug(f"World: {self.world}")
        self.logger.debug(f"Bestiary: {self.bestiary}")
        self.logger.debug(f"Game: {self}")

        class Flag:
            v = True

        while Flag.v:
            user = c.confirm("[green]Желаете загрузить сохранение? (yn): [/]")
            if user:
                self.eh.dispatch("load", self, successcb=lambda: setattr(Flag, "v", False))
            else:
                Flag.v = None

        if Flag.v == None:
            self.eh.dispatch("new_game")

        c.print(
            "[bold magenta]╭───╮ ╭─╮[bold red]       [bold blue]╭──────╮  [bold yellow]╭───────╮[bold green]╭───────╮\n"
            "[bold magenta]│   │ │ │[bold red]       [bold blue]│   ╭─╮│  [bold yellow]│       │[bold green]│       │\n"
            "[bold magenta]│   ╰─╯ │[bold red]╭────╮ [bold blue]│   │ ││  [bold yellow]│   ╭─╮ │[bold green]│   ╭───╯\n"
            "[bold magenta]│     ╭─╯[bold red]╰────╯ [bold blue]│   ╰─╯╰─╮[bold yellow]│   ╰─╯ │[bold green]│   │╭──╮\n"
            "[bold magenta]│     ╰─╮[bold red]       [bold blue]│   ╭──╮ │[bold yellow]│   ╭───╯[bold green]│   ││  │\n"
            "[bold magenta]│   ╭─╮ │[bold red]       [bold blue]│   │  │ │[bold yellow]│   │    [bold green]│   ╰╯  │\n"
            "[bold magenta]╰───╯ ╰─╯[bold red]       [bold blue]╰───╯  ╰─╯[bold yellow]╰───╯    [bold green]╰───────╯\n[/]"
        )

        c.print(
            "[magenta]K[red]-[blue]R[yellow]P[green]G[/] - Рпг игра, где вы изучаете мир и совершенствуетесь\n"
            "Сохранения доступны [red]только[/] в этой локации\n"
            "Задать имя персонажу можно [red]только один раз[/]!\n"
            "[blue]help[/] - Показать список команд\n"
            "[red]Игра находится на стадии тестирования![/]",
            min=0.002,
        )

        self.eh.dispatch("post_init")

    @action("exit", "Выйти из игры", "Основное")
    def exit(game: Game):
        game.console.print("Выход из игры")
        game.eh.dispatch("exit")

    @action("save", "Сохранить игру", "Основное")
    def save(game: Game):
        game.eh.dispatch("save", game=game)

    @action("load", "Загрузить игру", "Основное")
    def load(game: Game):
        game.eh.dispatch("load", game=game)

    @action("help", "Помощь", "Основное")
    def helps(game: Game):
        c = game.console
        for cat, cmds in game.get_all_categories().items():
            c.print(f"[red]{cat}[/]")
            for name, cmd in cmds.items():
                c.print(f"  [green]{name}[/] - {cmd.description}")

    def __repr__(self):
        return f"<Game as {ActionManager.__repr__(self)}>"

    __str__ = __repr__
