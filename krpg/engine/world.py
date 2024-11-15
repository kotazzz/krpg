import attr
from krpg.engine.npc import Npc
from krpg.entity.inventory import Item
from krpg.utils import Nameable


@attr.s(auto_attribs=True)
class Location(Nameable):
    items: list[tuple[Item, int]] = []
    npcs: list[Npc] = []
    locked: bool = False


@attr.s(auto_attribs=True)
class Map:
    locations: list[Location] = []
    current_location: Location | None = None
    start_location: Location | None = None
    roads: list[tuple[Location, Location]] = []
