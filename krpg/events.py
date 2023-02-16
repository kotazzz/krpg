from queue import Queue
from typing import Callable
from collections import defaultdict


class EventHandler:
    def __init__(self, locked: bool = False):
        self.listeners : dict[str, list[Callable]] = defaultdict(list)
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
        
        for listener in self.listeners["*"]+self.listeners["event"]:
            listener(event, *args, **kwargs)
            
        if event not in ["*", "event"]:
            for listener in self.listeners[event]:
                listener(*args, **kwargs)
        