from __future__ import annotations
from itertools import groupby
from textwrap import wrap
import msgpack
import zlib
from krpg.bestiary import Bestiary
from krpg.clock import Clock
from krpg.console import KrpgConsole
from krpg.actions import ActionManager, action
from krpg.events import EventHandler
from krpg.presenter import Presenter
from krpg.scenario import parse
from krpg.encoder import Encoder
from krpg.executer import Executer
from krpg.player import Player
from krpg.builder import Builder
from krpg.world import World
import time

__version__ = "8B"
DEBUG = True


class Game:
    version = __version__
    debug = DEBUG

    def __init__(self):
        self.state = "none"
        self.start_time = self.save_time = self.timestamp()
        self.console = KrpgConsole()
        self.log = self.console.log
        self.log.setLevel(DEBUG * 5)
        debug = self.log.debug

        self.actions = ActionManager()
        debug(f"Init [green]ActionManager[/]: {self.actions}")

        self.add_actions(self)
        self.encoder = Encoder()
        debug(f"Init [green]Encoder[/]: {self.encoder}")

        self.events = EventHandler(locked=True)
        debug(f"Init [green]EventHandler[/]: {self.events}")

        for attr in filter(lambda x: x.startswith("on_"), dir(self)):
            cb = getattr(self, attr)
            self.events.listen(attr[3:], cb)
            debug(f"Added [red]listener[/] for {attr[3:]}")

        scenario = open("scenario.krpg").read()
        self.scenario_hash = f"{zlib.crc32(scenario.encode()):x}"
        self.scenario = parse(scenario)
        debug(f"Loaded scenario with {len(self.scenario.children)} items")

        self.savers: dict[str, set[callable, callable]] = {}

        self.executer = Executer(self)
        debug(f"Init [green]Executer[/]: {self.executer}")

        self.player = Player(self)
        debug(f"Init [green]Player[/]: {self.player}")

        self.presenter = Presenter(self)
        debug(f"Init [green]Presenter[/]: {self.presenter}")

        self.bestiary = Bestiary(self)
        debug(f"Init [green]Bestiary[/]: {self.bestiary}")

        self.clock = Clock(self)
        debug(f"Init [green]Clock[/]: {self.clock}")

        self.world = World(self)
        debug(f"Init [green]World[/]: {self.world}")

        self.builder = Builder(self)
        debug(f"Starting build world...")

        self.builder.build()

    def timestamp(self):
        return int(time.time()) - 1667250000  # 1 Nov 2022 00:00 (+3)

    def add_actions(self, obj: object):
        self.log.debug(f"Add submanager {obj}")
        self.actions.submanagers.append(obj)

    @action("help", "Показать помощь", "Игра")
    def action_help(game: Game):
        actions = sorted(game.actions.get_actions(), key=lambda x: x.category)
        cmdcat = groupby(actions, key=lambda x: x.category)
        for cat, cmds in cmdcat:
            game.console.print(f"[b red]{cat}")
            for cmd in cmds:
                game.console.print(f" [green]{cmd.name}[/] - {cmd.description}")

    @action("credits", "Авторы и благодарности", "Игра")
    def action_credits(game: Game):
        game.console.print(
            "[green]Автор:[/] Kotaz\n"
            "[green]Язык:[/] Python 3\n"
            "[green]Библиотеки:[/] rich, prompt_toolkit, msgpack\n"
            "[green]Кол-во строк кода:[/] 1000+\n\n"
            "[bold green]Отдельная благодарность:[/]\n"
            "  [green]Никто[/]\n"
            "  [red]Конец[/]\n"
        )

    @action("guide", "Игровая справка", "Игра")
    def action_guide(game: Game):
        passages = {
            "FAQ": ("Тут пусто :("),
            "Changelog": ("Мне [red]лень[/] тут что-то писать... :( \n"),
            "Мне нужна помощь по командам": (
                "Используйте [green]help[/] или [green]guide[/] для получения справки\n"
            ),
            "[blue][AUTO][/] и аргументы": (
                "В игре все действия используют лишь одну фразу или слово. "
                "У них нет аргументов или какого либо синтаксиса. "
                "Если для определенного действия требуются аргументы - "
                "они будут запрошенные через отдельные поля ввода. Теперь "
                "вам не надо заучивать сложный синтаксис дял простых действий. "
                "Хотите ввести аргументы сразу? Разделяйте свои действия пробелом. "
                "Игра запоминает каждое слово отдельно и как только понадобится что-то "
                "ввести она сама вставит то, что вы вводили ранее. "
                "Таким образом вы можете одновременно вводить множество "
                "команд за раз и они все исполнятся сами\n"
                "Попробуйте ввести [green]e guide 1[/] и вы выйдете из "
                "справки и вернетесь, открыв первую страницу"
            ),
        }
        while True:
            game.console.print("[bold green]Гайды и справка[/]")
            game.console.print("[green]Выберите секцию (e - Выход)[/]")
            select = game.console.menu(2, list(passages.items()), "e", lambda x: x[0])
            if not select:
                return
            else:
                text = wrap(select[1], replace_whitespace=False)
                game.console.print("\n".join(text))

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
        self.save_time = self.timestamp()
        data = {name: funcs[0]() for name, funcs in self.savers.items()}
        bdata = msgpack.packb(data)
        zdata = zlib.compress(bdata, level=9)
        encoded = self.encoder.encode(zdata, type=0)
        self.log.debug(f"Data: {data}")
        self.log.debug(f"BinData ({len(bdata)}): {bdata.hex()}")
        self.log.debug(
            f"Zipped from {len(bdata)} to {len(zdata)}, string: {len(encoded)}"
        )
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
            if c.confirm(5):
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
