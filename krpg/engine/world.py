from __future__ import annotations
from typing import TYPE_CHECKING, Any, Generator
import attr
from rich.panel import Panel

from krpg.actions import ActionCategory, ActionManager, action
from krpg.commands import command
from krpg.components import component
from krpg.engine.executer import Ctx, Extension, NamedScript, executer_command
from krpg.engine.npc import Npc
from krpg.entity.inventory import Slot
from krpg.events_middleware import GameEvent
from krpg.parser import Command
from krpg.utils import Nameable, get_by_id

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
        select = game.console.select("Выберите локацию: ", {loc.name: loc for loc in avail}, True)
        if select:
            game.commands.execute(move(game.world, select))

@component
class NpcUtils(Extension):
    @executer_command("evolve")
    @staticmethod
    def evolve(ctx: Ctx, npc_id: str) -> None:
        game = ctx.game
        npc = game.bestiary.get_entity_by_id(npc_id, Npc)
        assert npc, f"Where is {npc_id}"
        npc.stage += 1

    @executer_command("goto")
    @staticmethod
    def goto(ctx: Ctx, npc_id: str, loc_id: str) -> None:
        game = ctx.game
        npc = game.bestiary.get_entity_by_id(npc_id, Npc)
        assert npc, f"Where is {npc_id}"
        for loc in game.world.locations:
            if npc in loc.npcs:
                loc.npcs.remove(npc)
                break
        # TODO: Move locations to bestiary?
        loc = get_by_id(game.world.locations, loc_id)
        assert loc, f"Where is {loc_id}"
        loc.npcs.append(npc)

    @executer_command("multiple")
    @staticmethod
    def multiple(ctx: Ctx, title: str, min: str, max: str, var_name: str, children: list[Command]):
        minv, maxv = int(min), int(max)
        completer: dict[str, int] = {}
        for opt in children:
            k, v = opt.args
            v = ctx.executer.process_text(v)
            completer[v] = int(k)
        res = ctx.game.console.multiple(title, completer, minv, maxv)
        ctx.executer.env[var_name] = res
        
@attr.s(auto_attribs=True)
class MoveEvent(GameEvent):
    old_loc: Location
    new_loc: Location


@attr.s(auto_attribs=True)
class UnlockEvent(GameEvent):
    loc: Location


@command
def move(world: World, new_loc: Location) -> Generator[MoveEvent, Any, None]:
    old_loc = world.current_location
    assert old_loc, "Move from None"
    yield MoveEvent(old_loc, new_loc)
    world.current_location = new_loc


@command
def unlock(loc: Location) -> Generator[UnlockEvent, Any, None]:
    loc.locked = False
    yield UnlockEvent(loc)


@attr.s(auto_attribs=True)
class Location(Nameable):
    items: list[Slot] = attr.ib(factory=list, repr=lambda x: str(len(x)))
    npcs: list[Npc] = attr.ib(factory=list, repr=lambda x: str(len(x)))
    locked: bool = False
    stage: int = 0
    stages: list[list[NamedScript]] = attr.ib(factory=list, repr=lambda x: str(len(x)))


@attr.s(auto_attribs=True)
class World:
    locations: list[Location] = attr.ib(factory=list, repr=lambda x: str(len(x)))
    current_location: Location = attr.ib(init=False, repr=lambda x: repr(x.id) if x else "None")
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
