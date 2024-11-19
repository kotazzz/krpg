from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from krpg.game import Game


class Player:
    def __init__(self, game: Game) -> None:
        self.game = game
