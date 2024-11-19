from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable


class ActionCategory(StrEnum):
    GAME = "Игра"
    PLAYER = "Игрок"
    INFO = "Информация"
    OTHER = "Другое"
    NOT_SET = "Не установлено"
    DEBUG = "Отладка"


@dataclass()
class Action:
    name: str
    description: str
    category: ActionCategory | str
    callback: Callable[..., Any]

    def __repr__(self) -> str:
        return f"<Action {self.name} from {self.category}>"


def action(name: str, description: str = "No description", category: ActionCategory = ActionCategory.NOT_SET) -> Callable[..., Action]:
    def decorator(callback: Callable[..., Any]) -> Action:
        return Action(name, description, category, callback)

    return decorator


def merge_actions(*managers: ActionManager) -> dict[str, Action]:
    actions: dict[str, Action] = {}
    for manager in managers:
        for name, act in manager.actions.items():
            if name in actions:
                raise ValueError(f"Action with name {name} already exists")
            actions[name] = act
    return actions


class ActionManager:
    def __init__(self) -> None:
        self.submanagers: list[ActionManager] = []
        self._actions: list[Action] = []

        for attr in dir(self):
            if attr == "actions":
                continue
            get = getattr(self, attr)
            if isinstance(get, Action):
                if get in self._actions:
                    raise ValueError(f"Action with name {get.name} already exists")
                self._actions.append(get)

    @property
    def actions(self) -> dict[str, Action]:
        actions = self._actions.copy()
        actions.extend(self.extract())
        for manager in self.submanagers:
            actions.extend(manager.actions.values())
        return {act.name: act for act in actions}

    def extract(self) -> list[Action]:
        return []

    def __repr__(self) -> str:
        return f"<ActionManager act={len(self.actions)}>"
