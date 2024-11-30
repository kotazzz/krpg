from __future__ import annotations
from typing import TYPE_CHECKING

from krpg.actions import ActionCategory, ActionManager, action
from krpg.console.entities import render_entity
from krpg.console.world import render_location_info
from krpg.engine.world import Location
from krpg.entity.entity import Entity

from rich.tree import Tree
from rich.panel import Panel


if TYPE_CHECKING:
    from krpg.game import Game


class Actions(ActionManager):
    @action("map", "Показать карту", ActionCategory.INFO)
    @staticmethod
    def action_map(game: Game) -> None:
        def format_name(loc: Location) -> str:
            if loc.locked:
                c = "red"
            elif loc == game.world.current_location:
                c = "green"
            else:
                c = "white"
            return f"[{c}]{loc.name}[/] - {loc.description}"

        def populate(tree: Tree, loc: Location) -> Tree:
            if loc.locked:
                return tree
            for sub in game.world.get_roads(loc):
                if sub in visited:
                    continue
                child = tree.add(format_name(sub))
                visited.append(sub)
                populate(child, sub)
            return tree

        cur = game.world.current_location
        assert cur is not None, "Current location is not set"
        visited: list[Location] = [cur]
        root = populate(Tree(format_name(cur)), cur)
        game.console.print(Panel(root, title="Карта мира"))

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

    @action("go", "Перейти в локацию", ActionCategory.PLAYER)
    @staticmethod
    def action_go(game: Game) -> None:
        avail = game.world.get_available_locations()
        if not avail:
            game.console.print("Нет доступных локаций")
            return
        game.console.print("Доступные локации:")
        for i, loc in enumerate(avail, 1):
            game.console.print(f"{i}. {loc.name}")
        # TODO: questionary
        select = game.console.select("Выберите локацию", {loc.name: loc for loc in avail})
        select += 1  # FIXME
        # game.world.move(select)


class Player:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.entity = Entity("player", "Игрок")
        self.game.add_action_manager(Actions())
