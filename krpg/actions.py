"""
Actions module contains classes and functions for actions in the game.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass()
class Action:
    """
    Main class for actions in the game
    """

    name: str
    description: str
    category: str
    callback: Callable

    def __repr__(self):
        return f"<Action {self.name} from {self.category}>"


def action(
    name: str, description: str = "No description", category: str = ""
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
        return Action(name, description, category, callback)

    return decorator


class HasExtract:
    """Interface for classes that can extract actions."""

    def extract(self) -> list[Action]:
        """Extracts actions from the class.

        Returns
        -------
        list[Action]
            A list of extracted actions.
        """
        raise NotImplementedError


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

    def __init__(self, *submanagers: ActionManager | HasExtract | object):
        self.submanagers: list[ActionManager | HasExtract | object] = list(submanagers)
        self.actions: list[Action] = []
        self.actions = self.extract(self)
        self.submanagers.clear()

    def extract(self, item: ActionManager | HasExtract | object) -> list[Action]:
        """
        Extracts actions from an item.

        Args:
            item (object): The item to extract actions from.

        Returns:
            list[Action]: A list of extracted actions.
        """
        if isinstance(item, ActionManager):
            return item.get_actions()

        if hasattr(item, "extract"):
            if not isinstance(item, HasExtract):
                raise ValueError(f"Item {item} does not have extract method")
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
        names: dict[str, Action] = {}
        for act in actions:
            if act.name in names:
                raise ValueError(f"Same names: {names[act.name]} and {act}")
            names[act.name] = act
        return actions

    def __repr__(self):
        """
        Returns a string representation of ActionManager.

        Returns:
            str: A string representation of ActionManager.
        """
        return f"<ActionManager act={len(self.actions)} sub={len(self.submanagers)}>"
