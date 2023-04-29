from collections import defaultdict
from queue import Queue
from typing import Callable

class Events:
    # clock.py
    TIMEPASS = "timepass"
    NEWDAY = "newday"

    # game.py
    SAVE = "save"
    LOAD = "load"
    LOAD_DONE = "load_done"
    STATE_CHANGE = "state_change"
    COMMAND = "command"

    # player.py
    PICKUP = "pickup"
    ADD_MONEY = "add_money"
    REMOVE_MONEY = "remove_money"
    ADD_FREE = "add_free"
    REMOVE_FREE = "remove_free"
    HEAL = "heal"

    # world.py
    ITEM_TAKE = "item_take"
    ITEM_DROP = "item_drop"
    MOVE = "move"

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
