from __future__ import annotations
import random
import time

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from krpg.game import Game


class RandomManager:
    def __init__(self, game: Game):
        self.game = game
        self.state = 0
        self.seed = int(time.time() * 10e5)
        self.rnd = random.Random(self.seed)
        self.game.add_saver("rnd", self.save, self.load)

    def set_seed(self, seed: int):
        self.seed = seed
        self.rnd.seed(seed)
        self.state = 0

    def save(self):
        return str(self.seed), self.state

    def load(self, data):
        seed = int(data[0])
        self.seed = seed
        self.rnd.seed(seed)
        self.state = 0
        for i in range(data[1]):
            self.random()


    def random(self):
        self.state += 1
        return self.rnd.random()

    def choices(self, options, weights=None, k=1):
        if weights is None:
            weights = [1] * len(options)
        total_weight = sum(weights)
        choices = []
        for i in range(k):
            r = self.random() * total_weight
            for j, w in enumerate(weights):
                r -= w
                if r <= 0:
                    choices.append(options[j])
                    break
        return choices