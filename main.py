from __future__ import annotations
import lzma
import msgpack
from krpg.console import Console
from krpg.encryptor import Encryptor
from krpg.scparse import Command, build, parse, Section

class Action:
    def __init__(self, sect: Section):
        self.command = sect.head.args[0]
        self.description = sect.head.args[1]
        self.script = StateScript(sect)
    
    def run(self, game):
        self.script.run(game)
        
    def __repr__(self) -> str:
        return f"<Action {self.command!r}>"
    
class Location:
    def __init__(self, sect: Section):
        self.id = sect.head.args[0]
        self.name = sect.head.args[1]
        self.description = sect.head.args[2]
        self.actions = [Action(a) for a in sect.action]

class Gamemap:
    def __init__(self, sect: Section):
        self.spawn = sect.spawn[0].args[0]
        self.locations = [Location(l) for l in sect.location]
        self.roads = [(i.args[0], i.args[1]) for i in sect.link]

        self.current = self.spawn
    
    def get(self, name):
        for loc in self.locations:
            if loc.id == name:
                return loc
        raise KeyError(f"Location {name!r} not found")
    
    def set(self, name):
        if name not in self.locations:
            raise KeyError(f"Location {name!r} not found")
        self.current = name
    
    def avaliable(self):
        def gen():
            for a, b in self.roads:
                if a == self.current:
                    yield b
                elif b == self.current:
                    yield a
        return list(gen())
    
    def actions(self):
        return self.get(self.current).actions
    
    def __repr__(self):
        return f"<Gamemap {self.current} {len(self.locations)}>"

class StateScript:
    def __init__(self, sect: Section, parrent=None):
        self.parrent = parrent
        self.states = {i.head.args[0]: StateScript(i, self) for i in sect.state}
        self.commands = sect.commands
        self.state = "main"
        self.need_stop = False
    
    @property
    def root(self):
        if self.parrent is None:
            return self
        return self.parrent.root
    
    def all_states(self):
        # return all states starting from root
        states = self.states.copy()
        if self.parrent is not None:
            states.update(self.parrent.all_states())
        return states
    
    def run(self, game):
        states = self.all_states()
        script = states[self.root.state]
        script.execute(game)
    
    def additional(self, game: Game, command: Command):
        game.log(f"2 Executing command: {command.command!r}")
        c, a, t, ft = (
            command.command,
            command.args,
            command.text[len(command.command) :],
            command.text,
        )
        if c == "goto":
            self.root.state = a[0]
            self.run(game)
        elif c == "run":
            states = self.all_states()
            script = states[a[0]]
            script.execute(game)
        elif c == "end":
            self.need_stop = True
            self.root.state = a[0]
    
    def execute(self, game):
        for cmd in self.commands:
            game.execute(cmd, self.additional)
            if self.need_stop:
                self.need_stop = False
                break
            
        
            

class Game:
    def save(self):
        data = self.scenario.save()
        bytedata = msgpack.packb(data, use_bin_type=True)
        zipped = lzma.compress(bytedata)
        encoded = Encryptor().encode(zipped, type=0)
        return encoded

    @classmethod
    def load(cls, data):
        decoded = Encryptor().decode(data, type=0)
        unzipped = lzma.decompress(decoded)
        data = msgpack.unpackb(unzipped, raw=False)

        base = cls()
        base.scenario = Section.load(data)  # TODO: load other data such as location

    def __init__(self):
        self.scenario = parse(open("scenario.krpg").read())
        self.console = Console()
        
        self.get_section = self.scenario.get_section
        self.log = self.console.log
        self.print = self.console.print
        self.prompt = self.console.prompt
        
        s = StateScript(self.scenario.test[0])
        s.run(self)
        print('!!!!!!!!!!!')
        s.run(self)

    def execute(self, command: Command, additional: callable = None):
        self.log(f"Executing command: {command.command!r}")
        c, a, t, ft = (
            command.command,
            command.args,
            command.text[len(command.command) :],
            command.text,
        )
        if c == "print":
            self.print(t)
        elif c == "exec":
            exec(t, globals(), {"game": self})
        elif c == "exit":
            self.state = "EXIT"
        else:
            if additional:
                additional(self, command)
            else:
                raise ValueError(f"Unknown command: {command.command!r}")

    def main(self):
        self.log(f"Global sections: {len(self.scenario.body)}")
        sc = self.scenario
        for cmd in sc.init[0].commands:
            self.execute(cmd)
        
        gm = Gamemap(sc.gamemap[0])
        
        sc.body.append(Section("data", [
            Command(f"location {sc.gamemap[0].spawn[0].args[0]}")
        ]))
        
        print(gm.get(gm.avaliable()[0]).actions)
        


if __name__ == "__main__":
    Game().main()
