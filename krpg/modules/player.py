from ..game import Game
from ..module import Module
from ..actions import action

class PlayerModule(Module):
    requires = ["base>=0.1"]
    name = "player"
    version = "0.1"
    
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
    
    def init(self):
        c = self.game.console
        user = c.confirm("[green]Желаете загрузить сохранение? (yn): [/]")
        if user:
            self.game.eh.dispatch("load", game=self.game)
        else:
            pass