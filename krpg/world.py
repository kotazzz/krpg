from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from krpg.actions import Action, HasExtract
from krpg.events import Events
from krpg.executer import Block, executer_command

if TYPE_CHECKING:
    from krpg.game import Game

class InvalidLocation(Exception):
    pass

class Location:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description
        self.locked: bool = True
        self.env: dict[str, Any] = {}
        self.actions: list[Action] = []
        self.items: list[tuple[str, int]] = []

        self.triggers: list[tuple[str, list, Block]] = []
        self.visited: bool = False

    def save(self) -> list[Any]:
        return [self.env, self.items, self.visited, self.locked]

    def load(self, data) -> None:
        self.env = data[0]
        self.items = data[1]
        self.visited = data[2]
        self.locked = data[3]

    def get_triggers(self, name) -> list[tuple[str, list, Block]]:
        # first_visit
        res = []
        for trig in self.triggers:
            if trig[0] == name:
                res.append(trig)
        return res

    def __repr__(self) -> str:
        return f"<Location name={self.id!r}>"


class World(HasExtract):
    """
    Represents the game world containing locations and roads.

    Attributes:
    - locations: A list of Location objects representing the different locations in the world.
    - roads: A list of tuples representing the roads between locations.
    - current: The current location the player is in.
    - game: The Game object associated with the world.
    - _start: The starting location of the world.

    Methods:
    - save(): Saves the state of the world.
    - load(data): Loads the state of the world from the given data.
    - take(location, item_id, remain): Removes an item from a location.
    - drop(item_id, count, location): Adds an item to a location.
    - set(new_loc): Sets the current location to the specified location.
    - extract(): Retrieves the list of actions available in the current location.
    - add(location): Adds a new location to the world.
    - get(*ids): Retrieves a location object based on the given ids.
    - get_road(loc): Retrieves the list of locations connected to the given location.
    - unlock(loc): Unlocks a locked location.
    - road(loc1, loc2): Adds a road between two locations.
    """

    def __init__(self, game: Game):
        self.locations: list[Location] = []
        self.roads: list[tuple[Location, Location]] = []
        self._current: Optional[Location] = None
        self.game = game
        self.game.add_saver("world", self.save, self.load)
        self.game.add_actions(self)
        self.game.executer.add_extension(self)
        self._start: Optional[str] = None

    @property
    def current(self) -> Location:
        if not self._current:
            raise InvalidLocation("No current location")
        return self._current

    def save(self) -> dict[str, list[Any] | str]:
        return {loc.id: loc.save() for loc in self.locations} | {
            "CURRENT": self.current.id
        }

    def load(self, data: dict):
        self._current = self.get(data.pop("CURRENT"))
        for id, locdata in data.items():
            self.get(id).load(locdata)

    def take(self, location: str | Location, item_id: str, remain: int = 0):
        loc = self.get(location)
        # TODO: Add check?
        self.game.events.dispatch(
            Events.WORLD_ITEM_TAKE, item_id=item_id, remain=remain
        )

        for i, (item, _) in enumerate(loc.items):
            if item == item_id:
                if remain:
                    loc.items[i] = (item, remain)
                else:
                    loc.items.pop(i)
                break

    def drop(
        self, item_id: str, count: int = 0, location: Optional[str | Location] = None
    ):
        loc = self.get(location) if location else self.current
        self.game.events.dispatch(Events.WORLD_ITEM_DROP, item_id=item_id, count=count)

        loc.items.append((item_id, count))

    def set_default(self):
        loc = self.get(self._start)
        self.set(loc)

    def set(self, new_loc: str | Location) -> bool:
        new_loc = self.get(new_loc)

        if self._current:
            for *_, block in self.current.get_triggers("on_exit"):
                block.run()

        for *_, block in new_loc.get_triggers("on_enter"):
            block.run()

        if not self.game.executer.env.get("_success", True):
            return False

        if not new_loc.visited:
            for *_, block in new_loc.get_triggers("first_visit"):
                block.run()

        new_loc.visited = True
        self.game.events.dispatch(Events.MOVE, before=self._current, after=new_loc)
        self._current = new_loc
        self._current.locked = False
        return True

    def extract(self) -> list[Action]:
        return self.current.actions

    def add(self, location: Location):
        self.locations.append(location)

    def get(self, id: str | Location) -> Location:
        if isinstance(id, str):
            for loc in self.locations:
                if loc.id == id:
                    return loc
        elif isinstance(id, Location):
            return id
        raise InvalidLocation(f"No location found for {id}")

    def get_list(self, *ids: str | Location) -> list[Location]:
        res = []
        for id in ids:
            if isinstance(id, str):
                for loc in self.locations:
                    if loc.id == id:
                        res.append(loc)
                        break
            elif isinstance(id, Location):
                res.append(id)
        if len(res) != len(ids):
            raise Exception(f"Not all locations found for {ids}")
        return res

    def get_road(self, loc: str | Location) -> list[Location]:
        loc = self.get(loc)
        res = []
        for a, b in self.roads:
            if a is loc and not b.locked:
                res.append(b)
            if b is loc and not a.locked:
                res.append(a)
        return res

    @executer_command("unlock")
    @staticmethod
    def unlock(game: Game, loc: str):
        location = game.world.get(loc)
        location.locked = False

    def road(self, loc1: str | Location, loc2: str | Location):
        location1, location2 = self.get_list(loc1, loc2)
        if location2 in self.get_road(location1):
            raise Exception(f"Road from {location1} to {location2} already exist")
        self.roads.append((location1, location2))

    def __repr__(self):
        return f"<World loc={len(self.locations)}>"
