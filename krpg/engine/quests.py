from __future__ import annotations
from enum import Enum, StrEnum, auto
from typing import Any
import attr

from krpg.utils import Nameable


class RewardType(StrEnum):
    UNLOCK = auto()
    RUN = auto()
    INTRODUCE = auto()


class ObjectiveType(StrEnum):
    PICKUP = auto()
    WEAR = auto()
    VISIT = auto()
    TALK = auto()
    FREEZE = auto()


args: dict[Enum, list[type]] = {
    ObjectiveType.PICKUP: [str],
    ObjectiveType.WEAR: [str],
    ObjectiveType.VISIT: [str],
    ObjectiveType.TALK: [str],
    ObjectiveType.FREEZE: [],
    RewardType.UNLOCK: [str],
    RewardType.RUN: [str],
    RewardType.INTRODUCE: [str],
}


@attr.s(auto_attribs=True)
class QuestManager:
    active: list[QuestState] = []
    completed: list[QuestState] = []


@attr.s(auto_attribs=True)
class Quest(Nameable):
    stages: list[Stage] = []


@attr.s(auto_attribs=True)
class Stage:
    description: str
    objectives: list[Objective] = []
    rewards: list[Reward] = []


@attr.s(auto_attribs=True)
class Objective:
    description: str
    type: ObjectiveType
    args: list[Any] = []


@attr.s(auto_attribs=True)
class Reward:
    type: RewardType
    args: list[Any] = []


@attr.s(auto_attribs=True)
class QuestState:
    quest: Quest
    stage: StageState


@attr.s(auto_attribs=True)
class StageState:
    stage: Stage
    objectives: list[ObjectiveState] = []


@attr.s(auto_attribs=True)
class ObjectiveState:
    objective: Objective
    progress: int = 0
    completed: bool = False

    def check(self) -> None:
        if self.objective.type == ObjectiveType.PICKUP:
            pass
        else:
            raise NotImplementedError(
                f"Objective type {self.objective.type} is not implemented"
            )
