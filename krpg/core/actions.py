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
        self.actions: dict[str, dict[str, Action]] = {}
        self.dynamic: list[callable[dict[str, Action]]] = []
        self.submanagers: list[ActionManager] = []

        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, Action):
                self.register(attr)

    @classmethod
    def from_list(cls, actions: list[Action]):
        obj = cls()
        for act in actions:
            obj.register(act)
        return obj

    def register(self, action: Action):
        if action.name in self.get_all_actions():
            raise Exception(f"Action {action.name} already exists.")
        if action.category not in self.actions:
            self.actions[action.category] = {}
        self.actions[action.category][action.name] = action

    def expand_actions(self, actionmanager: ActionManager):
        # for category, actions in actionmanager.actions.items():
        #     for name, action in actions.items():
        #         self.register(action)
        self.submanagers.append(actionmanager)

    def get_all_categories(self) -> dict[str, dict[str, Action]]:
        d = defaultdict(dict)
        for name, action in self.get_all_actions().items():
            d[action.category][action.name] = action
        return d

    def get_all_actions(self) -> dict[str, Action]:
        r = {}

        actions = self.actions
        for getter in self.dynamic:
            actions |= getter()
        # print(self.dynamic)

        for category, actions in actions.items():
            for name, action in actions.items():
                r[name] = action

        for actmanager in self.submanagers:
            r |= actmanager.get_all_actions()

        return r

    def __repr__(self):
        count = len(sum([list(act.values()) for act in self.actions.values()], []))
        return f"<ActionManager act={count} dyn={len(self.dynamic)} sub={len(self.submanagers)}>"
