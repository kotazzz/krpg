from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Generator

import attr
from rich.tree import Tree

from krpg.actions import ActionCategory, ActionManager, action
from krpg.commands import Command, command
from krpg.components import component
from krpg.engine.executer import Ctx, Extension, Scenario, executer_command, run_scenario
from krpg.engine.npc import Npc, TalkNpc, introduce
from krpg.engine.world import Location, MoveEvent, unlock
from krpg.entity.inventory import EquipEvent, PickupEvent, UnequipEvent
from krpg.events import Event, listener
from krpg.events_middleware import GameEvent, HasGame
from krpg.utils import Nameable

if TYPE_CHECKING:
    from krpg.game import Game

type StateUpdate[T] = tuple[T, bool] | bool | None

@attr.s(auto_attribs=True)
class StartQuest(GameEvent):
    quest: Quest

@command
def start_quest(qm: QuestManager, quest: Quest) -> Generator[StartQuest, Any, None]:
    yield StartQuest(quest)
    qm.start(quest)

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
            for objective in quest.current:
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
    


@attr.s(auto_attribs=True)
class QuestManager:
    active: list[QuestState] = attr.ib(factory=list)
    completed: list[QuestState] = attr.ib(factory=list)

    def start(self, quest: Quest) -> None:
        self.active.append(QuestState(quest=quest))


@attr.s(auto_attribs=True)
class Quest(Nameable):
    stages: list[Stage] = attr.ib(factory=list, repr=lambda x: str(len(x)))


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
        return self.quest.stages[:self.stage_index]

    @property
    def stage_data(self) -> Stage:
        return self.quest.stages[self.stage_index]

    def next_stage(self) -> None:
        if self.is_completed:
            return
        self.stage_index += 1
        self.current = [o.create() for o in self.stage_data.objectives]

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
    def check(self, event: GameEvent, state: StatusType, completed: bool) -> StateUpdate[StatusType]:
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

    def check(self, event: GameEvent) -> None:
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
    count: int
    def create(self) -> ObjectiveState:
        return ObjectiveState(self, 0)
    
    def check(self, event: GameEvent, state: int, completed: bool) -> StateUpdate[int]:
        if not isinstance(event, PickupEvent):
            return None
        if not event.item.id == self.item_id:
            return None
        new = state + event.count
        return new, new > self.count
    
    def status(self, state: int) -> str | None:
        return f"{state}/{self.count}"

@objective("WEAR")
@attr.s(auto_attribs=True)
class WearObjective(Objective):
    item_id: str
    def check(self, event: GameEvent, state: Any, completed: bool) -> StateUpdate[None]:
        if isinstance(event, EquipEvent):
            return event.item.id == self.item_id
        if isinstance(event, UnequipEvent):
            if not completed:
                return 
            return not event.item.id == self.item_id
        
@objective("VISIT")
@attr.s(auto_attribs=True)
class VisitObjective(Objective):
    loc_id: str
    def check(self, event: GameEvent, state: int, completed: bool) -> StateUpdate[None]:
        if isinstance(event, MoveEvent):
            return event.new_loc.id == self.loc_id

@objective("TALK")
@attr.s(auto_attribs=True)
class TalkObjective(Objective):
    npc_id: str
    def check(self, event: GameEvent, state: int, completed: bool) -> StateUpdate[None]:
        if isinstance(event, TalkNpc):
            return event.npc.id == self.npc_id
    
@objective("FREEZE")
@attr.s(auto_attribs=True)
class FreezeObjective(Objective):
    def check(self, event: GameEvent, state: int, completed: bool) -> StateUpdate[None]:
        return None


@reward("UNLOCK")
@attr.s(auto_attribs=True)
class UnlockReward(Reward):
    loc_id: str
    def run(self, game: Game) -> Command[...]:
        loc = game.bestiary.get_entity_by_id(self.loc_id, Location)
        assert loc, f"{self.loc_id} doesnt exist"
        return unlock(loc)

@reward("RUN")
@attr.s(auto_attribs=True)    
class RunReward(Reward):
    scenario_id: str
    def run(self, game: Game) -> Command[...]:
        sc = game.bestiary.get_entity_by_id(self.scenario_id, Scenario)
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
