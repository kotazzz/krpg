from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from krpg import ROOT_DIR
from krpg.engine.executer import Scenario
from krpg.engine.npc import Npc
from krpg.engine.quests import Objective, Quest, Reward, Stage, objectives_names, rewards_names
from krpg.engine.world import Location
from krpg.entity.enums import SlotType
from krpg.entity.inventory import Item, Slot
from krpg.parser import Section, parse, tokenize
from krpg.utils import get_by_id

if TYPE_CHECKING:
    from krpg.game import Game

MAIN_FILE = "main.krpg"

BASE_FOLDER = "content"


def wrap_log[T](game: Game, section: Section, name: str, func: Callable[[Game, Section], T], indent: int = 0) -> T:
    game.console.log.debug(f"[Builder] {'  '*indent}Building {name}")
    return func(game, section)


def build_scenario(game: Game, section: Section):
    game.bestiary.add(
        game.executer.create_scenario(section),
    )


def build_scenarios(game: Game, section: Section) -> None:
    for scenario in section.all(command=False):
        assert isinstance(scenario, Section)
        if not scenario.name:
            raise ValueError
        wrap_log(game, scenario, scenario.name, build_scenario, 1)


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


def create_stage(game: Game, section: Section) -> list[Scenario]:
    stage_actions: list[Scenario] = []
    for action in section.all():
        assert isinstance(action, Section)
        sc = game.executer.create_scenario(action)
        stage_actions.append(sc)
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
            location.items.append(Slot(item=item, count=int(item_data.args[1])))
        else:
            location.items.append(Slot(item=item, count=1))
    for npc_data in section.all("npc"):
        assert len(npc_data.args) == 1, "Syntax: npc [id]"
        npc_id = npc_data.args[0]
        npc = game.bestiary.get_entity_by_id(npc_id, Npc)
        assert npc
        location.npcs.append(npc)

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
            game.world.current_location = loc
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
    stage_description = section.content[0]

    objectives: list[Objective] = []
    rewards: list[Reward] = []

    for goal in section.all("goal"):
        obj_type, *args, description = goal.args
        assert obj_type in objectives_names, f"Unknown objective type {obj_type}"
        obj = objectives_names[obj_type](description, *args)
        objectives.append(obj)

    for reward in section.all("end"):
        reward_type, *args = reward.args
        assert reward_type in rewards_names, f"Unknown reward type {reward_type}"
        rewards.append(rewards_names[reward_type](*args))
    stage = Stage(description=stage_description, objectives=objectives, rewards=rewards)
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


def build(game: Game) -> None:
    if __package__ is None:
        raise ValueError("Package is not set")
    path = f"{ROOT_DIR}/{BASE_FOLDER}/{MAIN_FILE}"
    with open(path, "r", encoding="utf-8") as file:
        main_scenario = parse(tokenize(file.read()))

    steps = [
        ("scenarios", build_scenarios),
        ("items", build_items),
        ("npcs", build_npcs),
        ("locations", build_locations),
        ("quests", build_quests),
    ]
    for name, step in steps:
        section = main_scenario.get(name)
        if section:
            assert isinstance(section, Section)
            wrap_log(game, section, name, step)

    init = main_scenario.get("init")
    if not init:
        raise ValueError("No init section found")
    assert isinstance(init, Section)
    game.executer.run(init)
