
from __future__ import annotations

from typing import TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from .game import Game  
    
from .core.actions import Action, ActionManager, action
    
class Location(ActionManager):
    def __init__(self, name, description):
        ActionManager.__init__(self)
        self.name = name
        self.description = description

    
class World(ActionManager):
    def __init__(self, game: Game):
        self._current: Location = Location("Локация", "Описание")
        self.game = game
        self.game.savers['map'] = (self.save, self.load)
        self.locations: list[Location] = []
        self.edges: dict[str: list[str]] = defaultdict(list)
        
        ActionManager.__init__(self)
        self.dynamic = [self.get_actions]
        game.expand_actions(self)
        self.load_scenario()

    def get_actions(self):
        return self.current.actions

    def load_scenario(self):
        map = self.game.scenario.first("map")
        for loc in map.all("location"):
            name, description = loc.args
            self.game.logger.debug(f"Building location {name}, actions: {[a.args[0] for a in loc.all('action')]}")
            location = Location(name, description)
            for action in loc.all("action"):
                def action_cb(game: Game):
                    for cmd in action.children:
                        game.executer.execute(cmd)
                a_name, a_desc = action.args
                act = Action(a_name, a_desc, name, action_cb)
                location.register(act)
            self.add_location(location)
        self.set_current(map.first('start').args[0])
        for link in map.all("link"):
            a, b = link.args
            self.add_edge(a, b)
                
    
    def save(self):
        return self.current.name
    
    def load(self, data):
        self.set_current(data)
    
    @property
    def current(self):
        return self._current
    
    def set_current(self, location: str | Location):
        self._current = self.get_location(location)

    def add_location(self, location: Location):
        if self.get_location(location.name):
            raise Exception(f"{location.name!r} already exists")
        self.locations.append(location)

    def add_edge(self, loc1: str | Location, loc2: str | Location):
        loc1, loc2 = self.get_location(loc1), self.get_location(loc2)
        if loc1.name not in self.edges:
            self.edges[loc1.name] = []
        if loc2.name not in self.edges:
            self.edges[loc2.name] = []
        self.edges[loc1.name].append(loc2.name)
        self.edges[loc2.name].append(loc1.name)

    def remove_edge(self, loc1, loc2):
        loc1, loc2 = self.get_location(loc1), self.get_location(loc2)
        if loc1.name in self.edges:
            self.edges[loc1.name].remove(loc2.name)
        if loc2.name in self.edges:
            self.edges[loc2.name].remove(loc1.name)

    def get_locations(self) -> list[str]:
        return [location.name for location in self.locations]

    def get_linked_locations(self, location_name: str|Location) -> list[str]:
        location_name = self.get_location(location_name).name
        return self.edges[location_name]

    def get_location(self, location_name: Location | str) -> Location | None:
        if isinstance(location_name, Location):
            return location_name
        
        for location in self.locations:
            if location.name == location_name:
                return location
        return None
    
    @action("go", "Пойти", "Действия")
    def go(game: Game):
        world = game.world
        c = game.console
        
        locations = world.get_linked_locations(world.current)
        if not locations:
            return c.print('[red]Рядом нет доступных локаций[/]')
            
        for i, locname in enumerate(locations):
            loc = world.get_location(locname)
            c.print(f" [yellow]{i} [green] - {loc.name}: {loc.description}")
        select = c.number_menu("Выберите локацию (e-выход): ", len(locations), exit_cmd="e")
        if select != "e":
            world.set_current(locations[select])
        