from krpg.console import Console
from krpg.scparse import parse, Section

# decorator that have callback and name: @command("name")
def command(name: str):
        def decorator(func):
            func.name = name
            return func
        return decorator
class Commands:
    @command("print")
    def print_command(game, args):
            game.console.print(*args)
    def __init__(self):
        self.commands = {}
        for name, func in self.__class__.__dict__.items():
            if hasattr(func, "name"):
                self.commands[func.name] = func
                
class Game:
    commands = []
    def __init__(self):
        self.console = Console()
        self.commands = Commands()
        
        scenario = parse(open("scenario.krpg").read())
        self.init_scenario(scenario)
        self.main()
        

    def run_command(self, command):
        if command.command in self.commands.commands:
            self.commands.commands[command.command](self, command.args)
        else:
            self.console.print(f"Unknown command: {command.command}")
            exit(1)

    def run_commands(self, commands):
        for command in commands:
            self.run_command(command)
    
    def init_scenario(self, scenario: list[Section]):
        for section in scenario:
            if section.head.command == "init":
                self.run_commands(section.body)
                
    def main(self):
        pass

if __name__ == "__main__":
    Game()
    