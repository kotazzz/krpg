from __future__ import annotations

from enum import Enum, StrEnum, auto
from typing import TYPE_CHECKING, Any

import attr
from rich.tree import Tree

from krpg.actions import ActionCategory, ActionManager, action
from krpg.components import component
from krpg.engine.executer import Ctx, Extension, executer_command
from krpg.utils import Nameable

if TYPE_CHECKING:
    from krpg.game import Game


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


@component
class QuestActions(ActionManager):
    @action("quests", "Показывает квесты", ActionCategory.INFO)
    @staticmethod
    def quests(game: Game) -> None:
        def _format_state(state: QuestState) -> str:
            color = "green" if state.is_completed else "red"
            return f"[{color}]{state.quest.name}[/] - [white]{state.quest.description}"

        tree = Tree("[magenta]Квесты")

        branch = tree.add("[green b]Выполнено")
        for quest in game.quest_manager.completed:
            branch.add(_format_state(quest))
        branch = tree.add("[yellow b]В процессе")
        for quest in game.quest_manager.active:
            tree_quest = branch.add(_format_state(quest))
            for c in quest.completed_stages:
                tree_quest.add(f"[green]{c.description}")

            tree_stage = tree_quest.add(f"[yellow]{quest.stage_data.description}")
            for objective in quest.current:
                if objective.completed:
                    tree_stage.add(f"[cyan]{objective.objective.description}")
                else:
                    tree_stage.add(f"[blue]{objective.objective.description}")

        game.console.print(tree)


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
    stage_index: int = -1
    current: list[ObjectiveState] = attr.ib(factory=list)

    @property
    def is_completed(self) -> bool:
        return all(i.completed for i in self.current) and self.stage_index == len(self.quest.stages) - 1

    @property
    def completed_stages(self) -> list[Stage]:
        return self.quest.stages[: self.stage_index]

    @property
    def stage_data(self) -> Stage:
        return self.quest.stages[self.stage_index]

    def next_stage(self) -> None:
        if self.is_completed:
            return
        self.stage_index += 1
        self.current = [ObjectiveState(objective=o) for o in self.stage_data.objectives]

    def __attrs_post_init__(self) -> None:
        self.next_stage()


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
