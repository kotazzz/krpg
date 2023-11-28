from collections import defaultdict
from enum import StrEnum, auto
from typing import Callable


class Events(StrEnum):
    # clock.py
    TIMEPASS = auto()  # minutes: int
    NEWDAY = auto()  # day: int

    # game.py
    SAVE = auto()  # -
    LOAD = auto()  # successcb=None
    STATE_CHANGE = auto()  # state: str
    COMMAND = auto()  # command: str

    # player.py
    PICKUP = auto()  # item: Item, amount: int, total: int
    ADD_MONEY = auto()  # amount: int, new_balance: int
    REMOVE_MONEY = auto()  # amount: int, new_balance: int
    ADD_FREE = auto()  # amount: int, new_balance: int
    REMOVE_FREE = auto()  # amount: int, new_balance: int
    HEAL = auto()  # amount: int
    DAMAGE = auto()  # amount: int
    DEAD = auto()  # -

    # world.py
    WORLD_ITEM_TAKE = auto()  # item_id: str, remain: int
    WORLD_ITEM_DROP = auto()  # item_id: str, count: int
    MOVE = auto()  # before: Location, after: Location

    # settings.py
    SETTING_CHANGE = auto()  # setting: str, value: Any

    # battle.py
    KILL = auto()  # monster_id: str

    # quests.py
    QUEST_START = auto()  # quest_id: str
    QUEST_END = auto()  # state: QuestState

    # nps.py
    NPC_MEET = auto()  # npc_id: str
    NPC_STATE = auto()  # npc_id: str, state: str


class EventHandler:
    def __init__(self, *lookup: object):
        self.listeners: dict[str, list[Callable]] = defaultdict(list)
        for obj in lookup:
            self.lookup(obj)

    def listen(self, event: str, callback: Callable):
        self.listeners[event].append(callback)

    def lookup(self, obj: object):
        for attr in filter(lambda x: x.startswith("on_"), dir(obj)):
            cb = getattr(obj, attr)
            if callable(cb):
                self.listen(attr[3:], cb)

    def dispatch(self, event: str, *args, **kwargs):
        for listener in self.listeners["*"] + self.listeners["event"]:
            listener(event, *args, **kwargs)
        if event not in ["*", "event"]:
            for listener in self.listeners[event]:
                listener(*args, **kwargs)

    def __repr__(self):
        return f"<EventHandler listeners={len(self.listeners)}>"
