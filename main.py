import lzma
import msgpack
from krpg.console import Console
from krpg.encryptor import Encryptor
from krpg.scparse import Command, build, parse, Section


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
        self.get_section = self.scenario.get_section

        self.console = Console()
        self.log = self.console.log
        self.print = self.console.print
        self.prompt = self.console.prompt

    def execute(self, command: Command):
        self.log(f"Executing command: {command.command!r} {command.args!r}")
        c, a, t, ft = (
            command.command,
            command.args,
            command.text[len(command.command) :],
            command.text,
        )
        if c == "print":
            self.print(t)
        elif c == "exec":
            exec(t, globals(), {"ctx": self})
        elif c == "exit":
            self.state = "EXIT"
        elif c == "move":
            self.scenario["data":"one":"section"]["location":"one":"command"].args[
                0
            ] = a[0]

    def main(self):
        self.log(f"Global sections: {len(self.scenario.body)}")

        for cmd in self.scenario["init":"one":"section"][::"command"]:
            self.execute(cmd)

        location = self.scenario["gamemap":"one":"section"][
            "spawn":"one":"command"
        ].args[0]
        self.scenario.body.append(
            Section("data", [Command(f"location {location}"), Command(f"state RUN")])
        )

        get_state = lambda: self.scenario["data":"one":"section"][
            "state":"one":"command"
        ].args[0]
        get_location = lambda: self.scenario["data":"one":"section"][
            "location":"one":"command"
        ].args[0]

        while self.state == "RUN":
            cmd = self.prompt()
            self.execute(Command(cmd))


if __name__ == "__main__":
    Game().main()
