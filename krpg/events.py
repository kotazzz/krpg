from collections import defaultdict
from queue import Queue
from typing import Callable

class Events:
    # clock.py
    TIMEPASS = "timepass" # TIMEPASS
    NEWDAY = "newday" # NEWDAY

    # game.py
    SAVE = "save" # SAVE
    LOAD = "load" # LOAD
    LOAD_DONE = "load_done" # LOAD_DONE
    STATE_CHANGE = "state_change" # STATE_CHANGE
    COMMAND = "command" # COMMAND

    # player.py
    PICKUP = "pickup" # PICKUP
    ADD_MONEY = "add_money" # ADD_MONEY
    REMOVE_MONEY = "remove_money" # REMOVE_MONEY
    ADD_FREE = "add_free" # ADD_FREE
    REMOVE_FREE = "remove_free" # REMOVE_FREE

    # world.py
    ITEM_TAKE = "item_take" # ITEM_TAKE
    MOVE = "move" # MOVE

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
