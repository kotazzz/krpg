from __future__ import annotations
import random
import time

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game
    
class RandomManager:
    def __init__(self, game: Game):
        self.game = game
        self.state = 0
        self.seed = int(time.time()*10e5)
        self.rnd = random.Random(self.seed)
        self.game.add_saver('rnd', self.save, self.load)
        
    def set_seed(self, seed: int):
        self.seed = seed
        self.rnd.seed(seed)
        self.state = 0
        
    def save(self):
        return str(self.seed), self.state
    
    def load(self, data):
        self.seed = int(data[0])
        self.state = 0
        for i in range(data[1]):
            self.rnd()
    
    def random(self):
        self.state += 1
        return self.rnd.random()
    
    