from __future__ import annotations
from itertools import groupby
import msgpack
import zlib
from krpg.console import KrpgConsole
from krpg.actions import ActionManager, action
from krpg.events import EventHandler
from krpg.scenario import parse
from krpg.encoder import Encoder
from krpg.executer import Executer
from krpg.player import Player
from krpg.builder import Builder
from krpg.world import World

__version__ = "8B"
DEBUG = True


class Game:
    version = __version__
    debug = DEBUG
    def __init__(self):
        self.state = "none"

        self.console = KrpgConsole()
        self.log = self.console.log
        self.log.setLevel(DEBUG * 5)
        debug = self.log.debug

        self.actions = ActionManager()
        debug(f"ActionManager: {self.actions}")

        self.add_actions(self)
        self.encoder = Encoder()
        debug(f"Encoder: {self.encoder}")

        self.events = EventHandler(locked=True)
        debug(f"EventHandler: {self.events}")

        for attr in filter(lambda x: x.startswith("on_"), dir(self)):
            cb = getattr(self, attr)
            self.events.listen(attr[3:], cb)
            debug(f"Added listener for {attr[3:]}")

        scenario = open("scenario.krpg").read()
        self.scenario_hash = f"{zlib.crc32(scenario.encode()):x}"
        self.scenario = parse(scenario)
        debug(f"Loaded scenario with {len(self.scenario.children)} items")

        self.savers: dict[str, set[callable, callable]] = {}
        

        self.executer = Executer(self)
        debug(f"Init Executer: {self.executer}")

        self.player = Player(self)
        debug(f"Init Player: {self.player}")

        self.world = World()
        debug(f"Init World: {self.world}")
        self.builder = Builder(self)
        debug(f"Starting build world...")
        self.builder.build()

    def add_actions(self, obj: object):
        self.log.debug(f"Add submanager {obj}")
        self.actions.submanagers.append(obj)

    @action("help", "Показать помощь", "Игра")
    def action_help(game: Game):
        cmdcat = groupby(game.actions.get_actions(), key=lambda x: x.category)
        for cat, cmds in cmdcat:
            game.console.print(f"[b red]{cat}")
            for cmd in cmds:
                game.console.print(f" [green]{cmd.name}[/] - {cmd.description}")

    @action("exit", "Выйти из игры", "Игра")
    def action_exit(game: Game):
        game.state = exit

    @action("save", "Сохранить игру", "Игра")
    def action_save(game: Game):
        game.events.dispatch("save")

    @action("load", "Загрузить игру", "Игра")
    def action_load(game: Game):
        game.events.dispatch("load")

    def add_saver(self, name: str, save: callable, load: callable):
        def add_message(func, message):
            def deco(*args, **kwargs):
                self.log.debug(message)
                return func(*args, **kwargs)

            return deco

        self.log.debug(f"Added Savers {name!r}")
        self.savers[name] = (
            add_message(save, f"Saving {name}"),
            add_message(load, f"Loading {name}"),
        )

    def on_state_change(self, state):
        self.state = state

    def on_save(self):
        data = {name: funcs[0]() for name, funcs in self.savers.items()}
        bdata = msgpack.packb(data)
        zdata = zlib.compress(bdata, level=9)
        encoded = self.encoder.encode(zdata, type=0)
        self.log.debug(f"Data: {data}")
        self.console.print(f"[green]Код сохранения: [yellow]{encoded}[/]")

    def on_load(self, failcb=None, successcb=None):
        while True:
            self.console.print("[green]Введите код сохранения (e - выход):")
            encoded = self.console.prompt(2, raw=True)
            try:
                if encoded == "e":
                    break
                zdata = self.encoder.decode(encoded, type=0)
                bdata = zlib.decompress(zdata)
                data = msgpack.unpackb(bdata)
                for name, funcs in self.savers.items():
                    funcs[1](data[name])
            except Exception as e:
                self.console.print(f"[red]Ошибка при загрузке игры: {e}[/]")
                if not self.debug:
                    self.log.exception(e)
            else:
                self.console.print("[green]Игра загружена[/]")
                if successcb:
                    successcb()
                    self.eh.dispatch("load_done")
                return

        if failcb:
            failcb()

    def on_event(self, event, *args, **kwargs):
        self.log.debug(f"{event} {args} {kwargs}")

    def on_command(self, command):
        actions = self.actions.get_actions()
        cmds = {cmd.name: cmd for cmd in actions}
        if command in cmds:
            cmds[command].callback(self)
        else:
            self.console.print(f"[red]Неизвестная команда {command}[/]")
            self.console.print(f"[green]Доступные команды: {' '.join(cmds.keys())}[/]")

    def main(self):
        try:
            self.run()
        except Exception as e:
            self.log.exception(e)

    def run(self):
        self.log.debug("Hello, world!")
        self.events.unlock()
        c = self.console
        success = lambda: self.events.dispatch("state_change", state="playing")
        while self.state != "playing":
            c.print(f"[yellow]Желаете загрузить сохранение? (yn)[/]")
            if c.confirm(1):
                self.events.dispatch("load", successcb=success)
            else:
                c.print(f"[green]Введите имя:[/]")
                self.player.name = c.prompt(2)
                success()
        try:
            while True:
                actions = self.actions.get_actions()
                cmds_data = {cmd.name: cmd.description for cmd in actions}
                cmd = c.prompt(1, cmds_data)
                self.events.dispatch("command", command=cmd)

        except KeyboardInterrupt:
            c.print("[red]Выход из игры[/]")

    def __repr__(self):
        return "<Game>"
