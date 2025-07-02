from __future__ import annotations

from enum import Enum, StrEnum
from typing import TYPE_CHECKING, Any, Callable

import attr

if TYPE_CHECKING:
    from krpg.game import Game


class ActionCategory(StrEnum):
    GAME = "Игра"
    PLAYER = "Игрок"
    INFO = "Информация"
    OTHER = "Другое"
    NOT_SET = "Не установлено"
    DEBUG = "Отладка"
    ACTION = "Действие"

class ActionState(Enum):
    ACTIVE = "Активно"
    LOCKED = "Заблокировано"
    HIDDEN = "Скрыто"

type ActionCallback = Callable[[Game], Any]


@attr.s(auto_attribs=True)
class Action:
    name: str
    description: str
    category: ActionCategory | str
    callback: ActionCallback = attr.ib(repr=False)
    check: Callable[[Game], ActionState] = lambda game: ActionState.ACTIVE


def action(
    name: str,
    description: str = "No description",
    category: ActionCategory = ActionCategory.NOT_SET,
) -> Callable[[ActionCallback], Action]:
    def decorator(callback: ActionCallback) -> Action:
        return Action(name, description, category, callback)

    return decorator

# TODO: Unused code
def merge_actions(*managers: ActionManager) -> dict[str, Action]:
    actions: dict[str, Action] = {}
    for manager in managers:
        for act in manager.actions:
            if act.name in actions:
                raise ValueError(f"Action with name {act.name} already exists")
            actions[act.name] = act
    return actions


class ActionManager:
    def __init__(self) -> None:
        self.submanagers: list[ActionManager] = []
        self._actions: list[Action] = []

        for attrib in dir(self):
            if attrib == "actions":
                continue
            get = getattr(self, attrib)
            if isinstance(get, Action):
                if get in self._actions:
                    raise ValueError(f"Action with name {get.name} already exists")
                self._actions.append(get)

    @property
    def actions(self) -> list[Action]:
        actions = self._actions.copy()
        actions.extend(self.extract()) # TODO: Unused code
        for manager in self.submanagers:
            actions.extend(manager.actions)
        return actions

    def extract(self) -> list[Action]:
        return []

    def __repr__(self) -> str:
        return f"<ActionManager act={len(self.actions)}>"
