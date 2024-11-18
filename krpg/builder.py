from __future__ import annotations
from krpg.engine.actions import Action
from krpg.engine.npc import Npc
from krpg.engine.quests import Objective, ObjectiveType, Quest, Reward, RewardType, Stage, args_map
from krpg.entity.enums import SlotType
from krpg.entity.inventory import Item
from krpg.engine.world import Location
from krpg.parser import Section, parse, tokenize
from typing import TYPE_CHECKING, Any, Callable
import os

from krpg.utils import get_by_id


if TYPE_CHECKING:
    from krpg.game import Game

MAIN_FILE = "main.krpg"

BASE_FOLDER = "content"

type ScenarioBuilder = Callable[[Game, Section], Any]


def wrap_log(game: Game, section: Section, name: str, func: ScenarioBuilder, indent: int = 0) -> Any:
    game.console.log.debug(f"[Builder] {'  '*indent}Building {name}")
    return func(game, section)


def build_scenarios(game: Game, section: Section) -> None:
    for scenario in section.all(command=False):
        assert isinstance(scenario, Section)
        game.bestiary.add(
            game.executer.create_scenario(scenario),
        )


def build_item(game: Game, section: Section) -> None:
    assert len(section.content) == 3, f"Expected 3 arguments, got {len(section.content)}"
    id, name, description = section.content
    item = Item(id=id, name=name, description=description)
    for prop in section.all():
        if prop.name == "slot_type":
            assert len(prop.args) == 1, f"Expected 1 argument, got {len(prop.args)}"
            assert prop.args[0] in SlotType.__members__, f"Unknown slot type {prop.content}"
            item.slot_type = SlotType[prop.args[0]]
        elif prop.name == "stack":
            assert len(prop.args) == 1, f"Expected 1 argument, got {len(prop.args)}"
            assert prop.args[0].isdigit(), f"Expected digit, got {prop.args[0]}"
            item.stack = int(prop.args[0])
        # TODO: Add more properties
        else:
            raise ValueError(f"Unknown property {prop.name}")
    game.bestiary.add(item)


def build_items(game: Game, section: Section) -> None:
    for item in section.all(command=False):
        assert isinstance(item, Section)
        assert item.name, "Item id is required"
        wrap_log(game, item, item.name, build_item, 1)


def create_stage(game: Game, section: Section) -> list[Action]:
    stage_actions: list[Action] = []
    for action in section.all():
        assert isinstance(action, Section)
        act = game.executer.create_action(action)
        stage_actions.append(act)
    return stage_actions


def build_npc(game: Game, section: Section) -> None:
    assert len(section.content) == 3, f"Expected 3 arguments, got {len(section.content)}"
    id, name, description = section.content
    npc = Npc(id=id, name=name, description=description)
    for i, stage in enumerate(section.all()):
        assert isinstance(stage, Section)
        stage_actions = wrap_log(game, stage, str(i), create_stage, 2)
        npc.stages.append(stage_actions)
    game.bestiary.add(npc)


def build_npcs(game: Game, section: Section) -> None:
    for npc in section.all(command=False):
        assert isinstance(npc, Section)
        assert npc.name, "NPC id is required"
        wrap_log(game, npc, npc.name, build_npc, 1)


def build_location(game: Game, section: Section) -> None:
    assert len(section.content) == 3, f"Expected 3 arguments, got {len(section.content)}"
    id, name, description = section.content
    location = Location(id=id, name=name, description=description)
    for i, stage in enumerate(section.all(command=False)):
        assert isinstance(stage, Section)
        stage_actions = wrap_log(game, stage, str(i), create_stage, 2)
        location.stages.append(stage_actions)
    for item_data in section.all("item"):
        assert len(item_data.args) in (
            1,
            2,
        ), f"Expected 1 or 2 arguments, got {len(item_data.args)}"
        id = item_data.args[0]
        item = game.bestiary.get_entity_by_id(id, Item)
        assert item is not None, f"Item {id} not found"
        if len(item_data.args) == 2:
            assert item_data.args[1].isdigit(), f"Expected digit, got {item_data.args[1]}"
            location.items.append((item, int(item_data.args[1])))
        else:
            location.items.append((item, 1))

    game.world.locations.append(location)


def build_locations(game: Game, section: Section) -> None:
    for location in section.all(command=False):
        assert isinstance(location, Section)
        assert location.name, "Location id is required"
        wrap_log(game, location, location.name, build_location, 1)
    for command in section.all(section=False):
        if command.name == "start":
            loc = get_by_id(game.world.locations, command.args[0])
            assert loc is not None, f"Location {command.args[0]} not found"
            assert game.world.start_location is None, "Start location already set"
            game.world.start_location = loc
        elif command.name == "link":
            loc = get_by_id(game.world.locations, command.args[0])
            assert loc is not None, f"Location {command.args[0]} not found"
            loc2 = get_by_id(game.world.locations, command.args[1])
            assert loc2 is not None, f"Location {command.args[1]} not found"
            game.world.link(loc, loc2)
        elif command.name == "lock":
            loc = get_by_id(game.world.locations, command.args[0])
            assert loc is not None, f"Location {command.args[0]} not found"
            loc.locked = True


def create_quest_stage(game: Game, section: Section) -> Stage:
    assert len(section.content) == 1, f"Expected 1 argument, got {len(section.content)}"
    description = section.content[0]

    objectives: list[Objective] = []
    rewards: list[Reward] = []

    def convert_args(args: list[str], key: ObjectiveType | RewardType) -> list[Any]:
        assert len(args) == len(args_map[key]), f"Expected {len(args_map[key])} arguments, got {len(args)}"
        mapped = [args_map[key][i](arg) for i, arg in enumerate(args)]
        return mapped

    for goal in section.all("goal"):
        obj_type, *args, description = goal.args
        assert obj_type in ObjectiveType.__members__, f"Unknown objective type {obj_type}"
        objective_type = ObjectiveType[obj_type]
        mapped = convert_args(args, objective_type)
        obj = Objective(description=description, type=objective_type, args=mapped)
        objectives.append(obj)
    for reward in section.all("end"):
        reward_type, *args = reward.args
        assert reward_type in RewardType.__members__, f"Unknown reward type {reward_type}"
        reward_type = RewardType[reward_type]
        mapped = convert_args(args, reward_type)
        rew = Reward(type=reward_type, args=mapped)
        rewards.append(rew)
    stage = Stage(description=description, objectives=objectives, rewards=rewards)
    return stage


def build_quest(game: Game, section: Section) -> None:
    assert len(section.content) == 3, f"Expected 3 arguments, got {len(section.content)}"
    id, name, description = section.content
    quest = Quest(id=id, name=name, description=description)
    for stage in section.all():
        assert isinstance(stage, Section)
        quest_stage = create_quest_stage(game, stage)
        quest.stages.append(quest_stage)
    game.bestiary.add(quest)


def build_quests(game: Game, section: Section) -> None:
    for quest in section.all(command=False):
        assert isinstance(quest, Section)
        assert quest.name, "Quest id is required"
        wrap_log(game, quest, quest.name, build_quest, 1)


class Builder:
    def __init__(self, game: Game):
        self.game = game

    def build(self) -> None:
        if __package__ is None:
            raise ValueError("Package is not set")
        path = f"{os.path.abspath(__package__)}/{BASE_FOLDER}/{MAIN_FILE}"
        with open(path, "r", encoding="utf-8") as file:
            self.main = parse(tokenize(file.read()))

        steps = [
            ("scenarios", build_scenarios),
            ("items", build_items),
            ("npcs", build_npcs),
            ("locations", build_locations),
            ("quests", build_quests),
        ]
        for name, step in steps:
            section = self.main.get(name)
            if section:
                assert isinstance(section, Section)
                wrap_log(self.game, section, name, step)

        init = self.main.get("init")
        if not init:
            raise ValueError("No init section found")
        assert isinstance(init, Section)
        self.game.executer.run(init)
