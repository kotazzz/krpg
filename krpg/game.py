from __future__ import annotations
import msgpack
import zlib
from krpg.console import KrpgConsole
from krpg.actions import ActionManager, action
from krpg.events import EventHandler
from krpg.scenario import parse
from krpg.encoder import Encoder
from krpg.executer import Executer
from krpg.entity import Entity

__version__ = "8B"
DEBUG = True


class Game:
    def __init__(self):
        self.state = "none"

        self.console = KrpgConsole()
        self.log = self.console.log
        self.log.setLevel(DEBUG * 5)

        self.actions = ActionManager()
        self.actions.submanagers.append(self)
        self.encoder = Encoder()

        self.events = EventHandler(locked=True)

        for attr in filter(lambda x: x.startswith("on_"), dir(self)):
            cb = getattr(self, attr)
            self.events.listen(attr[3:], cb)
            self.log.debug(f"Added listener for {attr[3:]}")

        self.scenario = parse(open("scenario.krpg").read())

        self.savers: dict[str, set[callable, callable]] = {}

        self.executer = Executer(self)
        self.player = Entity("Player")

    @action("help", "Показать помощь", "Игра")
    def action_help(game: Game):
        print(game)

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

    def on_save(self, game: Game):
        data = {name: funcs[0]() for name, funcs in self.savers.items()}
        bdata = msgpack.packb(data)
        zdata = zlib.compress(bdata, level=9)
        encoded = game.encoder.encode(zdata, type=0)
        game.log.debug(f"Data: {data}")
        game.console.print(f"[green]Код сохранения: [yellow]{encoded}[/]")

    def on_load(self, failcb=None, successcb=None):
        while True:
            self.console.print("[green]Введите код сохранения (e - выход):")
            encoded = self.console.prompt(2)
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
