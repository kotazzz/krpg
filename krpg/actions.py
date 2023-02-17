from __future__ import annotations
from typing import Callable


class Action:
    def __init__(self, name: str, description: str, category: str, callback: Callable):
        self.name = name
        self.description = description
        self.category = category
        self.callback = callback


def action(name: str, description: str = "No description", category: str = ""):
    def decorator(callback: Callable):
        return Action(name, description, category, callback)

    return decorator


class ActionManager:
    def __init__(self):
        self.actions: dict[str, list[Action]] = {}

    def register(self, action: Action):
        if action.name in self.get_all():
            raise Exception(f"Action {action.name} already exists.")
        if action.category not in self.actions:
            self.actions[action.category] = {}
        self.actions[action.category][action.name] = action

    def expand(self, actionmanager: ActionManager):
        for category, actions in actionmanager.actions.items():
            for name, action in actions.items():
                self.register(action)

    def get_all(self) -> list[Action]:
        r = {}
        for category, actions in self.actions.items():
            for name, action in actions.items():
                r[name] = action
        return r
