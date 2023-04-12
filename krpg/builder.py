from __future__ import annotations
from typing import TYPE_CHECKING
from krpg.actions import action
from krpg.scenario import Section
from krpg.world import Location

if TYPE_CHECKING:
    from krpg.game import Game


class Builder:
    def __init__(self, game: Game):
        self.game = game
        self.scenario = game.scenario
        self.debug = self.game.log.debug
        self.game.add_saver("test", self.save, self.load)
    
    def save(self):
        return [self.game.scenario_hash, self.game.version]
    
    def load(self, data):
        if data[0] != self.game.scenario_hash:
            raise Exception(f"save:{data[0]} != game:{self.game.scenario_hash}")
        if data[1] != self.game.version:
            raise Exception(f"save:{data[1]} != game:{self.game.version}")
    
    def build(self):
        self.build_world(self.scenario.first("map"))

    def build_world(self, world: Section):

        locations = world.all("location")
        start = world.first("start")
        links = world.all("link")
        self.debug(f"Found {len(locations)} locations")
        self.debug(f"Found start={start}")
        self.debug(f"Found {len(links)} links")

        for location in locations:
            loc = self.build_location(location)
            self.game.world.add(loc)
        
        for link in links:
            a, b = link.args
            self.game.world.road(a, b)
            self.debug(f'Road {a} <-> {b}')
            
        self.game.world.set(start.args[0])

    def build_location(self, locdata: Section):

        id, name, description = locdata.args
        actions = [self.build_action(i) for i in locdata.children]
        location = Location(id, name, description)
        location.actions = actions
        self.debug(f"Built {location}")
        return location

    def build_action(self, command: Section):
        name, description = command.args

        def new_command(game: Game):
            for cmd in command.children:
                self.game.executer.execute(cmd)

        return action(name, description)(new_command)
