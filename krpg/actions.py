from __future__ import annotations

from typing import Callable


class Action:
    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        callback: Callable,
        time: int = 0,
    ):
        """
        Represents an action in the game.

        Args:
            name (str): The name of the action.
            description (str): The description of the action.
            category (str): The category of the action.
            callback (Callable): The callback function to be executed when the action is performed.
            time (int, optional): The time required to perform the action. Defaults to 0.
        """
        self.name = name
        self.description = description
        self.category = category
        self.callback = callback
        self.time = time

    def __repr__(self):
        return f"<Action {self.name} from {self.category}>"


def action(
    name: str, description: str = "No description", category: str = "", time: int = 0
) -> Callable[..., Action]:
    """
    Decorator function for creating actions.

    Args:
        name (str): The name of the action.
        description (str, optional): The description of the action. Defaults to "No description".
        category (str, optional): The category of the action. Defaults to "".
        time (int, optional): The time required for the action. Defaults to 0.

    Returns:
        Callable: The decorated callback function.
    """

    def decorator(callback: Callable):
        return Action(name, description, category, callback, time)

    return decorator


class ActionManager:
    """
    ActionManager class represents a manager for actions in a game.

    Attributes:
        submanagers (list[object | ActionManager]): A list of submanagers.
        actions (list[Action]): A list of actions.

    Methods:
        __init__(): Initializes an instance of ActionManager.
        extract(item: object) -> list[Action]: Extracts actions from an item.
        get_actions() -> list[Action]: Retrieves all actions from submanagers and actions attribute.
        __repr__(): Returns a string representation of ActionManager.
    """

    def __init__(self, *submanagers: object | ActionManager):
        self.submanagers: list[object | ActionManager] = list(submanagers)
        self.actions: list[Action] = {}
        self.actions = self.extract(self)
        self.submanagers.clear()

    def extract(self, item: object) -> list[Action]:
        """
        Extracts actions from an item.

        Args:
            item (object): The item to extract actions from.

        Returns:
            list[Action]: A list of extracted actions.
        """
        if isinstance(item, ActionManager):
            return item.get_actions()
        if "extract" in dir(item):
            return item.extract()
        actions = []
        for name in dir(item):
            attr = getattr(item, name)
            if isinstance(attr, Action):
                actions.append(attr)
        return actions

    def get_actions(self) -> list[Action]:
        """
        Retrieves all actions from submanagers and actions attribute.

        Returns:
            list[Action]: A list of all actions.
        """
        actions: list[Action] = []
        for submanager in self.submanagers:
            actions.extend(self.extract(submanager))
        actions.extend(self.actions)
        names = {}
        for action in actions:
            if action.name not in names:
                names[action.name] = action
            else:
                raise Exception(f"Same names: {names[action.name]} and {action}")
        return actions

    def __repr__(self):
        """
        Returns a string representation of ActionManager.

        Returns:
            str: A string representation of ActionManager.
        """
        return f"<ActionManager act={len(self.actions)} sub={len(self.submanagers)}>"
