from __future__ import annotations

import bisect
import itertools
import math
import random
import time
from typing import TYPE_CHECKING, Any

from git import Optional

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
        """Set seed for random number generation.

        Parameters
        ----------
        seed : int
            The seed to use.
        """
        self.seed = seed
        self.rnd.seed(seed)
        self.state = 0

    def save(self) -> tuple[str, int]:
        """Save the current state of the random number generator.

        Returns
        -------
        tuple[str, int]
            The seed and state of the random number generator.
        """
        return str(self.seed), self.state

    def load(self, data: tuple[str, int]):
        """Load the saved state of the random number generator.

        Parameters
        ----------
        data : tuple[str, int]
            The data to load.
        """
        seed = int(data[0])
        self.seed = seed
        self.rnd.seed(seed)
        self.state = 0
        for _ in range(data[1]):
            self.random()

    def random(self) -> float:
        """Generate a random float between 0 and 1.

        Returns
        -------
        float
            The generated random float.
        """
        self.state += 1
        return self.rnd.random()

    def randint(self, a, b):
        """Generate a random integer between a and b (inclusive).

        Parameters
        ----------
        a : int
            The lower bound.
        b : int
            The upper bound.

        Returns
        -------
        int
            The generated random integer.
        """
        self.state += 1
        return math.floor(self.rnd.random() * (b - a + 1)) + a

    def choice(self, options):
        """Choose a random item from a list of options.

        Parameters
        ----------
        options : list
            The list of options to choose from.

        Returns
        -------
        object
            The chosen item.
        """
        # use only self.random() for save state
        return options[math.floor(self.random() * len(options))]

    def choices(self, options, weights: Optional[list] = None, k=1) -> list[Any]:
        """Choose multiple items from a list of options with optional weights.

        Parameters
        ----------
        options : list
            The list of options to choose from.
        weights : Optional[list], optional
            The list of weights for each option. If None, the weights are assumed to be equal.
        k : int, optional
            The number of items to choose from options. Defaults to 1.

        Returns
        -------
        list[Any]
            The chosen items.
        """
        # options - list of items
        # weights - list of weights for items. If None, the weights are assumed to be equal.
        # k - number of items to choose from options
        # bigger weights - bigger chance to choose item
        # allowed call only self.random() for save state of random
        weights = weights or [1] * len(options)
        cum_weights = list(itertools.accumulate(weights))
        total = cum_weights[-1] + 0.0  # convert to float
        return [
            options[bisect.bisect(cum_weights, self.random() * total)] for i in range(k)
        ]

    def __repr__(self):
        return f"<RandomManager state={self.state} seed={self.seed}>"
