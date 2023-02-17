from __future__ import annotations
from .module import Module
from .resolver import resolve_dependencies
from .events import EventHandler
from .actions import ActionManager, Action
from .console import Console
from .encoder import Encoder
from .logger import Logger


class Game:
    def __init__(self):
        self.modules: list[Module] = []
        self.eh = EventHandler(locked=True)
        self.manager = ActionManager()
        self.console = Console(self)
        self.encoder = Encoder()
        self.logger = Logger(file=False)

    def add_module(self, module: Module):
        self.modules.append(module)

    def expand_modules(self, sequence: list):
        self.modules.extend(sequence)

    def get_modules(self):
        return {m.name: m for m in self.modules}

    def get_module(self, name):
        for m in self.modules:
            if name == m.name:
                return m

    def main(self):

        self.modules: list[Module] = resolve_dependencies(self.modules)

        for module in self.modules:
            self.eh.dispatch("pre_init", module=module)
            for name in dir(module):
                attr = getattr(module, name)
                if name.startswith("on_") and callable(attr):
                    self.eh.listen(name[3:], attr)
                    self.eh.dispatch("add_listener", name=name[3:], callback=attr)
                elif name.startswith("on_") and not callable(attr):
                    raise Exception(f"Invalid attribute {name} in module {module}")
                if isinstance(attr, Action):
                    self.manager.register(attr)
                    self.eh.dispatch("add_action", action=attr)

        for module in self.modules:
            module.init()

        self.eh.dispatch("post_init")
        self.eh.unlock()
