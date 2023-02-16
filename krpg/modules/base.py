from __future__ import annotations
from functools import reduce
import shlex
from ..game import Game
from ..module import Module
from ..actions import action
import msgpack
from ..resolver import compare_versions

class BaseModule(Module):
    requires = []
    name = "base"
    version = "0.1"
    
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.running = True
        self.storage = {}
    
    def generate_save_data(self):
        # module: version for all loaded modules
        return {m.name : m.version for m in self.game.modules}
    
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
                v1, v2 = loaded[module].version,version
                cr = compare_versions(v1, v2)
                c1 = 'red' if cr == -1 else 'green'
                c2 = 'red' if cr == 1 else 'green'
                table.append(("Version", f"{module} [{c1}]{v1}[/]", f"{module} [{c2}]{v2}[/]"))
                errors.append(f"Module {module} version mismatch: {v1} != {v2}")
        
        c = self.game.console
        for row in table:
            c.print(f"{row[0]}: {row[1]} {row[2]}")
        
        if errors and  not c.confirm("Вы уверены, что хотите продолжить загрузку? (yn): "):
            raise Exception("\n"+"\n".join(errors))
    
    
    def init(self):
        pass
    
    def on_post_init(self):
        c = self.game.console
        c.print("Добро пожаловать в игру!")
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
            self.game.console.print(f"[green]Доступные команды: {' '.join(cmds.keys())}[/]")
    
    @action("exit", "Exit game", "main")
    def exit(game: Game, base, **kwargs):
        game.console.print("Выход из игры")
        game.eh.dispatch("exit")
    
    @action("save", "Save game", "main")
    def save(game: Game, base, **kwargs):
        game.console.print("Сохранение игры")
        methods = [(m.name, m.generate_save_data) for m in game.modules if hasattr(m, "generate_save_data")]
        data = reduce(lambda x, y: {**x, **y}, [{mod: method()} for mod, method in methods])
        print(data)
        bdata = msgpack.packb(data)
        encoded = game.encoder.encode(bdata, type=0)
        game.console.print(f"[green]Код сохранения: [yellow]{encoded}[/]")
    
    @action("load", "Load game", "main")
    def load(game: Game, base, **kwargs):
        game.console.print("[green]Введите код сохранения: [yellow]")
        encoded = input()
        game.console.print("[/]")
        try:
            bdata = game.encoder.decode(encoded, type=0)
            data = msgpack.unpackb(bdata)
            methods = [(m.name, m.load_save_data) for m in game.modules if hasattr(m, "load_save_data")]
            for mod, method in methods:
                method(data[mod])
        except Exception as e:
            game.console.print(f"[red]Ошибка при загрузке игры: {e}[/]")
        else:
            game.console.print("Игра загружена")
    
        
            
    
    