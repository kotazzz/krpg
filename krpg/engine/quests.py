from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Generator

import attr
from rich.tree import Tree

from krpg.actions import ActionCategory, ActionManager, action
from krpg.commands import Command, command
from krpg.components import component
from krpg.engine.executer import Ctx, Extension, NamedScript, executer_command, run_scenario
from krpg.engine.npc import Npc, TalkNpc, introduce
from krpg.engine.world import MoveEvent, unlock
from krpg.entity.inventory import EquipEvent, PickupEvent, UnequipEvent
from krpg.events import Event, listener
from krpg.events_middleware import GameEvent, HasGame
from krpg.utils import Nameable, get_by_id

if TYPE_CHECKING:
    from krpg.game import Game

type StateUpdate[T] = tuple[T, bool] | bool | None


@attr.s(auto_attribs=True)
class StartQuest(GameEvent):
    quest: Quest


@attr.s(auto_attribs=True)
class RewardEvent(GameEvent):
    reward: Reward


@command
def start_quest(qm: QuestManager, quest: Quest) -> Generator[StartQuest, Any, None]:
    yield StartQuest(quest)
    qm.start(quest)


@command
def run_reward(game: Game, reward: Reward):
    cmd = reward.run(game)
    yield RewardEvent(reward)
    game.commands.execute(cmd)


@component
class QuestCommandsExtension(Extension):
    @executer_command("quest")
    @staticmethod
    def quest(ctx: Ctx, *args: str) -> None:
        assert len(args) == 1, f"Expected 1 argument, got {len(args)}"
        quest_id = args[0]
        quest = ctx.game.bestiary.get_entity_by_id(quest_id, Quest)
        assert quest, f"Quest {quest_id} not found"
        g = ctx.game
        g.commands.execute(start_quest(g.quest_manager, quest))


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
            for objective in quest.objectives:
                if objective.completed:
                    tree_stage.add(f"[cyan]{objective.objective.description}")
                else:
                    tree_stage.add(f"[blue]{objective.objective.description}")

        game.console.print(tree)


@component
@listener(Event)
def test(e: Event):
    if not isinstance(e, HasGame):
        return
    e.game.quest_manager.check_quests(e)


@attr.s(auto_attribs=True)
class QuestManager:
    active: list[QuestState] = attr.ib(factory=list)
    completed: list[QuestState] = attr.ib(factory=list)

    def start(self, quest: Quest) -> None:
        self.active.append(QuestState(quest=quest))

    def complete(self, quest: QuestState):
        self.active.remove(quest)
        self.completed.append(quest)

    def check_quests(self, event: Event):
        for q in self.active:
            q.check_stage(event)
            if q.is_completed:
                self.complete(q)


@attr.s(auto_attribs=True)
class Quest(Nameable):
    stages: list[Stage] = attr.ib(factory=list, repr=lambda x: str(len(x)))


@attr.s(auto_attribs=True)
class QuestState:
    quest: Quest
    stage_index: int = -1
    objectives: list[ObjectiveState] = attr.ib(factory=list)
    paused: bool = False

    @property
    def is_completed(self) -> bool:
        return all(i.completed for i in self.objectives) and self.stage_index == len(self.quest.stages) - 1

    @property
    def completed_stages(self) -> list[Stage]:
        return self.quest.stages[: self.stage_index]

    @property
    def stage_data(self) -> Stage:
        return self.quest.stages[self.stage_index]

    def next_stage(self) -> None:
        if self.stage_index < len(self.quest.stages):
            self.stage_index += 1
            self.objectives = [o.create() for o in self.stage_data.objectives]

    def check_stage(self, event: Event) -> None:
        if self.paused:
            return
        if not isinstance(event, HasGame):
            raise ValueError("Event must have game")
        for o in self.objectives:
            o.check(event)
        if all(i.completed for i in self.objectives):
            self.paused = True
            for r in self.stage_data.rewards:
                event.game.commands.execute(run_reward(event.game, r))
            self.next_stage()
            self.paused = False

    def __attrs_post_init__(self) -> None:
        self.next_stage()


@attr.s(auto_attribs=True)
class Stage:
    description: str
    objectives: list[Objective] = attr.ib(factory=list)
    rewards: list[Reward] = attr.ib(factory=list)


class Reward:
    @abstractmethod
    def run(self, game: Game) -> Command[...]:
        raise NotImplementedError


type StatusType = Any


@attr.s(auto_attribs=True)
class Objective(ABC):
    description: str

    @abstractmethod
    def check(self, event: Event, state: StatusType, completed: bool) -> StateUpdate[StatusType]:
        raise NotImplementedError

    def create(self) -> ObjectiveState:
        return ObjectiveState(self)

    def status(self, state: StatusType) -> str | None:
        return None


@attr.s(auto_attribs=True)
class ObjectiveState:
    objective: Objective
    state: StatusType | None = None
    completed: bool = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.completed = False

    def check(self, event: Event) -> None:
        res = self.objective.check(event, self.state, self.completed)
        if res is None:
            return
        if isinstance(res, tuple):
            state, completed = res
            self.state = state
            self.completed = completed
        else:
            self.completed = res


# TODO: Create Register as commands
objectives_names: dict[str, type[Objective]] = {}
rewards_names: dict[str, type[Reward]] = {}


def objective[T: type[Objective]](name: str) -> Callable[[T], T]:
    def decorator(obj: T) -> T:
        objectives_names[name] = obj
        return obj

    return decorator


def reward[T: type[Reward]](name: str) -> Callable[[T], T]:
    def decorator(obj: T) -> T:
        rewards_names[name] = obj
        return obj

    return decorator


@objective("PICKUP")
@attr.s(auto_attribs=True)
class PickupObjective(Objective):
    item_id: str
    count: int = attr.ib(converter=int)

    def create(self) -> ObjectiveState:
        return ObjectiveState(self, 0)

    def check(self, event: Event, state: int, completed: bool) -> StateUpdate[int]:
        if not isinstance(event, PickupEvent):
            return None
        if not event.item.id == self.item_id:
            return None
        new = state + event.count
        return new, new >= self.count

    def status(self, state: int) -> str | None:
        return f"{state}/{self.count}"


@objective("WEAR")
@attr.s(auto_attribs=True)
class WearObjective(Objective):
    item_id: str

    def check(self, event: Event, state: Any, completed: bool) -> StateUpdate[None]:
        if isinstance(event, EquipEvent) and not completed:
            return event.item.id == self.item_id
        if isinstance(event, UnequipEvent) and completed:
            return not event.item.id == self.item_id


@objective("VISIT")
@attr.s(auto_attribs=True)
class VisitObjective(Objective):
    loc_id: str

    def check(self, event: Event, state: int, completed: bool) -> StateUpdate[None]:
        if isinstance(event, MoveEvent):
            return event.new_loc.id == self.loc_id


@objective("TALK")
@attr.s(auto_attribs=True)
class TalkObjective(Objective):
    npc_id: str

    def check(self, event: Event, state: int, completed: bool) -> StateUpdate[None]:
        if isinstance(event, TalkNpc):
            print(event.npc.id == self.npc_id)
            print(event, self.npc_id)
            return event.npc.id == self.npc_id


@objective("FREEZE")
@attr.s(auto_attribs=True)
class FreezeObjective(Objective):
    def check(self, event: Event, state: int, completed: bool) -> StateUpdate[None]:
        return None


@reward("UNLOCK")
@attr.s(auto_attribs=True)
class UnlockReward(Reward):
    loc_id: str

    def run(self, game: Game) -> Command[...]:
        loc = get_by_id(game.world.locations, self.loc_id)
        assert loc, f"{self.loc_id} doesnt exist"
        return unlock(loc)


@reward("RUN")
@attr.s(auto_attribs=True)
class ScriptReward(Reward):
    scenario_id: str

    def run(self, game: Game) -> Command[...]:
        sc = game.bestiary.get_entity_by_id(self.scenario_id, NamedScript)
        assert sc, f"{self.scenario_id} doesnt exist"
        return run_scenario(sc)


@reward("INTRODUCE")
@attr.s(auto_attribs=True)
class IntroduceReward(Reward):
    npc_id: str

    def run(self, game: Game) -> Command[...]:
        npc = game.bestiary.get_entity_by_id(self.npc_id, Npc)
        assert npc, f"{self.npc_id} doesnt exist"
        return introduce(npc)


@reward("QUEST")
@attr.s(auto_attribs=True)
class QuestReward(Reward):
    quest_id: str

    def run(self, game: Game) -> Command[...]:
        q = game.bestiary.get_entity_by_id(self.quest_id, Quest)
        assert q, f"{self.quest_id} doesnt exist"
        return start_quest(game.quest_manager, q)
