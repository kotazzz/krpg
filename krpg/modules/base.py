from __future__ import annotations
import shlex
from ..game import Game
from ..module import Module
from ..actions import action

class BaseModule(Module):
    requires = []
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.running = True
        self.game.base = self
        
    def main(self):
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
            cmds[command].callback(self.game)
        else:
            self.game.console.print(f"[red]Неизвестная команда {command}[/]")
            self.game.console.print(f"[green]Доступные команды: {' '.join(cmds.keys())}[/]")
    
    @action("exit", "Exit game", "main")
    def exit(game: Game):
        game.console.print("Выход из игры")
        game.eh.dispatch("exit")
        
    
    