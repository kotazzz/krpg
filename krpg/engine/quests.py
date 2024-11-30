from __future__ import annotations

from enum import Enum, StrEnum, auto
from typing import Any

import attr

from krpg.components import component
from krpg.engine.executer import Ctx, Extension, executer_command
from krpg.utils import Nameable



class RewardType(StrEnum):
    UNLOCK = auto()
    RUN = auto()
    INTRODUCE = auto()
    QUEST = auto()


class ObjectiveType(StrEnum):
    PICKUP = auto()
    WEAR = auto()
    VISIT = auto()
    TALK = auto()
    FREEZE = auto()


args_map: dict[Enum, list[type]] = {
    ObjectiveType.PICKUP: [str, int],
    ObjectiveType.WEAR: [str],
    ObjectiveType.VISIT: [str],
    ObjectiveType.TALK: [str],
    ObjectiveType.FREEZE: [],
    RewardType.UNLOCK: [str],
    RewardType.RUN: [str],
    RewardType.INTRODUCE: [str],
    RewardType.QUEST: [str],
}


@attr.s(auto_attribs=True)
class Objective:
    description: str
    type: ObjectiveType
    args: list[Any] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class Reward:
    type: RewardType
    args: list[Any] = attr.ib(factory=list)

@component
class QuestCommandsExtension(Extension):
    @executer_command("quest")
    @staticmethod
    def quest(ctx: Ctx, *args: str) -> None:
        assert len(args) == 1, f"Expected 1 argument, got {len(args)}"
        quest_id = args[0]
        quest = ctx.game.bestiary.get_entity_by_id(quest_id, Quest)
        assert quest, f"Quest {quest_id} not found"
        ctx.game.quest_manager.start(quest)


@attr.s(auto_attribs=True)
class QuestManager:
    active: list[QuestState] = attr.ib(factory=list)
    completed: list[QuestState] = attr.ib(factory=list)

    def start(self, quest: Quest) -> None:
        self.active.append(QuestState(quest=quest))


@attr.s(auto_attribs=True)
class Quest(Nameable):
    stages: list[Stage] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class Stage:
    description: str
    objectives: list[Objective] = attr.ib(factory=list)
    rewards: list[Reward] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class QuestState:
    quest: Quest
    current: list[ObjectiveState] = attr.ib(factory=list)

    def __attrs_post_init__(self) -> None:
        self.current = [ObjectiveState(objective=stage.objectives[0]) for stage in self.quest.stages]


@attr.s(auto_attribs=True)
class ObjectiveState:
    objective: Objective
    progress: int = 0
    completed: bool = False

    def check(self) -> None:
        if self.objective.type == ObjectiveType.PICKUP:
            pass
        else:
            raise NotImplementedError(f"Objective type {self.objective.type} is not implemented")
