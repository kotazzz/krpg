from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.tree import Tree

from krpg.actions import action
from krpg.events import Events
from krpg.executer import executer_command

if TYPE_CHECKING:
    from krpg.game import Game


class Goal:
    def __init__(self, goal: list[str]):
        """
        Initializes a Goal object.

        Args:
            goal (list): A list containing the goal information.
                The list should have the following format:
                [type, *args, name, description]

        Attributes:
            completed (bool): Indicates whether the goal is completed or not.
            type (str): The type of the goal.
            args (list): Additional arguments for the goal.
            name (str): The name of the goal.
            description (str): The description of the goal.
            meta (dict): Additional metadata for the goal.
        """
        self.completed = False
        self.type = goal[0]
        self.args = goal[1:-2]
        self.name = goal[-2]
        self.description = goal[-1]
        self.meta: dict[Any, Any] = {}

    def save(self):
        """
        Saves the goal's completion status and metadata.

        Returns:
            Union[bool, list]: If the goal has metadata, returns a list
            containing the completion status and metadata. Otherwise,
            returns the completion status as a boolean.
        """
        if self.meta:
            return [self.completed, self.meta]
        return self.completed

    def load(self, data):
        """
        Loads the goal's completion status and metadata.

        Args:
            data (Union[bool, list]): The data to load. If the data is a list,
            it should contain the completion status and metadata. If the data
            is a boolean, it represents the completion status.
        """
        if isinstance(data, list):
            self.completed, self.meta = data
        else:
            self.completed = data

    def check(self, event, *_, **kwargs):
        """
        Checks if the goal is completed based on the given event and arguments.

        Args:
            event (str): The event to check against.
            **kwargs: Additional keyword arguments.

        Raises:
            KeyError: If the required keyword argument is missing.

        Note:
            The behavior of the check method depends on the type of the goal.
            - For "run" type goals, the completion status is based on whether
              the provided command matches the command in the arguments.
            - For "visit" type goals, the completion status is based on whether
              the destination ID matches the ID in the arguments.
            - For "meet" type goals, the completion status is based on whether
              the NPC ID matches the ID in the arguments.
            - For "state" type goals, the completion status is based on whether
              the NPC ID and state match the IDs and state in the arguments.
            - For "abc" type goals
        """
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

        elif self.type == "collect" and event == Events.PICKUP:
            required = int(self.args[1])
            self.completed = (
                self.args[0] == kwargs["item"].id and required == kwargs["total"]
            )

    def __repr__(self):
        """
        Returns a string representation of the Goal object.

        Returns:
            str: A string representation of the Goal object.
        """
        return f"<Goal name={self.name!r} completed={self.completed}>"


class Stage:
    def __init__(self, data: dict[str, Any]):
        self.name: str = data["name"]
        self.goals: list[list[str]] = data["goals"]
        self.rewards: list[str] = data["rewards"]

    def __repr__(self):
        return f"<Stage name={self.name!r} goals={len(self.goals)}>"


class Quest:
    def __init__(
        self,
        identifier: str,
        name: str,
        description: str,
        stages: dict[str | int, dict[str, Any]],
    ) -> None:
        """Initialize a new instance of Quest.

        Parameters
        ----------
        id : str
            id of the quest
        name : str
            name of the quest
        description : str
            description of the quest
        stages : dict[str  |  int, dict[str, Any]]
            stages of the quest:
            key: stage id
            value: dict with keys:
                name: name of the stage
                goals: list of goals
                rewards: list of rewards
        """
        self.id: str = identifier
        self.name: str = name
        self.description: str = description
        self.stages: dict[str | int, Stage] = {i: Stage(j) for i, j in stages.items()}

    def __repr__(self):
        return f"<Quest id={self.id!r} name={self.name!r} stages={len(self.stages)}>"


class QuestState:
    """Represents the state of a quest in the game.

    Attributes:
        game (Game): The game instance.
        quest (Quest): The quest associated with this state.
        done_stages (list[str | int]): The list of completed stages.
        done (bool): Indicates if the quest is done or not.
        stage (Stage): The current stage of the quest.
        stage_id (str | int): The ID of the current stage.
        goals (list[Goal]): The goals of the current stage.
        rewards (list): The rewards for completing the current stage.
    """

    def __init__(self, game: Game, quest: Quest):
        """Initialize a new instance of QuestState.

        Args:
            game (Game): The game instance.
            quest (Quest): The quest associated with this state.
        """
        self.game = game
        self.quest = quest
        self.done_stages: list[str | int] = []
        self.done = False
        self.update(next(iter(quest.stages)))

    def save(self):
        """Save the quest state.

        Returns:
            Union[bool, list]: The saved data.
        """
        if self.done:
            return True
        return [self.done_stages, self.stage_id, [g.save() for g in self.goals]]

    def load(self, data):
        """Load the quest state.

        Args:
            data (Union[bool, list]): The saved data.
        """
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
        """Update the quest state to the specified stage.

        Args:
            stage (str | int): The ID of the stage to update to.
        """
        self.stage = self.quest.stages[stage]
        self.stage_id = stage
        self.goals = [Goal(goal) for goal in self.stage.goals]
        self.rewards = self.stage.rewards

    def check(self, event, *args, **kwargs):
        """Check if the quest goals are completed based on the event.

        Args:
            event: The event triggering the check.
            *args: Additional arguments for the event.
            **kwargs: Additional keyword arguments for the event.
        """
        for goal in self.goals:
            if not goal.completed:
                goal.check(event, *args, **kwargs)
        if all(goal.completed for goal in self.goals):
            self.done_stages.append(self.stage_id)
            self.process_rewards()

    def process_rewards(self):
        """Process the rewards for completing the current stage."""
        rewards = self.rewards
        for reward in rewards:
            reward_type, *args = reward
            if reward_type == "stage":
                new_stage = int(args[0]) if args[0].isdigit() else args[0]
                self.update(new_stage)
            elif reward_type == "state":
                npc = self.game.npc_manager.get_npc(args[0])
                self.game.npc_manager.set_state(npc, args[1])
            elif reward_type == "end":
                self.done = True
                self.game.events.dispatch(Events.QUEST_END, state=self)

    def __repr__(self):
        """Return a string representation of the QuestState.

        Returns:
            str: The string representation of the QuestState.
        """
        count = len([goal for goal in self.goals if goal.completed])
        return f"<QuestState stage={self.stage} progress={count}/{len(self.goals)}>"


class QuestManager:
    """
    Class representing a quest manager in a game.

    Attributes:
        game (Game): The game instance.
        quests (list[Quest]): The list of all available quests.
        active_quests (list[QuestState]): The list of currently active quests.

    Methods:
        save(): Save the progress of active quests.
        load(data): Load the progress of active quests.
        get_quest(id): Get a quest by its ID.
        start_quest(id): Start a quest by its ID.
        on_event(event, *args, **kwargs): Handle game events.
    """

    def __init__(self, game: Game):
        self.game = game
        self.quests: list[Quest] = []
        self.active_quests: list[QuestState] = []
        self.game.executer.add_extension(self)
        self.game.add_actions(self)
        self.game.add_saver("quest", self.save, self.load)
        self.game.events.listen("*", self.on_event)

    def save(self):
        """
        Save the progress of active quests.

        Returns:
            dict: A dictionary containing the saved data for each active quest.
        """
        return {q.quest.id: q.save() for q in self.active_quests}

    def load(self, data):
        """
        Load the progress of active quests.

        Args:
            data (dict): A dictionary containing the saved data for each active quest.
        """
        self.active_quests = []
        for identifier, state in data.items():
            quest = self.get_quest(identifier)
            if quest:
                new_state = QuestState(self.game, quest)
                new_state.load(state)
                self.active_quests.append(new_state)
            else:
                raise ValueError(f"Quest {identifier} not found")

    def get_quest(self, identifier: str | Quest):
        """
        Get a quest by its ID.

        Args:
            id (str | Quest): The ID of the quest or the quest instance itself.

        Returns:
            Quest | None: The quest instance if found, None otherwise.
        """
        if isinstance(identifier, Quest):
            return identifier
        for quest in self.quests:
            if quest.id == identifier:
                return quest
        raise ValueError(f"Quest {identifier} not found")

    def start_quest(self, identifier: str):
        """
        Start a quest by its ID.

        Args:
            id (str): The ID of the quest.

        Raises:
            Exception: If the quest with the given ID is not found.
        """
        quest = self.get_quest(identifier)
        if quest:
            self.active_quests.append(QuestState(self.game, quest))
            self.game.events.dispatch(Events.QUEST_START, quest.id)
        else:
            raise ValueError(f"Quest {identifier} not found")

    def on_event(self, event, *args, **kwargs):
        """
        Handle game events.

        Args:
            event: The game event.
            *args: Additional arguments for the event.
            **kwargs: Additional keyword arguments for the event.
        """
        for active in self.active_quests:
            if not active.done:
                active.check(event, *args, **kwargs)

    def is_done(self, identifier: str) -> bool:
        """Check if a quest is done.

        Parameters
        ----------
        identifier : str
            The ID of the quest.

        Returns
        -------
        bool
            True if the quest is done, False otherwise.

        Raises
        ------
        ValueError
            If the quest with the given ID is not found.
        """
        quest = self.get_quest(identifier)
        if quest:
            return quest.id in [q.quest.id for q in self.active_quests if q.done]
        raise ValueError(f"Quest {identifier} not found")

    @executer_command("quest")
    @staticmethod
    def quest_command(game: Game, identifier: str):
        """Start a quest by its ID.

        Parameters
        ----------
        game : Game
            The game instance.
        identifier : str
            The ID of the quest.
        """
        game.quest_manager.start_quest(identifier)

    @action("quests", "Показать список квестов", "Информация")
    @staticmethod
    def show_quests(game: Game):
        """Show the list of active quests.

        Parameters
        ----------
        game : Game
            The game instance.
        """
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
