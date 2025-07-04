from __future__ import annotations

import bisect
import itertools
import math
import random
import time
from typing import Any, Optional, List

from krpg.saves import Savable


class RandomManager(Savable):
    def __init__(self):
        self.seed = int(time.time() * 1e6)
        self.rnd = random.Random(self.seed)
        self.state = 0

    def serialize(self) -> dict[str, Any]:
        return {"seed": self.seed, "state": self.state}

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> RandomManager:
        self = cls()
        self.seed = data["seed"]
        self.state = data["state"]
        self.rnd = random.Random(self.seed)
        return self

    def set_seed(self, seed: int):
        self.seed = seed
        self.rnd.seed(seed)
        self.state = 0

    def random(self) -> float:
        self.state += 1
        return self.rnd.random()

    def randint(self, a: int, b: int) -> int:
        self.state += 1
        # можно использовать rnd.randint(a, b), но с твоей механикой вызова random() так безопаснее
        return a + math.floor(self.random() * (b - a + 1))

    def choice[T](self, options: List[T]) -> T:
        if not options:
            raise IndexError("Cannot choose from an empty sequence")
        idx = math.floor(self.random() * len(options))
        return options[idx]

    def choices[T](self, options: List[T], weights: Optional[List[float]] = None, k: int = 1) -> List[T]:
        if not options:
            raise IndexError("Cannot choose from an empty sequence")
        if weights is None:
            weights = [1.0] * len(options)
        if len(weights) != len(options):
            raise ValueError("Length of weights must match length of options")
        cum_weights = list(itertools.accumulate(weights))
        total = cum_weights[-1]
        result: list[T] = []
        for _ in range(k):
            r = self.random() * total
            idx = bisect.bisect(cum_weights, r)
            result.append(options[idx])
        self.state += k
        return result

    def __repr__(self):
        return f"<RandomManager state={self.state} seed={self.seed}>"
