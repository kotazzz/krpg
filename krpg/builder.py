from __future__ import annotations
from typing import TYPE_CHECKING
from krpg.actions import Action
from krpg.attributes import Attributes
from krpg.bestiary import Meta
from krpg.inventory import Item, ItemType
from krpg.npc import Npc
from krpg.quests import Quest
from krpg.scenario import Command, Section
from krpg.world import Location

if TYPE_CHECKING:
    from krpg.game import Game


class Builder:
    """
    The Builder class is responsible for building various components of the game based on the scenario data.

    Args:
        game (Game): The game instance.

    Attributes:
        game (Game): The game instance.
        scenario (Scenario): The scenario instance.
        tag (str): The current tag for logging purposes.

    Methods:
        save: Saves the game data.
        load: Loads the game data.
        debug: Logs a debug message.
        build: Builds all components of the game.
        build_items: Builds the items in the game.
        build_entities: Builds the entities in the game.
        build_npcs: Builds the NPCs in the game.
        build_quests: Builds the quests in the game.
        build_world: Builds the world map in the game.
        build_location: Builds a location in the game.
        build_item: Builds an item in the game.
        build_action: Builds an action in the game.
        build_triggers: Builds triggers for a location in the game.
    """

    def __init__(self, game: Game):
        self.game = game
        self.scenario = game.scenario
        self.game.add_saver("test", self.save, self.load)
        self.tag = ""
        self.build()

    def save(self):
        # Save game data
        g = self.game
        return [g.scenario.hash, g.version, g.start_time, g.save_time]

    def load(self, data):
        # Load game data
        g = self.game
        if data[0] != g.scenario.hash:
            raise Exception(f"save:{data[0]} != game:{g.scenario.hash}")
        if data[1] != g.version:
            raise Exception(f"save:{data[1]} != game:{g.version}")

    def debug(self, msg: str):
        # Log a debug message
        self.game.log.debug(f"[cyan]\[{self.tag:^10}] {msg}", stacklevel=2)

    def build(self):
        # Build all components of the game
        blocks = {
            (self.build_items, "items"),
            (self.build_entities, "entities"),
            (self.build_npcs, "npcs"),
            (self.build_quests, "quests"),
            (self.build_world, "map"),
        }
        for func, tag in blocks:
            self.tag = tag
            section = self.scenario.first(tag)
            if section:
                self.debug(f"Building {tag}")
                func(section)
            else:
                self.debug(f"[red]No {tag} found")
        self.tag = ""

    def build_items(self, items: Section):
        # Build the items in the game
        item_list = items.all("item")
        for item in item_list:
            id, name, description = item.args
            obj = Item(id, name, description)
            self.debug(f"  Building [blue]{id}:{name}")
            if not isinstance(item, Command):
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
                    elif cmd.name == "throwable":
                        #! true, not True
                        obj.throwable = cmd.args[0] == "true"
            else:
                # "Краткая" запись предмета без уточнения аттрибутов чаще используется для квестовых предметов
                obj.throwable = False
            self.game.bestiary.items.append(obj)

    def build_entities(self, entities: Section):
        # Build the entities in the game
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
        # Build the NPCs in the game
        for npc in npcs.all("npc"):
            id, name, description = npc.args
            self.debug(f"  Creating [blue]{id}:{name}")
            init_state = npc.first("init").args[0]
            location = npc.first("location").args[0]
            actions = {}
            requirements = {}
            for state in npc.all("state"):
                state_name = state.args[0]
                actions[state_name] = []
                for req in state.all("action"):
                    actions[state_name].append(self.build_action(req))
                # action_req <action_name> <condition> 
                for req in state.all("action_req"):
                    # npc:
                    # self.requirements: dict[str, str] = requirements  # {state "." action: python_eval}
                    requirements[f"{state_name}.{req.args[0]}"] = req.args[1]
            new_npc = Npc(id, name, description, init_state, location, actions, requirements)
            self.game.npc_manager.npcs.append(new_npc)

    def build_quests(self, quests: Section):
        # Build the quests in the game
        for quest in quests.all("quest"):
            id, name, description = quest.args
            self.debug(f"  Building [blue]{id}:{name}")
            stages = {}
            for stage in quest.all("stage"):
                sid, sname = stage.args
                sid = int(sid) if sid.isdigit() else sid
                stages[sid] = {}
                stages[sid]["name"] = sname
                stages[sid]["goals"] = [i.args for i in stage.all("goal")]
                stages[sid]["rewards"] = [i.args for i in stage.all("reward")]
            self.game.quest_manager.quests.append(Quest(id, name, description, stages))

    def build_world(self, world: Section):
        # Build the world map in the game
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
        # Build a location in the game
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
        # Build an item in the game
        id, amo = item.args
        self.debug
        self.game.bestiary.get_item(id)  # Check if item exists
        amo = int(amo)
        return [id, amo]

    def build_action(self, command: Section):
        # Build an action in the game
        name, description = command.args
        block = self.game.executer.create_block(command)

        return Action(name, description, "", block.run)

    def build_triggers(self, triggers: Section | None):
        # Build triggers for a location in the game
        res = []
        if not triggers:
            return res
        for i in triggers.children:
            res.append((i.name, i.args, self.game.executer.create_block(i)))
        return res

    def __repr__(self):
        return "<Builder>"
