from __future__ import annotations
import msgpack
import zlib
from krpg.console import KrpgConsole
from krpg.actions import ActionManager
from krpg.events import EventHandler
from krpg.scenario import parse
from krpg.encoder import Encoder
from krpg.executer import Executer
import shlex

__version__ = "8B"
DEBUG = True


class Game:
    def __init__(self):
        self.console = KrpgConsole()
        self.log = self.console.log
        self.log.setLevel(DEBUG * 5)

        self.actions = ActionManager()
        self.encoder = Encoder()

        self.events = EventHandler(locked=True)

        for attr in filter(lambda x: x.startswith("on_"), dir(self)):
            cb = getattr(self, attr)
            self.events.listen(attr[3:], cb)

        self.scenario = parse(open("scenario.krpg").read())

        self.savers: dict[str, set[callable, callable]] = {}

        self.executer = Executer(self)

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

    def on_save(self, game: Game):
        data = {name: funcs[0]() for name, funcs in self.savers.items()}
        bdata = msgpack.packb(data)
        zdata = zlib.compress(bdata, level=9)
        encoded = game.encoder.encode(zdata, type=0)
        game.log.debug(f"Data: {data}")
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

    def on_event(self, event, *args, **kwargs):
        self.log.debug(f"{event} {args} {kwargs}")

    def on_command(self, command):
        cmds = {cmd.name: cmd for cmd in self.actions.get_actions()}
        if command in cmds:
            cmds[command].callback(self)
        else:
            self.console.print(f"[red]Неизвестная команда {command}[/]")
            self.console.print(f"[green]Доступные команды: {' '.join(cmds.keys())}[/]")

    def main(self):
        self.log.debug("Hello, world!")
        self.events.unlock()
        try:
            while True:
                cmd = self.console.prompt(1)
                self.events.dispatch("command", command=cmd)

        except KeyboardInterrupt:
            self.console.print("[red]Выход из игры[/]")
