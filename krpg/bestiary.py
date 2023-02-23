
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game  

class Bestiary:
    def __init__(self, game: Game):
        self.game = game
    
    