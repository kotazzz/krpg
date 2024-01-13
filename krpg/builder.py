from __future__ import annotations

from typing import TYPE_CHECKING, Any

from krpg.actions import Action
from krpg.attributes import Attributes
from krpg.bestiary import Meta
from krpg.executer import Block
from krpg.inventory import Item, ItemType
from krpg.npc import Npc
from krpg.quests import Quest
from krpg.scenario import Command, Section
from krpg.world import Location

if TYPE_CHECKING:
    from krpg.game import Game


class InvalidScenario(Exception):
    pass


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
        """Save game data.

        Returns
        -------
        list[Any]
            A list of game data.
        """
        # Save game data
        g = self.game
        return [g.scenario.hash, g.version, g.start_time, g.save_time]

    def load(self, data):
        """Load game data.

        Parameters
        ----------
        data : list[Any]
            A list of game data.

        Raises
        ------
        ValueError
            Scenario hash or game version mismatch
        """
        # Load game data
        g = self.game
        if data[0] != g.scenario.hash:
            raise ValueError(f"save:{data[0]} != game:{g.scenario.hash}")
        if data[1] != g.version:
            raise ValueError(f"save:{data[1]} != game:{g.version}")

    def debug(self, msg: str):
        """Log a debug message.

        Parameters
        ----------
        msg : str
            The message to log.
        """
        # Log a debug message
        self.game.log.debug(f"[cyan]\\[{self.tag:^10}] {msg}", stacklevel=2)

    def build(self):
        """Build all components of the game."""
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
            section = self.scenario.first_section(tag)
            if section:
                self.debug(f"Building {tag}")
                func(section)
            else:
                self.debug(f"[red]No {tag} found")
        self.tag = ""

    def build_items(self, items: Section):
        """Build the items in the game.

        Parameters
        ----------
        items : Section
            The items section of the scenario.

        Raises
        ------
        InvalidScenario
            If the item type is invalid.
        """
        # Build the items in the game
        item_list = items.all("item")
        for item in item_list:
            identifier, name, description = item.args
            obj = Item(identifier, name, description)
            self.debug(f"  Building [blue]{identifier}:{name}")
            if not isinstance(item, Command):
                for cmd in item.children:
                    if cmd.name == "wear":
                        wear, attrs = cmd.args[0], list(int(i) for i in cmd.args[1:])

                        if wear not in ItemType.__members__:
                            raise InvalidScenario(f"Invalid item type: {wear}")
                        if len(attrs) != 7:
                            raise InvalidScenario(
                                f"Invalid amount of SPECIAW attrs ({len(attrs)})"
                            )

                        obj.set_wear(
                            ItemType[wear],
                            Attributes(
                                attrs[0],
                                attrs[1],
                                attrs[2],
                                attrs[3],
                                attrs[4],
                                attrs[5],
                                attrs[6],
                                holder=None,
                            ),
                        )
                    elif cmd.name == "use":
                        act, am = cmd.args
                        obj.set_use(act, int(am))
                    elif cmd.name == "stack":
                        obj.set_stack(int(cmd.args[0]))
                    elif cmd.name == "cost":
                        sell, buy = map(int, cmd.args)
                        obj.set_cost(sell, buy)
                    elif cmd.name == "throwable":
                        obj.throwable = cmd.args[0] == "true"
            else:
                # "Краткая" запись предмета без уточнения аттрибутов чаще используется для квестовых предметов
                obj.throwable = False
            self.game.bestiary.items.append(obj)

    def build_entities(self, entities: Section):
        """Build the entities in the game.

        Parameters
        ----------
        entities : Section
            The entities section of the scenario.
        """
        # Build the entities in the game
        for entity in entities.all_sections("entity"):
            identifier, name, description = entity.args
            self.debug(f"  Assembling [blue]{identifier}:{name}")
            speciaw = [int(i) for i in entity.first_command("speciaw").args]
            if money_data := entity.first_command("money"):
                money = int(money_data.args[0])
            else:
                money = 0
            attr = Attributes(
                speciaw[0],
                speciaw[1],
                speciaw[2],
                speciaw[3],
                speciaw[4],
                speciaw[5],
                speciaw[6],
                free=0,
            )
            meta = Meta(identifier, name, description, attr, money)
            self.game.bestiary.entities.append(meta)

    def build_npcs(self, npcs: Section):
        """Build the NPCs in the game.

        Parameters
        ----------
        npcs : Section
            The NPCs section of the scenario.
        """
        # Build the NPCs in the game
        for npc in npcs.all_sections("npc"):
            identifier, name, description = npc.args
            self.debug(f"  Creating [blue]{identifier}:{name}")
            init_state = npc.first_command("init").args[0]
            location = npc.first_command("location").args[0]
            actions: dict[str, list[Action]] = {}
            requirements = {}
            for state in npc.all_sections("state"):
                state_name = state.args[0]
                actions[state_name] = []
                for act in state.all_sections("action"):
                    actions[state_name].append(self.build_action(act))
                # action_req <action_name> <condition>
                for req in state.all_commands("action_req"):
                    # npc:
                    # self.requirements: dict[str, str] = requirements  # {state "." action: python_eval}
                    requirements[f"{state_name}.{req.args[0]}"] = req.args[1]
            new_npc = Npc(
                identifier,
                name,
                description,
                init_state,
                location,
                actions,
                requirements,
            )
            self.game.npc_manager.npcs.append(new_npc)

    def build_quests(self, quests: Section):
        """Build the quests in the game.

        Parameters
        ----------
        quests : Section
            The quests section of the scenario.
        """
        # Build the quests in the game
        for quest in quests.all_sections("quest"):
            identifier, name, description = quest.args
            self.debug(f"  Building [blue]{identifier}:{name}")
            stages: dict[str | int, dict[str, Any]] = {}
            for stage in quest.all_sections("stage"):
                sid_str, sname = stage.args
                sid: int | str = int(sid_str) if sid_str.isdigit() else sid_str
                stages[sid] = {}
                stages[sid]["name"] = sname
                stages[sid]["goals"] = [i.args for i in stage.all("goal")]
                stages[sid]["rewards"] = [i.args for i in stage.all("reward")]
            self.game.quest_manager.quests.append(
                Quest(identifier, name, description, stages)
            )

    def build_world(self, world: Section):
        """Build the world map in the game.

        Parameters
        ----------
        world : Section
            The world section of the scenario.
        """
        # Build the world map in the game
        locations = world.all_sections("location")
        start = world.first_command("start")
        links = world.all_commands("link")
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

        self.game.world.set_start(start.args[0])

    def build_location(self, locdata: Section) -> Location:
        """Build a location in the game.

        Parameters
        ----------
        locdata : Section
            The location section of the scenario.

        Returns
        -------
        Location
            The created location object.
        """
        # Build a location in the game
        identifier, name, description = locdata.args
        location = Location(identifier, name, description)

        actions = [self.build_action(i) for i in locdata.all_sections("action")]
        location.actions = actions

        items = [self.build_item(i) for i in locdata.all("item")]
        location.items = items

        if locdata.has_section("triggers"):
            triggers = self.build_triggers(locdata.first_section("triggers"))
            location.triggers.extend(triggers)

        self.debug(f"    Built [blue]{identifier}:{name}")
        return location

    def build_item(self, item: Section | Command) -> tuple[str, int]:
        """Build an item in the game.

        Parameters
        ----------
        item : Section | Command
            The item section of the scenario.

        Returns
        -------
        tuple[str, int]
            The created item id and amount.
        """
        # Build an item in the game
        identifier: str = item.args[0]
        amo: int = int(item.args[1])
        self.debug(f"    Item [blue]{identifier}[/blue] x{amo}")
        self.game.bestiary.get_item(identifier)  # Check if item exists
        return (identifier, amo)

    def build_action(self, command: Section) -> Action:
        """Build an action in the game.

        Parameters
        ----------
        command : Section
            The action section of the scenario.

        Returns
        -------
        Action
            The created action object.
        """
        # Build an action in the game
        name, description = command.args
        block = self.game.executer.create_block(command)

        return Action(name, description, "", block.run)

    def build_triggers(self, triggers: Section) -> list[tuple[str, list[str], Block]]:
        """Build triggers for a location in the game.

        Parameters
        ----------
        triggers : Section
            The triggers section of the scenario.

        Returns
        -------
        list[tuple[str, list[str], Block]]
            A list of created triggers.
        """
        # Build triggers for a location in the game
        res: list[tuple[str, list[str], Block]] = []
        for i in triggers.all_sections():
            res.append((i.name, i.args, self.game.executer.create_block(i)))
        return res

    def __repr__(self):
        return "<Builder>"
