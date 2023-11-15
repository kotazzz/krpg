from __future__ import annotations

from krpg.actions import action
from typing import TYPE_CHECKING
from rich.tree import Tree

from krpg.executer import executer_command
from krpg.events import Events
from krpg.scenario import Command

if TYPE_CHECKING:
    from krpg.game import Game


class Goal:
    def __init__(self, goal: list):
        self.completed = False
        # [type, *args, name, description]
        self.type = goal[0]
        self.args = goal[1:-2]
        self.name = goal[-2]
        self.description = goal[-1]
        self.meta = {}

    def save(self):
        if self.meta:
            return [self.completed, self.meta]
        return self.completed

    def load(self, data):
        if isinstance(data, list):
            self.completed, self.meta = data
        else:
            self.completed = data

    def check(self, event, *args, **kwargs):
        if self.type == "run" and event == Events.COMMAND:
            self.completed = self.args[0] == kwargs["command"]

        elif self.type == "visit" and event == Events.MOVE:
            self.completed = self.args[0] == kwargs["after"].id

        elif self.type == "meet" and event == Events.NPC_MEET:
            self.completed = self.args[0] == kwargs["npc_id"]

        elif self.type == "state" and event == Events.NPC_STATE:
            self.completed = (
                self.args[0] == kwargs["npc_id"] and self.args[1] == kwargs["state"]
            )

    def __repr__(self):
        return f"<Goal name={self.name!r} completed={self.completed}>"


class Stage:
    def __init__(self, data):
        self.name: str = data["name"]
        self.goals: list[str] = data["goals"]
        self.rewards: list[str] = data["rewards"]


class Quest:
    def __init__(self, id, name, description, stages):
        self.id = id
        self.name = name
        self.description = description
        self.stages: dict[str | int, Stage] = {i: Stage(j) for i, j in stages.items()}


class QuestState:
    def __init__(self, game: Game, quest: Quest):
        self.game = game
        self.quest = quest
        self.done_stages: list[str | int] = []
        self.done = False
        # first key in stages is first stage
        self.update(next(iter(quest.stages)))

    def save(self):
        if self.done:
            return True
        return [self.done_stages, self.stage_id, [g.save() for g in self.goals]]

    def load(self, data):
        if data is True:
            self.done = True
            self.done_stages = list(self.quest.stages.keys())
            print(list(self.quest.stages.keys()))
        else:
            self.done_stages = data[0]
            self.update(data[1])
            for i, goal in enumerate(self.goals):
                goal.load(data[2][i])

    def update(self, stage):
        self.stage = self.quest.stages[stage]
        self.stage_id = stage
        self.goals = [Goal(goal) for goal in self.stage.goals]
        self.rewards = self.stage.rewards

    def check(self, event, *args, **kwargs):
        for goal in self.goals:
            if not goal.completed:
                goal.check(event, *args, **kwargs)
        if all(goal.completed for goal in self.goals):
            self.done_stages.append(self.stage_id)
            self.process_rewards()

    def process_rewards(self):
        rewards = self.rewards
        for reward in rewards:
            type, *args = reward
            if type == "stage":
                new_stage = int(args[0]) if args[0].isdigit() else args[0]
                self.update(new_stage)
            elif type == "state":
                # reward state jack delivery_end
                npc = self.game.npc_manager.get_npc(args[0])
                self.game.npc_manager.set_state(npc, args[1])
            elif type == "end":
                self.done = True

    def __repr__(self):
        # count completed goals
        count = len([goal for goal in self.goals if goal.completed])
        return f"<QuestState stage={self.stage} progress={count}/{len(self.goals)}>"


class QuestManager:
    def __init__(self, game: Game):
        self.game = game
        self.quests: list[Quest] = []
        self.active_quests: list[QuestState] = []
        self.game.executer.add_extension(self)
        self.game.add_actions(self)
        self.game.add_saver("quest", self.save, self.load)
        self.game.events.listen("*", self.on_event)

    def save(self):
        return {q.quest.id: q.save() for q in self.active_quests}

    def load(self, data):
        self.active_quests = []
        for id, state in data.items():
            quest = self.get_quest(id)
            if quest:
                new_state = QuestState(self.game, quest)
                new_state.load(state)
                self.active_quests.append(new_state)
            else:
                raise Exception(f"Quest {id} not found")

    def get_quest(self, id: str | Quest):
        if isinstance(id, Quest):
            return id
        else:
            for quest in self.quests:
                if quest.id == id:
                    return quest

    def start_quest(self, id: str):
        quest = self.get_quest(id)
        if quest:
            self.active_quests.append(QuestState(self.game, quest))
            self.game.events.dispatch(Events.QUEST_START, quest.id)
        else:
            raise Exception(f"Quest {id} not found")

    def on_event(self, event, *args, **kwargs):
        for active in self.active_quests:
            if not active.done:
                active.check(event, *args, **kwargs)

    @executer_command("quest")
    def quest_command(game: Game, id: str):
        game.quest_manager.start_quest(id)

    @action("quests", "Показать список квестов", "Информация")
    def show_quests(game: Game):
        tree = Tree("Квесты")
        for active in game.quest_manager.active_quests:
            # QUEST_NAME 1/3 QUEST_DESCRIPTION
            c = "green" if active.done else "red"
            quest_tree = tree.add(
                f"[{c} b]{active.quest.name}[white b] {len(active.done_stages)}/{len(active.quest.stages)}\n{active.quest.description}"
            )
            for sid in active.done_stages:
                # "[x] STAGE_NAME"
                stage = active.quest.stages[sid]
                quest_tree.add(f"[white][[green]x[white]] [green]{stage.name}")
            # if completed, skip stage progress tree
            if active.done:
                continue
            # "[ ] STAGE_NAME"
            stage_tree = quest_tree.add(f"[white][ ] [green]{active.stage.name}")
            for goal in active.goals:
                # "[ ] GOAL_NAME"
                #       GOAL_DESCRIPTION
                mark = "v" if goal.completed else " "
                stage_tree.add(
                    f"[white][[green]{mark}[white]] [blue]{goal.name}\n"
                    f"[yellow]{goal.description}"
                )
        game.console.print(tree)

    def __repr__(self):
        return f"<QuestManager q={len(self.quests)}>"
