from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator

import attr
from rich.panel import Panel
from rich.tree import Tree

from krpg.actions import Action, ActionCategory, ActionManager, action
from krpg.bestiary import BESTIARY
from krpg.commands import command
from krpg.components import component
from krpg.engine.executer import Ctx, Extension, NamedScript, executer_command
from krpg.engine.npc import Npc
from krpg.entity.inventory import Slot
from krpg.events_middleware import GameEvent
from krpg.parser import Command
from krpg.saves import Savable
from krpg.utils import Nameable

if TYPE_CHECKING:
    from krpg.game import Game


@component
class WorldActions(ActionManager):
    @action("map", "Показать карту", ActionCategory.INFO)
    @staticmethod
    def action_map(game: Game) -> None:
        def format_name(loc: LocationState) -> str:
            if loc.is_locked:
                c = "red"
            elif loc == game.world.current_location:
                c = "green"
            else:
                c = "white"
            return f"[{c}]{loc.location.name}[/] - {loc.location.description}"

        def populate(tree: Tree, loc: LocationState) -> Tree:
            if loc.is_locked:
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
        visited: list[LocationState] = [cur]
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
            game.console.print(f"{i}. {loc.location.name}")
        # TODO: questionary
        select = game.console.select("Выберите локацию: ", {loc.location.name: loc for loc in avail}, True)
        if select:
            game.commands.execute(move(game.world, select))


@component
class NpcUtils(Extension):  # TODO: move to npc
    @executer_command("evolve")
    @staticmethod
    def evolve(ctx: Ctx, npc_id: str) -> None:
        game = ctx.game
        npc = game.npc_manager.npcs[npc_id]
        assert npc, f"Where is {npc_id}"
        npc.stage += 1

    @executer_command("goto")
    @staticmethod
    def goto(ctx: Ctx, npc_id: str, loc_id: str) -> None:
        game = ctx.game
        npc = ctx.game.npc_manager.npcs[npc_id]
        assert npc, f"Where is {npc_id}"
        for loc in game.world.locations:
            if npc.npc in loc.npcs:
                loc.npcs.remove(npc.npc)
                break
        # TODO: Move locations to bestiary?
        loc = game.world.get_location_by_id(loc_id)
        assert loc, f"Where is {loc_id}"
        loc.npcs.append(npc.npc)

    @executer_command("unlock")
    @staticmethod
    def unlock(ctx: Ctx, loc_id: str) -> None:
        loc = ctx.game.world.get_location_by_id(loc_id)
        if not loc:
            raise ValueError(f"Location {loc_id} not found")
        ctx.game.commands.execute(unlock(loc))

    @executer_command("multiple")
    @staticmethod  # TODO: move to std
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
    old_loc: LocationState
    new_loc: LocationState


@attr.s(auto_attribs=True)
class UnlockEvent(GameEvent):
    loc: LocationState


@command
def move(world: World, new_loc: LocationState) -> Generator[MoveEvent, Any, None]:
    old_loc = world.current_location
    assert old_loc, "Move from None"
    yield MoveEvent(old_loc, new_loc)
    world.current_location = new_loc


@command
def unlock(loc: LocationState) -> Generator[UnlockEvent, Any, None]:
    loc.is_locked = False
    yield UnlockEvent(loc)


@attr.s(auto_attribs=True)
class LocationState(Savable):
    location: Location = attr.ib(repr=lambda loc: loc.id)
    is_locked: bool = False
    stage: int = 0
    items: list[Slot] = attr.ib(factory=lambda: [], repr=lambda x: str(len(x)))
    npcs: list[Npc] = attr.ib(factory=lambda: [], repr=lambda x: str(len(x)))

    def serialize(self) -> dict[str, Any]:
        return {
            "location": self.location.id,
            "is_locked": self.is_locked,
            "stage": self.stage,
            "items": [item.serialize() for item in self.items],
            "npcs": [npc.id for npc in self.npcs],
        }

    @classmethod
    def deserialize(cls, data: Any, *args: Any, **kwargs: Any) -> LocationState:
        location = BESTIARY.strict_get_entity_by_id(data["location"], Location)
        is_locked = data["is_locked"]
        stage = data["stage"]
        items = [Slot.deserialize(item) for item in data["items"]]
        npcs = [BESTIARY.strict_get_entity_by_id(npc_id, Npc) for npc_id in data["npcs"]]
        # TODO: Use strict_get_entity_by_id in more places
        return cls(location=location, is_locked=is_locked, stage=stage, items=items, npcs=npcs)

    @property
    def actions(self) -> list[Action]:
        if not self.location.stages:
            return []
        return [a.as_action for a in self.location.stages[self.stage]]

    @classmethod
    def from_location(cls, location: Location) -> LocationState:
        self = cls(location=location)
        self.npcs = location.init_npcs
        # TODO: Optimize copying?
        self.items = [Slot(slot.type, slot.item, slot.count) for slot in location.init_items]
        self.is_locked = location.locked
        return self


@attr.s(auto_attribs=True)
class Location(Nameable):
    stages: list[list[NamedScript]] = attr.ib(factory=lambda: [], repr=lambda x: str(len(x)))
    is_start: bool = False
    connections: list[Location] = attr.ib(factory=lambda: [])
    init_npcs: list[Npc] = attr.ib(factory=lambda: [])
    init_items: list[Slot] = attr.ib(factory=lambda: [])
    locked: bool = False


@attr.s(auto_attribs=True)
class World(Savable):
    locations: list[LocationState] = attr.ib(factory=lambda: [], repr=lambda x: str(len(x)))
    current_location: LocationState = attr.ib(init=False, repr=lambda x: repr(x.id) if x else "None")

    def __attrs_post_init__(self):
        locations = BESTIARY.get_all(Location)
        self.locations = [LocationState.from_location(loc) for loc in locations]
        start_location = None
        for loc in self.locations:
            if loc.location.is_start:
                start_location = loc
                break
        else:
            raise ValueError("Start location not found")
        start_location_state = self.get_location_state(start_location.location)
        if not start_location_state:
            raise ValueError("Start location state not found")
        self.current_location = start_location_state

    def serialize(self) -> dict[str, Any]:
        return {"locations": [loc.serialize() for loc in self.locations], "current_location": self.current_location.location.id}

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> World:
        instance = cls()
        instance.locations = [LocationState.deserialize(loc) for loc in data["locations"]]
        loc = instance.get_location_by_id(data["current_location"])
        if not loc:
            raise ValueError("Current location not found")
        instance.current_location = loc
        return instance

    def get_roads(self, location: LocationState) -> list[LocationState]:
        connections = location.location.connections
        states: list[LocationState] = []
        for conn in connections:
            state = self.get_location_state(conn)
            if not state:
                raise ValueError(f"Location state for {conn} not found")
            states.append(state)
        return states

    def get_available_locations(self) -> list[LocationState]:
        assert self.current_location, "Current location is not set"
        return [loc for loc in self.get_roads(self.current_location) if not loc.is_locked]

    def get_location_state(self, location: Location) -> LocationState | None:
        for loc_state in self.locations:
            if loc_state.location == location:
                return loc_state
        return None

    def get_location_by_id(self, id: str) -> LocationState | None:
        for loc_state in self.locations:
            if loc_state.location.id == id:
                return loc_state
        return None
