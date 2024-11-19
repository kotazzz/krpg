import attr

from krpg.actions import Action
from krpg.engine.npc import Npc
from krpg.entity.inventory import Item
from krpg.utils import Nameable


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

    def link(self, location1: Location, location2: Location) -> None:
        assert location1 in self.locations, f"Location {location1} not found"
        assert location2 in self.locations, f"Location {location2} not found"
        assert location1 != location2, "Cannot link location to itself"
        assert location1 not in self.get_roads(location2), "Road already exists"
        self.roads.append((location1, location2))
