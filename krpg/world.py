from __future__ import annotations

from typing import TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from .game import Game

from .core.actions import Action, ActionManager, action


class Location:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

        self.state = "none"
        self.dynamic = [self.get_actions]
        self.states: dict[str, ActionManager] = {}

    def save(self):
        return self.state

    def load(self, data):
        self.state = data

    def add_state(self, name: str, manager: ActionManager):
        self.states[name] = manager

    def get_actions(self):
        return self.states[self.state].actions


class World(ActionManager):
    def __init__(self, game: Game):
        self._current: Location = Location("loc", "Локация", "Описание")
        self.game = game
        game.add_saver("map", self.save, self.load)
        self.locations: list[Location] = []
        self.edges: dict[str : list[str]] = defaultdict(list)

        ActionManager.__init__(self)
        self.dynamic = [self.get_actions]
        game.expand_actions(self)
        self.load_scenario()

    def save(self):
        return [self.current.id, {loc.id: loc.save() for loc in self.locations}]

    def load(self, data):
        current, states = data
        self.set_current(current)
        for locid, state in states.items():
            self.get_location(locid).state = state

    def get_actions(self):
        return self.current.get_actions()

    def load_scenario(self):
        map = self.game.scenario.first("map")
        for loc in map.all("location"):
            id, name, description = loc.args
            self.game.logger.debug(f"Building location {name}")
            location = Location(id, name, description)

            for state in loc.all("state"):
                actions = []
                self.game.logger.debug(f"  Building state {state.args[0]}")
                for action in state.all("action"):
                    self.game.logger.debug(f"    Building action {action.args[0]}")

                    def action_cb(game: Game):
                        for cmd in action.children:
                            game.executer.execute(cmd)

                    a_name, a_desc = action.args
                    act = Action(a_name, a_desc, name, action_cb)
                    actions.append(act)
                state_name = state.args[0]
                manager = ActionManager.from_list(actions)
                location.add_state(state_name, manager)

            self.add_location(location)

        self.set_current(map.first("start").args[0])
        for link in map.all("link"):
            a, b = link.args
            self.add_edge(a, b)

    @property
    def current(self):
        return self._current

    def set_current(self, location: str | Location):
        self._current = self.get_location(location)

    def add_location(self, location: Location):
        if self.get_location(location.id):
            raise Exception(f"{location.id!r} already exists")
        self.locations.append(location)

    def add_edge(self, loc1: str | Location, loc2: str | Location):
        loc1, loc2 = self.get_location(loc1), self.get_location(loc2)
        if loc1.id not in self.edges:
            self.edges[loc1.id] = []
        if loc2.id not in self.edges:
            self.edges[loc2.id] = []
        self.edges[loc1.id].append(loc2.id)
        self.edges[loc2.id].append(loc1.id)

    def remove_edge(self, loc1, loc2):
        loc1, loc2 = self.get_location(loc1), self.get_location(loc2)
        if loc1.id in self.edges:
            self.edges[loc1.id].remove(loc2.id)
        if loc2.id in self.edges:
            self.edges[loc2.id].remove(loc1.id)

    def get_locations(self) -> list[str]:
        return [location.id for location in self.locations]

    def get_linked_locations(self, location_id: str | Location) -> list[str]:
        location_id = self.get_location(location_id).id
        return self.edges[location_id]

    def get_location(self, location_id: Location | str) -> Location | None:
        if isinstance(location_id, Location):
            return location_id

        for location in self.locations:
            if location.id == location_id:
                return location
        return None

    @action("go", "Пойти", "Действия")
    def go(game: Game):
        world = game.world
        c = game.console

        locations = world.get_linked_locations(world.current)
        if not locations:
            return c.print("[red]Рядом нет доступных локаций[/]")

        for i, locid in enumerate(locations, 1):
            loc = world.get_location(locid)
            c.print(f" [yellow]{i} [green] - {loc.name}: {loc.description}")
        select = c.number_menu(
            "Выберите локацию (e-выход): ", len(locations), exit_cmd="e"
        )
        if select != "e":
            game.eh.dispatch(
                "player_move", before=world.current.id, after=locations[select]
            )
            world.set_current(locations[select])
            loc = world.get_location(locations[select])
            c.print(f"[green]Вы отправляетесь в {loc.name}[/]")
    
#     @action("go", "Пойти", "Действия")
    
    def __repr__(self):
        return f"<World loc={len(self.locations)}>"
