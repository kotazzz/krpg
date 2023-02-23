from __future__ import annotations
from .core.events import EventHandler
from .core.actions import ActionManager, action
from .core.console import Console
from .core.encoder import Encoder
from .core.logger import Logger
from .core.scenario import parse
from .executer import Executer

class Game(ActionManager):
    def __init__(self):
        self.eh = EventHandler(locked=True)
        self.manager = ActionManager()
        self.console = Console()
        self.encoder = Encoder()
        self.logger = Logger(file=False)
        self.scenario = parse(open("scenario.krpg").read())
        
        self.executer = Executer(self)
    def main(self):
        print("Игра тут")
    
