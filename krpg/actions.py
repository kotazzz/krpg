from __future__ import annotations

from collections import defaultdict
from typing import Callable


class Action:
    def __init__(self, name: str, description: str, category: str, callback: Callable):
        self.name = name
        self.description = description
        self.category = category
        self.callback = callback

    def __repr__(self):
        return f"<Action {self.name} from {self.category}>"


def action(name: str, description: str = "No description", category: str = ""):
    def decorator(callback: Callable):
        return Action(name, description, category, callback)

    return decorator


class ActionManager:
    def __init__(self):
        self.submanagers: list[object | ActionManager] = []
        self.actions: list[Action] = {}
        self.actions = self.extract(self)

    def extract(self, item: object) -> list[Action]:
        if isinstance(item, ActionManager):
            return item.get_actions()
        actions = []
        for name in dir(item):
            attr = getattr(item, name)
            if isinstance(attr, Action):
                actions.append(attr)
        return actions

    def get_actions(self) -> list[Action]:
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
        return f"<ActionManager act={len(self.actions)} sub={len(self.submanagers)}>"
