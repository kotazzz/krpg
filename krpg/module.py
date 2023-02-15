from __future__ import annotations
class Module:
    requires = []
    
    def __init__(self):
        self._commands = {}
    
    def main(self):
        raise NotImplementedError
    
    def __repr__(self):
        return f"<Module {self.__class__.__name__}>"