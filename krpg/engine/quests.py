from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Generator

import attr
from rich.tree import Tree

from krpg.actions import ActionCategory, ActionManager, action
from krpg.bestiary import BESTIARY
from krpg.commands import Command, command
from krpg.components import component
from krpg.engine.executer import Ctx, Extension, NamedScript, Predicate, executer_command, add_predicate, run_scenario
from krpg.engine.npc import TalkNpc, introduce
from krpg.engine.world import MoveEvent, unlock
from krpg.entity.inventory import EquipEvent, PickupEvent, UnequipEvent
from krpg.events import Event, listener
from krpg.events_middleware import GameEvent, HasGame
from krpg.saves import Savable
from krpg.utils import Nameable

if TYPE_CHECKING:
    from krpg.game import Game

type StateUpdate[T] = tuple[T, bool] | bool | None

type StatusType = Any


@attr.s(auto_attribs=True)
class StartQuest(GameEvent):
    quest: Quest


@attr.s(auto_attribs=True)
class RewardEvent(GameEvent):
    reward: Reward


@attr.s(auto_attribs=True)
class UnfreezeEvent(GameEvent):
    quest: Quest


@command
def start_quest(qm: QuestManager, quest: Quest) -> Generator[StartQuest, Any, None]:
    yield StartQuest(quest)
    qm.start(quest)


@command
def run_reward(game: Game, reward: Reward) -> Generator[RewardEvent, Any, None]:
    cmd = reward.run(game)
    yield RewardEvent(reward)
    game.commands.execute(cmd)


@command
def unfreeze_quest(quest: Quest) -> Generator[UnfreezeEvent, Any, None]:
    yield UnfreezeEvent(quest)


@component
class QuestCommandsExtension(Extension):
    @executer_command("quest")
    @staticmethod
    def quest(ctx: Ctx, *args: str) -> None:
        assert len(args) == 1, f"Expected 1 argument, got {len(args)}"
        quest_id = args[0]
        quest = BESTIARY.get_entity_by_id(quest_id, Quest)
        assert quest, f"Quest {quest_id} not found"
        g = ctx.game
        g.commands.execute(start_quest(g.quest_manager, quest))

    @executer_command("complete")
    @staticmethod
    def complete(ctx: Ctx, *args: str) -> None:
        assert len(args) == 1, f"Expected 1 argument, got {len(args)}"
        quest_id = args[0]
        quest = BESTIARY.get_entity_by_id(quest_id, Quest)
        assert quest, f"Quest {quest_id} not found"
        g = ctx.game
        g.commands.execute(unfreeze_quest(quest))


@add_predicate
class QuestPredicate(Predicate):
    name = "quest"

    @staticmethod
    def parse(*args: str) -> tuple[tuple[Any, ...], int]:
        match args:
            case [quest_id, "stage", stage_id]:
                return (quest_id, "stage", int(stage_id)), 3
            case [quest_id, "started"]:
                return (quest_id, "started"), 2
            case _:
                raise ValueError(f"Unknown arguments: {args}")

    @staticmethod
    def eval(game: Game, quest_id: str, cond: str, *args: Any) -> bool:
        quest = BESTIARY.get_entity_by_id(quest_id, Quest)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")
        match cond, args:
            case "stage", [stage_id]:
                state = game.quest_manager.get_state(quest)
                if not state:
                    return False
                return state.stage_index == stage_id and not state.is_completed
            case "started", []:
                state = game.quest_manager.get_state(quest)
                if not state:
                    return False
                return not state.is_completed
            case _:
                raise ValueError(f"Unknown condition: {cond}")
        return False


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
                    tree_stage.add(f"[blue]{objective.objective.description} [yellow]{objective.progress}")

        game.console.print(tree)


@component
@listener(Event)
def test(e: Event):
    if not isinstance(e, HasGame):  # TODO: Rewrite to GameEvent listen
        return
    e.game.quest_manager.check_quests(e)


class Reward:
    @abstractmethod
    def run(self, game: Game) -> Command[...]:
        raise NotImplementedError


@attr.s(auto_attribs=True)
class Objective(ABC, Savable):
    description: str  # FIXME: is not loadable

    def serialize(self) -> Any:
        return get_objective_name(self)

    @classmethod
    def deserialize(cls, data: Any) -> Objective:
        rcls = objectives_names.get(data["type"])
        if not rcls:
            raise ValueError(f"Unknown objective type {data['type']}")
        return rcls.deserialize(data)

    @abstractmethod
    def check(self, event: Event, state: StatusType, completed: bool) -> StateUpdate[StatusType]:
        raise NotImplementedError

    def create(self, state: StatusType[QuestState]) -> ObjectiveStatus:
        return ObjectiveStatus(self, state=state)

    def status(self, status: StatusType) -> str | None:
        return None


@attr.s(auto_attribs=True)
class Stage:
    description: str
    objectives: list[Objective] = attr.ib(factory=lambda: [])
    rewards: list[Reward] = attr.ib(factory=lambda: [])


@attr.s(auto_attribs=True)
class ObjectiveStatus(Savable):
    objective: Objective
    state: StatusType | None = None
    completed: bool = False

    def serialize(self) -> dict[str, Any]:
        return {"objective": self.objective.serialize(), "state": self.state, "completed": self.completed}

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> ObjectiveStatus:
        self = cls(objective=Objective.deserialize(data["objective"]), state=data["state"], completed=data["completed"])

        return self

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

    @property
    def progress(self) -> str:
        return self.objective.status(self.state) or ""


@attr.s(auto_attribs=True)
class Quest(Nameable, Savable):
    stages: list[Stage] = attr.ib(factory=lambda: [], repr=False)

    def serialize(self) -> str:
        return self.id

    @classmethod
    def deserialize(cls, data: str) -> Quest:
        q = BESTIARY.get_entity_by_id(data, Quest)
        if not q:
            raise ValueError(f"Quest {data} not found")
        return q


@attr.s(auto_attribs=True)
class QuestState(Savable):
    quest: Quest
    stage_index: int = -1
    objectives: list[ObjectiveStatus] = attr.ib(factory=lambda: [])
    paused: bool = False

    def serialize(self) -> dict[str, Any]:
        return {"quest": self.quest.serialize(), "stage_index": self.stage_index, "objectives": [o.serialize() for o in self.objectives], "paused": self.paused}

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> QuestState:
        self = cls(
            quest=Quest.deserialize(data["quest"]),
            stage_index=data["stage_index"],
            objectives=[ObjectiveStatus.deserialize(o) for o in data["objectives"]],
            paused=data["paused"],
        )
        return self

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
        if self.stage_index + 1 < len(self.quest.stages):
            self.stage_index += 1
            self.objectives = [o.create(self) for o in self.stage_data.objectives]

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
class QuestManager(Savable):
    quests: list[QuestState] = attr.ib(factory=lambda: [])

    def serialize(self) -> dict[str, Any]:
        return {"quests": [q.serialize() for q in self.quests]}

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Savable:
        self = cls()
        self.quests = [QuestState.deserialize(q) for q in data["quests"]]
        return self

    @property
    def active(self) -> list[QuestState]:
        return [q for q in self.quests if not q.is_completed]

    @property
    def completed(self) -> list[QuestState]:
        return [q for q in self.quests if q.is_completed]

    def start(self, quest: Quest) -> None:
        self.quests.append(QuestState(quest=quest))

    def check_quests(self, event: Event):
        for q in self.active:
            q.check_stage(event)

    def get_state(self, quest: Quest) -> QuestState | None:
        for q in self.quests:
            if q.quest == quest:
                return q
        return None


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


def get_reward_name(reward: Reward) -> str | None:
    for name, cls in rewards_names.items():
        if cls == reward.__class__:
            return name
    return None


def get_objective_name(objective: Objective) -> str | None:
    for name, cls in objectives_names.items():
        if cls == objective.__class__:
            return name
    return None


@objective("PICKUP")
@attr.s(auto_attribs=True)
class PickupObjective(Objective):
    item_id: str
    count: int = attr.ib(converter=int)

    def create(self, state: QuestState) -> ObjectiveStatus:
        return ObjectiveStatus(self, 0)

    def check(self, event: Event, state: int, completed: bool) -> StateUpdate[int]:
        if not isinstance(event, PickupEvent):
            return None
        if not event.item.id == self.item_id:
            return None
        new = state + event.count
        return new, new >= self.count

    def status(self, status: int) -> str:
        return f"{status}/{self.count}"


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
            return event.new_loc.location.id == self.loc_id


@objective("TALK")
@attr.s(auto_attribs=True)
class TalkObjective(Objective):
    npc_id: str

    def check(self, event: Event, state: int, completed: bool) -> StateUpdate[None]:
        if isinstance(event, TalkNpc):
            return event.npc.npc.id == self.npc_id


@objective("FREEZE")
@attr.s(auto_attribs=True)
class FreezeObjective(Objective):
    def check(self, event: Event, state: QuestState, completed: bool) -> StateUpdate[None]:
        if isinstance(event, UnfreezeEvent):
            return event.quest.id == state.quest.id


@reward("UNLOCK")
@attr.s(auto_attribs=True)
class UnlockReward(Reward):
    loc_id: str

    def run(self, game: Game) -> Command[...]:
        loc = game.world.get_location_by_id(self.loc_id)
        assert loc, f"{self.loc_id} doesnt exist"
        return unlock(loc)


@reward("RUN")
@attr.s(auto_attribs=True)
class ScriptReward(Reward):
    scenario_id: str

    def run(self, game: Game) -> Command[...]:
        sc = BESTIARY.get_entity_by_id(self.scenario_id, NamedScript)
        assert sc, f"{self.scenario_id} doesnt exist"
        return run_scenario(game.executer, sc)


@reward("INTRODUCE")
@attr.s(auto_attribs=True)
class IntroduceReward(Reward):
    npc_id: str

    def run(self, game: Game) -> Command[...]:
        npc = game.npc_manager.npcs[self.npc_id]
        assert npc, f"{self.npc_id} doesnt exist"
        return introduce(npc)


@reward("QUEST")
@attr.s(auto_attribs=True)
class QuestReward(Reward):
    quest_id: str

    def run(self, game: Game) -> Command[...]:
        q = BESTIARY.get_entity_by_id(self.quest_id, Quest)
        assert q, f"{self.quest_id} doesnt exist"
        return start_quest(game.quest_manager, q)
