
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game



class BattleManager:
    def __init__(self, game: Game):
        self.game = game
        
    def __repr__(self) -> str:
        return f"<BattleManager>"
    