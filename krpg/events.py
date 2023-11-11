from collections import defaultdict
from queue import Queue
from typing import Callable


class Events:
    # clock.py
    TIMEPASS = "timepass"  # minutes: int
    NEWDAY = "newday"  # day: int

    # game.py
    SAVE = "save"  # -
    LOAD = "load"  # successcb=None
    STATE_CHANGE = "state_change"  # state: str
    COMMAND = "command"  # command: str

    # player.py
    PICKUP = "pickup"  # item: Item, amount: int
    ADD_MONEY = "add_money"  # amount: int, new_balance: int
    REMOVE_MONEY = "remove_money"  # amount: int, new_balance: int
    ADD_FREE = "add_free"  # amount: int, new_balance: int
    REMOVE_FREE = "remove_free"  # amount: int, new_balance: int
    HEAL = "heal"  # amount: int
    DAMAGE = "damage"  # amount: int
    DEAD = "dead"  # -

    # world.py
    WORLD_ITEM_TAKE = "world_item_take"  # item_id: str, remain: int
    WORLD_ITEM_DROP = "world_item_drop"  # item_id: str, count: int
    MOVE = "move"  # before: Location, after: Location

    # settings.py
    SETTING_CHANGE = "setting_change"  # setting: str, value: Any

    # battle.py
    KILL = "kill"  # monster_id: str

    # quests.py
    QUEST_START = "quest_start"  # quest_id: str

    # nps.py
    NPC_MEET = "npc_meet"  # npc_id: str


class EventHandler:
    def __init__(self, locked: bool = False):
        self.listeners: dict[str, list[Callable]] = defaultdict(list)
        self._lock = locked
        self.queue = Queue()

    def unlock(self):
        self._lock = False
        while not self.queue.empty():
            event, args, kwargs = self.queue.get()
            self.dispatch(event, *args, **kwargs)

    def lock(self):
        self._lock = True

    def listen(self, event: str, callback: Callable):
        self.listeners[event].append(callback)

    def dispatch(self, event: str, *args, **kwargs):
        if self._lock:
            self.queue.put((event, args, kwargs))
            return

        for listener in self.listeners["*"] + self.listeners["event"]:
            listener(event, *args, **kwargs)

        if event not in ["*", "event"]:
            for listener in self.listeners[event]:
                listener(*args, **kwargs)

    def __repr__(self):
        return f"<EventHandler listeners={len(self.listeners)}>"
