from __future__ import annotations
from typing import TYPE_CHECKING

from krpg.actions import ActionCategory, ActionManager, action
from krpg.components import component
from krpg.console.entities import render_entity
from krpg.console.world import render_location_info
from krpg.entity.entity import Entity


if TYPE_CHECKING:
    from krpg.game import Game

@component
class Actions(ActionManager):
    @action("me", "Показать информацию о себе", ActionCategory.INFO)
    @staticmethod
    def action_me(game: Game) -> None:
        player = game.player
        player_entity = player.entity
        game.console.print(render_entity(player_entity))

    @action("look", "Посмотреть на местность", ActionCategory.INFO)
    @staticmethod
    def action_look(game: Game) -> None:
        loc = game.world.current_location
        assert loc is not None, "Current location is not set"
        game.console.print(render_location_info(loc))



class Player:
    def __init__(self) -> None:
        self.entity = Entity("player", "Игрок")
        
