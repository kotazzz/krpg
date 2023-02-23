from __future__ import annotations
from dataclasses import dataclass
from functools import reduce
import zlib
from ..game import Game
from ..scenario import Section, parse
from ..module import Module
from ..actions import action
from ..executer import Executer
import msgpack
from ..resolver import compare_versions

__version__ = "8"
@dataclass
class EntityInfo:
    s: int
    d: int
    w: int
    e: int
    f: int
    m: int

class Entity:
    def __init__(self,
     name: str,
     s: int,
     d: int,
     w: int,
     e: int,
     f: int,
     money: int,
     ):
        self.name = name
        self.s = s # strength
        self.d = d # dexterity
        self.w = w # wisdom
        self.e = e # endurance
        self.f = f
        self.money = money
        self.current_health = self.max_health
        self.current_mana     = self.max_mana
        
    @property
    def attack(self):
        s, d, w, e,  = self.s, self.d, self.w, self.e
        return ((s**1.5) * 2.8) + ((d**1.5) * 1.5) + ((w**0.8) * 1.2) + ((e**0.5) * 0.5) + (((s*d)**1.2) / ((w+1)**0.8)) + 25
        
    @property
    def defense(self):
        s, d, w, e,  = self.s, self.d, self.w, self.e
        return ((d**1.5) * 2.8) + ((s**1.5) * 1.5) + ((w**0.5) * 0.5) + ((e**0.8) * 1.2) + (((d*e)**1.2) / ((s+1)**0.8)) + 25
        
    @property
    def max_health(self):
        s, d, w, e,  = self.s, self.d, self.w, self.e
        return ((e**2.2) * 11) + ((s**1.8) * 1.8) + ((d**0.5) * 0.6) + ((w**0.3) * 0.3) + (((s*e)**1.5) / ((d+1)**0.8)) + 100
        
        
    @property
    def max_mana(self):
        s, d, w, e,  = self.s, self.d, self.w, self.e
        return ((w**2.2) * 8) + ((d**1.8) * 1.8) + ((s**0.5) * 0.6) + ((e**0.3) * 0.3) + (((w*d)**1.5) / ((s+1)**0.8)) + 80
        

    def __repr__(self):
        s, d, w, e,  = self.s, self.d, self.w, self.e
        return f"<Entity {s=} {d=} {w=} {e=}>"
    
    def save(self):
        return [
            self.name,
            self.s,
            self.d,
            self.w,
            self.e,
            self.f,
            self.money,
            self.current_health,
            self.current_mana,
        ]

    def load(self, data):
        self.name = data[0]
        self.s = data[1]
        self.d = data[2]
        self.w = data[3]
        self.e = data[4]
        self.f = data[5]
        self.money = data[6]
        self.current_health = data[7]
        self.current_mana     = data[8]
        
class PlayerModule(Module):
    requires = ["base>=0"]
    name = "player"
    version = __version__

    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.e = Entity("Игрок", 0, 0, 0, 0, 4, 100)
        
        

    def generate_save_data(self):
        return self.e.save()

    def load_save_data(self, data):
        self.e.load(data)

    def init(self):
        c = self.game.console
        class Flag:
            v = True
            
        while Flag.v:
            user = c.confirm("[green]Желаете загрузить сохранение? (yn): [/]")
            if user:
                self.game.eh.dispatch("load", game=self.game, successcb=lambda: setattr(Flag, 'v', False))
            else:
                self.e.name = c.prompt("[green]Введите имя: [/]")
                Flag.v = None
        
        if Flag.v == None:
            base = self.game.get_module("base")
            sc: Section = base.scenario
            executer: Executer = base.executer
            
            self.game.eh.dispatch("new_game")
            sec = sc.first("init")
            for command in sec.children:
                executer.execute(command)
            
        

    @action("me", "Информация о себе", "Игрок")    
    def me(game: Game, player: PlayerModule, **kwargs):
        s, d, w, e = player.e.s, player.e.d, player.e.w, player.e.e
        print("sdwe: ", s, d, w, e)

class Location:
    def __init__(self, name):
        self.name = name
        
    

class MapModule(Module):
    requires = ["base>=0"]
    name = "map"
    version = __version__

    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.locations: list[Location] = []
        self.current = None
    
    def get_location(self, name):
        for loc in self.locations:
            if loc.name == name:
                return loc

    def generate_save_data(self):
        return [self.current]

    def load_save_data(self, data):
        self.current = data[0]

    def init(self):
        base = self.game.get_module("base")
        sc: Section = base.scenario
        map = sc.first("map")
        for loc in map.all("location"):
            location = Location(loc.args[0])
            self.locations.append(location)
        self.current = map.first("start").args[0]
    
    
        
        
    


class BaseModule(Module):
    
    requires = []
    name = "base"
    version = __version__

    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        game.expand_modules([PlayerModule(game), MapModule(game)])
        self.running = True
        self.scenario = self.load_scenario()
        self.executer = Executer(game)

    def load_scenario(self):
        with open("scenario.krpg") as f:
            content = f.read()
            return parse(content)

    def generate_save_data(self):
        # module: version for all loaded modules
        return {m.name: m.version for m in self.game.modules}

    def load_save_data(self, data):
        # check if module list is the same
        table = []
        errors = []
        # mismatch = set(data.keys()) ^ set(map(lambda x: x.name, self.game.modules))
        in_save = set(data.keys())
        in_game = set(map(lambda x: x.name, self.game.modules))

        for not_loaded in in_save - in_game:
            table.append(("Mismatch", "[red]-Not in game-[/]", f"{not_loaded}"))
            errors.append(f"Module {not_loaded} not loaded in game")
        for not_saved in in_game - in_save:
            table.append(("Mismatch", f"{not_saved}", "[red]-Not in save-[/]"))
            errors.append(f"Module {not_saved} not found in save")

        loaded = self.game.get_modules()
        for module, version in data.items():
            if module in loaded and loaded[module].version != version:
                v1, v2 = loaded[module].version, version
                cr = compare_versions(v1, v2)
                c1 = "red" if cr == -1 else "green"
                c2 = "red" if cr == 1 else "green"
                table.append(
                    ("Version", f"{module} [{c1}]{v1}[/]", f"{module} [{c2}]{v2}[/]")
                )
                errors.append(f"Module {module} version mismatch: {v1} != {v2}")

        c = self.game.console
        for row in table:
            c.print(f"{row[0]}: {row[1]} {row[2]}")

        if errors and not c.confirm(
            "Вы уверены, что хотите продолжить загрузку? (yn): "
        ):
            raise Exception("\n" + "\n".join(errors))

    def init(self):
        c = self.game.console
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
            "[red]Игра находится на стадии тестирования![/]", min=0.002
        )

    def on_post_init(self):
        c = self.game.console
        while self.running:
            cmd = c.prompt()
            self.game.eh.dispatch("command", command=cmd)

    def on_exit(self):
        self.running = False

    def on_command(self, command):
        cmds = self.game.manager.get_all()
        if command in cmds:
            cmds[command].callback(self.game, **self.game.get_modules())
        else:
            self.game.console.print(f"[red]Неизвестная команда {command}[/]")
            self.game.console.print(
                f"[green]Доступные команды: {' '.join(cmds.keys())}[/]"
            )

    def on_save(self, game: Game):
        game.console.print("Сохранение игры")
        methods = [
            (m.name, m.generate_save_data)
            for m in game.modules
            if hasattr(m, "generate_save_data")
        ]
        data = reduce(
            lambda x, y: {**x, **y}, [{mod: method()} for mod, method in methods]
        )
        print(data)
        bdata = msgpack.packb(data)
        zdata = zlib.compress(bdata, level=9)
        encoded = game.encoder.encode(zdata, type=0)
        game.console.print(f"[green]Код сохранения: [yellow]{encoded}[/]")

    def on_load(self, game: Game, failcb = None, successcb = None):
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
                methods = [
                    (m.name, m.load_save_data)
                    for m in game.modules
                    if hasattr(m, "load_save_data")
                ]
                for mod, method in methods:
                    method(data[mod])
                
            except Exception as e:
                game.console.print(f"[red]Ошибка при загрузке игры: {e}[/]")
            else:
                game.console.print("Игра загружена")
                if successcb:
                    successcb()
                    game.eh.dispatch("load_done")
                return
        
        if failcb:
            failcb()
            

    @action("exit", "Выйти из игры", "Основное")
    def exit(game: Game, base, **kwargs):
        game.console.print("Выход из игры")
        game.eh.dispatch("exit")

    @action("save", "Сохранить игру", "Основное")
    def save(game: Game, **kwargs):
        game.eh.dispatch("save", game=game)

    @action("load", "Загрузить игру", "Основное")
    def load(game: Game, **kwargs):
        game.eh.dispatch("load", game=game)

    @action("help", "Помощь", "Основное")
    def helps(game: Game, **kwargs):
        c = game.console
        for cat, cmds in game.manager.actions.items():
            c.print(f"[red]{cat}[/]")
            for name, cmd in cmds.items():
                c.print(f"  [green]{name}[/] - {cmd.description}")
