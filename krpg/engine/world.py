from __future__ import annotations
from typing import TYPE_CHECKING, Any, Generator
import attr
from rich.panel import Panel

from krpg.actions import Action, ActionCategory, ActionManager, action
from krpg.commands import command
from krpg.components import component
from krpg.engine.npc import Npc
from krpg.entity.inventory import Item
from krpg.events import Event
from krpg.utils import Nameable

from rich.tree import Tree

if TYPE_CHECKING:
    from krpg.game import Game


@component
class WorldActions(ActionManager):
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
        print(select)


@attr.s(auto_attribs=True)
class MoveEvent(Event):
    old_loc: Location
    new_loc: Location


@command
def move(world: World, new_loc: Location) -> Generator[MoveEvent, Any, None]:
    old_loc = world.current_location
    assert old_loc, "Move from None"
    yield MoveEvent(old_loc, new_loc)
    world.current_location = new_loc


@attr.s(auto_attribs=True)
class Location(Nameable):
    items: list[tuple[Item, int]] = attr.ib(factory=list)
    npcs: list[Npc] = attr.ib(factory=list)
    locked: bool = False
    stage: int = 0
    stages: list[list[Action]] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class World:
    locations: list[Location] = attr.ib(factory=list)
    current_location: Location | None = attr.ib(default=None, repr=lambda x: repr(x.id) if x else "None")
    start_location: Location | None = attr.ib(default=None, repr=lambda x: repr(x.id) if x else "None")
    roads: list[tuple[Location, Location]] = attr.ib(factory=list, repr=lambda x: f"{len(x)} roads")

    def get_roads(self, location: Location) -> list[Location]:
        froms = [road[0] for road in self.roads if road[1] == location]
        tos = [road[1] for road in self.roads if road[0] == location]
        return froms + tos

    def get_available_locations(self) -> list[Location]:
        assert self.current_location, "Current location is not set"
        return [loc for loc in self.get_roads(self.current_location) if not loc.locked]

    def link(self, location1: Location, location2: Location) -> None:
        assert location1 in self.locations, f"Location {location1} not found"
        assert location2 in self.locations, f"Location {location2} not found"
        assert location1 != location2, "Cannot link location to itself"
        assert location1 not in self.get_roads(location2), "Road already exists"
        self.roads.append((location1, location2))
