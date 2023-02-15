from typing import Callable
from collections import defaultdict


class EventHandler:
    def __init__(self):
        self.listeners : dict[str, list[Callable]] = defaultdict(list)
    
    def listen(self, event: str, callback: Callable):
        self.listeners[event].append(callback)
    
    def dispatch(self, event: str, *args, **kwargs):
        for listener in self.listeners["*"]+self.listeners["event"]:
            listener(event, *args, **kwargs)
            
        if event not in ["*", "event"]:
            for listener in self.listeners[event]:
                listener(*args, **kwargs)
        