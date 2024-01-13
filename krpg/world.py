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
    def __init__(self, identifier: str, name: str, description: str):
        self.id = identifier
        self.name = name
        self.description = description
        self.locked: bool = True
        self.env: dict[str, Any] = {}
        self.actions: list[Action] = []
        self.items: list[tuple[str, int]] = []

        self.triggers: list[tuple[str, list, Block]] = []
        self.visited: bool = False

    def save(self) -> list[Any]:
        """Save the location state.

        Returns
        -------
        list[Any]
            The list of data to save.
        """
        return [self.env, self.items, self.visited, self.locked]

    def load(self, data) -> None:
        """Load the location state.

        Parameters
        ----------
        data : list[Any]
            The data to load.
        """
        self.env = data[0]
        self.items = data[1]
        self.visited = data[2]
        self.locked = data[3]

    def get_triggers(self, name) -> list[tuple[str, list, Block]]:
        """Get a list of triggers with the specified name.

        Parameters
        ----------
        name : str
            The name of the trigger.

        Returns
        -------
        list[tuple[str, list, Block]]
            list of triggers with the specified name.
        """
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
        """Return current location"""
        if not self._current:
            raise AttributeError("No current location")
        return self._current

    def save(self) -> dict[str, list[Any] | str]:
        """Save the world state.

        Returns
        -------
        dict[str, list[Any] | str]
            The dictionary of data to save.
        """
        return {loc.id: loc.save() for loc in self.locations} | {
            "CURRENT": self.current.id
        }

    def load(self, data: dict):
        """Load the world state.

        Parameters
        ----------
        data : dict
            The data to load.
        """
        self._current = self.get(data.pop("CURRENT"))
        for identifier, locdata in data.items():
            self.get(identifier).load(locdata)

    def take(self, location: str | Location, item_id: str, remain: int = 0):
        """Remove an item from a location.

        Parameters
        ----------
        location : str | Location
            location to take item from
        item_id : str
            item id
        remain : int, optional
            remaining count of item, by default 0
        """
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
        """Add an item to a location.

        Parameters
        ----------
        item_id : str
            item id
        count : int, optional
            count, by default 0
        location : Optional[str  |  Location], optional
            location, by default None
        """
        loc = self.get(location) if location else self.current
        self.game.events.dispatch(Events.WORLD_ITEM_DROP, item_id=item_id, count=count)

        loc.items.append((item_id, count))

    def set_default(self):
        """Set the current location to the starting location."""
        if not self._start:
            raise InvalidLocation("No starting location")
        loc = self.get(self._start)
        self._current = loc
        self.set(loc)

    def set_start(self, start: str):
        """Set the starting location.

        Parameters
        ----------
        start : str
            The id of the starting location.
        """
        self._start = start

    def set(self, new_loc: str | Location) -> bool:
        """Set the current location.

        Parameters
        ----------
        new_loc : str | Location
            The new location.

        Returns
        -------
        bool
            Whether the location was successfully set.
        """
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
        """Get the list of actions available in the current location.

        Returns
        -------
        list[Action]
            The list of actions available in the current location.
        """
        return self.current.actions

    def add(self, location: Location):
        """Add a new location to the world.

        Parameters
        ----------
        location : Location
            The location to add.
        """
        self.locations.append(location)

    def get(self, identifier: str | Location) -> Location:
        """Get a location object based on the given identifier.

        Parameters
        ----------
        identifier : str | Location
            The identifier of the location.

        Returns
        -------
        Location
            The location object.

        Raises
        ------
        InvalidLocation
            If the location with the specified identifier is not found.
        """
        if isinstance(identifier, str):
            for loc in self.locations:
                if loc.id == identifier:
                    return loc
        elif isinstance(identifier, Location):
            return identifier
        raise InvalidLocation(f"No location found for {identifier}")

    def get_list(self, *ids: str | Location) -> list[Location]:
        """Get a list of location objects based on the given identifiers.

        Returns
        -------
        list[Location]
            The list of location objects.

        Raises
        ------
        ValueError
            If not all locations are found.
        """
        res = []
        for identifier in ids:
            if isinstance(identifier, str):
                for loc in self.locations:
                    if loc.id == identifier:
                        res.append(loc)
                        break
            elif isinstance(identifier, Location):
                res.append(identifier)
        if len(res) != len(ids):
            raise ValueError(f"Not all locations found for {ids}")
        return res

    def get_road(self, loc: str | Location) -> list[Location]:
        """Get a list of locations connected to the given location.

        Parameters
        ----------
        loc : str | Location
            The location to get the roads from.

        Returns
        -------
        list[Location]
            The list of locations connected to the given location.
        """
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
        """Unlock a locked location.

        Parameters
        ----------
        game : Game
            The game instance.
        loc : str
            The location to unlock.
        """
        location = game.world.get(loc)
        location.locked = False

    def road(self, loc1: str | Location, loc2: str | Location):
        """Add a road between two locations.

        Parameters
        ----------
        loc1 : str | Location
            Location 1.
        loc2 : str | Location
            Location 2.

        Raises
        ------
        ValueError
            If the road already exists.
        """
        location1, location2, *_ = self.get_list(loc1, loc2)
        if location2 in self.get_road(location1):
            raise ValueError(f"Road from {location1} to {location2} already exist")
        self.roads.append((location1, location2))

    def __repr__(self):
        return f"<World loc={len(self.locations)}>"
