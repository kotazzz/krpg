from .scenario import Command

class CommandEngine:
    def __init__(self):
        self.commands = {}
    
    # @register('command') def callback
    def register(self, name: str):
        def decorator(callback):
            self.commands[name] = callback
            return callback
        return decorator
    
    def execute(self, command: Command):
        c, args = command.name, command.args
        if c in self.commands:
            return self.commands[c](*args)
        else:
            raise Exception(f'Unknown command: {c}')

