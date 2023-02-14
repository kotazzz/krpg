from __future__ import annotations
from .module import Module

class Game:
    def __init__(self):
        self.modules = []
        
    def get_modules(self):
        return {
            module.__class__.__name__: module for module in self.modules
        }
    def add_module(self, module: Module):
        self.modules.append(module)
    
    def expand_modules(self, sequence: list):
        self.modules.extend(sequence)
        
    
    def main(self):
        mod = {
            m: m.requires for m in self.modules
        }
        resolved = []
        #FIXME: This is a terrible way to do this
        while len(mod) > 0:
            for module, requires in mod.copy().items():
                if len(requires) == 0:
                    resolved.append(module)
                    del mod[module]
                    continue
                for requirement in requires:
                    if requirement in mod:
                        break
                else:
                    resolved.append(module)
                    del mod[module]
                    
        
        for module in resolved:
            module.load()
            
        
    