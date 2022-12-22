from krpg.console import Console
from krpg.scparse import parse, Section




class Game:
    commands = []
    def __init__(self):
        self.console = Console()
        scenario = parse(open("scenario.krpg").read())
        self.init_scenario(scenario)
        self.main()
        

    def run_command(self, command):
        if command.command == 'print':
            self.console.print(*command.args)
        else:
            self.console.log(f"Unknown command: {command.command}", 5)
            exit(1)

    def execute(self, commands):
        for command in commands:
            self.run_command(command)
    
    def init_scenario(self, scenario: list[Section]):
        for section in scenario:
            if section.head.command == "init":
                self.execute(section.body)
            elif section.head.command == "map":
                __import__('rich').print(section)
                
    def main(self):
        pass

if __name__ == "__main__":
    Game()
    