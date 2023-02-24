from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from .core.scenario import Command

if TYPE_CHECKING:
    from .game import Game  

def executer_command(name):
    def wrapper(callback):
        return ExecuterCommand(name, callback)
    return wrapper


class ExecuterCommand:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback
        
class ExecuterExtension:
    def get_executer_additions(self):
        cmds: list[ExecuterCommand] = []
        for i in dir(self):
            attr = getattr(self, i)
            if isinstance(attr, ExecuterCommand):
                cmds.append(attr)
        return {cmd.name: cmd.callback for cmd in cmds}

class Base(ExecuterExtension):
    @executer_command("print")
    def builtin_print(game: Game, *args, **kwargs):
        args = [ast.literal_eval('"' + arg + '"') for arg in args]
        newkwargs = {}
        argtypes = {"min": float}
        for name, func in argtypes.items():
            if name in kwargs:
                newkwargs[name] = func(kwargs[name])
        game.console.print(*args, **newkwargs)
    
    @executer_command("exec")
    def builtin_exec(game: Game, code):
        exec(code, {"game": game})

       

class Executer:
    def __init__(self, game: Game):
        self.game = game
        self.extensions: list[ExecuterExtension] = [Base()]

    def add_extension(self, ext: ExecuterExtension):
        self.game.logger.debug(f"Added ExecuterExtension {ext}")
        self.extensions.append(ext)
    
    def get_all_commands(self):
        commands = {}
        for ext in self.extensions:
            commands |= ext.get_executer_additions()
        return commands
            
    def execute(self, command: Command):
        commands = self.get_all_commands()
        if command.name in commands:
            self.game.logger.debug(f"Executing {command.name} ")
            commands[command.name](self.game, *command.args, **command.kwargs)
        else:
            raise Exception(f"Unknown command: {command.name}")
    

    