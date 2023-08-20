from __future__ import annotations
from typing import TYPE_CHECKING
from krpg.actions import action
from krpg.attributes import Attributes
from krpg.bestiary import Meta
from krpg.inventory import Item, ItemType
from krpg.npc import Npc
from krpg.quests import Quest
from krpg.scenario import Section
from krpg.world import Location

if TYPE_CHECKING:
    from krpg.game import Game


class Builder:
    def __init__(self, game: Game):
        self.game = game
        self.scenario = game.scenario
        self.game.add_saver("test", self.save, self.load)
        self.tag = ""
    def save(self):
        g = self.game
        return [g.scenario_hash, g.version, g.start_time, g.save_time]

    def load(self, data):
        g = self.game
        if data[0] != g.scenario_hash:
            raise Exception(f"save:{data[0]} != game:{g.scenario_hash}")
        if data[1] != g.version:
            raise Exception(f"save:{data[1]} != game:{g.version}")

    def debug(self, msg: str):
        self.game.log.debug(f"[cyan]\[{self.tag:^10}] {msg}", stacklevel=2)

    def build(self):
        
        self.tag = "items"
        self.build_items(self.scenario.first("items"))
        self.tag = "entities"
        self.build_entities(self.scenario.first("entities"))
        self.tag = "npc"
        self.build_npcs(self.scenario.first("npcs"))
        self.tag = "quests"
        self.build_quests(self.scenario.first("quests"))
        self.tag = "world"
        self.build_world(self.scenario.first("map"))
        self.tag = ""

    def build_items(self, items: Section):
        item_list = items.all("item")
        for item in item_list:
            id, name, description = item.args
            obj = Item(id, name, description)
            self.debug(f"  Building [blue]{id}:{name}")
            for cmd in item.children:
                if cmd.name == "wear":
                    wear, *attrs = cmd.args
                    attrs = list(map(int, attrs))
                    if wear not in ItemType.__members__:
                        raise Exception(f"Invalid item type: {wear}")
                    if len(attrs) != 7:
                        raise Exception(
                            f"Invalid amount of SPECIAW attrs ({len(attrs)})"
                        )
                    obj.set_wear(ItemType[wear], Attributes(*attrs))
                elif cmd.name == "use":
                    act, am = cmd.args
                    am = int(am)
                    obj.set_use(act, am)
                elif cmd.name == "stack":
                    obj.set_stack(int(cmd.args[0]))
                elif cmd.name == "cost":
                    sell, buy = map(int, cmd.args)
                    obj.set_cost(sell, buy)
            self.game.bestiary.items.append(obj)

    def build_entities(self, entities: Section):
        for entity in entities.all("entity"):
            id, name, description = entity.args
            self.debug(f"  Assembling [blue]{id}:{name}")
            speciaw = entity.first("speciaw")
            speciaw = map(int, speciaw.args)
            if money := entity.first("money"):
                money = int(money.args[0])
            else:
                money = 0
            attr = Attributes(*speciaw, free=0)
            meta = Meta(id, name, description, attr, money)
            self.game.bestiary.entities.append(meta)

    def build_npcs(self, npcs: Section):
        for npc in npcs.all("npc"):
            id, name, description = npc.args
            self.debug(f"  Creating [blue]{id}:{name}")
            init_state = npc.first("init").args[0]
            location = npc.first("location").args[0]
            actions = {}
            for state in npc.all("state"):
                actions[state.args[0]] = []
                for act in state.all("action"):
                    actions[state.args[0]].append(self.build_action(act))
            new_npc = Npc(id, name, description, init_state, location, actions)
            self.game.npc_manager.npcs.append(new_npc)

    def build_quests(self, quests: Section):
        for quest in quests.all("quest"):
            id, name, description = quest.args
            self.debug(f"  Building [blue]{id}:{name}")
            stages = {}
            for stage in quest.all("stage"):
                sid, sname = stage.args
                stages[sid] = {}
                stages[sid]["name"] = sname
                stages[sid]["goals"] = stage.all("goal")
                stages[sid]["rewards"] = stage.all("reward")
            self.game.quest_manager.quests.append(Quest(id, name, description, stages))
        
                

    def build_world(self, world: Section):
        locations = world.all("location")
        start = world.first("start")
        links = world.all("link")
        self.debug(f"  Found {len(locations)} locations")
        self.debug(f"  Found {len(links)} links")
        self.debug(f"  Found start={start.args[0]}")

        for location in locations:
            loc = self.build_location(location)
            self.game.world.add(loc)

        for link in links:
            a, b = link.args
            self.game.world.road(a, b)
            self.debug(f"  Road {a} <-> {b}")

        self.game.world._start = start.args[0]

    def build_location(self, locdata: Section):

        id, name, description = locdata.args
        actions = [self.build_action(i) for i in locdata.all("action")]
        items = [self.build_item(i) for i in locdata.all("item")]
        triggers = self.build_triggers(locdata.first("triggers"))
        location = Location(id, name, description)
        location.actions = actions
        location.items = items
        location.triggers = triggers
        self.debug(f"    Built [blue]{id}:{name}")
        return location

    def build_item(self, item: Section):
        id, amo = item.args
        self.debug
        self.game.bestiary.get_item(id)  # Check if item exists
        amo = int(amo)
        return [id, amo]

    def build_action(self, command: Section):
        name, description = command.args
        block = self.game.executer.create_block(command)

        def new_command(game: Game):
            block.run()

        return action(name, description)(new_command)

    def build_triggers(self, triggers: Section | None):
        res = []
        if not triggers:
            return res
        for i in triggers.children:
            res.append((i.name, i.args, self.game.executer.create_block(i)))
        return res