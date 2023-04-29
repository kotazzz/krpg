from __future__ import annotations

from krpg.actions import Action

from typing import TYPE_CHECKING

from krpg.events import Events

if TYPE_CHECKING:
    from krpg.game import Game


class Location:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description
        self.env: dict = {}
        self.actions: list[Action] = []
        self.items: list[str, int] = []

    def save(self):
        return [self.env, self.items]

    def load(self, data):
        self.env = data[0]
        self.items = data[1]

    def __repr__(self) -> str:
        return f"<Location name={self.id!r}>"


class World:
    def __init__(self, game: Game):
        self.locations: list[Location] = []
        self.roads = []
        self.current: Location | None = None
        self.game = game
        self.game.add_saver("world", self.save, self.load)

    def save(self):
        return {loc.id: loc.env for loc in self.locations} | {
            "CURRENT": self.current.id
        }

    def load(self, data):
        self.current = self.get(data.pop("CURRENT"))
        for id, env in data.items():
            self.get(id).env = env

    def take(self, location: str | Location, item_id: str, remain: int = 0):
        loc = self.get(location)
        # TODO: Add check
        self.game.events.dispatch(Events.ITEM_TAKE, item_id=item_id, remain=remain)

        for i, (item, _) in enumerate(loc.items):
            if item == item_id:
                if remain:
                    loc.items[i] = (item, remain)
                else:
                    loc.items.pop(i)
                break

    def drop(self, item_id: str, count: int = 0, location: str | Location = None):
        loc = self.get(location) if location else self.current
        # TODO: Add check
        self.game.events.dispatch(Events.ITEM_DROP, item_id=item_id, count=count)

        loc.items.append((item_id, count))

    def set(self, current_loc: str | Location):
        self.game.events.dispatch(Events.MOVE, before=self.current, after=current_loc)
        self.current = self.get(current_loc)

    def extract(self) -> list[Action]:
        return self.current.actions

    def add(self, location: Location):
        self.locations.append(location)

    def get(self, *ids: list[str | Location]) -> Location:
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
            raise Exception(f"{res} != {ids}")
        if len(res) == 1:
            return res[0]
        return res

    def get_road(self, loc: str | Location) -> list[Location]:
        loc = self.get(loc)
        res = []
        for a, b in self.roads:
            if a is loc:
                res.append(b)
            if b is loc:
                res.append(a)
        return res

    def road(self, loc1: str | Location, loc2: str | Location):
        loc1, loc2 = self.get(loc1, loc2)
        if loc2 in self.get_road(loc1):
            raise Exception(f"Road from {loc1} to {loc2} already exist")
        self.roads.append((loc1, loc2))

    def __repr__(self):
        return f"<World loc={len(self.locations)}>"
