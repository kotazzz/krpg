from __future__ import annotations
from .module import Module
from .resolver import resolve_dependencies
from .events import EventHandler
from .actions import ActionManager, Action
from .console import Console
from .encryptor import Encryptor
from .logger import Logger
class Game:
    def __init__(self):
        self.modules: list[Module] = []
        self.eh = EventHandler()
        self.manager = ActionManager()
        self.console = Console(self)
        self.encryptor = Encryptor()
        self.logger = Logger(file=False)
        
    def add_module(self, module: Module):
        self.modules.append(module)
    
    def expand_modules(self, sequence: list):
        self.modules.extend(sequence)
        
    
    def main(self):
        names = {
            m.__class__.__name__: m for m in self.modules
        }
        deptree = {
            m.__class__.__name__: m.requires for m in self.modules
        }
        resolved = resolve_dependencies(deptree)
        modsorted = [names[name] for name in resolved]
        for module in modsorted:
            for name in dir(module):
                attr = getattr(module, name)
                if name.startswith("on_") and callable(attr):
                    self.eh.listen(name[3:], attr)
                elif name.startswith("on_") and  not callable(attr):
                    raise Exception(f"Invalid attribute {name} in module {module}")
                    
                if isinstance(attr, Action):
                    self.manager.register(attr)
        for module in modsorted:
            module.main()
        
        self.eh.dispatch("post_init")
                