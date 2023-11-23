from __future__ import annotations
import bisect
import itertools
import math
import random
import time

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game


class RandomManager:
    """
    A class that manages random number generation and state saving.

    Attributes:
        game (Game): The game instance.
        state (int): The current state of the random number generator.
        seed (int): The seed used for random number generation.
        rnd (random.Random): The random number generator instance.
    
    Methods:
        __init__(self, game: Game): Initializes the RandomManager instance.
        set_seed(self, seed: int): Sets the seed for random number generation.
        save(self): Saves the current state of the random number generator.
        load(self, data): Loads the saved state of the random number generator.
        random(self): Generates a random float between 0 and 1.
        randint(self, a, b): Generates a random integer between a and b (inclusive).
        choice(self, options): Chooses a random item from a list of options.
        choices(self, options, weights=None, k=1): Chooses multiple items from a list of options with optional weights.
        __repr__(self): Returns a string representation of the RandomManager instance.
    """
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

    def randint(self, a, b):
        self.state += 1
        return math.floor(self.rnd.random() * (b - a + 1)) + a

    def choice(self, options):
        # use only self.random() for save state
        return options[math.floor(self.random() * len(options))]

    def choices(self, options, weights=None, k=1):
        # options - list of items
        # weights - list of weights for items. If None, the weights are assumed to be equal.
        # k - number of items to choose from options
        # bigger weights - bigger chance to choose item
        # allowed call only self.random() for save state of random
        n = len(options)
        weights = weights or [1] * len(options)
        cum_weights = list(itertools.accumulate(weights))
        total = cum_weights[-1] + 0.0  # convert to float
        return [
            options[bisect.bisect(cum_weights, self.random() * total)] for i in range(k)
        ]

    def __repr__(self):
        return f"<RandomManager state={self.state} seed={self.seed}>"
