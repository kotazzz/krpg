from krpg.console import Console
from krpg.scparse import Command, parse, Section




class Game:
    commands = []
    def __init__(self):
        self.console = Console()
        
        self.locations = {}
        self.roads = {}
        self.state = "RUN"
        
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
                self.map_update(section)
    
    def map_update(self, section: Section):
        for item in section.body:
            if isinstance(item, Section):
                if item.head.command == "location":
                    self.locations[item.head.args[0]] = item
                    continue
            else:
                if item.command == "link":
                    self.roads[(item.args[0], item.args[1])] = True if len(item.args) == 3 else False
                    continue
            self.console.log(f"Unknown map command: {item}", 5)
            exit(1)
        print(self.locations)
    
    
    def gen_panels(self):
        return [
            lambda: "Hello world"
        ]
                
    def main(self):
        while self.state == "RUN":
            self.console.panels = self.gen_panels()
            command = self.console.prompt()
            self.console.panels = []
            if not command.split():
                continue
            names = {i.command: i for i in self.manager.list_actions()}
            if command in names:
                self.handler.event(type="command", command=command, game=self)
                names[command].callback(self)
                self.clock.wait(names[command].time)
            else:
                self.console.print(
                    f"[bold white]Команда {repr(command)} не найдена. Введите help для просмотра списка команд.[/]"
                )
                for category, actions in self.manager.actions().items():
                    self.console.print(f"[bold white]{category}[/]: ", end="")
                    self.console.print(
                        ", ".join(f"[green]{action.command}[/]" for action in actions)
                    )

if __name__ == "__main__":
    try:
        Game()
    except KeyboardInterrupt:
        print("Bye!")
    except Exception as e:
        print('\033[0m')
        raise e from None
    